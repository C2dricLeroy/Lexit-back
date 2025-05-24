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
    API_VERSION: str = "api/v1"

    @property
    def database_url(self) -> str:
        """Returns the database URL."""
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}" f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        """Defines the environement file."""

        env_file = ".env"


settings = Settings()
