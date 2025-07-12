Follow the instructions in backend_spec.md to initialize the repo.

Make sure all the just commands run and the tests pass.

# Before starting implementation
Please check all the things you have to do, and before you start doing them check that you have the relevant permissins (e.g. write, git, just, etc) to run your commands by attempting to create tmp files in this directory, and then cleaning them up.

## Implementation Progress

Track progress in `jdl-symphony-core/todo.md`
See high-level implementation plan in `jdl-symphony-core/project-plan.md`
See architectural patterns and conventions in `jdl-symphony-core/architecture.md`

Current status: Domain services layer completed (Commit 6). Next step is to implement application layer with CQRS patterns (Commit 7).

When resuming work:
1. Check todo.md for current progress
2. Review project-plan.md for implementation strategy
3. Continue from the next uncompleted task
4. Make commits at each major milestone (as outlined in project plan)
5. Ensure tests pass before each commit

## Post-Commit Documentation Updates

After making a commit, ALWAYS:
1. Update the "Current status" section in CLAUDE.md to reflect what was just completed
2. Update todo.md to mark completed items and reflect current progress
3. Update architecture.md if you've made any architectural decisions or changes
4. If you used any development strategies or patterns not captured in CLAUDE.md or referenced files, document them
5. If you discovered any important patterns or decisions during implementation, add them to the relevant documentation

This ensures continuity between sessions and helps maintain accurate project state.


## Development Decisions and Patterns

### Justfile Commands
- All commands use `uv run` directly instead of `hatch run` for better compatibility
- The default recipe shows available commands with `just --list`
- Each major feature has its own demo script (e.g., `just demo-domain-models`)

### Domain Model Implementation
- Used `@dataclass` with validation in `__post_init__` for clean domain models
- Implemented UTC-aware datetime handling with `datetime.UTC` 
- Created comprehensive exception hierarchy with base classes for common patterns
- Validation methods return bool for consistency and reusability

### Database Model Implementation
- Created SQLAlchemy ORM models with proper relationships and cascades
- Used Mapped[] annotations for better type safety
- Implemented proper foreign key constraints with CASCADE delete
- Created conversion functions between domain and database models
- Added greenlet dependency for async SQLAlchemy support
- Manual migration created at alembic/versions/001_initial_schema.py

### Demo Mode Configuration
- Added `demo_mode` flag and `demo_database_url` to Settings
- Created `get_demo_settings()` helper in `symphony.config.demo`
- Updated database connection module to support demo mode
- When `demo_mode=True`, uses in-memory SQLite instead of PostgreSQL
- Demos are isolated from production database - no risk of data pollution
- All demos use `get_demo_settings()` to ensure they run in safe mode

### Repository Pattern Implementation
- Abstract repository interfaces in domain layer following clean architecture
- Generic base repository with CRUD operations
- Concrete SQLAlchemy implementations with domain-to-database model conversion
- Repository-specific methods for domain queries (e.g., get_by_username)
- Unit of Work pattern for transaction management across repositories
- Demo mode support with separate database connection
- Type-safe generic implementation using Python's Generic[T] pattern
- Added `reportUnknownVariableType = false` to pyright config for dict[str, Any] annotations

### Domain Services Implementation
- Service layer orchestrates business logic across multiple aggregates
- Each entity has dedicated service (UserProfileService, WorkspaceService, RepoService, VaultService)
- Services enforce business rules and limits (50 workspaces/user, 100 repos/workspace, 20 vaults/workspace)
- Ownership validation for all operations ensuring users can only access their resources
- Lock/unlock functionality for vaults with proper business logic
- Comprehensive exception handling with domain-specific errors
- Async/await pattern throughout with proper transaction boundaries
- Demo script shows complete CRUD operations and business rule enforcement

## Creating working demo before each commit
Before each of your commits, create a fully working demo showing off the features you have added that can be run, end-to-end, with `just demo`. `just demo` runs all of the feature demos, (e.g. `just demo-domain-models`). Test the newly added demo, and all the demos, before commiting, and fix anything needed to make them work.

