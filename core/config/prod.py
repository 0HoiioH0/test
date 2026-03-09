from pydantic_settings import SettingsConfigDict

from .base import CommonSettings


class ProdSettings(CommonSettings):
    ENV: str = "prod"
    DEBUG: bool = False
    DOCS_URL: str | None = None
    REDOC_URL: str | None = None
    OPENAPI_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
