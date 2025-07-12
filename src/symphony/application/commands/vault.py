"""Vault command handlers."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from symphony.application.commands.base import Command, CommandHandler
from symphony.application.dto import VaultDTO
from symphony.domain.services.vault import VaultService


@dataclass(frozen=True)
class CreateVaultCommand(Command):
    """Command to create a new vault."""

    workspace_id: UUID
    user_id: UUID
    name: str
    path: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class UpdateVaultCommand(Command):
    """Command to update an existing vault."""

    vault_id: UUID
    user_id: UUID
    name: str | None = None
    path: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class DeleteVaultCommand(Command):
    """Command to delete a vault."""

    vault_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class LockVaultCommand(Command):
    """Command to lock a vault."""

    vault_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class UnlockVaultCommand(Command):
    """Command to unlock a vault."""

    vault_id: UUID
    user_id: UUID


class CreateVaultHandler(CommandHandler[CreateVaultCommand, VaultDTO]):
    """Handler for creating vaults."""

    async def handle(self, command: CreateVaultCommand) -> VaultDTO:
        """Handle vault creation."""
        service = VaultService(self._uow)

        vault = await service.create_vault(
            workspace_id=command.workspace_id,
            user_id=command.user_id,
            name=command.name,
            path=command.path,
            metadata=command.metadata,
        )

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


class UpdateVaultHandler(CommandHandler[UpdateVaultCommand, VaultDTO]):
    """Handler for updating vaults."""

    async def handle(self, command: UpdateVaultCommand) -> VaultDTO:
        """Handle vault update."""
        service = VaultService(self._uow)

        vault = await service.update_vault(
            vault_id=command.vault_id,
            user_id=command.user_id,
            name=command.name,
            path=command.path,
            metadata=command.metadata,
        )

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


class DeleteVaultHandler(CommandHandler[DeleteVaultCommand, None]):
    """Handler for deleting vaults."""

    async def handle(self, command: DeleteVaultCommand) -> None:
        """Handle vault deletion."""
        service = VaultService(self._uow)
        await service.delete_vault(command.vault_id, command.user_id)


class LockVaultHandler(CommandHandler[LockVaultCommand, VaultDTO]):
    """Handler for locking vaults."""

    async def handle(self, command: LockVaultCommand) -> VaultDTO:
        """Handle vault locking."""
        service = VaultService(self._uow)

        vault = await service.lock_vault(command.vault_id, command.user_id)

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


class UnlockVaultHandler(CommandHandler[UnlockVaultCommand, VaultDTO]):
    """Handler for unlocking vaults."""

    async def handle(self, command: UnlockVaultCommand) -> VaultDTO:
        """Handle vault unlocking."""
        service = VaultService(self._uow)

        vault = await service.unlock_vault(command.vault_id, command.user_id)

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
