"""Workspace domain model representing independent work contexts."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

WorkspaceType = Literal["general", "client", "personal", "research"]


@dataclass
class Workspace:
    """
    Workspace aggregate root representing an independent work context.

    Self-contained working environments for specific themes/projects.
    Can reference/link to global UserProfile resources but maintains
    full autonomy for workspace-specific data and workflows.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str | None = None
    user_profile_id: UUID = field(default_factory=uuid4)  # References owner, not owned by
    workspace_type: WorkspaceType = "general"
    settings: dict[str, Any] = field(default_factory=dict)
    shared_resources: dict[str, list[UUID]] = field(
        default_factory=dict
    )  # resource_type -> [resource_ids]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate the workspace after initialization."""
        if not self.validate_name():
            raise ValueError(f"Invalid workspace name: {self.name}")
        if not self.validate_workspace_type():
            raise ValueError(f"Invalid workspace type: {self.workspace_type}")

    def validate_name(self) -> bool:
        """
        Validate workspace name according to business rules.

        Rules:
        - Must not be empty
        - Must be between 1 and 255 characters
        - Must not be only whitespace
        """
        if not self.name or not self.name.strip():
            return False
        if len(self.name) > 255:
            return False
        return True

    def validate_workspace_type(self) -> bool:
        """Validate workspace type is one of the allowed values."""
        allowed_types = {"general", "client", "personal", "research"}
        return self.workspace_type in allowed_types

    def can_be_deleted(self, has_active_resources: bool = False) -> bool:
        """
        Business rule to determine if workspace can be deleted.

        Args:
            has_active_resources: Whether workspace has active resources (repos, vaults, etc.)

        Returns:
            True if workspace can be deleted
        """
        # In Phase 0, workspaces can always be deleted
        # In future phases, we might check for active resources, ongoing operations, etc.
        return not has_active_resources

    def add_shared_resource(self, resource_id: UUID, resource_type: str) -> None:
        """
        Link to a global resource (contacts, templates, etc.).

        Args:
            resource_id: ID of the global resource
            resource_type: Type of resource (e.g., 'contact', 'template', 'snippet')
        """
        if resource_type not in self.shared_resources:
            self.shared_resources[resource_type] = []

        if resource_id not in self.shared_resources[resource_type]:
            self.shared_resources[resource_type].append(resource_id)
            self.updated_at = datetime.now(UTC)

    def remove_shared_resource(self, resource_id: UUID, resource_type: str) -> None:
        """
        Remove link to a global resource.

        Args:
            resource_id: ID of the global resource
            resource_type: Type of resource
        """
        if resource_type in self.shared_resources:
            if resource_id in self.shared_resources[resource_type]:
                self.shared_resources[resource_type].remove(resource_id)
                self.updated_at = datetime.now(UTC)

    def update_settings(self, new_settings: dict[str, Any]) -> None:
        """
        Update workspace settings.

        Args:
            new_settings: Dictionary of settings to update
        """
        self.settings.update(new_settings)
        self.updated_at = datetime.now(UTC)

    def update_description(self, description: str | None) -> None:
        """
        Update workspace description.

        Args:
            description: New description or None to clear
        """
        self.description = description
        self.updated_at = datetime.now(UTC)

    def rename(self, new_name: str) -> None:
        """
        Rename the workspace with validation.

        Args:
            new_name: New workspace name

        Raises:
            ValueError: If name is invalid
        """
        old_name = self.name
        self.name = new_name

        if not self.validate_name():
            self.name = old_name
            raise ValueError(f"Invalid workspace name: {new_name}")

        self.updated_at = datetime.now(UTC)
