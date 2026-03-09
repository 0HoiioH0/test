from pydantic_settings import SettingsConfigDict

from .base import CommonSettings


class DevSettings(CommonSettings):
    ENV: str = "dev"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.dev"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
