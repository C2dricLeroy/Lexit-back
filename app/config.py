from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = Field(default="PROD", env="ENVIRONMENT")
    APP_NAME: str = "Lexit"
    DB_USER: str = "fastapi"
    DB_PASSWORD: str = "fastapi"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "fastapi"
    API_VERSION: str = "api/v1"
    JWT_SECRET_KEY: str = Field(default="secret", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    @property
    def DEBUG(self) -> bool:
        """Returns True if DEBUG mode is enabled."""
        return self.ENV != "PROD"

    @property
    def database_url(self) -> str:
        """Returns the database URL."""
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
