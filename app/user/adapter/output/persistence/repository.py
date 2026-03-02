from collections.abc import Sequence

from sqlalchemy import select

from app.user.domain.entity.user import User
from app.user.domain.repository.user import UserRepository
from core.db.session import session
from core.db.sqlalchemy.models.user import user_table


class UserPersistenceAdapter(UserRepository):
    async def save(self, user: User) -> User:
        merged_user = await session.merge(user)
        return merged_user

    async def get_by_id(self, id: any) -> User | None:
        query = select(User).where(user_table.c.id == id, user_table.c.is_deleted == False)
        result = await session.execute(query)
        return result.scalar_one_of_none()

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(user_table.c.email == email, user_table.c.is_deleted == False)
        result = await session.execute(query)
        return result.scalar_one_of_none()

    async def list(self) -> Sequence[User]:
        query = select(User).where(user_table.c.is_deleted == False)
        result = await session.execute(query)
        return result.scalars().all()

    async def delete(self, user: User) -> None:
        await session.merge(user)
