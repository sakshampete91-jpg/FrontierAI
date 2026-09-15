import asyncio

from app.research.citations import CitationBuilder
from app.research.fetcher import WebSourceFetcher
from app.research.pipeline import ResearchPipeline
from app.research.service import ResearchSearchService
from app.research.simple_provider import (
    SimpleWebSearchProvider,
)


async def main():
    provider = SimpleWebSearchProvider(
        timeout=15
    )

    search_service = ResearchSearchService(
        provider
    )

    fetcher = WebSourceFetcher(
        timeout=15,
        max_bytes=1_000_000,
    )

    pipeline = ResearchPipeline(
        search_service=search_service,
        fetcher=fetcher,
        citation_builder=CitationBuilder(),
    )

    print("Starting research pipeline...")

    result = await pipeline.research(
        "Python programming language",
        search_limit=5,
        fetch_limit=2,
    )

    print(
        "\nQuery:",
        result["query"],
    )

    print(
        "Search provider:",
        result["search_provider"],
    )

    print(
        "Search results:",
        len(result["search_results"]),
    )

    print(
        "Sources processed:",
        len(result["sources"]),
    )

    for source in result["sources"]:
        print("\nTitle:")
        print(source.title)

        print("URL:")
        print(source.url)

        print(
            "Extracted characters:",
            len(source.extracted_text),
        )

    print("\nCitations:")
    print(
        result["citation_text"]
    )

    if (
        result["search_results"]
        and result["sources"]
        and result["citations"]
    ):
        print(
            "\nResearch pipeline: OK"
        )
    else:
        print(
            "\nResearch pipeline: FAILED"
        )


if __name__ == "__main__":
    asyncio.run(main())