from uuid import uuid4

from app.research.citations import CitationBuilder
from app.research.fetcher import (
    FetchedWebPage,
    WebSourceFetcher,
)
from app.research.service import (
    ResearchSearchService,
)
from app.research.sources import (
    ResearchSource,
)


class ResearchPipeline:
    """Coordinates search, source fetching, and citation creation."""

    def __init__(
        self,
        search_service: ResearchSearchService,
        fetcher: WebSourceFetcher,
        citation_builder: CitationBuilder | None = None,
    ) -> None:
        self.search_service = search_service
        self.fetcher = fetcher
        self.citation_builder = (
            citation_builder
            or CitationBuilder()
        )

    async def research(
        self,
        query: str,
        *,
        search_limit: int = 5,
        fetch_limit: int = 3,
    ) -> dict:
        query = query.strip()

        if not query:
            raise ValueError(
                "Research query cannot be empty."
            )

        if search_limit <= 0:
            raise ValueError(
                "search_limit must be greater than zero."
            )

        if fetch_limit <= 0:
            raise ValueError(
                "fetch_limit must be greater than zero."
            )

        search_response = (
            await self.search_service.search(
                query,
                limit=search_limit,
            )
        )

        sources: list[ResearchSource] = []

        for result in search_response.results[
            :fetch_limit
        ]:
            extracted_text = ""

            try:
                page = await self.fetcher.fetch(
                    result.url
                )

                extracted_text = page.text

            except Exception as exc:
                extracted_text = (
                    f"Source could not be fetched: "
                    f"{exc}"
                )

            source = ResearchSource(
                source_id=str(
                    uuid4()
                ),
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                extracted_text=extracted_text,
                source_type="web",
                metadata={
                    "search_provider": result.source,
                    "fetch_success": bool(
                        extracted_text
                        and not extracted_text.startswith(
                            "Source could not be fetched:"
                        )
                    ),
                },
            )

            sources.append(source)

        citations = (
            self.citation_builder.build(
                sources
            )
        )

        return {
            "query": query,
            "search_provider": (
                search_response.provider
            ),
            "search_results": (
                search_response.results
            ),
            "sources": sources,
            "citations": citations,
            "citation_text": (
                self.citation_builder.format_markdown(
                    citations
                )
            ),
        }