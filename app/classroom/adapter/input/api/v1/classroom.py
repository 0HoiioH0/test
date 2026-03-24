from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.auth.adapter.input.api.v1.deps import (
    require_authenticated_user,
    require_professor_or_admin_user,
)
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


@router.post("", response_model=ClassroomResponse)
@inject
async def create_classroom(
    request: CreateClassroomRequest,
    current_user: CurrentUser = Depends(require_professor_or_admin_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classroom = await usecase.create_classroom(
        current_user=current_user,
        command=CreateClassroomCommand(
            organization_id=current_user.organization_id,
            name=request.name,
            professor_ids=request.professor_ids,
            grade=request.grade,
            semester=request.semester,
            section=request.section,
            description=request.description,
            student_ids=request.student_ids,
        ),
    )
    return ClassroomResponse(data=_to_payload(classroom))


@router.get("", response_model=ClassroomListResponse)
@inject
async def list_classrooms(
    current_user: CurrentUser = Depends(require_authenticated_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classrooms = await usecase.list_classrooms(current_user=current_user)
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
    classroom = await usecase.get_classroom(
        classroom_id=classroom_id,
        current_user=current_user,
    )
    return ClassroomResponse(data=_to_payload(classroom))


@router.patch("/{classroom_id}", response_model=ClassroomResponse)
@inject
async def update_classroom(
    classroom_id: UUID,
    request: UpdateClassroomRequest,
    current_user: CurrentUser = Depends(require_professor_or_admin_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classroom = await usecase.update_classroom(
        classroom_id=classroom_id,
        current_user=current_user,
        command=UpdateClassroomCommand(
            **request.model_dump(exclude_unset=True)
        ),
    )
    return ClassroomResponse(data=_to_payload(classroom))


@router.delete("/{classroom_id}", response_model=ClassroomResponse)
@inject
async def delete_classroom(
    classroom_id: UUID,
    current_user: CurrentUser = Depends(require_professor_or_admin_user),
    usecase: ClassroomUseCase = Depends(Provide[ClassroomContainer.service]),
):
    classroom = await usecase.delete_classroom(
        classroom_id=classroom_id,
        current_user=current_user,
    )
    return ClassroomResponse(data=_to_payload(classroom))
