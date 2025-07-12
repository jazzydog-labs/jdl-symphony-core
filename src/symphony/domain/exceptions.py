"""Domain-specific exceptions for Symphony."""


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code


class ValidationError(DomainError):
    """Raised when domain validation fails."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class NotFoundError(DomainError):
    """Base exception for entity not found errors."""

    def __init__(self, entity_type: str, entity_id: str):
        message = f"{entity_type} with id '{entity_id}' not found"
        super().__init__(message, code="NOT_FOUND")
        self.entity_type = entity_type
        self.entity_id = entity_id


class AlreadyExistsError(DomainError):
    """Base exception for entity already exists errors."""

    def __init__(self, entity_type: str, field: str, value: str):
        message = f"{entity_type} with {field} '{value}' already exists"
        super().__init__(message, code="ALREADY_EXISTS")
        self.entity_type = entity_type
        self.field = field
        self.value = value


# User-specific exceptions
class UserNotFoundError(NotFoundError):
    """Raised when a user profile is not found."""

    def __init__(self, user_id: str):
        super().__init__("UserProfile", user_id)


class UserAlreadyExistsError(AlreadyExistsError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, field: str, value: str):
        super().__init__("UserProfile", field, value)


class InvalidUsernameError(ValidationError):
    """Raised when username validation fails."""

    def __init__(self, message: str):
        super().__init__(message, field="username")


class InvalidEmailError(ValidationError):
    """Raised when email validation fails."""

    def __init__(self, message: str):
        super().__init__(message, field="email")


# Workspace-specific exceptions
class WorkspaceNotFoundError(NotFoundError):
    """Raised when a workspace is not found."""

    def __init__(self, workspace_id: str):
        super().__init__("Workspace", workspace_id)


class WorkspaceNameConflictError(AlreadyExistsError):
    """Raised when workspace name conflicts with existing workspace."""

    def __init__(self, workspace_name: str):
        super().__init__("Workspace", "name", workspace_name)


class WorkspaceCreationNotAllowedError(DomainError):
    """Raised when user cannot create more workspaces."""

    def __init__(self, message: str):
        super().__init__(message, code="WORKSPACE_LIMIT_EXCEEDED")


class WorkspaceDeletionNotAllowedError(DomainError):
    """Raised when workspace cannot be deleted due to business rules."""

    def __init__(self, message: str):
        super().__init__(message, code="WORKSPACE_DELETION_NOT_ALLOWED")


# Repo-specific exceptions
class RepoNotFoundError(NotFoundError):
    """Raised when a repository is not found."""

    def __init__(self, repo_id: str):
        super().__init__("Repo", repo_id)


class RepoNameConflictError(AlreadyExistsError):
    """Raised when repo name conflicts with existing repo in workspace."""

    def __init__(self, repo_name: str):
        super().__init__("Repo", "name", repo_name)


class InvalidRepoPathError(ValidationError):
    """Raised when repository path is invalid."""

    def __init__(self, message: str):
        super().__init__(message, field="path")


class InvalidRemoteUrlError(ValidationError):
    """Raised when repository remote URL is invalid."""

    def __init__(self, message: str):
        super().__init__(message, field="remote_url")


# Vault-specific exceptions
class VaultNotFoundError(NotFoundError):
    """Raised when a vault is not found."""

    def __init__(self, vault_id: str):
        super().__init__("Vault", vault_id)


class VaultNameConflictError(AlreadyExistsError):
    """Raised when vault name conflicts with existing vault in workspace."""

    def __init__(self, vault_name: str):
        super().__init__("Vault", "name", vault_name)


class InvalidVaultPathError(ValidationError):
    """Raised when vault path is invalid."""

    def __init__(self, message: str):
        super().__init__(message, field="path")
