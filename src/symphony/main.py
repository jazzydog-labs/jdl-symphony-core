"""Symphony API main application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from symphony.config import get_settings
from symphony.infrastructure.database.connection import get_engine

settings = get_settings()
engine = get_engine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting up Symphony API...")
    yield
    # Shutdown
    print("Shutting down Symphony API...")
    await engine.dispose()


app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()

        return {
            "status": "healthy",
            "database": "connected",
            "service": "symphony-api",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "service": "symphony-api",
            "error": str(e),
        }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Symphony API",
        "version": "0.1.0",
        "docs": f"{settings.api_v1_str}/docs",
    }
