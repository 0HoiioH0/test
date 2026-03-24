from sqlalchemy import Boolean, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from core.db.sqlalchemy.models.base import BaseTable, metadata

classroom_table = BaseTable(
    "t_classroom",
    metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column(
        "organization_id",
        PG_UUID(as_uuid=True),
        ForeignKey("t_organization.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column(
        "instructor_id",
        PG_UUID(as_uuid=True),
        ForeignKey("t_user.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("code", String(50), nullable=False),
    Column("name", String(100), nullable=False),
    Column("term", String(50), nullable=False),
    Column("section", String(50), nullable=True),
    Column("description", String(500), nullable=True),
    Column("is_active", Boolean, nullable=False, default=True),
    UniqueConstraint("organization_id", "code"),
)
