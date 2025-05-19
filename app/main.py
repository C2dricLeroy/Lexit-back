from fastapi import FastAPI
from app.config import settings
from contextlib import asynccontextmanager
from app.database import init_db

app = FastAPI(title=f"{settings.APP_NAME} ({settings.ENV})", debug=settings.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


@app.get("/")
def read_root():
    return {
        "env": settings.ENV,
        "debug": settings.DEBUG,
        "message": "Hello from Lexit!"
    }
