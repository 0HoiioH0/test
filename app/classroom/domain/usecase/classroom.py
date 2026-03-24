from abc import ABC, abstractmethod
from uuid import UUID

from app.classroom.domain.command import (
    CreateClassroomCommand,
    UpdateClassroomCommand,
)
from app.classroom.domain.entity import Classroom


class ClassroomUseCase(ABC):
    @abstractmethod
    async def create_classroom(
        self,
        command: CreateClassroomCommand,
    ) -> Classroom:
        """Create classroom."""

    @abstractmethod
    async def get_classroom(self, classroom_id: UUID) -> Classroom:
        """Get classroom."""

    @abstractmethod
    async def list_classrooms(
        self,
        organization_id: UUID,
    ) -> list[Classroom]:
        """List classrooms for organization."""

    @abstractmethod
    async def update_classroom(
        self,
        classroom_id: UUID,
        command: UpdateClassroomCommand,
    ) -> Classroom:
        """Update classroom."""

    @abstractmethod
    async def delete_classroom(self, classroom_id: UUID) -> Classroom:
        """Delete classroom."""
