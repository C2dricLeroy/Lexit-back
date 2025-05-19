from sqlmodel import SQLModel, create_engine
from app.config import settings

engine = create_engine(settings.database_url, echo=settings.DEBUG)

def init_db():
    SQLModel.metadata.create_all(engine)
