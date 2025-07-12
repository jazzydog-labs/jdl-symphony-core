# Development commands

# Install dependencies
install:
    uv sync

# Run linting
lint:
    hatch run lint:all

# Run type checking
typecheck:
    hatch run typecheck:check

# Run tests with coverage
test:
    hatch run test:cov

# Run development server
run:
    hatch run dev:server

# Start database
db-up:
    docker-compose up -d postgres

# Stop database
db-down:
    docker-compose down

# Run database migrations
db-migrate:
    hatch run alembic upgrade head

# Generate new migration
db-revision name:
    hatch run alembic revision --autogenerate -m "{{name}}"

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