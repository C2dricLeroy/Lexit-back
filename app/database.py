from logging import getLogger
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

log = getLogger(__name__)

engine = create_engine(settings.database_url)

Base = SQLModel


def init_db():
    """Initialize the database."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, Session, None]:
    """Return a generator for a database session to be used in routers."""
    log.info("Initialising database session...")
    with Session(engine) as session:
        yield session
