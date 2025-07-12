"""User profile query handlers."""

from dataclasses import dataclass
from uuid import UUID

from symphony.application.dto import UserProfileDTO
from symphony.application.queries.base import Query, QueryHandler
from symphony.domain.services.user_profile import UserProfileService


@dataclass(frozen=True)
class GetUserProfileQuery(Query):
    """Query to get a user profile by ID."""

    user_id: UUID


@dataclass(frozen=True)
class GetUserProfileByUsernameQuery(Query):
    """Query to get a user profile by username."""

    username: str


@dataclass(frozen=True)
class GetUserProfileByEmailQuery(Query):
    """Query to get a user profile by email."""

    email: str


class GetUserProfileHandler(QueryHandler[GetUserProfileQuery, UserProfileDTO]):
    """Handler for getting user profiles by ID."""

    async def handle(self, query: GetUserProfileQuery) -> UserProfileDTO:
        """Handle user profile retrieval by ID."""
        service = UserProfileService(self._uow)

        user_profile = await service.get_user_profile(query.user_id)

        return UserProfileDTO(
            id=user_profile.id,
            username=user_profile.username,
            email=user_profile.email,
            preferences=user_profile.preferences,
            created_at=user_profile.created_at,
            updated_at=user_profile.updated_at,
        )


class GetUserProfileByUsernameHandler(QueryHandler[GetUserProfileByUsernameQuery, UserProfileDTO]):
    """Handler for getting user profiles by username."""

    async def handle(self, query: GetUserProfileByUsernameQuery) -> UserProfileDTO:
        """Handle user profile retrieval by username."""
        service = UserProfileService(self._uow)

        user_profile = await service.get_user_profile_by_username(query.username)

        return UserProfileDTO(
            id=user_profile.id,
            username=user_profile.username,
            email=user_profile.email,
            preferences=user_profile.preferences,
            created_at=user_profile.created_at,
            updated_at=user_profile.updated_at,
        )


class GetUserProfileByEmailHandler(QueryHandler[GetUserProfileByEmailQuery, UserProfileDTO]):
    """Handler for getting user profiles by email."""

    async def handle(self, query: GetUserProfileByEmailQuery) -> UserProfileDTO:
        """Handle user profile retrieval by email."""
        service = UserProfileService(self._uow)

        user_profile = await service.get_user_profile_by_email(query.email)

        return UserProfileDTO(
            id=user_profile.id,
            username=user_profile.username,
            email=user_profile.email,
            preferences=user_profile.preferences,
            created_at=user_profile.created_at,
            updated_at=user_profile.updated_at,
        )
