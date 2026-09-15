from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WebSearchResult:
    """A single result returned by a web search provider."""

    title: str
    url: str
    snippet: str = ""
    source: str = "unknown"
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class WebSearchProvider(ABC):
    """Base interface for web search providers."""

    @abstractmethod
    async def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[WebSearchResult]:
        """Search the web for relevant results."""
        raise NotImplementedError