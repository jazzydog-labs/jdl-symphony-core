"""UserProfile domain service for business logic orchestration."""

from typing import Any
from uuid import UUID

from symphony.domain.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserProfileNotFoundError,
    WorkspaceLimitExceeded,
)
from symphony.domain.models.user_profile import UserProfile
from symphony.domain.unit_of_work import UnitOfWork


class UserProfileService:
    """
    Domain service for UserProfile business logic.

    Coordinates operations that involve multiple aggregates or repositories,
    enforces business rules, and handles cross-cutting concerns.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize service with unit of work."""
        self._uow = uow

    async def create_user_profile(
        self, username: str, email: str, preferences: dict[str, Any] | None = None
    ) -> UserProfile:
        """
        Create a new user profile with validation.

        Args:
            username: Unique username
            email: User email address
            preferences: Optional user preferences

        Returns:
            Created user profile

        Raises:
            UsernameAlreadyExistsError: If username is taken
            EmailAlreadyExistsError: If email is taken
            ValueError: If validation fails
        """
        # Create domain model (validates in constructor)
        user_profile = UserProfile(username=username, email=email, preferences=preferences or {})

        async with self._uow:
            # Check username uniqueness
            if await self._uow.user_profiles.username_exists(username):
                raise UsernameAlreadyExistsError(username)

            # Check email uniqueness
            if await self._uow.user_profiles.email_exists(email):
                raise EmailAlreadyExistsError(email)

            # Save user profile
            saved_profile = await self._uow.user_profiles.save(user_profile)
            await self._uow.commit()

            return saved_profile

    async def update_user_profile(
        self,
        user_id: UUID,
        username: str | None = None,
        email: str | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> UserProfile:
        """
        Update an existing user profile.

        Args:
            user_id: User profile ID
            username: New username (optional)
            email: New email (optional)
            preferences: New preferences (optional)

        Returns:
            Updated user profile

        Raises:
            UserProfileNotFoundError: If user doesn't exist
            UsernameAlreadyExistsError: If new username is taken
            EmailAlreadyExistsError: If new email is taken
        """
        async with self._uow:
            # Get existing profile
            user_profile = await self._uow.user_profiles.get(user_id)
            if not user_profile:
                raise UserProfileNotFoundError(str(user_id))

            # Check username uniqueness if changing
            if username and username != user_profile.username:
                if await self._uow.user_profiles.username_exists(username, exclude_id=user_id):
                    raise UsernameAlreadyExistsError(username)
                user_profile.username = username

            # Check email uniqueness if changing
            if email and email != user_profile.email:
                if await self._uow.user_profiles.email_exists(email, exclude_id=user_id):
                    raise EmailAlreadyExistsError(email)
                user_profile.email = email

            # Update preferences if provided
            if preferences is not None:
                user_profile.preferences = preferences

            # Update timestamp
            user_profile.update_timestamp()

            # Save changes
            saved_profile = await self._uow.user_profiles.save(user_profile)
            await self._uow.commit()

            return saved_profile

    async def get_user_profile(self, user_id: UUID) -> UserProfile:
        """
        Get a user profile by ID.

        Args:
            user_id: User profile ID

        Returns:
            User profile

        Raises:
            UserProfileNotFoundError: If user doesn't exist
        """
        async with self._uow:
            user_profile = await self._uow.user_profiles.get(user_id)
            if not user_profile:
                raise UserProfileNotFoundError(str(user_id))
            return user_profile

    async def get_user_profile_by_username(self, username: str) -> UserProfile:
        """
        Get a user profile by username.

        Args:
            username: Username to search for

        Returns:
            User profile

        Raises:
            UserProfileNotFoundError: If user doesn't exist
        """
        async with self._uow:
            user_profile = await self._uow.user_profiles.get_by_username(username)
            if not user_profile:
                raise UserProfileNotFoundError(f"Username: {username}")
            return user_profile

    async def get_user_profile_by_email(self, email: str) -> UserProfile:
        """
        Get a user profile by email.

        Args:
            email: Email to search for

        Returns:
            User profile

        Raises:
            UserProfileNotFoundError: If user doesn't exist
        """
        async with self._uow:
            user_profile = await self._uow.user_profiles.get_by_email(email)
            if not user_profile:
                raise UserProfileNotFoundError(f"Email: {email}")
            return user_profile

    async def delete_user_profile(self, user_id: UUID) -> None:
        """
        Delete a user profile and all associated data.

        This will cascade delete all workspaces, repos, and vaults
        owned by the user.

        Args:
            user_id: User profile ID

        Raises:
            UserProfileNotFoundError: If user doesn't exist
        """
        async with self._uow:
            # Verify user exists
            if not await self._uow.user_profiles.exists(user_id):
                raise UserProfileNotFoundError(str(user_id))

            # Delete user (cascades to workspaces, repos, vaults)
            await self._uow.user_profiles.delete(user_id)
            await self._uow.commit()

    async def can_create_workspace(self, user_id: UUID) -> bool:
        """
        Check if a user can create more workspaces.

        Enforces business rule: max 50 workspaces per user.

        Args:
            user_id: User profile ID

        Returns:
            True if user can create more workspaces

        Raises:
            UserProfileNotFoundError: If user doesn't exist
        """
        async with self._uow:
            # Verify user exists
            if not await self._uow.user_profiles.exists(user_id):
                raise UserProfileNotFoundError(str(user_id))

            # Check workspace count
            workspace_count = await self._uow.user_profiles.count_workspaces(user_id)
            return workspace_count < 50

    async def check_workspace_limit(self, user_id: UUID) -> None:
        """
        Check workspace limit and raise exception if exceeded.

        Args:
            user_id: User profile ID

        Raises:
            UserProfileNotFoundError: If user doesn't exist
            WorkspaceLimitExceeded: If user has reached workspace limit
        """
        if not await self.can_create_workspace(user_id):
            raise WorkspaceLimitExceeded()
