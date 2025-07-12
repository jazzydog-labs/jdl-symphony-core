"""Vault query handlers."""

from dataclasses import dataclass
from uuid import UUID

from symphony.application.dto import VaultDTO
from symphony.application.queries.base import Query, QueryHandler
from symphony.domain.services.vault import VaultService


@dataclass(frozen=True)
class GetVaultQuery(Query):
    """Query to get a vault by ID."""

    vault_id: UUID
    user_id: UUID | None = None


@dataclass(frozen=True)
class ListWorkspaceVaultsQuery(Query):
    """Query to list all vaults in a workspace."""

    workspace_id: UUID
    user_id: UUID | None = None


class GetVaultHandler(QueryHandler[GetVaultQuery, VaultDTO]):
    """Handler for getting vaults by ID."""

    async def handle(self, query: GetVaultQuery) -> VaultDTO:
        """Handle vault retrieval."""
        service = VaultService(self._uow)

        vault = await service.get_vault(query.vault_id, query.user_id)

        return VaultDTO(
            id=vault.id,
            name=vault.name,
            workspace_id=vault.workspace_id,
            path=vault.path,
            metadata=vault.metadata,
            is_locked=vault.is_locked,
            created_at=vault.created_at,
            updated_at=vault.updated_at,
        )


class ListWorkspaceVaultsHandler(QueryHandler[ListWorkspaceVaultsQuery, list[VaultDTO]]):
    """Handler for listing workspace vaults."""

    async def handle(self, query: ListWorkspaceVaultsQuery) -> list[VaultDTO]:
        """Handle workspace vaults listing."""
        service = VaultService(self._uow)

        vaults = await service.list_workspace_vaults(query.workspace_id, query.user_id)

        return [
            VaultDTO(
                id=vault.id,
                name=vault.name,
                workspace_id=vault.workspace_id,
                path=vault.path,
                metadata=vault.metadata,
                is_locked=vault.is_locked,
                created_at=vault.created_at,
                updated_at=vault.updated_at,
            )
            for vault in vaults
        ]
