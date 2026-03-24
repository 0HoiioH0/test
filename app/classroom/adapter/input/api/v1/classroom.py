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
        organization_id=str(classroom.organization_id),
        instructor_id=str(classroom.instructor_id),
        code=classroom.code,
        name=classroom.name,
        term=classroom.term,
        section=classroom.section,
        description=classroom.description,
        is_active=classroom.is_active,
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
    if classroom.instructor_id == current_user.id:
        return

    raise AuthForbiddenException()


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
            instructor_id=current_user.id,
            **request.model_dump(),
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
        data=[_to_payload(classroom) for classroom in classrooms]
    )


@router.get("/{classroom_id}", response_model=ClassroomResponse)
@inject
async def get_classroom(
    classroom_id: UUID,
    current_user: CurrentUser = Depends(require_authenticated_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classroom = await usecase.get_classroom(classroom_id)
    _ensure_same_organization(classroom, current_user)
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
        UpdateClassroomCommand(**request.model_dump(exclude_unset=True)),
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
