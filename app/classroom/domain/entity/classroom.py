from dataclasses import dataclass
from uuid import UUID

from core.common.entity import Entity


@dataclass
class Classroom(Entity):
    organization_id: UUID
    instructor_id: UUID
    code: str
    name: str
    term: str
    section: str | None = None
    description: str | None = None
    is_active: bool = True

    def delete(self) -> None:
        self.is_active = False
