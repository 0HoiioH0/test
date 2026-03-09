from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"


class Config(BaseSettings):
    # App
    ENV: Env = Env.DEV
    APP_NAME: str = "Development Outsourcing Platform"
    APP_DESCRIPTION: str = "LLM 기반 외주 고도화 플랫폼 백엔드"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    DOCS_URL: str | None = "/docs"
    REDOC_URL: str | None = "/redoc"
    OPENAPI_URL: str | None = "/openapi.json"
    ALGORITHM: str = "HS256"

    # JWT
    ACCESS_TOKEN_SECRET_KEY: str = "very-secret-key-change-it-in-prod"
    REFRESH_TOKEN_SECRET_KEY: str = "very-secret-key-change-it-in-prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080

    # RDBMS
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"

    # In-Memory Database
    VALKEY_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


config = Config()


def get_env() -> Env:
    return config.ENV
