"""Base command and command handler interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from symphony.domain.unit_of_work import UnitOfWork

TCommand = TypeVar("TCommand")
TResult = TypeVar("TResult")


class Command(ABC):
    """Base command interface for CQRS write operations."""
    pass


class CommandHandler(ABC, Generic[TCommand, TResult]):
    """Base command handler interface."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize handler with unit of work."""
        self._uow = uow

    @abstractmethod
    async def handle(self, command: TCommand) -> TResult:
        """Handle the command and return result."""
        pass


class CommandBus:
    """Command bus for dispatching commands to handlers."""

    def __init__(self) -> None:
        """Initialize command bus."""
        self._handlers: dict[type[Any], CommandHandler[Any, Any]] = {}

    def register(
        self,
        command_type: type[Any],
        handler: CommandHandler[Any, Any]
    ) -> None:
        """Register a command handler."""
        self._handlers[command_type] = handler

    async def execute(self, command: Any) -> Any:
        """Execute a command through its handler."""
        command_type = type(command)
        if command_type not in self._handlers:
            raise ValueError(f"No handler registered for command {command_type.__name__}")

        handler = self._handlers[command_type]
        return await handler.handle(command)
