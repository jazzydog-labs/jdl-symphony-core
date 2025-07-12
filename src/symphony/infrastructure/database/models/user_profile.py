"""SQLAlchemy ORM model for UserProfile."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from symphony.infrastructure.database.base import Base

if TYPE_CHECKING:
    from symphony.infrastructure.database.models.workspace import WorkspaceDB


class UserProfileDB(Base):
    """SQLAlchemy ORM model for UserProfile entity."""

    __tablename__ = "user_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    workspaces: Mapped[list["WorkspaceDB"]] = relationship(
        "WorkspaceDB", back_populates="user_profile", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of UserProfileDB."""
        return f"<UserProfileDB(id={self.id}, username='{self.username}', email='{self.email}')>"
