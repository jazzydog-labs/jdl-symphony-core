"""Use case orchestration layer for the application."""

from symphony.application.commands import (
    CommandBus,
    CreateRepoHandler,
    CreateUserProfileHandler,
    CreateVaultHandler,
    CreateWorkspaceHandler,
    DeleteRepoHandler,
    DeleteUserProfileHandler,
    DeleteVaultHandler,
    DeleteWorkspaceHandler,
    LockVaultHandler,
    SyncRepoHandler,
    UnlockVaultHandler,
    UpdateRepoHandler,
    UpdateUserProfileHandler,
    UpdateVaultHandler,
    UpdateWorkspaceHandler,
)
from symphony.application.commands.repo import (
    CreateRepoCommand,
    DeleteRepoCommand,
    SyncRepoCommand,
    UpdateRepoCommand,
)
from symphony.application.commands.user_profile import (
    CreateUserProfileCommand,
    DeleteUserProfileCommand,
    UpdateUserProfileCommand,
)
from symphony.application.commands.vault import (
    CreateVaultCommand,
    DeleteVaultCommand,
    LockVaultCommand,
    UnlockVaultCommand,
    UpdateVaultCommand,
)
from symphony.application.commands.workspace import (
    CreateWorkspaceCommand,
    DeleteWorkspaceCommand,
    UpdateWorkspaceCommand,
)
from symphony.application.queries import (
    GetRepoHandler,
    GetUserProfileByEmailHandler,
    GetUserProfileByUsernameHandler,
    GetUserProfileHandler,
    GetVaultHandler,
    GetWorkspaceHandler,
    GetWorkspaceStatsHandler,
    ListUserWorkspacesHandler,
    ListWorkspaceReposHandler,
    ListWorkspaceVaultsHandler,
    QueryBus,
)
from symphony.application.queries.repo import GetRepoQuery, ListWorkspaceReposQuery
from symphony.application.queries.user_profile import (
    GetUserProfileByEmailQuery,
    GetUserProfileByUsernameQuery,
    GetUserProfileQuery,
)
from symphony.application.queries.vault import GetVaultQuery, ListWorkspaceVaultsQuery
from symphony.application.queries.workspace import (
    GetWorkspaceQuery,
    GetWorkspaceStatsQuery,
    ListUserWorkspacesQuery,
)
from symphony.domain.unit_of_work import UnitOfWork


class ApplicationService:
    """
    Main application service that orchestrates use cases.

    This service sets up the command and query buses with their handlers
    and provides a unified interface for executing application operations.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize application service with unit of work."""
        self._uow = uow
        self._command_bus = CommandBus()
        self._query_bus = QueryBus()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Register all command and query handlers."""
        # Register command handlers
        self._command_bus.register(CreateUserProfileCommand, CreateUserProfileHandler(self._uow))
        self._command_bus.register(UpdateUserProfileCommand, UpdateUserProfileHandler(self._uow))
        self._command_bus.register(DeleteUserProfileCommand, DeleteUserProfileHandler(self._uow))

        self._command_bus.register(CreateWorkspaceCommand, CreateWorkspaceHandler(self._uow))
        self._command_bus.register(UpdateWorkspaceCommand, UpdateWorkspaceHandler(self._uow))
        self._command_bus.register(DeleteWorkspaceCommand, DeleteWorkspaceHandler(self._uow))

        self._command_bus.register(CreateRepoCommand, CreateRepoHandler(self._uow))
        self._command_bus.register(UpdateRepoCommand, UpdateRepoHandler(self._uow))
        self._command_bus.register(DeleteRepoCommand, DeleteRepoHandler(self._uow))
        self._command_bus.register(SyncRepoCommand, SyncRepoHandler(self._uow))

        self._command_bus.register(CreateVaultCommand, CreateVaultHandler(self._uow))
        self._command_bus.register(UpdateVaultCommand, UpdateVaultHandler(self._uow))
        self._command_bus.register(DeleteVaultCommand, DeleteVaultHandler(self._uow))
        self._command_bus.register(LockVaultCommand, LockVaultHandler(self._uow))
        self._command_bus.register(UnlockVaultCommand, UnlockVaultHandler(self._uow))

        # Register query handlers
        self._query_bus.register(GetUserProfileQuery, GetUserProfileHandler(self._uow))
        self._query_bus.register(GetUserProfileByUsernameQuery, GetUserProfileByUsernameHandler(self._uow))
        self._query_bus.register(GetUserProfileByEmailQuery, GetUserProfileByEmailHandler(self._uow))

        self._query_bus.register(GetWorkspaceQuery, GetWorkspaceHandler(self._uow))
        self._query_bus.register(ListUserWorkspacesQuery, ListUserWorkspacesHandler(self._uow))
        self._query_bus.register(GetWorkspaceStatsQuery, GetWorkspaceStatsHandler(self._uow))

        self._query_bus.register(GetRepoQuery, GetRepoHandler(self._uow))
        self._query_bus.register(ListWorkspaceReposQuery, ListWorkspaceReposHandler(self._uow))

        self._query_bus.register(GetVaultQuery, GetVaultHandler(self._uow))
        self._query_bus.register(ListWorkspaceVaultsQuery, ListWorkspaceVaultsHandler(self._uow))

    @property
    def commands(self) -> CommandBus:
        """Get the command bus for executing write operations."""
        return self._command_bus

    @property
    def queries(self) -> QueryBus:
        """Get the query bus for executing read operations."""
        return self._query_bus
