"""SQLAlchemy implementation of UserProfileRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from symphony.domain.models.user_profile import UserProfile
from symphony.domain.repositories.user_profile import UserProfileRepository
from symphony.infrastructure.database.models.user_profile import UserProfileDB
from symphony.infrastructure.database.models.workspace import WorkspaceDB
from symphony.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyUserProfileRepository(
    SQLAlchemyRepository[UserProfile, UserProfileDB], UserProfileRepository
):
    """SQLAlchemy implementation of UserProfileRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository."""
        super().__init__(session, UserProfileDB)

    async def get_by_username(self, username: str) -> UserProfile | None:
        """Find a user profile by username."""
        stmt = select(UserProfileDB).where(UserProfileDB.username == username)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> UserProfile | None:
        """Find a user profile by email."""
        stmt = select(UserProfileDB).where(UserProfileDB.email == email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def username_exists(self, username: str, exclude_id: UUID | None = None) -> bool:
        """Check if a username is already in use."""
        stmt = select(UserProfileDB.id).where(UserProfileDB.username == username)
        if exclude_id:
            stmt = stmt.where(UserProfileDB.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def email_exists(self, email: str, exclude_id: UUID | None = None) -> bool:
        """Check if an email is already in use."""
        stmt = select(UserProfileDB.id).where(UserProfileDB.email == email)
        if exclude_id:
            stmt = stmt.where(UserProfileDB.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def count_workspaces(self, user_id: UUID) -> int:
        """Count the number of workspaces owned by a user."""
        stmt = select(func.count(WorkspaceDB.id)).where(WorkspaceDB.user_profile_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    def _to_entity(self, model: UserProfileDB) -> UserProfile:
        """Convert database model to domain entity."""
        return UserProfile(
            id=model.id,
            username=model.username,
            email=model.email,
            preferences=model.preferences,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: UserProfile) -> UserProfileDB:
        """Convert domain entity to database model."""
        return UserProfileDB(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            preferences=entity.preferences,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
