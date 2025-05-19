from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from logging import INFO, basicConfig, getLogger
from app.config import settings

log = getLogger(__name__)
basicConfig(level=INFO)

engine = create_engine(settings.database_url, echo=settings.DEBUG)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, Session, None]:
    """
    Generator for a database session to be used in routers.

    Return: Database session generator
    """

    log.info("Initialising database session...")
    with Session(engine) as session:
        yield session