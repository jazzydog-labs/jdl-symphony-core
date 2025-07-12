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
class UserProfileNotFoundError(NotFoundError):
    """Raised when a user profile is not found."""

    def __init__(self, user_id: str):
        super().__init__("UserProfile", str(user_id))


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


class UsernameAlreadyExistsError(AlreadyExistsError):
    """Raised when username is already taken."""

    def __init__(self, username: str):
        super().__init__("UserProfile", "username", username)


class EmailAlreadyExistsError(AlreadyExistsError):
    """Raised when email is already taken."""

    def __init__(self, email: str):
        super().__init__("UserProfile", "email", email)


# Workspace-specific exceptions
class WorkspaceNotFoundError(NotFoundError):
    """Raised when a workspace is not found."""

    def __init__(self, workspace_id: str):
        super().__init__("Workspace", str(workspace_id))


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


class WorkspaceLimitExceeded(DomainError):
    """Raised when user has reached maximum workspace limit."""

    def __init__(self):
        super().__init__("User has reached maximum workspace limit (50)", code="WORKSPACE_LIMIT_EXCEEDED")


class WorkspaceNotOwnedByUserError(DomainError):
    """Raised when user tries to access workspace they don't own."""

    def __init__(self, workspace_id: str, user_id: str):
        message = f"Workspace {workspace_id} is not owned by user {user_id}"
        super().__init__(message, code="WORKSPACE_NOT_OWNED")


# Repo-specific exceptions
class RepoNotFoundError(NotFoundError):
    """Raised when a repository is not found."""

    def __init__(self, repo_id: str):
        super().__init__("Repo", str(repo_id))


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


class DuplicateRepoNameError(AlreadyExistsError):
    """Raised when repo name already exists in workspace."""

    def __init__(self, repo_name: str, workspace_id: str):
        super().__init__("Repo", "name", f"{repo_name} in workspace {workspace_id}")


class RepoLimitExceeded(DomainError):
    """Raised when workspace has reached maximum repo limit."""

    def __init__(self):
        super().__init__("Workspace has reached maximum repo limit (100)", code="REPO_LIMIT_EXCEEDED")


# Vault-specific exceptions
class VaultNotFoundError(NotFoundError):
    """Raised when a vault is not found."""

    def __init__(self, vault_id: str):
        super().__init__("Vault", str(vault_id))


class VaultNameConflictError(AlreadyExistsError):
    """Raised when vault name conflicts with existing vault in workspace."""

    def __init__(self, vault_name: str):
        super().__init__("Vault", "name", vault_name)


class InvalidVaultPathError(ValidationError):
    """Raised when vault path is invalid."""

    def __init__(self, message: str):
        super().__init__(message, field="path")


class DuplicateVaultNameError(AlreadyExistsError):
    """Raised when vault name already exists in workspace."""

    def __init__(self, vault_name: str, workspace_id: str):
        super().__init__("Vault", "name", f"{vault_name} in workspace {workspace_id}")


class VaultLimitExceeded(DomainError):
    """Raised when workspace has reached maximum vault limit."""

    def __init__(self):
        super().__init__("Workspace has reached maximum vault limit (20)", code="VAULT_LIMIT_EXCEEDED")
