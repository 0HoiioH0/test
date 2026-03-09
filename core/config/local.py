from pydantic_settings import SettingsConfigDict

from .base import CommonSettings


class LocalSettings(CommonSettings):
    ENV: str = "local"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
