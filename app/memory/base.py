from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class MemoryItem:
    """A single piece of conversation memory."""

    role: str
    content: str
    timestamp: datetime
    metadata: dict[str, Any]
    conversation_id: str = "default"


class MemoryStore(ABC):
    """Base interface for FrontierAI memory implementations."""

    @abstractmethod
    def add(
        self,
        role: str,
        content: str,
        *,
        conversation_id: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> MemoryItem:
        """Store a new memory item."""
        raise NotImplementedError

    @abstractmethod
    def get_recent(
        self,
        limit: int = 10,
        *,
        conversation_id: str = "default",
    ) -> list[MemoryItem]:
        """Return recent memories for one conversation."""
        raise NotImplementedError

    @abstractmethod
    def clear(
        self,
        *,
        conversation_id: str | None = None,
    ) -> None:
        """Clear one conversation or all memory."""
        raise NotImplementedError