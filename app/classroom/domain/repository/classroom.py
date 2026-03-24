from abc import abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.classroom.domain.entity import Classroom
from core.repository.base import BaseRepository


class ClassroomRepository(BaseRepository[Classroom]):
    @abstractmethod
    async def get_by_organization_and_code(
        self,
        organization_id: UUID,
        code: str,
    ) -> Classroom | None:
        pass

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: UUID,
    ) -> Sequence[Classroom]:
        pass
