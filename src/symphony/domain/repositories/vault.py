"""Vault repository interface."""

from abc import abstractmethod
from uuid import UUID

from symphony.domain.models.vault import Vault
from symphony.domain.repositories.base import Repository


class VaultRepository(Repository[Vault]):
    """
    Repository interface for Vault aggregate.

    Extends the base repository with Vault-specific operations.
    """

    @abstractmethod
    async def get_by_workspace(self, workspace_id: UUID) -> list[Vault]:
        """
        Get all vaults in a workspace.

        Args:
            workspace_id: The workspace's ID

        Returns:
            List of vaults in the workspace
        """
        pass

    @abstractmethod
    async def get_by_name(self, workspace_id: UUID, name: str) -> Vault | None:
        """
        Find a vault by name within a workspace.

        Args:
            workspace_id: The workspace's ID
            name: The vault name

        Returns:
            The vault if found, None otherwise
        """
        pass

    @abstractmethod
    async def name_exists_in_workspace(
        self, workspace_id: UUID, name: str, exclude_id: UUID | None = None
    ) -> bool:
        """
        Check if a vault name already exists in a workspace.

        Args:
            workspace_id: The workspace's ID
            name: The vault name to check
            exclude_id: Optional ID to exclude from the check (for updates)

        Returns:
            True if the name exists, False otherwise
        """
        pass

    @abstractmethod
    async def count_by_workspace(self, workspace_id: UUID) -> int:
        """
        Count vaults in a workspace.

        Args:
            workspace_id: The workspace's ID

        Returns:
            The number of vaults
        """
        pass
