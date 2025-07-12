"""UserProfile repository interface."""

from abc import abstractmethod
from uuid import UUID

from symphony.domain.models.user_profile import UserProfile
from symphony.domain.repositories.base import Repository


class UserProfileRepository(Repository[UserProfile]):
    """
    Repository interface for UserProfile aggregate.

    Extends the base repository with UserProfile-specific operations.
    """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserProfile | None:
        """
        Find a user profile by username.

        Args:
            username: The username to search for

        Returns:
            The user profile if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserProfile | None:
        """
        Find a user profile by email.

        Args:
            email: The email to search for

        Returns:
            The user profile if found, None otherwise
        """
        pass

    @abstractmethod
    async def username_exists(self, username: str, exclude_id: UUID | None = None) -> bool:
        """
        Check if a username is already in use.

        Args:
            username: The username to check
            exclude_id: Optional ID to exclude from the check (for updates)

        Returns:
            True if the username exists, False otherwise
        """
        pass

    @abstractmethod
    async def email_exists(self, email: str, exclude_id: UUID | None = None) -> bool:
        """
        Check if an email is already in use.

        Args:
            email: The email to check
            exclude_id: Optional ID to exclude from the check (for updates)

        Returns:
            True if the email exists, False otherwise
        """
        pass

    @abstractmethod
    async def count_workspaces(self, user_id: UUID) -> int:
        """
        Count the number of workspaces owned by a user.

        Args:
            user_id: The user's ID

        Returns:
            The number of workspaces
        """
        pass
