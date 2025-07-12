"""Base query and query handler interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from symphony.domain.unit_of_work import UnitOfWork

TQuery = TypeVar("TQuery")
TResult = TypeVar("TResult")


class Query(ABC):
    """Base query interface for CQRS read operations."""
    pass


class QueryHandler(ABC, Generic[TQuery, TResult]):
    """Base query handler interface."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize handler with unit of work."""
        self._uow = uow

    @abstractmethod
    async def handle(self, query: TQuery) -> TResult:
        """Handle the query and return result."""
        pass


class QueryBus:
    """Query bus for dispatching queries to handlers."""

    def __init__(self) -> None:
        """Initialize query bus."""
        self._handlers: dict[type[Any], QueryHandler[Any, Any]] = {}

    def register(
        self,
        query_type: type[Any],
        handler: QueryHandler[Any, Any]
    ) -> None:
        """Register a query handler."""
        self._handlers[query_type] = handler

    async def execute(self, query: Any) -> Any:
        """Execute a query through its handler."""
        query_type = type(query)
        if query_type not in self._handlers:
            raise ValueError(f"No handler registered for query {query_type.__name__}")

        handler = self._handlers[query_type]
        return await handler.handle(query)
