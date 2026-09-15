import asyncio

from app.research.free_provider import (
    FreeSearchProvider,
)


async def main():
    provider = FreeSearchProvider()

    print("Searching Wikipedia...")

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
        print("\nFree search: OK")
    else:
        print("\nFree search returned no results.")


if __name__ == "__main__":
    asyncio.run(main())