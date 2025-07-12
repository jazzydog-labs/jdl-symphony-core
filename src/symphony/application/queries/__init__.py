"""Query handlers for CQRS read operations."""

from symphony.application.queries.base import Query, QueryBus, QueryHandler
from symphony.application.queries.repo import (
    GetRepoHandler,
    GetRepoQuery,
    ListWorkspaceReposHandler,
    ListWorkspaceReposQuery,
)
from symphony.application.queries.user_profile import (
    GetUserProfileByEmailHandler,
    GetUserProfileByEmailQuery,
    GetUserProfileByUsernameHandler,
    GetUserProfileByUsernameQuery,
    GetUserProfileHandler,
    GetUserProfileQuery,
)
from symphony.application.queries.vault import (
    GetVaultHandler,
    GetVaultQuery,
    ListWorkspaceVaultsHandler,
    ListWorkspaceVaultsQuery,
)
from symphony.application.queries.workspace import (
    GetWorkspaceHandler,
    GetWorkspaceQuery,
    GetWorkspaceStatsHandler,
    GetWorkspaceStatsQuery,
    ListUserWorkspacesHandler,
    ListUserWorkspacesQuery,
)

__all__ = [
    # Base classes
    "Query",
    "QueryHandler",
    "QueryBus",
    # User profile queries
    "GetUserProfileQuery",
    "GetUserProfileHandler",
    "GetUserProfileByUsernameQuery",
    "GetUserProfileByUsernameHandler",
    "GetUserProfileByEmailQuery",
    "GetUserProfileByEmailHandler",
    # Workspace queries
    "GetWorkspaceQuery",
    "GetWorkspaceHandler",
    "ListUserWorkspacesQuery",
    "ListUserWorkspacesHandler",
    "GetWorkspaceStatsQuery",
    "GetWorkspaceStatsHandler",
    # Repo queries
    "GetRepoQuery",
    "GetRepoHandler",
    "ListWorkspaceReposQuery",
    "ListWorkspaceReposHandler",
    # Vault queries
    "GetVaultQuery",
    "GetVaultHandler",
    "ListWorkspaceVaultsQuery",
    "ListWorkspaceVaultsHandler",
]
