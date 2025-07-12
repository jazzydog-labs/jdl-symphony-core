"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from symphony.config import Settings, get_settings


def get_engine(settings: Settings | None = None) -> AsyncEngine:
    """
    Get SQLAlchemy async engine.

    Uses demo database URL if demo_mode is True in settings.
    """
    if settings is None:
        settings = get_settings()

    # Use demo database URL if in demo mode
    database_url = settings.demo_database_url if settings.demo_mode else str(settings.database_url)

    # SQLite doesn't support pool configuration
    if settings.demo_mode:
        return create_async_engine(
            database_url,
            echo=settings.debug,
            future=True,
        )

    # PostgreSQL with full pool configuration
    return create_async_engine(
        database_url,
        echo=settings.debug,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


# Lazy initialization for default engine and session maker
_default_engine: AsyncEngine | None = None
_default_session_maker: async_sessionmaker[AsyncSession] | None = None


def _ensure_defaults() -> None:
    """Ensure default engine and session maker are initialized."""
    global _default_engine, _default_session_maker
    if _default_engine is None:
        _default_engine = get_engine()
        _default_session_maker = async_sessionmaker(
            _default_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )


def get_session_maker(settings: Settings | None = None) -> async_sessionmaker[AsyncSession]:
    """
    Get session maker for creating database sessions.

    If settings provided with demo_mode=True, creates a new session maker
    with demo database. Otherwise returns the default session maker.
    """
    if settings and settings.demo_mode:
        engine = get_engine(settings)
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    _ensure_defaults()
    assert _default_session_maker is not None
    return _default_session_maker


async def get_db(settings: Settings | None = None) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Args:
        settings: Optional settings to override defaults (e.g., for demo mode)
    """
    session_maker = get_session_maker(settings)
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
