from app.user.application.dto.request import CreateUserRequest
from app.user.domain.entity.user import Profile, User
from app.user.domain.repository.user import UserRepository
from core.db.transactional import transactional
from core.helpers.argon2 import Argon2Helper


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    @transactional
    async def create_user(self, request: CreateUserRequest) -> User:
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(request.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash password
        hashed_password = Argon2Helper.hash(request.password)

        # Create Entity
        profile = Profile(nickname=request.nickname, real_name=request.real_name, phone_number=request.phone_number)
        user = User(username=request.username, password=hashed_password, email=request.email, profile=profile)

        return await self.user_repo.save(user)
