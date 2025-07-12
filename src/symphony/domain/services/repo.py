"""Repo domain service for business logic orchestration."""

from typing import Any
from uuid import UUID

from symphony.domain.exceptions import (
    DuplicateRepoNameError,
    RepoLimitExceeded,
    RepoNotFoundError,
    WorkspaceNotFoundError,
    WorkspaceNotOwnedByUserError,
)
from symphony.domain.models.repo import Repo
from symphony.domain.unit_of_work import UnitOfWork


class RepoService:
    """
    Domain service for Repo business logic.

    Coordinates operations that involve multiple aggregates or repositories,
    enforces business rules, and handles cross-cutting concerns.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize service with unit of work."""
        self._uow = uow

    async def create_repo(
        self,
        workspace_id: UUID,
        user_id: UUID,
        name: str,
        path: str | None = None,
        remote_url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Repo:
        """
        Create a new repo in a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User creating the repo (for ownership check)
            name: Repo name
            path: Optional local file path
            remote_url: Optional remote Git URL
            metadata: Optional metadata

        Returns:
            Created repo

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
            RepoLimitExceeded: If workspace has reached repo limit
            DuplicateRepoNameError: If repo name already exists in workspace
            ValueError: If validation fails
        """
        async with self._uow:
            # Verify workspace exists and user owns it
            workspace = await self._uow.workspaces.get(workspace_id)
            if not workspace:
                raise WorkspaceNotFoundError(str(workspace_id))

            if workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(workspace_id), str(user_id))

            # Check repo limit (max 100 per workspace)
            resource_counts = await self._uow.workspaces.count_resources(workspace_id)
            if resource_counts.get("repos", 0) >= 100:
                raise RepoLimitExceeded()

            # Check for duplicate name
            if await self._uow.repos.name_exists_in_workspace(workspace_id, name):
                raise DuplicateRepoNameError(name, str(workspace_id))

            # Create repo
            repo = Repo(
                name=name,
                workspace_id=workspace_id,
                path=path or "",
                remote_url=remote_url,
                metadata=metadata or {},
            )

            # Save repo
            saved_repo = await self._uow.repos.save(repo)
            await self._uow.commit()

            return saved_repo

    async def update_repo(
        self,
        repo_id: UUID,
        user_id: UUID,
        name: str | None = None,
        path: str | None = None,
        remote_url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Repo:
        """
        Update an existing repo.

        Args:
            repo_id: Repo ID
            user_id: User making the update (for ownership check)
            name: New name (optional)
            path: New local path (optional)
            remote_url: New remote URL (optional)
            metadata: New metadata (optional)

        Returns:
            Updated repo

        Raises:
            RepoNotFoundError: If repo doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
            DuplicateRepoNameError: If new name already exists
        """
        async with self._uow:
            # Get repo
            repo = await self._uow.repos.get(repo_id)
            if not repo:
                raise RepoNotFoundError(str(repo_id))

            # Check workspace ownership
            workspace = await self._uow.workspaces.get(repo.workspace_id)
            if not workspace or workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(repo.workspace_id), str(user_id))

            # Check for duplicate name if changing
            if name and name != repo.name:
                if await self._uow.repos.name_exists_in_workspace(
                    repo.workspace_id, name, exclude_id=repo_id
                ):
                    raise DuplicateRepoNameError(name, str(repo.workspace_id))
                repo.name = name

            # Update other fields
            if path is not None:
                repo.path = path
            if remote_url is not None:
                repo.remote_url = remote_url
            if metadata is not None:
                repo.metadata = metadata

            # Update timestamp
            repo.update_timestamp()

            # Save changes
            saved_repo = await self._uow.repos.save(repo)
            await self._uow.commit()

            return saved_repo

    async def get_repo(self, repo_id: UUID, user_id: UUID | None = None) -> Repo:
        """
        Get a repo by ID.

        Args:
            repo_id: Repo ID
            user_id: Optional user ID for ownership check

        Returns:
            Repo

        Raises:
            RepoNotFoundError: If repo doesn't exist
            WorkspaceNotOwnedByUserError: If user_id provided and doesn't own workspace
        """
        async with self._uow:
            repo = await self._uow.repos.get(repo_id)
            if not repo:
                raise RepoNotFoundError(str(repo_id))

            # Check ownership if user_id provided
            if user_id:
                workspace = await self._uow.workspaces.get(repo.workspace_id)
                if not workspace or workspace.user_profile_id != user_id:
                    raise WorkspaceNotOwnedByUserError(str(repo.workspace_id), str(user_id))

            return repo

    async def list_workspace_repos(
        self, workspace_id: UUID, user_id: UUID | None = None
    ) -> list[Repo]:
        """
        List all repos in a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: Optional user ID for ownership check

        Returns:
            List of repos

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

            # Get repos
            return await self._uow.repos.get_by_workspace(workspace_id)

    async def delete_repo(self, repo_id: UUID, user_id: UUID) -> None:
        """
        Delete a repo.

        Args:
            repo_id: Repo ID
            user_id: User making the deletion (for ownership check)

        Raises:
            RepoNotFoundError: If repo doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
        """
        async with self._uow:
            # Get repo
            repo = await self._uow.repos.get(repo_id)
            if not repo:
                raise RepoNotFoundError(str(repo_id))

            # Check workspace ownership
            workspace = await self._uow.workspaces.get(repo.workspace_id)
            if not workspace or workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(repo.workspace_id), str(user_id))

            # Delete repo
            await self._uow.repos.delete(repo_id)
            await self._uow.commit()

    async def sync_with_remote(self, repo_id: UUID, user_id: UUID) -> Repo:
        """
        Sync repo metadata with remote repository.

        This is a placeholder for future Git integration.
        Currently just updates the last_synced timestamp.

        Args:
            repo_id: Repo ID
            user_id: User making the sync (for ownership check)

        Returns:
            Updated repo

        Raises:
            RepoNotFoundError: If repo doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
        """
        async with self._uow:
            # Get repo
            repo = await self._uow.repos.get(repo_id)
            if not repo:
                raise RepoNotFoundError(str(repo_id))

            # Check workspace ownership
            workspace = await self._uow.workspaces.get(repo.workspace_id)
            if not workspace or workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(repo.workspace_id), str(user_id))

            # Update sync timestamp
            repo.mark_synced()

            # Save changes
            saved_repo = await self._uow.repos.save(repo)
            await self._uow.commit()

            return saved_repo
