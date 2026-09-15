import asyncio

from app.research.service import ResearchSearchService
from app.research.simple_provider import (
    SimpleWebSearchProvider,
)


async def main():
    provider = SimpleWebSearchProvider()

    service = ResearchSearchService(
        provider
    )

    print("Running research search...")

    response = await service.search(
        "Python programming language",
        limit=5,
    )

    print(
        "\nQuery:",
        response.query,
    )

    print(
        "Provider:",
        response.provider,
    )

    print(
        "Results:",
        len(response.results),
    )

    for result in response.results:
        print("\nTitle:", result.title)
        print("URL:", result.url)
        print("Source:", result.source)

    if response.results:
        print(
            "\nResearch search service: OK"
        )
    else:
        print(
            "\nResearch search service returned no results."
        )


if __name__ == "__main__":
    asyncio.run(main())