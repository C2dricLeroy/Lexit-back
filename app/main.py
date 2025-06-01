import importlib
import pkgutil
from contextlib import asynccontextmanager
from logging import INFO, basicConfig, getLogger

from fastapi import FastAPI

from app import models  # noqa: F401
from app.config import settings
from app.database import init_db
from app.routes import __name__ as routes_pkg
from app.routes import __path__ as routes_path
from app.routes import country


def get_app() -> FastAPI:
    """Return the fastapi App instance."""
    fastapi_app = FastAPI(
        title=f"{settings.APP_NAME} ({settings.ENV})",
        docs_url=None if settings.ENV == "PROD" else "/docs",
        redoc_url=None if settings.ENV == "PROD" else "/redoc",
        openapi_url=None if settings.ENV == "PROD" else "/openapi.json",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    return fastapi_app


basicConfig(level=INFO)
_logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database at startup."""
    _logger.info("Starting up...")
    init_db()

    data = country.load_csv_at_startup()
    _logger.info("CSV loaded with %s rows", len(data))
    yield
    _logger.info("Shutting down...")
    _logger.info("Finished shutting down.")


def include_all_routers(app: FastAPI):
    """Import all routers from the routes package."""
    for _, module_name, _ in pkgutil.iter_modules(routes_path):
        full_module_name = f"{routes_pkg}.{module_name}"
        module = importlib.import_module(full_module_name)

        if hasattr(module, "router"):
            router = getattr(module, "router")  # noqa: B009
            app.include_router(
                router,
                prefix=f"/{settings.API_VERSION}/{module_name}",
                tags=[module_name.capitalize()],
            )


app = get_app()
include_all_routers(app)


@app.get("/")
def read_root():
    """Root Method."""
    return {
        "env": settings.ENV,
        "debug": settings.DEBUG,
        "message": "Hello from Lexit!",
    }
