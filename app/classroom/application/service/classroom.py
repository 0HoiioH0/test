from collections.abc import Iterable
from uuid import UUID

from app.classroom.application.exception import (
    ClassroomAlreadyExistsException,
    ClassroomInvalidProfessorRoleException,
    ClassroomInvalidStudentRoleException,
    ClassroomNotFoundException,
    ClassroomProfessorNotFoundException,
    ClassroomStudentNotFoundException,
)
from app.classroom.domain.command import (
    CreateClassroomCommand,
    UpdateClassroomCommand,
)
from app.classroom.domain.entity import Classroom
from app.classroom.domain.repository import ClassroomRepository
from app.classroom.domain.usecase import ClassroomUseCase
from app.user.domain.entity import User, UserRole
from app.user.domain.repository import UserRepository
from core.db.transactional import transactional


class ClassroomService(ClassroomUseCase):
    def __init__(
        self,
        *,
        repository: ClassroomRepository,
        user_repository: UserRepository,
    ):
        self.repository = repository
        self.user_repository = user_repository

    @transactional
    async def create_classroom(
        self,
        command: CreateClassroomCommand,
    ) -> Classroom:
        professor_ids = _unique_ids(command.professor_ids)
        student_ids = _unique_ids(command.student_ids)

        await self._validate_members(
            organization_id=command.organization_id,
            professor_ids=professor_ids,
            student_ids=student_ids,
        )

        existing_classroom = (
            await self.repository.get_by_organization_and_name_and_term(
                command.organization_id,
                command.name,
                command.grade,
                command.semester,
                command.section,
            )
        )
        if existing_classroom is not None:
            raise ClassroomAlreadyExistsException()

        classroom = Classroom(
            command.organization_id,
            name=command.name,
            professor_ids=professor_ids,
            grade=command.grade,
            semester=command.semester,
            section=command.section,
            description=command.description,
            student_ids=student_ids,
        )
        return await self.repository.save(classroom)

    async def get_classroom(self, classroom_id: UUID) -> Classroom:
        classroom = await self.repository.get_by_id(classroom_id)
        if classroom is None:
            raise ClassroomNotFoundException()
        return classroom

    async def list_classrooms(self, organization_id: UUID) -> list[Classroom]:
        return list(await self.repository.list_by_organization(organization_id))

    @transactional
    async def update_classroom(
        self,
        classroom_id: UUID,
        command: UpdateClassroomCommand,
    ) -> Classroom:
        classroom = await self.get_classroom(classroom_id)
        delivered_fields = command.model_fields_set

        name = classroom.name
        if "name" in delivered_fields and command.name is not None:
            name = command.name

        grade = classroom.grade
        if "grade" in delivered_fields and command.grade is not None:
            grade = command.grade

        semester = classroom.semester
        if "semester" in delivered_fields and command.semester is not None:
            semester = command.semester

        section = classroom.section
        if "section" in delivered_fields and command.section is not None:
            section = command.section

        if (
            name != classroom.name
            or grade != classroom.grade
            or semester != classroom.semester
            or section != classroom.section
        ):
            existing_classroom = (
                await self.repository.get_by_organization_and_name_and_term(
                    classroom.organization_id,
                    name,
                    grade,
                    semester,
                    section,
                )
            )
            if (
                existing_classroom is not None
                and existing_classroom.id != classroom.id
            ):
                raise ClassroomAlreadyExistsException()

        professor_ids = classroom.professor_ids
        if (
            "professor_ids" in delivered_fields
            and command.professor_ids is not None
        ):
            professor_ids = _unique_ids(command.professor_ids)

        student_ids = classroom.student_ids
        if (
            "student_ids" in delivered_fields
            and command.student_ids is not None
        ):
            student_ids = _unique_ids(command.student_ids)

        await self._validate_members(
            organization_id=classroom.organization_id,
            professor_ids=professor_ids,
            student_ids=student_ids,
        )

        classroom.name = name
        classroom.grade = grade
        classroom.semester = semester
        classroom.section = section
        if "description" in delivered_fields:
            classroom.description = command.description
        classroom.professor_ids = professor_ids
        classroom.student_ids = student_ids

        return await self.repository.save(classroom)

    @transactional
    async def delete_classroom(self, classroom_id: UUID) -> Classroom:
        classroom = await self.get_classroom(classroom_id)
        await self.repository.delete(classroom)
        return classroom

    async def _validate_members(
        self,
        *,
        organization_id: UUID,
        professor_ids: list[UUID],
        student_ids: list[UUID],
    ) -> None:
        users = await self.user_repository.list()
        users_by_id = {
            user.id: user
            for user in users
            if user.organization_id == organization_id and not user.is_deleted
        }

        self._validate_professors(users_by_id, professor_ids)
        self._validate_students(users_by_id, student_ids)

    @staticmethod
    def _validate_professors(
        users_by_id: dict[UUID, User],
        professor_ids: list[UUID],
    ) -> None:
        missing_ids = [
            user_id for user_id in professor_ids if user_id not in users_by_id
        ]
        if missing_ids:
            raise ClassroomProfessorNotFoundException(
                detail={
                    "professor_ids": [str(user_id) for user_id in missing_ids]
                }
            )

        invalid_ids = [
            user_id
            for user_id in professor_ids
            if users_by_id[user_id].role != UserRole.PROFESSOR
        ]
        if invalid_ids:
            raise ClassroomInvalidProfessorRoleException(
                detail={
                    "professor_ids": [str(user_id) for user_id in invalid_ids]
                }
            )

    @staticmethod
    def _validate_students(
        users_by_id: dict[UUID, User],
        student_ids: list[UUID],
    ) -> None:
        missing_ids = [
            user_id for user_id in student_ids if user_id not in users_by_id
        ]
        if missing_ids:
            raise ClassroomStudentNotFoundException(
                detail={
                    "student_ids": [str(user_id) for user_id in missing_ids]
                }
            )

        invalid_ids = [
            user_id
            for user_id in student_ids
            if users_by_id[user_id].role != UserRole.STUDENT
        ]
        if invalid_ids:
            raise ClassroomInvalidStudentRoleException(
                detail={
                    "student_ids": [str(user_id) for user_id in invalid_ids]
                }
            )


def _unique_ids(user_ids: Iterable[UUID]) -> list[UUID]:
    return list(dict.fromkeys(user_ids))
