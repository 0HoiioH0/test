from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.user.adapter.input.api.v1.request import (
    CreateUserRequest,
    UpdateUserRequest,
)
from app.user.adapter.input.api.v1.response import (
    UserListResponse,
    UserPayload,
    UserResponse,
)
from app.user.application.dto.command import (
    CreateUserCommand,
    UpdateUserCommand,
)
from app.user.application.service.user import UserService
from app.user.container import UserContainer

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse)
@inject
async def create_user(
    request: CreateUserRequest,
    service: UserService = Depends(Provide[UserContainer.service]),
):
    user = await service.create_user(CreateUserCommand(**request.model_dump()))
    return UserResponse(
        data=UserPayload(
            id=str(user.id),
            username=user.username,
            email=user.email,
            nickname=user.profile.nickname,
            real_name=user.profile.real_name,
            phone_number=user.profile.phone_number,
            is_deleted=user.is_deleted,
        )
    )


@router.get("", response_model=UserListResponse)
@inject
async def list_users(
    service: UserService = Depends(Provide[UserContainer.service]),
):
    users = await service.list_users()
    return UserListResponse(
        data=[
            UserPayload(
                id=str(user.id),
                username=user.username,
                email=user.email,
                nickname=user.profile.nickname,
                real_name=user.profile.real_name,
                phone_number=user.profile.phone_number,
                is_deleted=user.is_deleted,
            )
            for user in users
        ]
    )


@router.get("/{user_id}", response_model=UserResponse)
@inject
async def get_user(
    user_id: UUID,
    service: UserService = Depends(Provide[UserContainer.service]),
):
    user = await service.get_user(user_id)
    return UserResponse(
        data=UserPayload(
            id=str(user.id),
            username=user.username,
            email=user.email,
            nickname=user.profile.nickname,
            real_name=user.profile.real_name,
            phone_number=user.profile.phone_number,
            is_deleted=user.is_deleted,
        )
    )


@router.patch("/{user_id}", response_model=UserResponse)
@inject
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    service: UserService = Depends(Provide[UserContainer.service]),
):
    user = await service.update_user(
        user_id,
        UpdateUserCommand(**request.model_dump(exclude_unset=True)),
    )
    return UserResponse(
        data=UserPayload(
            id=str(user.id),
            username=user.username,
            email=user.email,
            nickname=user.profile.nickname,
            real_name=user.profile.real_name,
            phone_number=user.profile.phone_number,
            is_deleted=user.is_deleted,
        )
    )


@router.delete("/{user_id}", response_model=UserResponse)
@inject
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(Provide[UserContainer.service]),
):
    user = await service.delete_user(user_id)
    return UserResponse(
        data=UserPayload(
            id=str(user.id),
            username=user.username,
            email=user.email,
            nickname=user.profile.nickname,
            real_name=user.profile.real_name,
            phone_number=user.profile.phone_number,
            is_deleted=user.is_deleted,
        )
    )
