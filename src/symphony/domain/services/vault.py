"""Vault domain service for business logic orchestration."""

from typing import Any
from uuid import UUID

from symphony.domain.exceptions import (
    DuplicateVaultNameError,
    VaultLimitExceeded,
    VaultNotFoundError,
    WorkspaceNotFoundError,
    WorkspaceNotOwnedByUserError,
)
from symphony.domain.models.vault import Vault
from symphony.domain.unit_of_work import UnitOfWork


class VaultService:
    """
    Domain service for Vault business logic.

    Coordinates operations that involve multiple aggregates or repositories,
    enforces business rules, and handles cross-cutting concerns.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize service with unit of work."""
        self._uow = uow

    async def create_vault(
        self,
        workspace_id: UUID,
        user_id: UUID,
        name: str,
        path: str,
        metadata: dict[str, Any] | None = None,
    ) -> Vault:
        """
        Create a new vault in a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User creating the vault (for ownership check)
            name: Vault name
            path: Path to vault storage
            metadata: Optional metadata

        Returns:
            Created vault

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
            VaultLimitExceeded: If workspace has reached vault limit
            DuplicateVaultNameError: If vault name already exists in workspace
            ValueError: If validation fails
        """
        async with self._uow:
            # Verify workspace exists and user owns it
            workspace = await self._uow.workspaces.get(workspace_id)
            if not workspace:
                raise WorkspaceNotFoundError(str(workspace_id))

            if workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(workspace_id), str(user_id))

            # Check vault limit (max 20 per workspace)
            resource_counts = await self._uow.workspaces.count_resources(workspace_id)
            if resource_counts.get("vaults", 0) >= 20:
                raise VaultLimitExceeded()

            # Check for duplicate name
            if await self._uow.vaults.name_exists_in_workspace(workspace_id, name):
                raise DuplicateVaultNameError(name, str(workspace_id))

            # Create vault
            vault = Vault(
                name=name,
                workspace_id=workspace_id,
                path=path,
                metadata=metadata or {},
            )

            # Save vault
            saved_vault = await self._uow.vaults.save(vault)
            await self._uow.commit()

            return saved_vault

    async def update_vault(
        self,
        vault_id: UUID,
        user_id: UUID,
        name: str | None = None,
        path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Vault:
        """
        Update an existing vault.

        Args:
            vault_id: Vault ID
            user_id: User making the update (for ownership check)
            name: New name (optional)
            path: New vault path (optional)
            metadata: New metadata (optional)

        Returns:
            Updated vault

        Raises:
            VaultNotFoundError: If vault doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
            DuplicateVaultNameError: If new name already exists
        """
        async with self._uow:
            # Get vault
            vault = await self._uow.vaults.get(vault_id)
            if not vault:
                raise VaultNotFoundError(str(vault_id))

            # Check workspace ownership
            workspace = await self._uow.workspaces.get(vault.workspace_id)
            if not workspace or workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(vault.workspace_id), str(user_id))

            # Check for duplicate name if changing
            if name and name != vault.name:
                if await self._uow.vaults.name_exists_in_workspace(
                    vault.workspace_id, name, exclude_id=vault_id
                ):
                    raise DuplicateVaultNameError(name, str(vault.workspace_id))
                vault.name = name

            # Update other fields
            if path is not None:
                vault.path = path
            if metadata is not None:
                vault.metadata = metadata

            # Update timestamp
            vault.update_timestamp()

            # Save changes
            saved_vault = await self._uow.vaults.save(vault)
            await self._uow.commit()

            return saved_vault

    async def get_vault(self, vault_id: UUID, user_id: UUID | None = None) -> Vault:
        """
        Get a vault by ID.

        Args:
            vault_id: Vault ID
            user_id: Optional user ID for ownership check

        Returns:
            Vault

        Raises:
            VaultNotFoundError: If vault doesn't exist
            WorkspaceNotOwnedByUserError: If user_id provided and doesn't own workspace
        """
        async with self._uow:
            vault = await self._uow.vaults.get(vault_id)
            if not vault:
                raise VaultNotFoundError(str(vault_id))

            # Check ownership if user_id provided
            if user_id:
                workspace = await self._uow.workspaces.get(vault.workspace_id)
                if not workspace or workspace.user_profile_id != user_id:
                    raise WorkspaceNotOwnedByUserError(str(vault.workspace_id), str(user_id))

            return vault

    async def list_workspace_vaults(
        self, workspace_id: UUID, user_id: UUID | None = None
    ) -> list[Vault]:
        """
        List all vaults in a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: Optional user ID for ownership check

        Returns:
            List of vaults

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspaceNotOwnedByUserError: If user_id provided and doesn't own workspace
        """
        async with self._uow:
            # Verify workspace exists
            workspace = await self._uow.workspaces.get(workspace_id)
            if not workspace:
                raise WorkspaceNotFoundError(str(workspace_id))

            # Check ownership if user_id provided
            if user_id and workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(workspace_id), str(user_id))

            # Get vaults
            return await self._uow.vaults.get_by_workspace(workspace_id)

    async def delete_vault(self, vault_id: UUID, user_id: UUID) -> None:
        """
        Delete a vault.

        Args:
            vault_id: Vault ID
            user_id: User making the deletion (for ownership check)

        Raises:
            VaultNotFoundError: If vault doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
        """
        async with self._uow:
            # Get vault
            vault = await self._uow.vaults.get(vault_id)
            if not vault:
                raise VaultNotFoundError(str(vault_id))

            # Check workspace ownership
            workspace = await self._uow.workspaces.get(vault.workspace_id)
            if not workspace or workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(vault.workspace_id), str(user_id))

            # Delete vault
            await self._uow.vaults.delete(vault_id)
            await self._uow.commit()

    async def lock_vault(self, vault_id: UUID, user_id: UUID) -> Vault:
        """
        Lock a vault to prevent access.

        Args:
            vault_id: Vault ID
            user_id: User making the lock (for ownership check)

        Returns:
            Updated vault

        Raises:
            VaultNotFoundError: If vault doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
        """
        async with self._uow:
            # Get vault
            vault = await self._uow.vaults.get(vault_id)
            if not vault:
                raise VaultNotFoundError(str(vault_id))

            # Check workspace ownership
            workspace = await self._uow.workspaces.get(vault.workspace_id)
            if not workspace or workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(vault.workspace_id), str(user_id))

            # Lock vault
            vault.lock()

            # Save changes
            saved_vault = await self._uow.vaults.save(vault)
            await self._uow.commit()

            return saved_vault

    async def unlock_vault(self, vault_id: UUID, user_id: UUID) -> Vault:
        """
        Unlock a vault to allow access.

        Args:
            vault_id: Vault ID
            user_id: User making the unlock (for ownership check)

        Returns:
            Updated vault

        Raises:
            VaultNotFoundError: If vault doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
        """
        async with self._uow:
            # Get vault
            vault = await self._uow.vaults.get(vault_id)
            if not vault:
                raise VaultNotFoundError(str(vault_id))

            # Check workspace ownership
            workspace = await self._uow.workspaces.get(vault.workspace_id)
            if not workspace or workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(vault.workspace_id), str(user_id))

            # Unlock vault
            vault.unlock()

            # Save changes
            saved_vault = await self._uow.vaults.save(vault)
            await self._uow.commit()

            return saved_vault
