"""SQLAlchemy ORM model for Workspace."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from symphony.infrastructure.database.base import Base
from symphony.infrastructure.database.types import UUIDType

if TYPE_CHECKING:
    from symphony.infrastructure.database.models.repo import RepoDB
    from symphony.infrastructure.database.models.user_profile import UserProfileDB
    from symphony.infrastructure.database.models.vault import VaultDB


class WorkspaceDB(Base):
    """SQLAlchemy ORM model for Workspace entity."""

    __tablename__ = "workspaces"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_profile_id: Mapped[UUID] = mapped_column(
        UUIDType, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workspace_type: Mapped[str] = mapped_column(
        Enum("general", "client", "personal", "research", name="workspace_type_enum"),
        nullable=False,
        default="general",
    )
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    shared_resources: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
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
    user_profile: Mapped["UserProfileDB"] = relationship(
        "UserProfileDB", back_populates="workspaces"
    )
    repos: Mapped[list["RepoDB"]] = relationship(
        "RepoDB", back_populates="workspace", cascade="all, delete-orphan"
    )
    vaults: Mapped[list["VaultDB"]] = relationship(
        "VaultDB", back_populates="workspace", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of WorkspaceDB."""
        return f"<WorkspaceDB(id={self.id}, name='{self.name}', type='{self.workspace_type}')>"
