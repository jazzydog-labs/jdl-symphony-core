# Development commands

# List available commands
default:
    @just --list

# Install dependencies
install:
    uv sync

# Run linting
lint:
    uv run ruff check src tests
    uv run ruff format --check src tests

# Run type checking
typecheck:
    uv run pyright src

# Run tests with coverage
test:
    uv run pytest tests/ -v --cov=symphony --cov-report=term-missing

# Run development server
run:
    uv run uvicorn symphony.main:app --reload --host 0.0.0.0 --port 8000

# Start database
db-up:
    docker-compose up -d postgres

# Stop database
db-down:
    docker-compose down

# Run database migrations
db-migrate:
    uv run alembic upgrade head

# Generate new migration
db-revision name:
    uv run alembic revision --autogenerate -m "{{name}}"

# Build docker image
build:
    docker buildx build --platform linux/amd64,linux/arm64 -t jdl-symphony-core:latest .

# Build debug docker image
build-debug:
    docker buildx build --build-arg DEBUG_IMAGE=true -t jdl-symphony-core:debug .

# Demo commands
demo:
    uv run python demos/run_all_demos.py

demo-config:
    uv run python demos/demo_config.py

demo-database:
    uv run python demos/demo_database.py

demo-api:
    uv run python demos/demo_api.py

demo-domain-models:
    uv run python demos/demo_domain_models.py

demo-database-models:
    uv run python demos/demo_database_models.py

demo-repositories:
    uv run python demos/demo_repositories.py

demo-domain-services:
    uv run python demos/demo_domain_services.py

demo-application-layer:
    uv run python demos/demo_application_layer.py