"""Custom SQLAlchemy types for database compatibility."""

from typing import Any
from uuid import UUID

from sqlalchemy import String, TypeDecorator


class UUIDType(TypeDecorator[UUID]):
    """Platform-independent UUID type.

    Uses char(32) to store UUID as string for SQLite compatibility.
    PostgreSQL has native UUID support, but we use string for consistency.
    """

    impl = String(32)
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> str | None:
        """Convert UUID to string for database storage."""
        if value is None:
            return None
        if isinstance(value, UUID):
            return value.hex
        if isinstance(value, str):
            # If it's already a string, ensure it's just the hex without dashes
            return value.replace("-", "")
        raise ValueError(f"Invalid UUID value: {value}")

    def process_result_value(self, value: Any, dialect: Any) -> UUID | None:
        """Convert string from database to UUID."""
        if value is None:
            return None
        if isinstance(value, str):
            # Add dashes back to create proper UUID format
            if len(value) == 32:
                # Format: 8-4-4-4-12
                formatted = f"{value[:8]}-{value[8:12]}-{value[12:16]}-{value[16:20]}-{value[20:]}"
                return UUID(formatted)
            return UUID(value)
        return value
