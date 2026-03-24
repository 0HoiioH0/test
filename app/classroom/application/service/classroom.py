from uuid import UUID

from app.classroom.application.exception import (
    ClassroomCodeAlreadyExistsException,
    ClassroomNotFoundException,
)
from app.classroom.domain.command import (
    CreateClassroomCommand,
    UpdateClassroomCommand,
)
from app.classroom.domain.entity import Classroom
from app.classroom.domain.repository import ClassroomRepository
from app.classroom.domain.usecase import ClassroomUseCase
from core.db.transactional import transactional


class ClassroomService(ClassroomUseCase):
    def __init__(self, *, repository: ClassroomRepository):
        self.repository = repository

    @transactional
    async def create_classroom(
        self,
        command: CreateClassroomCommand,
    ) -> Classroom:
        existing_classroom = await self.repository.get_by_organization_and_code(
            command.organization_id,
            command.code,
        )
        if existing_classroom is not None:
            raise ClassroomCodeAlreadyExistsException()

        classroom = Classroom(
            organization_id=command.organization_id,
            instructor_id=command.instructor_id,
            code=command.code,
            name=command.name,
            term=command.term,
            section=command.section,
            description=command.description,
            is_active=command.is_active,
        )
        return await self.repository.save(classroom)

    async def get_classroom(self, classroom_id: UUID) -> Classroom:
        classroom = await self.repository.get_by_id(classroom_id)
        if classroom is None:
            raise ClassroomNotFoundException()
        return classroom

    async def list_classrooms(self, organization_id: UUID) -> list[Classroom]:
        return await self.repository.list_by_organization(organization_id)

    @transactional
    async def update_classroom(
        self,
        classroom_id: UUID,
        command: UpdateClassroomCommand,
    ) -> Classroom:
        classroom = await self.get_classroom(classroom_id)
        delivered_fields = command.model_fields_set

        if (
            "code" in delivered_fields
            and command.code is not None
            and command.code != classroom.code
        ):
            existing_classroom = (
                await self.repository.get_by_organization_and_code(
                    classroom.organization_id,
                    command.code,
                )
            )
            if existing_classroom is not None:
                raise ClassroomCodeAlreadyExistsException()
            classroom.code = command.code

        if "name" in delivered_fields and command.name is not None:
            classroom.name = command.name
        if "term" in delivered_fields and command.term is not None:
            classroom.term = command.term
        if "section" in delivered_fields:
            classroom.section = command.section
        if "description" in delivered_fields:
            classroom.description = command.description
        if "is_active" in delivered_fields and command.is_active is not None:
            classroom.is_active = command.is_active

        return await self.repository.save(classroom)

    @transactional
    async def delete_classroom(self, classroom_id: UUID) -> Classroom:
        classroom = await self.get_classroom(classroom_id)
        classroom.delete()
        return await self.repository.save(classroom)
