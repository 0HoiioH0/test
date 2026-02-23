from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from core.db.sqlalchemy.models.base import BaseTable, metadata
from app.user.domain.entity.user import UserStatus

user_table = BaseTable(
    "users",
    metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("username", String(50), unique=True, nullable=False),
    Column("password", String(255), nullable=True),
    Column("email", String(255), unique=True, nullable=False),
    Column("nickname", String(100), nullable=False),
    Column("real_name", String(100), nullable=False),
    Column("phone_number", String(20), nullable=True),
    Column("profile_image_id", PG_UUID(as_uuid=True), ForeignKey("files.id", ondelete="SET NULL"), nullable=True),
    Column("status", Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE),
    Column("is_deleted", Boolean, nullable=False, default=False),
    Column("oauth_provider", String(50), nullable=True),
    Column("oauth_id", String(255), nullable=True),
)
