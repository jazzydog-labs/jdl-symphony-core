"""Workspace command handlers."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from symphony.application.commands.base import Command, CommandHandler
from symphony.application.dto import WorkspaceDTO
from symphony.domain.models.workspace import WorkspaceType
from symphony.domain.services.workspace import WorkspaceService


@dataclass(frozen=True)
class CreateWorkspaceCommand(Command):
    """Command to create a new workspace."""

    user_id: UUID
    name: str
    workspace_type: WorkspaceType = "general"
    description: str | None = None
    settings: dict[str, Any] | None = None


@dataclass(frozen=True)
class UpdateWorkspaceCommand(Command):
    """Command to update an existing workspace."""

    workspace_id: UUID
    user_id: UUID
    name: str | None = None
    description: str | None = None
    settings: dict[str, Any] | None = None
    shared_resources: dict[str, list[UUID]] | None = None


@dataclass(frozen=True)
class DeleteWorkspaceCommand(Command):
    """Command to delete a workspace."""

    workspace_id: UUID
    user_id: UUID


class CreateWorkspaceHandler(CommandHandler[CreateWorkspaceCommand, WorkspaceDTO]):
    """Handler for creating workspaces."""

    async def handle(self, command: CreateWorkspaceCommand) -> WorkspaceDTO:
        """Handle workspace creation."""
        service = WorkspaceService(self._uow)

        workspace = await service.create_workspace(
            user_id=command.user_id,
            name=command.name,
            workspace_type=command.workspace_type,
            description=command.description,
            settings=command.settings,
        )

        return WorkspaceDTO(
            id=workspace.id,
            name=workspace.name,
            user_profile_id=workspace.user_profile_id,
            workspace_type=workspace.workspace_type,
            description=workspace.description,
            settings=workspace.settings,
            shared_resources=workspace.shared_resources,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
        )


class UpdateWorkspaceHandler(CommandHandler[UpdateWorkspaceCommand, WorkspaceDTO]):
    """Handler for updating workspaces."""

    async def handle(self, command: UpdateWorkspaceCommand) -> WorkspaceDTO:
        """Handle workspace update."""
        service = WorkspaceService(self._uow)

        workspace = await service.update_workspace(
            workspace_id=command.workspace_id,
            user_id=command.user_id,
            name=command.name,
            description=command.description,
            settings=command.settings,
            shared_resources=command.shared_resources,
        )

        return WorkspaceDTO(
            id=workspace.id,
            name=workspace.name,
            user_profile_id=workspace.user_profile_id,
            workspace_type=workspace.workspace_type,
            description=workspace.description,
            settings=workspace.settings,
            shared_resources=workspace.shared_resources,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
        )


class DeleteWorkspaceHandler(CommandHandler[DeleteWorkspaceCommand, None]):
    """Handler for deleting workspaces."""

    async def handle(self, command: DeleteWorkspaceCommand) -> None:
        """Handle workspace deletion."""
        service = WorkspaceService(self._uow)
        await service.delete_workspace(command.workspace_id, command.user_id)
