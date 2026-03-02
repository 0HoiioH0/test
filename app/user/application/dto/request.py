from pydantic import EmailStr, Field

from core.common.request.base import BaseRequest


class CreateUserRequest(BaseRequest):
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    email: EmailStr = Field(...)
    nickname: str = Field(..., min_length=2, max_length=100)
    real_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str | None = Field(None, pattern=r"^\d{2,3}-\d{3,4}-\d{4}$")
