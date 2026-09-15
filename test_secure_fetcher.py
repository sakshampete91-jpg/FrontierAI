import asyncio
import traceback

from app.research.fetcher import WebSourceFetcher


async def main():
    fetcher = WebSourceFetcher(
        timeout=15,
        max_bytes=1_000_000,
    )

    print("Testing allowed URL...")

    try:
        page = await fetcher.fetch(
            "https://www.python.org/"
        )

        print("Status:", page.status_code)
        print("Title:", page.title)
        print("Characters:", len(page.text))

    except Exception as exc:
        print("\nREAL ERROR:")
        print(type(exc).__name__)
        print(str(exc))

        print("\nFULL TRACEBACK:")
        traceback.print_exc()

    print("\nTesting blocked URL...")

    try:
        await fetcher.fetch(
            "http://127.0.0.1:11434/"
        )

        print(
            "SECURITY FAILURE: blocked URL was allowed."
        )

    except ValueError as exc:
        print(
            "Blocked correctly:",
            exc,
        )


if __name__ == "__main__":
    asyncio.run(main())