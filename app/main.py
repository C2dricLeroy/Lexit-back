from fastapi import FastAPI
from app.config import settings
from contextlib import asynccontextmanager
from app.database import init_db
from logging import INFO, basicConfig, getLogger

def get_app() -> FastAPI:
    app = FastAPI(title=f"{settings.APP_NAME} ({settings.ENV})", debug=settings.DEBUG)
    # app.include_router(product.router)
    return app

FastAPI(title=f"{settings.APP_NAME} ({settings.ENV})", debug=settings.DEBUG)

logger = getLogger(__name__)
basicConfig(level=INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    init_db()
    yield
    logger.info("Shutting down...")
    logger.info("Finished shutting down.")

app = get_app()


@app.get("/")
def read_root():
    return {
        "env": settings.ENV,
        "debug": settings.DEBUG,
        "message": "Hello from Lexit!"
    }
