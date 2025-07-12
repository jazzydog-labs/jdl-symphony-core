"""Vault domain model representing a secure data storage location."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4


@dataclass
class Vault:
    """
    Vault aggregate root representing a secure data storage location within a workspace.

    Vaults are used to store sensitive information, notes, and other data
    that should be organized separately from code repositories. In Phase 0,
    this is purely metadata - actual file operations are out of scope.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    path: str = ""
    workspace_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate the vault after initialization."""
        if not self.validate_name():
            raise ValueError(f"Invalid vault name: {self.name}")
        if not self.validate_path():
            raise ValueError(f"Invalid vault path: {self.path}")

    def validate_name(self) -> bool:
        """
        Validate vault name according to business rules.

        Rules:
        - Must not be empty
        - Must be between 1 and 255 characters
        - Must not contain path separators
        - Must be valid as a directory name
        """
        if not self.name or not self.name.strip():
            return False
        if len(self.name) > 255:
            return False
        # Check for path separators
        if "/" in self.name or "\\" in self.name:
            return False
        # Check for special characters that might cause issues
        invalid_chars = {"<", ">", ":", '"', "|", "?", "*", "\0"}
        if any(char in self.name for char in invalid_chars):
            return False
        return True

    def validate_path(self) -> bool:
        """
        Validate vault path.

        Rules:
        - Must not be empty
        - Must be a valid path format
        """
        if not self.path or not self.path.strip():
            return False
        try:
            # Check if it's a valid path format
            Path(self.path)
            return True
        except (ValueError, OSError):
            return False

    def update_path(self, new_path: str) -> None:
        """
        Update the vault path with validation.

        Args:
            new_path: New vault path

        Raises:
            ValueError: If path is invalid
        """
        old_path = self.path
        self.path = new_path

        if not self.validate_path():
            self.path = old_path
            raise ValueError(f"Invalid vault path: {new_path}")

        self.updated_at = datetime.now(UTC)

    def rename(self, new_name: str) -> None:
        """
        Rename the vault with validation.

        Args:
            new_name: New vault name

        Raises:
            ValueError: If name is invalid
        """
        old_name = self.name
        self.name = new_name

        if not self.validate_name():
            self.name = old_name
            raise ValueError(f"Invalid vault name: {new_name}")

        self.updated_at = datetime.now(UTC)
