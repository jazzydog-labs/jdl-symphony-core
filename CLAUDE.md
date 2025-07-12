Follow the instructions in backend_spec.md to initialize the repo.

Make sure all the just commands run and the tests pass.

# Before starting implementation
Please check all the things you have to do, and before you start doing them check that you have the relevant permissins (e.g. write, git, just, etc) to run your commands by attempting to create tmp files in this directory, and then cleaning them up.

## Implementation Progress

Track progress in `jdl-symphony-core/todo.md`
See high-level implementation plan in `jdl-symphony-core/project-plan.md`

Current status: Domain models implemented (Commit 3). Next step is to implement database models and migrations (Commit 4).

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
3. If you used any development strategies or patterns not captured in CLAUDE.md or referenced files, document them
4. If you discovered any important patterns or decisions during implementation, add them to the relevant documentation

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

## Creating working demo before each commit
Before each of your commits, create a fully working demo showing off the features you have added that can be run, end-to-end, with `just demo`. `just demo` runs all of the feature demos, (e.g. `just demo-domain-models`) in