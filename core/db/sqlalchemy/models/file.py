from sqlalchemy import Column, String, BigInteger, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from core.db.sqlalchemy.models.base import BaseTable, metadata
from app.file.domain.entity.file import FileStatus

file_table = BaseTable(
    "files",
    metadata,
    Column("id", PG_UUID(as_uuid=True), primary_key=True),
    Column("file_name", String(255), nullable=False),
    Column("file_path", String(512), nullable=False),
    Column("file_extension", String(10), nullable=False),
    Column("file_size", BigInteger, nullable=False),
    Column("mime_type", String(100), nullable=False),
    Column("status", Enum(FileStatus), nullable=False, default=FileStatus.PENDING),
)
