from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional
from uuid import UUID
from core.common.entity import Entity
from core.common.value_object import ValueObject

class UserStatus(ValueObject, StrEnum):
    ACTIVE = "active"
    PENDING = "pending"
    BLOCKED = "blocked"

@dataclass
class Profile(ValueObject):
    nickname: str
    real_name: str
    phone_number: Optional[str] = None
    profile_image_id: Optional[UUID] = None

@dataclass
class User(Entity):
    username: str
    password: Optional[str]  # Social login might not have a password initially
    email: str
    profile: Profile
    status: UserStatus = UserStatus.ACTIVE
    is_deleted: bool = False
    
    # OAuth2 support
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None

    def update_profile(self, new_profile: Profile) -> None:
        self.profile = new_profile

    def delete(self) -> None:
        self.is_deleted = True
        self.status = UserStatus.BLOCKED
