# JDL Symphony Core

Local work organization system backend - the orchestral core that harmonizes your development workflow

## Project Status

✅ **Completed:**
- Project structure and dependencies setup
- Database configuration (Pydantic settings)
- SQLAlchemy async engine setup
- Alembic migrations initialized
- FastAPI application with health check endpoint

🚧 **In Progress:**
- Domain models implementation
- Repository pattern implementation
- API routes and schemas

## Quick Start

```bash
# Install dependencies
just install

# Start database (requires Docker)
just db-up

# Run migrations
just db-migrate

# Start development server
just run
```

### Alternative without Docker

If Docker is not available, you can run the API without the database:

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn symphony.main:app --reload --host 0.0.0.0 --port 8000
```

## Development

```bash
# Run linting
just lint

# Run type checking
just typecheck

# Run tests
just test
```

## API Endpoints

- **Health Check**: `GET /health` - Returns API and database status
- **Root**: `GET /` - Returns API information
- **API Documentation**: 
  - Interactive docs: http://localhost:8000/api/v1/docs (when implemented)
  - OpenAPI spec: http://localhost:8000/api/v1/openapi.json

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=symphony
POSTGRES_PASSWORD=symphony
POSTGRES_DB=symphony_dev

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# API
API_DEBUG=true
```

## Architecture

The project follows clean architecture principles with:
- **Domain Layer**: Pure Python business logic
- **Application Layer**: Use cases and DTOs
- **Infrastructure Layer**: Database, external services
- **API Layer**: FastAPI routes and schemas

Two-level aggregate design:
- **UserProfile**: Global aggregate for user management
- **Workspace**: Independent contexts for work organization