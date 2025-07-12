"""Workspace query handlers."""

from dataclasses import dataclass
from uuid import UUID

from symphony.application.dto import WorkspaceDTO, WorkspaceStatsDTO
from symphony.application.queries.base import Query, QueryHandler
from symphony.domain.models.workspace import WorkspaceType
from symphony.domain.services.workspace import WorkspaceService


@dataclass(frozen=True)
class GetWorkspaceQuery(Query):
    """Query to get a workspace by ID."""

    workspace_id: UUID
    user_id: UUID | None = None


@dataclass(frozen=True)
class ListUserWorkspacesQuery(Query):
    """Query to list all workspaces for a user."""

    user_id: UUID
    workspace_type: WorkspaceType | None = None


@dataclass(frozen=True)
class GetWorkspaceStatsQuery(Query):
    """Query to get workspace statistics."""

    workspace_id: UUID


class GetWorkspaceHandler(QueryHandler[GetWorkspaceQuery, WorkspaceDTO]):
    """Handler for getting workspaces by ID."""

    async def handle(self, query: GetWorkspaceQuery) -> WorkspaceDTO:
        """Handle workspace retrieval."""
        service = WorkspaceService(self._uow)

        workspace = await service.get_workspace(query.workspace_id, query.user_id)

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


class ListUserWorkspacesHandler(QueryHandler[ListUserWorkspacesQuery, list[WorkspaceDTO]]):
    """Handler for listing user workspaces."""

    async def handle(self, query: ListUserWorkspacesQuery) -> list[WorkspaceDTO]:
        """Handle user workspaces listing."""
        service = WorkspaceService(self._uow)

        workspaces = await service.list_user_workspaces(query.user_id, query.workspace_type)

        return [
            WorkspaceDTO(
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
            for workspace in workspaces
        ]


class GetWorkspaceStatsHandler(QueryHandler[GetWorkspaceStatsQuery, WorkspaceStatsDTO]):
    """Handler for getting workspace statistics."""

    async def handle(self, query: GetWorkspaceStatsQuery) -> WorkspaceStatsDTO:
        """Handle workspace statistics retrieval."""
        service = WorkspaceService(self._uow)

        stats = await service.get_workspace_stats(query.workspace_id)

        return WorkspaceStatsDTO(
            workspace_id=query.workspace_id,
            repo_count=stats.get("repos", 0),
            vault_count=stats.get("vaults", 0),
            total_resources=stats.get("repos", 0) + stats.get("vaults", 0),
        )
