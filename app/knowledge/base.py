from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class KnowledgeDocument:
    """A document stored in FrontierAI's knowledge system."""

    document_id: str
    title: str
    content: str
    source: str = "unknown"
    metadata: dict[str, Any] = field(
        default_factory=dict
    )
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class KnowledgeChunk:
    """A searchable chunk extracted from a knowledge document."""

    chunk_id: str
    document_id: str
    content: str
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class KnowledgeStore(ABC):
    """Base interface for FrontierAI knowledge storage."""

    @abstractmethod
    def add_document(
        self,
        document: KnowledgeDocument,
    ) -> None:
        """Store a knowledge document."""
        raise NotImplementedError

    @abstractmethod
    def get_document(
        self,
        document_id: str,
    ) -> KnowledgeDocument:
        """Retrieve a document by ID."""
        raise NotImplementedError

    @abstractmethod
    def list_documents(
        self,
    ) -> list[KnowledgeDocument]:
        """List stored documents."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored knowledge."""
        raise NotImplementedError