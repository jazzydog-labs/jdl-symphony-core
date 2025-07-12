"""Repository command handlers."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from symphony.application.commands.base import Command, CommandHandler
from symphony.application.dto import RepoDTO
from symphony.domain.services.repo import RepoService


@dataclass(frozen=True)
class CreateRepoCommand(Command):
    """Command to create a new repository."""

    workspace_id: UUID
    user_id: UUID
    name: str
    path: str | None = None
    remote_url: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class UpdateRepoCommand(Command):
    """Command to update an existing repository."""

    repo_id: UUID
    user_id: UUID
    name: str | None = None
    path: str | None = None
    remote_url: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class DeleteRepoCommand(Command):
    """Command to delete a repository."""

    repo_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class SyncRepoCommand(Command):
    """Command to sync repository with remote."""

    repo_id: UUID
    user_id: UUID


class CreateRepoHandler(CommandHandler[CreateRepoCommand, RepoDTO]):
    """Handler for creating repositories."""

    async def handle(self, command: CreateRepoCommand) -> RepoDTO:
        """Handle repository creation."""
        service = RepoService(self._uow)

        repo = await service.create_repo(
            workspace_id=command.workspace_id,
            user_id=command.user_id,
            name=command.name,
            path=command.path,
            remote_url=command.remote_url,
            metadata=command.metadata,
        )

        return RepoDTO(
            id=repo.id,
            name=repo.name,
            workspace_id=repo.workspace_id,
            path=repo.path,
            remote_url=repo.remote_url,
            metadata=repo.metadata,
            last_synced=repo.last_synced,
            created_at=repo.created_at,
            updated_at=repo.updated_at,
        )


class UpdateRepoHandler(CommandHandler[UpdateRepoCommand, RepoDTO]):
    """Handler for updating repositories."""

    async def handle(self, command: UpdateRepoCommand) -> RepoDTO:
        """Handle repository update."""
        service = RepoService(self._uow)

        repo = await service.update_repo(
            repo_id=command.repo_id,
            user_id=command.user_id,
            name=command.name,
            path=command.path,
            remote_url=command.remote_url,
            metadata=command.metadata,
        )

        return RepoDTO(
            id=repo.id,
            name=repo.name,
            workspace_id=repo.workspace_id,
            path=repo.path,
            remote_url=repo.remote_url,
            metadata=repo.metadata,
            last_synced=repo.last_synced,
            created_at=repo.created_at,
            updated_at=repo.updated_at,
        )


class DeleteRepoHandler(CommandHandler[DeleteRepoCommand, None]):
    """Handler for deleting repositories."""

    async def handle(self, command: DeleteRepoCommand) -> None:
        """Handle repository deletion."""
        service = RepoService(self._uow)
        await service.delete_repo(command.repo_id, command.user_id)


class SyncRepoHandler(CommandHandler[SyncRepoCommand, RepoDTO]):
    """Handler for syncing repositories."""

    async def handle(self, command: SyncRepoCommand) -> RepoDTO:
        """Handle repository sync."""
        service = RepoService(self._uow)

        repo = await service.sync_with_remote(command.repo_id, command.user_id)

        return RepoDTO(
            id=repo.id,
            name=repo.name,
            workspace_id=repo.workspace_id,
            path=repo.path,
            remote_url=repo.remote_url,
            metadata=repo.metadata,
            last_synced=repo.last_synced,
            created_at=repo.created_at,
            updated_at=repo.updated_at,
        )
