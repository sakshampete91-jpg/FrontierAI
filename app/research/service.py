from dataclasses import dataclass, field
from typing import Any

from app.research.web_base import (
    WebSearchProvider,
    WebSearchResult,
)


@dataclass
class ResearchSearchResponse:
    """Normalized response from the research search layer."""

    query: str
    results: list[WebSearchResult] = field(
        default_factory=list
    )
    provider: str = "unknown"
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class ResearchSearchService:
    """Provides a stable search interface for FrontierAI research."""

    def __init__(
        self,
        provider: WebSearchProvider,
    ) -> None:
        self.provider = provider

    async def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> ResearchSearchResponse:
        query = query.strip()

        if not query:
            raise ValueError(
                "Research query cannot be empty."
            )

        if limit <= 0:
            raise ValueError(
                "Search limit must be greater than zero."
            )

        results = await self.provider.search(
            query,
            limit=limit,
        )

        provider_name = (
            results[0].source
            if results
            else self.provider.__class__.__name__
        )

        return ResearchSearchResponse(
            query=query,
            results=results,
            provider=provider_name,
            metadata={
                "result_count": len(results),
            },
        )