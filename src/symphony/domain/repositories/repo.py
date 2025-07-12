"""Repo repository interface."""

from abc import abstractmethod
from uuid import UUID

from symphony.domain.models.repo import Repo
from symphony.domain.repositories.base import Repository


class RepoRepository(Repository[Repo]):
    """
    Repository interface for Repo aggregate.

    Extends the base repository with Repo-specific operations.
    """

    @abstractmethod
    async def get_by_workspace(self, workspace_id: UUID) -> list[Repo]:
        """
        Get all repos in a workspace.

        Args:
            workspace_id: The workspace's ID

        Returns:
            List of repos in the workspace
        """
        pass

    @abstractmethod
    async def get_by_name(self, workspace_id: UUID, name: str) -> Repo | None:
        """
        Find a repo by name within a workspace.

        Args:
            workspace_id: The workspace's ID
            name: The repo name

        Returns:
            The repo if found, None otherwise
        """
        pass

    @abstractmethod
    async def name_exists_in_workspace(
        self, workspace_id: UUID, name: str, exclude_id: UUID | None = None
    ) -> bool:
        """
        Check if a repo name already exists in a workspace.

        Args:
            workspace_id: The workspace's ID
            name: The repo name to check
            exclude_id: Optional ID to exclude from the check (for updates)

        Returns:
            True if the name exists, False otherwise
        """
        pass

    @abstractmethod
    async def count_by_workspace(self, workspace_id: UUID) -> int:
        """
        Count repos in a workspace.

        Args:
            workspace_id: The workspace's ID

        Returns:
            The number of repos
        """
        pass
