"""UserProfile domain model representing global user data."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class UserProfile:
    """
    UserProfile aggregate root representing global user data.

    Acts as the identity anchor for users but doesn't own workspaces.
    Contains personal information, preferences, and authentication data.
    """

    id: UUID = field(default_factory=uuid4)
    username: str = ""
    email: str = ""
    preferences: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate the user profile after initialization."""
        if not self.validate_username():
            raise ValueError(f"Invalid username: {self.username}")
        if not self.validate_email():
            raise ValueError(f"Invalid email: {self.email}")

    def validate_username(self) -> bool:
        """
        Validate username according to business rules.

        Rules:
        - Must be at least 3 characters long
        - Must contain only alphanumeric characters and underscores
        - Must start with a letter
        """
        if not self.username or len(self.username) < 3:
            return False
        if not self.username[0].isalpha():
            return False
        return all(c.isalnum() or c == "_" for c in self.username)

    def validate_email(self) -> bool:
        """
        Basic email validation.

        This is a simple validation - in production, consider using
        a more robust email validation library.
        """
        if not self.email or "@" not in self.email:
            return False
        parts = self.email.split("@")
        if len(parts) != 2:
            return False
        local, domain = parts
        if not local or not domain:
            return False
        if "." not in domain:
            return False
        return True

    def can_create_workspace(
        self, current_workspace_count: int = 0, max_workspaces: int = 50
    ) -> bool:
        """
        Business rule to determine if user can create more workspaces.

        Args:
            current_workspace_count: Number of workspaces user currently has
            max_workspaces: Maximum allowed workspaces per user

        Returns:
            True if user can create more workspaces
        """
        return current_workspace_count < max_workspaces

    def update_preferences(self, new_preferences: dict[str, Any]) -> None:
        """
        Update user preferences with new values.

        Args:
            new_preferences: Dictionary of preferences to update
        """
        self.preferences.update(new_preferences)
        self.updated_at = datetime.now(UTC)

    def update_email(self, new_email: str) -> None:
        """
        Update user email with validation.

        Args:
            new_email: New email address

        Raises:
            ValueError: If email is invalid
        """
        # Temporarily store old email
        old_email = self.email
        self.email = new_email

        # Validate new email
        if not self.validate_email():
            self.email = old_email
            raise ValueError(f"Invalid email: {new_email}")

        self.updated_at = datetime.now(UTC)
