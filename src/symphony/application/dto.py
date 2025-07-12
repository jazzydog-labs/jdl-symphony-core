"""Data Transfer Objects for application layer."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from symphony.domain.models.workspace import WorkspaceType


@dataclass(frozen=True)
class UserProfileDTO:
    """User profile data transfer object."""

    id: UUID
    username: str
    email: str
    preferences: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class WorkspaceDTO:
    """Workspace data transfer object."""

    id: UUID
    name: str
    user_profile_id: UUID
    workspace_type: WorkspaceType
    description: str | None
    settings: dict[str, Any]
    shared_resources: dict[str, list[UUID]]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class RepoDTO:
    """Repository data transfer object."""

    id: UUID
    name: str
    workspace_id: UUID
    path: str
    remote_url: str | None
    metadata: dict[str, Any]
    last_synced: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class VaultDTO:
    """Vault data transfer object."""

    id: UUID
    name: str
    workspace_id: UUID
    path: str
    metadata: dict[str, Any]
    is_locked: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class WorkspaceStatsDTO:
    """Workspace statistics data transfer object."""

    workspace_id: UUID
    repo_count: int
    vault_count: int
    total_resources: int
