"""Workspace repository interface."""

from abc import abstractmethod
from uuid import UUID

from symphony.domain.models.workspace import Workspace, WorkspaceType
from symphony.domain.repositories.base import Repository


class WorkspaceRepository(Repository[Workspace]):
    """
    Repository interface for Workspace aggregate.

    Extends the base repository with Workspace-specific operations.
    """

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[Workspace]:
        """
        Get all workspaces for a user.

        Args:
            user_id: The user's ID

        Returns:
            List of workspaces owned by the user
        """
        pass

    @abstractmethod
    async def get_by_user_and_type(
        self, user_id: UUID, workspace_type: WorkspaceType
    ) -> list[Workspace]:
        """
        Get workspaces for a user filtered by type.

        Args:
            user_id: The user's ID
            workspace_type: The type of workspace to filter by

        Returns:
            List of workspaces matching the criteria
        """
        pass

    @abstractmethod
    async def count_resources(self, workspace_id: UUID) -> dict[str, int]:
        """
        Count resources (repos, vaults) in a workspace.

        Args:
            workspace_id: The workspace's ID

        Returns:
            Dictionary with resource counts, e.g., {"repos": 5, "vaults": 3}
        """
        pass

    @abstractmethod
    async def has_active_resources(self, workspace_id: UUID) -> bool:
        """
        Check if a workspace has any active resources.

        Args:
            workspace_id: The workspace's ID

        Returns:
            True if the workspace has resources, False otherwise
        """
        pass
