from pydantic import BaseModel, Field

from core.common.response.base import BaseResponse


class ClassroomPayload(BaseModel):
    id: str
    organization_id: str
    instructor_id: str
    code: str
    name: str
    term: str
    section: str | None = None
    description: str | None = None
    is_active: bool


class ClassroomResponse(BaseResponse):
    data: ClassroomPayload = Field(default=...)


class ClassroomListResponse(BaseResponse):
    data: list[ClassroomPayload] = Field(default=...)
