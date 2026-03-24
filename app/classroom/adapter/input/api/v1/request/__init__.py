from pydantic import Field, model_validator

from core.common.request.base import BaseRequest


class CreateClassroomRequest(BaseRequest):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    term: str = Field(..., min_length=2, max_length=50)
    section: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=500)
    is_active: bool = Field(default=True)


class UpdateClassroomRequest(BaseRequest):
    null_fields = {"section", "description"}

    code: str | None = Field(None, min_length=2, max_length=50)
    name: str | None = Field(None, min_length=2, max_length=100)
    term: str | None = Field(None, min_length=2, max_length=50)
    section: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=500)
    is_active: bool | None = Field(None)

    @model_validator(mode="after")
    def validate_non_empty_update(self):
        if not self.model_fields_set:
            raise ValueError("최소 하나 이상의 수정 필드가 필요합니다.")
        return self
