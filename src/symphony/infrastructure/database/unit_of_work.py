"""SQLAlchemy Unit of Work implementation."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from symphony.config import Settings
from symphony.domain.unit_of_work import UnitOfWork
from symphony.infrastructure.database.connection import get_session_maker
from symphony.infrastructure.database.repositories.repo import SQLAlchemyRepoRepository
from symphony.infrastructure.database.repositories.user_profile import (
    SQLAlchemyUserProfileRepository,
)
from symphony.infrastructure.database.repositories.vault import SQLAlchemyVaultRepository
from symphony.infrastructure.database.repositories.workspace import (
    SQLAlchemyWorkspaceRepository,
)


class SQLAlchemyUnitOfWork(UnitOfWork):
    """
    SQLAlchemy implementation of Unit of Work pattern.

    Manages database sessions and transactions, providing access
    to all repositories within a single transaction context.
    """

    def __init__(self, settings: Settings | None = None):
        """
        Initialize the unit of work.

        Args:
            settings: Optional settings to override defaults (e.g., for demo mode)
        """
        self.session_factory = get_session_maker(settings)
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        """Enter the unit of work context."""
        self._session = self.session_factory()
        await self._session.__aenter__()

        # Initialize repositories
        self.user_profiles = SQLAlchemyUserProfileRepository(self._session)
        self.workspaces = SQLAlchemyWorkspaceRepository(self._session)
        self.repos = SQLAlchemyRepoRepository(self._session)
        self.vaults = SQLAlchemyVaultRepository(self._session)

        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the unit of work context."""
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)
            self._session = None

    async def commit(self) -> None:
        """Commit the transaction."""
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the transaction."""
        if self._session:
            await self._session.rollback()
