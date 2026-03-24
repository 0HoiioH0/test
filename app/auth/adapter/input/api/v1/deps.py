from abc import ABC, abstractmethod
from uuid import UUID

import jwt
from fastapi import Cookie, Depends, Request

from app.auth.application.exception import (
    AuthForbiddenException,
    AuthUnauthorizedException,
)
from app.auth.domain.entity import CurrentUser
from app.user.adapter.output.persistence.sqlalchemy import (
    UserSQLAlchemyRepository,
)
from app.user.domain.entity import UserRole, UserStatus
from app.user.domain.repository import UserRepository
from core.config import config
from core.domain.types import TokenType
from core.helpers.token import TokenHelper


async def require_authenticated_user(
    access_token: str | None = Cookie(
        default=None,
        alias=config.ACCESS_TOKEN_COOKIE_NAME,
    ),
    user_repository: UserRepository = Depends(UserSQLAlchemyRepository),
) -> CurrentUser:
    if access_token is None:
        raise AuthUnauthorizedException()

    try:
        payload = TokenHelper.decode_token(access_token)
        if payload.get("type") != TokenType.ACCESS.value:
            raise AuthUnauthorizedException()
        user_id = UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise AuthUnauthorizedException() from exc

    user = await user_repository.get_by_id(user_id)
    if user is None or user.status == UserStatus.BLOCKED:
        raise AuthUnauthorizedException()

    return CurrentUser.from_user(user)


class BasePermission(ABC):
    exception = AuthForbiddenException

    @abstractmethod
    async def has_permission(
        self,
        _request: Request,
        current_user: CurrentUser,
    ) -> bool:
        pass


class IsAuthenticated(BasePermission):
    exception = AuthUnauthorizedException

    async def has_permission(
        self,
        _request: Request,
        current_user: CurrentUser,
    ) -> bool:
        return current_user.authenticated


class IsAdmin(BasePermission):
    async def has_permission(
        self,
        _request: Request,
        current_user: CurrentUser,
    ) -> bool:
        return current_user.role == UserRole.ADMIN


class IsProfessorOrAdmin(BasePermission):
    async def has_permission(
        self,
        _request: Request,
        current_user: CurrentUser,
    ) -> bool:
        return current_user.role in (UserRole.PROFESSOR, UserRole.ADMIN)


class PermissionDependency:
    def __init__(self, permissions: list[type[BasePermission]]):
        self.permissions = permissions

    async def __call__(
        self,
        request: Request,
        current_user: CurrentUser = Depends(require_authenticated_user),
    ) -> CurrentUser:
        for permission in self.permissions:
            checker = permission()
            if not await checker.has_permission(request, current_user):
                raise checker.exception()

        return current_user
