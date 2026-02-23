from dataclasses import dataclass
from core.common.entity import Entity
from core.common.value_object import ValueObject

@dataclass
class User(Entity):
    email: str = None
    password: str = None
    nickname: str = None
    is_active: bool = True
    
    def update_nickname(self, new_nickname: str) -> None:
        self.nickname = new_nickname
