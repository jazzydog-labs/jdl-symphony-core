"""Repo domain model representing a git repository."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4


@dataclass
class Repo:
    """
    Repo aggregate root representing a git repository within a workspace.

    Manages repository metadata and location information. In Phase 0,
    this is purely metadata - actual git operations are out of scope.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    path: str = ""
    workspace_id: UUID = field(default_factory=uuid4)
    remote_url: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate the repo after initialization."""
        if not self.validate_name():
            raise ValueError(f"Invalid repo name: {self.name}")
        if not self.validate_path():
            raise ValueError(f"Invalid repo path: {self.path}")
        if self.remote_url and not self.validate_remote_url():
            raise ValueError(f"Invalid remote URL: {self.remote_url}")

    def validate_name(self) -> bool:
        """
        Validate repository name according to business rules.

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
        return not any(char in self.name for char in invalid_chars)

    def validate_path(self) -> bool:
        """
        Validate repository path.

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

    def validate_remote_url(self) -> bool:
        """
        Basic validation for git remote URLs.

        Supports:
        - HTTP(S) URLs
        - SSH URLs (git@...)
        - Git protocol URLs
        """
        if not self.remote_url:
            return True  # Remote URL is optional

        url = self.remote_url.strip()

        # Check for common git URL patterns
        if url.startswith(("http://", "https://", "git://", "ssh://", "git@")):
            return True

        # Check for SCP-style SSH URLs (e.g., user@host:path)
        return ":" in url and not url.startswith("/")

    def update_remote_url(self, remote_url: str | None) -> None:
        """
        Update the remote URL with validation.

        Args:
            remote_url: New remote URL or None to remove

        Raises:
            ValueError: If remote URL is invalid
        """
        old_url = self.remote_url
        self.remote_url = remote_url

        if self.remote_url and not self.validate_remote_url():
            self.remote_url = old_url
            raise ValueError(f"Invalid remote URL: {remote_url}")

        self.updated_at = datetime.now(UTC)

    def update_path(self, new_path: str) -> None:
        """
        Update the repository path with validation.

        Args:
            new_path: New repository path

        Raises:
            ValueError: If path is invalid
        """
        old_path = self.path
        self.path = new_path

        if not self.validate_path():
            self.path = old_path
            raise ValueError(f"Invalid repo path: {new_path}")

        self.updated_at = datetime.now(UTC)

    def rename(self, new_name: str) -> None:
        """
        Rename the repository with validation.

        Args:
            new_name: New repository name

        Raises:
            ValueError: If name is invalid
        """
        old_name = self.name
        self.name = new_name

        if not self.validate_name():
            self.name = old_name
            raise ValueError(f"Invalid repo name: {new_name}")

        self.updated_at = datetime.now(UTC)
