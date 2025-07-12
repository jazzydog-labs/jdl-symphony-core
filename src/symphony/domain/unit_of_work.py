"""Unit of Work interface."""

from abc import ABC, abstractmethod
from typing import Any

from symphony.domain.repositories import (
    RepoRepository,
    UserProfileRepository,
    VaultRepository,
    WorkspaceRepository,
)


class UnitOfWork(ABC):
    """
    Unit of Work pattern interface.

    Manages a database transaction and provides access to repositories.
    Ensures that all operations within a unit of work are committed
    or rolled back together.
    """

    # Repository properties
    user_profiles: UserProfileRepository
    workspaces: WorkspaceRepository
    repos: RepoRepository
    vaults: VaultRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        """Enter the unit of work context."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the unit of work context."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction."""
        pass
