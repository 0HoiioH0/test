from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from core.db.session import Base
from core.db.mixins import TimestampMixin, OptimisticLockMixin
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class UserModel(Base, TimestampMixin, OptimisticLockMixin):
    __tablename__ = "users"

    id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
