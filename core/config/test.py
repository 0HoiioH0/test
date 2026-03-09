from pydantic_settings import SettingsConfigDict

from .base import CommonSettings


class TestSettings(CommonSettings):
    ENV: str = "test"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.test"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
