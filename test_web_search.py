import asyncio

from app.research.simple_provider import (
    SimpleWebSearchProvider,
)


async def main():
    provider = SimpleWebSearchProvider()

    print("Searching the web...")

    results = await provider.search(
        "Python programming language",
        limit=5,
    )

    print(
        "Results:",
        len(results),
    )

    for result in results:
        print("\nTitle:", result.title)
        print("URL:", result.url)
        print("Snippet:", result.snippet)
        print("Source:", result.source)

    if results:
        print("\nWeb search: OK")
    else:
        print("\nWeb search returned no results.")


if __name__ == "__main__":
    asyncio.run(main())