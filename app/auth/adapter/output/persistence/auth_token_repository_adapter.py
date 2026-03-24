from uuid import UUID

from app.auth.domain.repository.auth_token import AuthTokenRepository


class AuthTokenRepositoryAdapter:
    def __init__(self, *, repository: AuthTokenRepository):
        self.repository = repository

    async def save(
        self,
        *,
        user_id: UUID,
        jti: str,
        refresh_token: str,
        expires_in: int,
    ) -> None:
        await self.repository.save(
            user_id=user_id,
            jti=jti,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    async def get(self, *, user_id: UUID, jti: str) -> str | None:
        return await self.repository.get(user_id=user_id, jti=jti)

    async def delete(self, *, user_id: UUID, jti: str) -> None:
        await self.repository.delete(user_id=user_id, jti=jti)
