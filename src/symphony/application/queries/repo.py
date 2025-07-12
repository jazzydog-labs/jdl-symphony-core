"""Repository query handlers."""

from dataclasses import dataclass
from uuid import UUID

from symphony.application.dto import RepoDTO
from symphony.application.queries.base import Query, QueryHandler
from symphony.domain.services.repo import RepoService


@dataclass(frozen=True)
class GetRepoQuery(Query):
    """Query to get a repository by ID."""

    repo_id: UUID
    user_id: UUID | None = None


@dataclass(frozen=True)
class ListWorkspaceReposQuery(Query):
    """Query to list all repositories in a workspace."""

    workspace_id: UUID
    user_id: UUID | None = None


class GetRepoHandler(QueryHandler[GetRepoQuery, RepoDTO]):
    """Handler for getting repositories by ID."""

    async def handle(self, query: GetRepoQuery) -> RepoDTO:
        """Handle repository retrieval."""
        service = RepoService(self._uow)

        repo = await service.get_repo(query.repo_id, query.user_id)

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


class ListWorkspaceReposHandler(QueryHandler[ListWorkspaceReposQuery, list[RepoDTO]]):
    """Handler for listing workspace repositories."""

    async def handle(self, query: ListWorkspaceReposQuery) -> list[RepoDTO]:
        """Handle workspace repositories listing."""
        service = RepoService(self._uow)

        repos = await service.list_workspace_repos(query.workspace_id, query.user_id)

        return [
            RepoDTO(
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
            for repo in repos
        ]
