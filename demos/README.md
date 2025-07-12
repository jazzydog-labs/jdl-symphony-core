# Symphony Demos

Interactive demonstrations of Symphony's features and architecture.

## Running All Demos

Run the complete demo suite:

```bash
just demo
```

This will run all demos in sequence, showing:
1. Configuration system with Pydantic
2. Database connection and Alembic setup
3. API endpoints and health checks

## Individual Demos

You can also run specific demos:

```bash
# Configuration system demo
just demo-config

# Database connection demo
just demo-database

# API endpoints demo (requires server running)
just demo-api
```

## Demo Features

### Configuration Demo (`demo-config`)
- Shows Pydantic settings validation
- Displays current configuration
- Demonstrates environment variable handling
- Shows type safety and validation

### Database Demo (`demo-database`)
- Tests PostgreSQL connection
- Shows async SQLAlchemy setup
- Displays connection pooling details
- Demonstrates Alembic migration commands

### API Demo (`demo-api`)
- Tests health check endpoint
- Shows API information endpoint
- Displays available routes
- Demonstrates error handling

## Requirements

- Python 3.11+
- Dependencies installed (`just install`)
- For database demos: Docker running with PostgreSQL (`just db-up`)
- For API demos: Server running (automatic in `just demo`)

## Notes

- The main demo runner will automatically start the API server if needed
- Demos use rich for enhanced terminal output
- Each demo is self-contained and can be run independently