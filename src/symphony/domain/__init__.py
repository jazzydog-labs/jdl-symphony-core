"""Symphony domain layer."""

from symphony.domain.exceptions import (
    AlreadyExistsError,
    DomainError,
    InvalidEmailError,
    InvalidRemoteUrlError,
    InvalidRepoPathError,
    InvalidUsernameError,
    InvalidVaultPathError,
    NotFoundError,
    RepoNameConflictError,
    RepoNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
    VaultNameConflictError,
    VaultNotFoundError,
    WorkspaceCreationNotAllowedError,
    WorkspaceDeletionNotAllowedError,
    WorkspaceNameConflictError,
    WorkspaceNotFoundError,
)
from symphony.domain.models import Repo, UserProfile, Vault, Workspace, WorkspaceType

__all__ = [
    # Models
    "UserProfile",
    "Workspace",
    "WorkspaceType",
    "Repo",
    "Vault",
    # Base Exceptions
    "DomainError",
    "ValidationError",
    "NotFoundError",
    "AlreadyExistsError",
    # User Exceptions
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "InvalidUsernameError",
    "InvalidEmailError",
    # Workspace Exceptions
    "WorkspaceNotFoundError",
    "WorkspaceNameConflictError",
    "WorkspaceCreationNotAllowedError",
    "WorkspaceDeletionNotAllowedError",
    # Repo Exceptions
    "RepoNotFoundError",
    "RepoNameConflictError",
    "InvalidRepoPathError",
    "InvalidRemoteUrlError",
    # Vault Exceptions
    "VaultNotFoundError",
    "VaultNameConflictError",
    "InvalidVaultPathError",
]
