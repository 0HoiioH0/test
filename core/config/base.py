from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    ENV: str = "dev"

    # App
    APP_NAME: str = "Development Outsourcing Platform"
    APP_DESCRIPTION: str = "LLM 기반 외주 고도화 플랫폼 백엔드"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    DOCS_URL: str | None = "/api/docs"
    REDOC_URL: str | None = "/api/redoc"
    OPENAPI_URL: str | None = "/api/openapi.json"

    # Auth
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_SECRET_KEY: str = "very-secret-key-change-it-in-prod"
    REFRESH_TOKEN_SECRET_KEY: str = "very-secret-key-change-it-in-prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080

    # App runtime
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"
    VALKEY_URL: str = "redis://localhost:6379/0"
