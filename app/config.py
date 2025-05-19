import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "DEV")
    DEBUG: bool = ENV != "PROD"
    APP_NAME: str = "Lexit"
    DB_USER: str = "fastapi"
    DB_PASSWORD: str = "fastapi"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "fastapi"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
