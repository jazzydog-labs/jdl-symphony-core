"""Base SQLAlchemy repository implementation."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from symphony.domain.repositories.base import Repository

# Type variables
TEntity = TypeVar("TEntity")  # Domain entity type
TModel = TypeVar("TModel")  # Database model type


class SQLAlchemyRepository(Repository[TEntity], Generic[TEntity, TModel]):
    """
    Base SQLAlchemy repository implementation.

    Provides common CRUD operations for all repositories.
    Subclasses must implement the conversion methods between
    domain entities and database models.
    """

    def __init__(self, session: AsyncSession, model_class: type[TModel]):
        """
        Initialize the repository.

        Args:
            session: The database session
            model_class: The SQLAlchemy model class
        """
        self.session = session
        self.model_class = model_class

    async def get(self, id: UUID) -> TEntity | None:
        """Retrieve an entity by its ID."""
        result = await self.session.get(self.model_class, id)
        if result is None:
            return None
        return self._to_entity(result)

    async def save(self, entity: TEntity) -> TEntity:
        """Save an entity (create or update)."""
        model = self._to_model(entity)

        # Check if this is an update or create
        existing = await self.session.get(self.model_class, model.id)  # type: ignore
        if existing:
            # Update existing record
            for key, value in model.__dict__.items():
                if not key.startswith("_"):
                    setattr(existing, key, value)
            await self.session.flush()
            return self._to_entity(existing)
        else:
            # Create new record
            self.session.add(model)
            await self.session.flush()
            return self._to_entity(model)

    async def delete(self, id: UUID) -> None:
        """Delete an entity by its ID."""
        result = await self.session.get(self.model_class, id)
        if result:
            await self.session.delete(result)
            await self.session.flush()

    async def exists(self, id: UUID) -> bool:
        """Check if an entity exists."""
        stmt = select(self.model_class).where(self.model_class.id == id)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    # Abstract methods that subclasses must implement
    def _to_entity(self, model: TModel) -> TEntity:
        """Convert database model to domain entity."""
        raise NotImplementedError

    def _to_model(self, entity: TEntity) -> TModel:
        """Convert domain entity to database model."""
        raise NotImplementedError
