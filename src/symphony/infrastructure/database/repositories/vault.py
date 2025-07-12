"""SQLAlchemy implementation of VaultRepository."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from symphony.domain.models.vault import Vault
from symphony.domain.repositories.vault import VaultRepository
from symphony.infrastructure.database.models.vault import VaultDB
from symphony.infrastructure.database.repositories.base import SQLAlchemyRepository


class SQLAlchemyVaultRepository(SQLAlchemyRepository[Vault, VaultDB], VaultRepository):
    """SQLAlchemy implementation of VaultRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository."""
        super().__init__(session, VaultDB)

    async def get_by_workspace(self, workspace_id: UUID) -> list[Vault]:
        """Get all vaults in a workspace."""
        stmt = select(VaultDB).where(VaultDB.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_by_name(self, workspace_id: UUID, name: str) -> Vault | None:
        """Find a vault by name within a workspace."""
        stmt = select(VaultDB).where(VaultDB.workspace_id == workspace_id, VaultDB.name == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def name_exists_in_workspace(
        self, workspace_id: UUID, name: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if a vault name already exists in a workspace."""
        stmt = select(VaultDB.id).where(VaultDB.workspace_id == workspace_id, VaultDB.name == name)
        if exclude_id:
            stmt = stmt.where(VaultDB.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def count_by_workspace(self, workspace_id: UUID) -> int:
        """Count vaults in a workspace."""
        stmt = select(func.count(VaultDB.id)).where(VaultDB.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    def _to_entity(self, model: VaultDB) -> Vault:
        """Convert database model to domain entity."""
        return Vault(
            id=model.id,
            name=model.name,
            path=model.path,
            workspace_id=model.workspace_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Vault) -> VaultDB:
        """Convert domain entity to database model."""
        return VaultDB(
            id=entity.id,
            name=entity.name,
            path=entity.path,
            workspace_id=entity.workspace_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
