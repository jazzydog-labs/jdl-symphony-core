"""User profile command handlers."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from symphony.application.commands.base import Command, CommandHandler
from symphony.application.dto import UserProfileDTO
from symphony.domain.services.user_profile import UserProfileService


@dataclass(frozen=True)
class CreateUserProfileCommand(Command):
    """Command to create a new user profile."""

    username: str
    email: str
    preferences: dict[str, Any] | None = None


@dataclass(frozen=True)
class UpdateUserProfileCommand(Command):
    """Command to update an existing user profile."""

    user_id: UUID
    username: str | None = None
    email: str | None = None
    preferences: dict[str, Any] | None = None


@dataclass(frozen=True)
class DeleteUserProfileCommand(Command):
    """Command to delete a user profile."""

    user_id: UUID


class CreateUserProfileHandler(CommandHandler[CreateUserProfileCommand, UserProfileDTO]):
    """Handler for creating user profiles."""

    async def handle(self, command: CreateUserProfileCommand) -> UserProfileDTO:
        """Handle user profile creation."""
        service = UserProfileService(self._uow)

        user_profile = await service.create_user_profile(
            username=command.username,
            email=command.email,
            preferences=command.preferences,
        )

        return UserProfileDTO(
            id=user_profile.id,
            username=user_profile.username,
            email=user_profile.email,
            preferences=user_profile.preferences,
            created_at=user_profile.created_at,
            updated_at=user_profile.updated_at,
        )


class UpdateUserProfileHandler(CommandHandler[UpdateUserProfileCommand, UserProfileDTO]):
    """Handler for updating user profiles."""

    async def handle(self, command: UpdateUserProfileCommand) -> UserProfileDTO:
        """Handle user profile update."""
        service = UserProfileService(self._uow)

        user_profile = await service.update_user_profile(
            user_id=command.user_id,
            username=command.username,
            email=command.email,
            preferences=command.preferences,
        )

        return UserProfileDTO(
            id=user_profile.id,
            username=user_profile.username,
            email=user_profile.email,
            preferences=user_profile.preferences,
            created_at=user_profile.created_at,
            updated_at=user_profile.updated_at,
        )


class DeleteUserProfileHandler(CommandHandler[DeleteUserProfileCommand, None]):
    """Handler for deleting user profiles."""

    async def handle(self, command: DeleteUserProfileCommand) -> None:
        """Handle user profile deletion."""
        service = UserProfileService(self._uow)
        await service.delete_user_profile(command.user_id)
