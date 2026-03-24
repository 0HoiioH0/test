from uuid import UUID

from pydantic import BaseModel


class CreateClassroomCommand(BaseModel):
    organization_id: UUID
    instructor_id: UUID
    code: str
    name: str
    term: str
    section: str | None = None
    description: str | None = None
    is_active: bool = True


class UpdateClassroomCommand(BaseModel):
    code: str | None = None
    name: str | None = None
    term: str | None = None
    section: str | None = None
    description: str | None = None
    is_active: bool | None = None
