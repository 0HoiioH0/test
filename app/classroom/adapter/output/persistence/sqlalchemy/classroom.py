from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select

from app.classroom.domain.entity import Classroom
from app.classroom.domain.repository import ClassroomRepository
from core.db.session import session
from core.db.sqlalchemy.models.classroom import classroom_table


class ClassroomSQLAlchemyRepository(ClassroomRepository):
    async def get_by_id(self, entity_id: UUID) -> Classroom | None:
        query = select(Classroom).where(classroom_table.c.id == entity_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_organization_and_code(
        self,
        organization_id: UUID,
        code: str,
    ) -> Classroom | None:
        query = select(Classroom).where(
            classroom_table.c.organization_id == organization_id,
            classroom_table.c.code == code,
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def list(self) -> list[Classroom]:
        query = select(Classroom).order_by(classroom_table.c.created_at.desc())
        result = await session.execute(query)
        return list(result.scalars().all())

    async def list_by_organization(
        self,
        organization_id: UUID,
    ) -> Sequence[Classroom]:
        query = (
            select(Classroom)
            .where(classroom_table.c.organization_id == organization_id)
            .order_by(classroom_table.c.created_at.desc())
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    async def save(self, entity: Classroom) -> Classroom:
        session.add(entity)
        return entity
