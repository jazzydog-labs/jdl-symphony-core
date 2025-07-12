"""SQLAlchemy ORM model for Vault."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from symphony.infrastructure.database.base import Base

if TYPE_CHECKING:
    from symphony.infrastructure.database.models.workspace import WorkspaceDB


class VaultDB(Base):
    """SQLAlchemy ORM model for Vault entity."""

    __tablename__ = "vaults"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
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
    workspace: Mapped["WorkspaceDB"] = relationship("WorkspaceDB", back_populates="vaults")

    def __repr__(self) -> str:
        """String representation of VaultDB."""
        return f"<VaultDB(id={self.id}, name='{self.name}', path='{self.path}')>"
