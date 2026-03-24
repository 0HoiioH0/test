from collections.abc import Sequence
from uuid import UUID, uuid4

import pytest

from app.classroom.application.exception import (
    ClassroomCodeAlreadyExistsException,
    ClassroomNotFoundException,
)
from app.classroom.application.service import ClassroomService
from app.classroom.domain.command import (
    CreateClassroomCommand,
    UpdateClassroomCommand,
)
from app.classroom.domain.entity import Classroom
from app.classroom.domain.repository import ClassroomRepository

ORG_ID = UUID("11111111-1111-1111-1111-111111111111")
USER_ID = UUID("22222222-2222-2222-2222-222222222222")


class InMemoryClassroomRepository(ClassroomRepository):
    def __init__(self, classrooms: list[Classroom] | None = None):
        self.classrooms = {
            classroom.id: classroom for classroom in classrooms or []
        }

    async def save(self, entity: Classroom) -> Classroom:
        self.classrooms[entity.id] = entity
        return entity

    async def get_by_id(self, entity_id: UUID) -> Classroom | None:
        return self.classrooms.get(entity_id)

    async def list(self) -> list[Classroom]:
        return list(self.classrooms.values())

    async def get_by_organization_and_code(
        self,
        organization_id: UUID,
        code: str,
    ) -> Classroom | None:
        return next(
            (
                classroom
                for classroom in self.classrooms.values()
                if classroom.organization_id == organization_id
                and classroom.code == code
            ),
            None,
        )

    async def list_by_organization(
        self,
        organization_id: UUID,
    ) -> Sequence[Classroom]:
        return [
            classroom
            for classroom in self.classrooms.values()
            if classroom.organization_id == organization_id
        ]


def make_classroom() -> Classroom:
    classroom = Classroom(
        organization_id=ORG_ID,
        instructor_id=USER_ID,
        code="ai-101",
        name="AI 기초",
        term="2026-1",
        section="01",
        description="AI 입문 강의실",
    )
    classroom.id = UUID("33333333-3333-3333-3333-333333333333")
    return classroom


@pytest.mark.asyncio
async def test_create_classroom_success():
    service = ClassroomService(repository=InMemoryClassroomRepository())

    classroom = await service.create_classroom(
        CreateClassroomCommand(
            organization_id=ORG_ID,
            instructor_id=USER_ID,
            code="ai-101",
            name="AI 기초",
            term="2026-1",
            section="01",
            description="AI 입문 강의실",
        )
    )

    assert classroom.code == "ai-101"
    assert classroom.organization_id == ORG_ID


@pytest.mark.asyncio
async def test_create_classroom_duplicate_code_raises():
    service = ClassroomService(
        repository=InMemoryClassroomRepository([make_classroom()])
    )

    with pytest.raises(ClassroomCodeAlreadyExistsException):
        await service.create_classroom(
            CreateClassroomCommand(
                organization_id=ORG_ID,
                instructor_id=USER_ID,
                code="ai-101",
                name="다른 강의실",
                term="2026-1",
            )
        )


@pytest.mark.asyncio
async def test_list_classrooms_returns_organization_classrooms():
    service = ClassroomService(
        repository=InMemoryClassroomRepository([make_classroom()])
    )

    classrooms = await service.list_classrooms(ORG_ID)

    assert len(classrooms) == 1
    assert classrooms[0].name == "AI 기초"


@pytest.mark.asyncio
async def test_get_classroom_not_found_raises():
    service = ClassroomService(repository=InMemoryClassroomRepository())

    with pytest.raises(ClassroomNotFoundException):
        await service.get_classroom(uuid4())


@pytest.mark.asyncio
async def test_update_classroom_success():
    service = ClassroomService(
        repository=InMemoryClassroomRepository([make_classroom()])
    )

    classroom = await service.update_classroom(
        UUID("33333333-3333-3333-3333-333333333333"),
        UpdateClassroomCommand(
            name="AI 심화",
            description=None,
            is_active=False,
        ),
    )

    assert classroom.name == "AI 심화"
    assert classroom.description is None
    assert classroom.is_active is False


@pytest.mark.asyncio
async def test_update_classroom_duplicate_code_raises():
    another_classroom = Classroom(
        organization_id=ORG_ID,
        instructor_id=USER_ID,
        code="ai-102",
        name="다른 강의실",
        term="2026-1",
    )
    another_classroom.id = uuid4()
    service = ClassroomService(
        repository=InMemoryClassroomRepository([
            make_classroom(),
            another_classroom,
        ])
    )

    with pytest.raises(ClassroomCodeAlreadyExistsException):
        await service.update_classroom(
            another_classroom.id,
            UpdateClassroomCommand(code="ai-101"),
        )


@pytest.mark.asyncio
async def test_delete_classroom_sets_inactive():
    service = ClassroomService(
        repository=InMemoryClassroomRepository([make_classroom()])
    )

    classroom = await service.delete_classroom(
        UUID("33333333-3333-3333-3333-333333333333")
    )

    assert classroom.is_active is False
