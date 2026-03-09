import os
from enum import StrEnum
from functools import lru_cache

from .base import CommonSettings
from .dev import DevSettings
from .local import LocalSettings
from .prod import ProdSettings
from .stage import StageSettings
from .test import TestSettings

Config = CommonSettings


class Env(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    STAGE = "stage"
    TEST = "test"
    PROD = "prod"


def get_env() -> Env:
    value = os.getenv("ENV", Env.DEV.value)
    return Env(value)


@lru_cache
def get_settings() -> CommonSettings:
    match get_env():
        case Env.PROD:
            return ProdSettings()
        case Env.STAGE:
            return StageSettings()
        case Env.TEST:
            return TestSettings()
        case Env.LOCAL:
            return LocalSettings()
        case _:
            return DevSettings()


config = get_settings()
