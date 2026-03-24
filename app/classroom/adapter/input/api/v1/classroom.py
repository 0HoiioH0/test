from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.auth.adapter.input.api.v1.deps import (
    require_authenticated_user,
    require_professor_or_admin_user,
)
from app.auth.application.exception import AuthForbiddenException
from app.auth.domain.entity import CurrentUser
from app.classroom.adapter.input.api.v1.request import (
    CreateClassroomRequest,
    UpdateClassroomRequest,
)
from app.classroom.adapter.input.api.v1.response import (
    ClassroomListResponse,
    ClassroomPayload,
    ClassroomResponse,
)
from app.classroom.container import ClassroomContainer
from app.classroom.domain.command import (
    CreateClassroomCommand,
    UpdateClassroomCommand,
)
from app.classroom.domain.entity import Classroom
from app.classroom.domain.usecase import ClassroomUseCase
from app.user.domain.entity import UserRole

router = APIRouter(prefix="/classrooms", tags=["classrooms"])


def _to_payload(classroom: Classroom) -> ClassroomPayload:
    return ClassroomPayload(
        id=str(classroom.id),
        name=classroom.name,
        professor_ids=[str(user_id) for user_id in classroom.professor_ids],
        grade=classroom.grade,
        semester=classroom.semester,
        section=classroom.section,
        description=classroom.description,
        student_ids=[str(user_id) for user_id in classroom.student_ids],
    )


def _ensure_same_organization(
    classroom: Classroom,
    current_user: CurrentUser,
) -> None:
    if classroom.organization_id != current_user.organization_id:
        raise AuthForbiddenException()


def _ensure_classroom_manager(
    classroom: Classroom,
    current_user: CurrentUser,
) -> None:
    _ensure_same_organization(classroom, current_user)

    if current_user.role == UserRole.ADMIN:
        return
    if current_user.id in classroom.professor_ids:
        return

    raise AuthForbiddenException()


def _can_access_classroom(
    classroom: Classroom,
    current_user: CurrentUser,
) -> bool:
    if classroom.organization_id != current_user.organization_id:
        return False
    if current_user.role == UserRole.ADMIN:
        return True
    if current_user.role == UserRole.PROFESSOR:
        return current_user.id in classroom.professor_ids
    return current_user.id in classroom.student_ids


def _professor_ids_for_create(
    request: CreateClassroomRequest,
    current_user: CurrentUser,
) -> list[UUID]:
    professor_ids = list(request.professor_ids)
    if (
        current_user.role == UserRole.PROFESSOR
        and current_user.id not in professor_ids
    ):
        professor_ids.append(current_user.id)
    return professor_ids


def _professor_ids_for_update(
    professor_ids: list[UUID] | None,
    current_user: CurrentUser,
) -> list[UUID] | None:
    if professor_ids is None:
        return None

    professor_ids = list(professor_ids)
    if (
        current_user.role == UserRole.PROFESSOR
        and current_user.id not in professor_ids
    ):
        professor_ids.append(current_user.id)
    return professor_ids


def _build_update_command(
    request: UpdateClassroomRequest,
    current_user: CurrentUser,
) -> UpdateClassroomCommand:
    payload = request.model_dump(exclude_unset=True)
    if "professor_ids" in payload:
        payload["professor_ids"] = _professor_ids_for_update(
            payload["professor_ids"],
            current_user,
        )
    return UpdateClassroomCommand(**payload)


@router.post("", response_model=ClassroomResponse)
@inject
async def create_classroom(
    request: CreateClassroomRequest,
    current_user: CurrentUser = Depends(require_professor_or_admin_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classroom = await usecase.create_classroom(
        CreateClassroomCommand(
            organization_id=current_user.organization_id,
            name=request.name,
            professor_ids=_professor_ids_for_create(request, current_user),
            grade=request.grade,
            semester=request.semester,
            section=request.section,
            description=request.description,
            student_ids=request.student_ids,
        )
    )
    return ClassroomResponse(data=_to_payload(classroom))


@router.get("", response_model=ClassroomListResponse)
@inject
async def list_classrooms(
    current_user: CurrentUser = Depends(require_authenticated_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classrooms = await usecase.list_classrooms(current_user.organization_id)
    return ClassroomListResponse(
        data=[
            _to_payload(classroom)
            for classroom in classrooms
            if _can_access_classroom(classroom, current_user)
        ]
    )


@router.get("/{classroom_id}", response_model=ClassroomResponse)
@inject
async def get_classroom(
    classroom_id: UUID,
    current_user: CurrentUser = Depends(require_authenticated_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classroom = await usecase.get_classroom(classroom_id)
    if not _can_access_classroom(classroom, current_user):
        raise AuthForbiddenException()
    return ClassroomResponse(data=_to_payload(classroom))


@router.patch("/{classroom_id}", response_model=ClassroomResponse)
@inject
async def update_classroom(
    classroom_id: UUID,
    request: UpdateClassroomRequest,
    current_user: CurrentUser = Depends(require_professor_or_admin_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classroom = await usecase.get_classroom(classroom_id)
    _ensure_classroom_manager(classroom, current_user)
    classroom = await usecase.update_classroom(
        classroom_id,
        _build_update_command(request, current_user),
    )
    return ClassroomResponse(data=_to_payload(classroom))


@router.delete("/{classroom_id}", response_model=ClassroomResponse)
@inject
async def delete_classroom(
    classroom_id: UUID,
    current_user: CurrentUser = Depends(require_professor_or_admin_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classroom = await usecase.get_classroom(classroom_id)
    _ensure_classroom_manager(classroom, current_user)
    classroom = await usecase.delete_classroom(classroom_id)
    return ClassroomResponse(data=_to_payload(classroom))
