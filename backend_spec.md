# JDL Symphony Backend Implementation Specification

**Project Name:** `jdl-symphony-core`  
**Description:** Local work organization system backend - the orchestral core that harmonizes your development workflow

## Phase 0 Implementation Goals

Build a minimal, explorable backend following the provided Python project framework that demonstrates the domain model with basic CRUD operations for core aggregates.

## Technology Stack (Per Framework Document)

- **Project Management:** Hatch + uv + Just
- **Code Quality:** Ruff + Pyright + pre-commit
- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy 2.0+
- **Validation:** Pydantic v2
- **Testing:** pytest + pytest-cov
- **Configuration:** Pydantic BaseSettings
- **Containerization:** Docker with Chainguard images

## Project Structure

```
jdl-symphony-core/
├── pyproject.toml              # Single source of truth (Hatch config)
├── Justfile                    # Developer command aliases
├── uv.lock                     # Deterministic dependencies
├── Dockerfile                  # Multi-stage with Chainguard base
├── docker-compose.yml          # Local PostgreSQL
├── .pre-commit-config.yaml     # Ruff + GitGuardian hooks
├── README.md
├── src/symphony/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Pydantic settings
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/             # Pure domain entities
│   │   │   ├── __init__.py
│   │   │   ├── user_profile.py
│   │   │   ├── workspace.py
│   │   │   ├── repo.py
│   │   │   └── vault.py
│   │   ├── repositories/       # Abstract interfaces
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user_profile.py
│   │   │   ├── workspace.py
│   │   │   ├── repo.py
│   │   │   └── vault.py
│   │   └── services/           # Domain business logic
│   │       ├── __init__.py
│   │       ├── user_profile_service.py
│   │       └── workspace_service.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py   # SQLAlchemy session management
│   │   │   ├── models/         # ORM models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── user_context.py
│   │   │   │   ├── workspace.py
│   │   │   │   ├── repo.py
│   │   │   │   └── vault.py
│   │   │   └── repositories/   # Concrete implementations
│   │   │       ├── __init__.py
│   │   │       ├── user_context.py
│   │   │       ├── workspace.py
│   │   │       ├── repo.py
│   │   │       └── vault.py
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── dependencies.py # FastAPI dependency injection
│   │       ├── schemas/        # Pydantic request/response models
│   │       │   ├── __init__.py
│   │       │   ├── user_context.py
│   │       │   ├── workspace.py
│   │       │   ├── repo.py
│   │       │   └── vault.py
│   │       └── routes/         # FastAPI route handlers
│   │           ├── __init__.py
│   │           ├── health.py
│   │           ├── user_contexts.py
│   │           ├── workspaces.py
│   │           ├── repos.py
│   │           └── vaults.py
│   └── application/
│       ├── __init__.py
│       ├── commands/           # Command handlers (CQRS)
│       │   ├── __init__.py
│       │   ├── user_profile_commands.py
│       │   └── workspace_commands.py
│       └── queries/            # Query handlers
│           ├── __init__.py
│           ├── user_profile_queries.py
│           └── workspace_queries.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   └── application/
│   ├── integration/
│   │   ├── __init__.py
│   │   └── api/
│   └── fixtures/              # Test data
└── docs/
    ├── index.md
    ├── api.md
    └── development.md
```

## Proposed Aggregate Architecture

### Two-Level Aggregate Design

**UserProfile** - Global user data and cross-workspace resources
- Personal information, preferences, authentication
- Global contacts, templates, standards that can be shared
- User-level habits, goals, and calendar
- Acts as the identity anchor but doesn't "own" workspaces

**Workspace** - Independent work contexts 
- Self-contained working environments for specific themes/projects
- Can reference/link to global UserProfile resources
- Contains domain-specific repos, vaults, projects, todos
- Full autonomy for workspace-specific data and workflows

### Benefits of This Design
- **Workspace Independence**: Each workspace can be developed, backed up, shared independently
- **Resource Sharing**: Global resources (contacts, templates) can be selectively shared
- **Clean Boundaries**: Clear separation between personal identity and work contexts  
- **Scalability**: Workspaces don't compete for resources in a single massive aggregate
- **Flexibility**: Different workspace types (client work, research, personal) with different access patterns

### Core Implementation Requirements

### 1. Domain Models (Phase 0 Scope)

Implement these 4 core aggregates with pure Python domain models:

#### UserProfile (Aggregate Root - Global User Data)
```python
@dataclass
class UserProfile:
    id: UUID
    username: str
    email: str
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def validate_username(self) -> bool:
        # Domain validation rules
        return len(self.username) >= 3 and self.username.isalnum()
    
    def can_create_workspace(self) -> bool:
        # Business rules for workspace creation limits
        return True
    
    def update_preferences(self, new_preferences: Dict[str, Any]) -> None:
        # Domain logic for preference updates
        self.preferences.update(new_preferences)
        self.updated_at = datetime.utcnow()
```

### Domain Services

#### UserProfileService
```python
class UserProfileService:
    def __init__(self, user_repository: UserProfileRepository):
        self.user_repository = user_repository
    
    async def create_user_profile(self, username: str, email: str) -> UserProfile:
        # Business logic for user creation
        if await self.user_repository.exists_by_username(username):
            raise UserAlreadyExistsError(f"Username {username} already exists")
        
        if await self.user_repository.exists_by_email(email):
            raise UserAlreadyExistsError(f"Email {email} already exists")
            
        user_profile = UserProfile(
            id=uuid.uuid4(),
            username=username,
            email=email,
            preferences={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        if not user_profile.validate_username():
            raise InvalidUsernameError("Username must be at least 3 characters and alphanumeric")
            
        return await self.user_repository.save(user_profile)
    
    async def get_user_workspaces_count(self, user_id: UUID) -> int:
        # Cross-aggregate query coordination
        return await self.user_repository.count_user_workspaces(user_id)
```

#### WorkspaceService  
```python
class WorkspaceService:
    def __init__(self, 
                 workspace_repository: WorkspaceRepository,
                 user_repository: UserProfileRepository):
        self.workspace_repository = workspace_repository
        self.user_repository = user_repository
    
    async def create_workspace(self, user_id: UUID, name: str, 
                             description: Optional[str] = None,
                             workspace_type: str = 'general') -> Workspace:
        # Verify user exists and can create workspace
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
            
        if not user.can_create_workspace():
            raise WorkspaceCreationNotAllowedError("User cannot create more workspaces")
        
        # Check for workspace name uniqueness per user
        existing = await self.workspace_repository.get_by_user_and_name(user_id, name)
        if existing:
            raise WorkspaceNameConflictError(f"Workspace '{name}' already exists for user")
            
        workspace = Workspace(
            id=uuid.uuid4(),
            name=name,
            description=description,
            user_profile_id=user_id,
            workspace_type=workspace_type,
            settings={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self.workspace_repository.save(workspace)
```

#### Workspace (Aggregate Root - Independent Work Context)
```python
@dataclass
class Workspace:
    id: UUID
    name: str
    description: Optional[str]
    user_profile_id: UUID  # References owner, not owned by
    workspace_type: str  # 'client', 'personal', 'research', etc.
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def can_be_deleted(self) -> bool:
        # Business rules for deletion
        pass
    
    def add_shared_resource(self, resource_id: UUID, resource_type: str) -> None:
        # Link to global resources (contacts, templates)
        pass
```

#### Repo (Aggregate Root)
```python
@dataclass
class Repo:
    id: UUID
    name: str
    path: str
    workspace_id: UUID
    remote_url: Optional[str]
    created_at: datetime
    updated_at: datetime
```

#### Vault (Aggregate Root)
```python
@dataclass
class Vault:
    id: UUID
    name: str
    path: str
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime
```

### 2. Database Schema

Create PostgreSQL tables respecting aggregate boundaries:

```sql
-- Core tables for Phase 0
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id),
    workspace_type VARCHAR(50) DEFAULT 'general',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Future: Global resources table for cross-workspace sharing
CREATE TABLE global_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id),
    resource_type VARCHAR(50) NOT NULL, -- 'contact', 'template', 'snippet'
    resource_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Junction table for workspace access to global resources
CREATE TABLE workspace_global_resources (
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES global_resources(id) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'read', -- 'read', 'write', 'copy'
    PRIMARY KEY (workspace_id, resource_id)
);

CREATE TABLE repos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    path TEXT NOT NULL,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    remote_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE vaults (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    path TEXT NOT NULL,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. API Endpoints (Phase 0 Scope)

Implement basic CRUD operations for core aggregates:

#### User Profiles  
- `POST /user-profiles` - Create user profile
- `GET /user-profiles/{id}` - Get user profile  
- `PUT /user-profiles/{id}` - Update user profile

#### Workspaces
- `POST /user-profiles/{user_id}/workspaces` - Create workspace for user
- `GET /user-profiles/{user_id}/workspaces` - List user's workspaces
- `GET /workspaces/{id}` - Get workspace
- `PUT /workspaces/{id}` - Update workspace
- `DELETE /workspaces/{id}` - Delete workspace

#### Repos
- `POST /workspaces/{workspace_id}/repos` - Create repo
- `GET /workspaces/{workspace_id}/repos` - List repos in workspace
- `GET /repos/{id}` - Get repo
- `PUT /repos/{id}` - Update repo
- `DELETE /repos/{id}` - Delete repo

#### Vaults
- `POST /workspaces/{workspace_id}/vaults` - Create vault
- `GET /workspaces/{workspace_id}/vaults` - List vaults in workspace
- `GET /vaults/{id}` - Get vault
- `PUT /vaults/{id}` - Update vault
- `DELETE /vaults/{id}` - Delete vault

### 4. Configuration Management

Implement Pydantic BaseSettings for environment-based configuration:

```python
# src/symphony/config.py
from pydantic import BaseSettings, Field

class DatabaseSettings(BaseSettings):
    url: str = Field(..., env="DATABASE_URL")
    echo: bool = Field(False, env="DATABASE_ECHO")
    
class APISettings(BaseSettings):
    title: str = Field("JDL Symphony Core", env="API_TITLE")
    version: str = Field("0.1.0", env="API_VERSION")
    debug: bool = Field(False, env="API_DEBUG")

class UserSettings(BaseSettings):
    max_workspaces_per_user: int = Field(50, env="USER_MAX_WORKSPACES")
    username_min_length: int = Field(3, env="USER_USERNAME_MIN_LENGTH")
    
class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    api: APISettings = APISettings()
    user: UserSettings = UserSettings()
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
```

### 5. Development Commands (Justfile)

```makefile
# Justfile
install:
    uv sync

lint:
    hatch run lint:all

typecheck:
    hatch run typecheck:check

test:
    hatch run test:cov

run:
    hatch run dev:server

db-up:
    docker-compose up -d postgres

db-down:
    docker-compose down

db-migrate:
    hatch run alembic upgrade head

build:
    docker buildx build --platform linux/amd64,linux/arm64 -t jdl-symphony-core:latest .

build-debug:
    docker buildx build --build-arg DEBUG_IMAGE=true -t jdl-symphony-core:debug .
```

## Testing Strategy

### Unit Tests
- Domain model business logic
- Repository interfaces (with mocks)
- Application services

### Integration Tests
- Database repositories with real PostgreSQL
- API endpoints with test database
- Full request/response cycles

### Test Configuration
```python
# tests/conftest.py
@pytest.fixture
async def test_db():
    # Create isolated test database
    pass

@pytest.fixture
async def client():
    # FastAPI test client
    pass
```

## Docker Configuration

### Multi-stage Dockerfile
```dockerfile
# Build stage with Chainguard
FROM chainguard/python:latest-dev as builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Production stage
FROM chainguard/python:latest
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
USER nonroot
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/app/.venv/bin/python", "-m", "symphony"]
```

### Docker Compose for Development
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: symphony_dev
      POSTGRES_USER: symphony
      POSTGRES_PASSWORD: symphony
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Success Criteria

### Phase 0 Deliverables
1. **Setup Time < 30 minutes**
   - `just install && just db-up && just db-migrate && just run`
   - Service running on `http://localhost:8000`
   - Interactive API docs at `http://localhost:8000/docs`

2. **"Hello World" in < 5 commands**
   ```bash
   git clone <repo>
   cd jdl-symphony-core
   just install
   just db-up && just db-migrate
   just run
   ```

3. **Core Functionality Demonstrated**
   - Create a user profile via API
   - Create multiple workspaces for that user (e.g., "Client Work", "Personal Projects")  
   - Add repos and vaults to different workspaces
   - Query each workspace independently with its contents
   - Demonstrate workspace isolation and independence

### API Documentation
- Automatic OpenAPI generation via FastAPI
- Interactive Swagger UI at `/docs`
- ReDoc documentation at `/redoc`

## Out of Scope for Phase 0

- Authentication/authorization
- Advanced entity relationships (Projects, Todos, etc.)
- File system integration for repos/vaults
- External synchronization
- Advanced querying/filtering
- Event sourcing/CQRS complexity
- Performance optimization
- CI/CD pipeline

## Next Phase Preparation

The architecture should be extensible for:
- Additional domain entities from the full model
- Authentication middleware
- File system watchers for repos/vaults
- External API integrations
- Event-driven architecture
- Advanced querying capabilities

This specification provides a solid foundation for implementing the JDL Symphony backend while following the established project framework and maintaining focus on core domain modeling and API functionality.