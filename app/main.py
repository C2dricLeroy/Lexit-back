from fastapi import FastAPI
from app.config import settings
from contextlib import asynccontextmanager
from app.database import init_db
from logging import INFO, basicConfig, getLogger
from fastapi import Depends
from sqlmodel import Session
from .database import get_session
from sqlalchemy import text
from app.models.user import User
from app.models.language import Language
from app.models.entry import Entry
from app.models.dictionary import Dictionary
from app.models.description import Description
from app.models.dictionaryEntry import DictionaryEntryLink
from app.models.country import Country
from app.models.countryLanguage import CountryLanguageLink
from app.routes import language


def get_app() -> FastAPI:
    app = FastAPI(title=f"{settings.APP_NAME} ({settings.ENV})", debug=settings.DEBUG, lifespan=lifespan)
    return app

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

app.include_router(language.router, prefix="/language", tags=["Languages"])

@app.get("/test-db")
def test_db(session: Session = Depends(get_session)):
    result = session.exec(text("SELECT 1"))
    return {"result": result.scalar()}


@app.get("/")
def read_root():
    return {
        "env": settings.ENV,
        "debug": settings.DEBUG,
        "message": "Hello from Lexit!"
    }
