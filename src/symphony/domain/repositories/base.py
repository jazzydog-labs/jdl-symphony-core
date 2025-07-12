"""Base repository interface."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

# Type variable for domain entities
T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """
    Abstract base repository interface.

    Defines the common operations that all repositories must implement.
    This interface belongs to the domain layer and should not depend on
    any infrastructure concerns.
    """

    @abstractmethod
    async def get(self, id: UUID) -> T | None:
        """
        Retrieve an entity by its ID.

        Args:
            id: The UUID of the entity

        Returns:
            The entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        Save an entity (create or update).

        Args:
            entity: The entity to save

        Returns:
            The saved entity
        """
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """
        Delete an entity by its ID.

        Args:
            id: The UUID of the entity to delete
        """
        pass

    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        """
        Check if an entity exists.

        Args:
            id: The UUID to check

        Returns:
            True if the entity exists, False otherwise
        """
        pass
