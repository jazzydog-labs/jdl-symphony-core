"""SQLAlchemy implementation of RepoRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from symphony.domain.models.repo import Repo
from symphony.domain.repositories.repo import RepoRepository
from symphony.infrastructure.database.models.repo import RepoDB
from symphony.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyRepoRepository(SQLAlchemyRepository[Repo, RepoDB], RepoRepository):
    """SQLAlchemy implementation of RepoRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository."""
        super().__init__(session, RepoDB)

    async def get_by_workspace(self, workspace_id: UUID) -> list[Repo]:
        """Get all repos in a workspace."""
        stmt = select(RepoDB).where(RepoDB.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_by_name(self, workspace_id: UUID, name: str) -> Repo | None:
        """Find a repo by name within a workspace."""
        stmt = select(RepoDB).where(RepoDB.workspace_id == workspace_id, RepoDB.name == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def name_exists_in_workspace(
        self, workspace_id: UUID, name: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if a repo name already exists in a workspace."""
        stmt = select(RepoDB.id).where(RepoDB.workspace_id == workspace_id, RepoDB.name == name)
        if exclude_id:
            stmt = stmt.where(RepoDB.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def count_by_workspace(self, workspace_id: UUID) -> int:
        """Count repos in a workspace."""
        stmt = select(func.count(RepoDB.id)).where(RepoDB.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    def _to_entity(self, model: RepoDB) -> Repo:
        """Convert database model to domain entity."""
        return Repo(
            id=model.id,
            name=model.name,
            path=model.path,
            workspace_id=model.workspace_id,
            remote_url=model.remote_url,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Repo) -> RepoDB:
        """Convert domain entity to database model."""
        return RepoDB(
            id=entity.id,
            name=entity.name,
            path=entity.path,
            workspace_id=entity.workspace_id,
            remote_url=entity.remote_url,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
