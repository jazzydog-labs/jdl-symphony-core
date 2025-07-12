"""SQLAlchemy implementation of WorkspaceRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from symphony.domain.models.workspace import Workspace, WorkspaceType
from symphony.domain.repositories.workspace import WorkspaceRepository
from symphony.infrastructure.database.models.repo import RepoDB
from symphony.infrastructure.database.models.vault import VaultDB
from symphony.infrastructure.database.models.workspace import WorkspaceDB
from symphony.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyWorkspaceRepository(
    SQLAlchemyRepository[Workspace, WorkspaceDB], WorkspaceRepository
):
    """SQLAlchemy implementation of WorkspaceRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository."""
        super().__init__(session, WorkspaceDB)

    async def get_by_user(self, user_id: UUID) -> list[Workspace]:
        """Get all workspaces for a user."""
        stmt = select(WorkspaceDB).where(WorkspaceDB.user_profile_id == user_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_by_user_and_type(
        self, user_id: UUID, workspace_type: WorkspaceType
    ) -> list[Workspace]:
        """Get workspaces for a user filtered by type."""
        stmt = select(WorkspaceDB).where(
            WorkspaceDB.user_profile_id == user_id, WorkspaceDB.workspace_type == workspace_type
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count_resources(self, workspace_id: UUID) -> dict[str, int]:
        """Count resources (repos, vaults) in a workspace."""
        # Count repos
        repos_stmt = select(func.count(RepoDB.id)).where(RepoDB.workspace_id == workspace_id)
        repos_result = await self.session.execute(repos_stmt)
        repos_count = repos_result.scalar() or 0

        # Count vaults
        vaults_stmt = select(func.count(VaultDB.id)).where(VaultDB.workspace_id == workspace_id)
        vaults_result = await self.session.execute(vaults_stmt)
        vaults_count = vaults_result.scalar() or 0

        return {
            "repos": repos_count,
            "vaults": vaults_count,
        }

    async def has_active_resources(self, workspace_id: UUID) -> bool:
        """Check if a workspace has any active resources."""
        counts = await self.count_resources(workspace_id)
        return sum(counts.values()) > 0

    def _to_entity(self, model: WorkspaceDB) -> Workspace:
        """Convert database model to domain entity."""
        return Workspace(
            id=model.id,
            name=model.name,
            description=model.description,
            user_profile_id=model.user_profile_id,
            workspace_type=model.workspace_type,  # type: ignore
            settings=model.settings,
            shared_resources=model.shared_resources,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Workspace) -> WorkspaceDB:
        """Convert domain entity to database model."""
        return WorkspaceDB(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            user_profile_id=entity.user_profile_id,
            workspace_type=entity.workspace_type,
            settings=entity.settings,
            shared_resources=entity.shared_resources,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
