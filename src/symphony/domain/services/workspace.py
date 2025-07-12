"""Workspace domain service for business logic orchestration."""

from typing import Any
from uuid import UUID

from symphony.domain.exceptions import (
    RepoLimitExceeded,
    UserProfileNotFoundError,
    VaultLimitExceeded,
    WorkspaceLimitExceeded,
    WorkspaceNotFoundError,
    WorkspaceNotOwnedByUserError,
)
from symphony.domain.models.workspace import Workspace, WorkspaceType
from symphony.domain.unit_of_work import UnitOfWork


class WorkspaceService:
    """
    Domain service for Workspace business logic.

    Coordinates operations that involve multiple aggregates or repositories,
    enforces business rules, and handles cross-cutting concerns.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize service with unit of work."""
        self._uow = uow

    async def create_workspace(
        self,
        user_id: UUID,
        name: str,
        workspace_type: WorkspaceType = "general",
        description: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Workspace:
        """
        Create a new workspace for a user.

        Args:
            user_id: Owner's user profile ID
            name: Workspace name
            workspace_type: Type of workspace
            description: Optional description
            settings: Optional workspace settings

        Returns:
            Created workspace

        Raises:
            UserProfileNotFoundError: If user doesn't exist
            WorkspaceLimitExceeded: If user has reached workspace limit
            ValueError: If validation fails
        """
        async with self._uow:
            # Verify user exists
            if not await self._uow.user_profiles.exists(user_id):
                raise UserProfileNotFoundError(str(user_id))

            # Check workspace limit (max 50 per user)
            workspace_count = await self._uow.user_profiles.count_workspaces(user_id)
            if workspace_count >= 50:
                raise WorkspaceLimitExceeded()

            # Create workspace
            workspace = Workspace(
                name=name,
                user_profile_id=user_id,
                workspace_type=workspace_type,
                description=description,
                settings=settings or {},
            )

            # Save workspace
            saved_workspace = await self._uow.workspaces.save(workspace)
            await self._uow.commit()

            return saved_workspace

    async def update_workspace(
        self,
        workspace_id: UUID,
        user_id: UUID,
        name: str | None = None,
        description: str | None = None,
        settings: dict[str, Any] | None = None,
        shared_resources: dict[str, list[UUID]] | None = None,
    ) -> Workspace:
        """
        Update an existing workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User making the update (for ownership check)
            name: New name (optional)
            description: New description (optional)
            settings: New settings (optional)
            shared_resources: New shared resources (optional)

        Returns:
            Updated workspace

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
        """
        async with self._uow:
            # Get workspace
            workspace = await self._uow.workspaces.get(workspace_id)
            if not workspace:
                raise WorkspaceNotFoundError(str(workspace_id))

            # Check ownership
            if workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(workspace_id), str(user_id))

            # Update fields
            if name is not None:
                workspace.name = name
            if description is not None:
                workspace.description = description
            if settings is not None:
                workspace.settings = settings
            if shared_resources is not None:
                workspace.shared_resources = shared_resources

            # Update timestamp
            workspace.update_timestamp()

            # Save changes
            saved_workspace = await self._uow.workspaces.save(workspace)
            await self._uow.commit()

            return saved_workspace

    async def get_workspace(self, workspace_id: UUID, user_id: UUID | None = None) -> Workspace:
        """
        Get a workspace by ID.

        Args:
            workspace_id: Workspace ID
            user_id: Optional user ID for ownership check

        Returns:
            Workspace

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspaceNotOwnedByUserError: If user_id provided and doesn't own workspace
        """
        async with self._uow:
            workspace = await self._uow.workspaces.get(workspace_id)
            if not workspace:
                raise WorkspaceNotFoundError(str(workspace_id))

            # Check ownership if user_id provided
            if user_id and workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(workspace_id), str(user_id))

            return workspace

    async def list_user_workspaces(
        self, user_id: UUID, workspace_type: WorkspaceType | None = None
    ) -> list[Workspace]:
        """
        List all workspaces for a user.

        Args:
            user_id: User profile ID
            workspace_type: Optional filter by type

        Returns:
            List of workspaces

        Raises:
            UserProfileNotFoundError: If user doesn't exist
        """
        async with self._uow:
            # Verify user exists
            if not await self._uow.user_profiles.exists(user_id):
                raise UserProfileNotFoundError(str(user_id))

            # Get workspaces
            if workspace_type:
                return await self._uow.workspaces.get_by_user_and_type(user_id, workspace_type)
            else:
                return await self._uow.workspaces.get_by_user(user_id)

    async def delete_workspace(self, workspace_id: UUID, user_id: UUID) -> None:
        """
        Delete a workspace and all its resources.

        This will cascade delete all repos and vaults in the workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User making the deletion (for ownership check)

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspaceNotOwnedByUserError: If user doesn't own workspace
        """
        async with self._uow:
            # Get workspace to check ownership
            workspace = await self._uow.workspaces.get(workspace_id)
            if not workspace:
                raise WorkspaceNotFoundError(str(workspace_id))

            # Check ownership
            if workspace.user_profile_id != user_id:
                raise WorkspaceNotOwnedByUserError(str(workspace_id), str(user_id))

            # Delete workspace (cascades to repos and vaults)
            await self._uow.workspaces.delete(workspace_id)
            await self._uow.commit()

    async def can_add_repo(self, workspace_id: UUID) -> bool:
        """
        Check if a workspace can add more repos.

        Enforces business rule: max 100 repos per workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            True if workspace can add more repos

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
        """
        async with self._uow:
            # Verify workspace exists
            if not await self._uow.workspaces.exists(workspace_id):
                raise WorkspaceNotFoundError(str(workspace_id))

            # Check repo count
            resource_counts = await self._uow.workspaces.count_resources(workspace_id)
            return resource_counts.get("repos", 0) < 100

    async def can_add_vault(self, workspace_id: UUID) -> bool:
        """
        Check if a workspace can add more vaults.

        Enforces business rule: max 20 vaults per workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            True if workspace can add more vaults

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
        """
        async with self._uow:
            # Verify workspace exists
            if not await self._uow.workspaces.exists(workspace_id):
                raise WorkspaceNotFoundError(str(workspace_id))

            # Check vault count
            resource_counts = await self._uow.workspaces.count_resources(workspace_id)
            return resource_counts.get("vaults", 0) < 20

    async def check_repo_limit(self, workspace_id: UUID) -> None:
        """
        Check repo limit and raise exception if exceeded.

        Args:
            workspace_id: Workspace ID

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            RepoLimitExceeded: If workspace has reached repo limit
        """
        if not await self.can_add_repo(workspace_id):
            raise RepoLimitExceeded()

    async def check_vault_limit(self, workspace_id: UUID) -> None:
        """
        Check vault limit and raise exception if exceeded.

        Args:
            workspace_id: Workspace ID

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            VaultLimitExceeded: If workspace has reached vault limit
        """
        if not await self.can_add_vault(workspace_id):
            raise VaultLimitExceeded()

    async def get_workspace_stats(self, workspace_id: UUID) -> dict[str, int]:
        """
        Get statistics for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Dictionary with resource counts

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
        """
        async with self._uow:
            # Verify workspace exists
            if not await self._uow.workspaces.exists(workspace_id):
                raise WorkspaceNotFoundError(str(workspace_id))

            # Get resource counts
            return await self._uow.workspaces.count_resources(workspace_id)
