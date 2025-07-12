# Symphony Architecture Guide

This document explains the architectural patterns, naming conventions, and design decisions used in the Symphony codebase.

## Table of Contents
- [Overall Architecture](#overall-architecture)
- [Domain-Driven Design (DDD)](#domain-driven-design-ddd)
- [Repository Pattern](#repository-pattern)
- [Naming Conventions](#naming-conventions)
- [Clean Architecture Layers](#clean-architecture-layers)
- [Unit of Work Pattern](#unit-of-work-pattern)

## Overall Architecture

Symphony follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
│                  Routes, Schemas, DTOs                      │
├─────────────────────────────────────────────────────────────┤
│                  Application Layer                          │
│                  Services, Use Cases                        │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer                             │
│          Models, Repositories (interfaces), Services        │
├─────────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                        │
│        Database, External APIs, Implementations             │
└─────────────────────────────────────────────────────────────┘
```

## Domain-Driven Design (DDD)

### Aggregates
Symphony uses a two-level aggregate design:

1. **UserProfile** - Global user identity aggregate
   - Represents the user across the entire system
   - Contains authentication info, preferences, and global settings
   - Does NOT own workspaces (workspaces reference users)

2. **Workspace** - Independent work context aggregate
   - Self-contained environments for specific themes/projects
   - Types: general, client, personal, research
   - Owns Repos and Vaults as child entities
   - References but doesn't own UserProfile

### Entities vs Value Objects
- **Entities**: Have unique identity (UUID) - UserProfile, Workspace, Repo, Vault
- **Value Objects**: Defined by their attributes - WorkspaceType, preferences, settings

## Repository Pattern

The Repository pattern provides an abstraction over data storage, allowing the domain layer to remain ignorant of database implementation details.

### Naming Convention
Repositories follow the pattern: `[DomainModel]Repository`

This can lead to seemingly redundant names:
- `UserProfileRepository` - Repository for UserProfile entities ✓
- `WorkspaceRepository` - Repository for Workspace entities ✓
- `RepoRepository` - Repository for Repo entities (Git repositories) 🤔
- `VaultRepository` - Repository for Vault entities ✓

#### Why "RepoRepository"?
The name `RepoRepository` appears redundant because:
- **Repo** (domain model) = A Git repository (like a GitHub repo)
- **Repository** (pattern) = A class that handles database operations

So `RepoRepository` means "the database handler for Git repository entities". This follows our consistent naming pattern even though it creates this linguistic oddity.

### Repository Responsibilities
Each repository:
- Provides CRUD operations (Create, Read, Update, Delete)
- Implements domain-specific queries (e.g., `get_by_username`)
- Converts between domain models and database models
- Maintains transaction boundaries (via Unit of Work)

## Naming Conventions

### General Patterns
- **Domain Models**: Simple names (`UserProfile`, `Workspace`, `Repo`, `Vault`)
- **Database Models**: Suffix with `DB` (`UserProfileDB`, `WorkspaceDB`)
- **Repositories**: Suffix with `Repository` (`UserProfileRepository`)
- **Services**: Suffix with `Service` (`UserProfileService`, `WorkspaceService`)
- **Exceptions**: Descriptive names (`UsernameTakenError`, `WorkspaceLimitExceeded`)

### File Organization
```
src/symphony/
├── domain/               # Pure business logic
│   ├── models/          # Domain entities
│   ├── repositories/    # Repository interfaces (abstract)
│   ├── services/        # Domain services
│   └── exceptions.py    # Domain exceptions
├── infrastructure/      # External concerns
│   └── database/
│       ├── models.py    # SQLAlchemy ORM models
│       └── repositories/  # Concrete implementations
├── application/         # Use cases and application services
└── api/                # HTTP layer (FastAPI)
```

## Clean Architecture Layers

### Domain Layer
- **No external dependencies** - Pure Python only
- Contains business rules and logic
- Defines interfaces (protocols/ABCs) for infrastructure
- Examples: `UserProfile`, `WorkspaceRepository` (interface)

### Infrastructure Layer
- Implements interfaces defined by domain
- Handles external concerns (database, APIs, file system)
- Contains framework-specific code (SQLAlchemy, FastAPI)
- Examples: `SQLAlchemyUserProfileRepository`, database models

### Application Layer
- Orchestrates domain objects to perform use cases
- Transaction management
- Cross-cutting concerns (logging, validation)
- Examples: `CreateWorkspaceService`, `AuthenticationService`

### API Layer
- HTTP-specific concerns
- Request/response DTOs (Pydantic schemas)
- Route definitions
- Authentication/authorization middleware

## Unit of Work Pattern

The Unit of Work pattern ensures that all repository operations within a business transaction either complete successfully or roll back together.

```python
# Usage example
async with uow:
    user = await uow.user_profiles.get(user_id)
    workspace = Workspace(name="New Project", user_profile_id=user.id)
    await uow.workspaces.save(workspace)
    await uow.commit()  # All changes committed together
```

Benefits:
- Atomic transactions across multiple repositories
- Consistent database state
- Simplified transaction management in services
- Testability (can mock the entire UoW)

## Design Decisions

### Async-First
All database operations are async using SQLAlchemy's async support. This allows for better scalability and non-blocking I/O operations.

### Type Safety
- Extensive use of type hints
- Generic repository base classes
- Pydantic for runtime validation
- Pyright in strict mode for static analysis

### Demo Mode
Special configuration for demos that:
- Uses in-memory SQLite instead of PostgreSQL
- Isolates demo data from production
- Enables SQL echo for educational purposes
- Accessible via `get_demo_settings()`