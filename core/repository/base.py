from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import UUID

from core.common.entity import Entity

T = TypeVar("T", bound=Entity)


class BaseRepository(Generic[T], ABC):
    @abstractmethod
    async def save(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        pass

    @abstractmethod
    async def list(self) -> Sequence[T]:
        pass

    @abstractmethod
    async def delete(self, entity: T) -> None:
        pass
