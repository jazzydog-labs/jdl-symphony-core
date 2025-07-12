"""Command handlers for CQRS write operations."""

from symphony.application.commands.base import Command, CommandBus, CommandHandler
from symphony.application.commands.repo import (
    CreateRepoCommand,
    CreateRepoHandler,
    DeleteRepoCommand,
    DeleteRepoHandler,
    SyncRepoCommand,
    SyncRepoHandler,
    UpdateRepoCommand,
    UpdateRepoHandler,
)
from symphony.application.commands.user_profile import (
    CreateUserProfileCommand,
    CreateUserProfileHandler,
    DeleteUserProfileCommand,
    DeleteUserProfileHandler,
    UpdateUserProfileCommand,
    UpdateUserProfileHandler,
)
from symphony.application.commands.vault import (
    CreateVaultCommand,
    CreateVaultHandler,
    DeleteVaultCommand,
    DeleteVaultHandler,
    LockVaultCommand,
    LockVaultHandler,
    UnlockVaultCommand,
    UnlockVaultHandler,
    UpdateVaultCommand,
    UpdateVaultHandler,
)
from symphony.application.commands.workspace import (
    CreateWorkspaceCommand,
    CreateWorkspaceHandler,
    DeleteWorkspaceCommand,
    DeleteWorkspaceHandler,
    UpdateWorkspaceCommand,
    UpdateWorkspaceHandler,
)

__all__ = [
    # Base classes
    "Command",
    "CommandHandler",
    "CommandBus",
    # User profile commands
    "CreateUserProfileCommand",
    "CreateUserProfileHandler",
    "UpdateUserProfileCommand",
    "UpdateUserProfileHandler",
    "DeleteUserProfileCommand",
    "DeleteUserProfileHandler",
    # Workspace commands
    "CreateWorkspaceCommand",
    "CreateWorkspaceHandler",
    "UpdateWorkspaceCommand",
    "UpdateWorkspaceHandler",
    "DeleteWorkspaceCommand",
    "DeleteWorkspaceHandler",
    # Repo commands
    "CreateRepoCommand",
    "CreateRepoHandler",
    "UpdateRepoCommand",
    "UpdateRepoHandler",
    "DeleteRepoCommand",
    "DeleteRepoHandler",
    "SyncRepoCommand",
    "SyncRepoHandler",
    # Vault commands
    "CreateVaultCommand",
    "CreateVaultHandler",
    "UpdateVaultCommand",
    "UpdateVaultHandler",
    "DeleteVaultCommand",
    "DeleteVaultHandler",
    "LockVaultCommand",
    "LockVaultHandler",
    "UnlockVaultCommand",
    "UnlockVaultHandler",
]
