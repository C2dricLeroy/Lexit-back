from contextlib import asynccontextmanager
from logging import INFO, basicConfig, getLogger

from fastapi import FastAPI

from app import models  # noqa: F401
from app.config import settings
from app.database import init_db
from app.routes import country, language


def get_app() -> FastAPI:
    """Return the fastapi App instance."""
    fastapi_app = FastAPI(
        title=f"{settings.APP_NAME} ({settings.ENV})",
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


app = get_app()


app.include_router(
    language.router,
    prefix=f"/{settings.API_VERSION}/language",
    tags=["Language"],
)
app.include_router(
    country.router,
    prefix=f"/{settings.API_VERSION}/country",
    tags=["Country"],
)


@app.get("/")
def read_root():
    """Root Method."""
    return {
        "env": settings.ENV,
        "debug": settings.DEBUG,
        "message": "Hello from Lexit!",
    }
