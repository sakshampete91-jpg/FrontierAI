import asyncio

from app.research.fetcher import WebSourceFetcher


async def main():
    fetcher = WebSourceFetcher(
        timeout=15,
        max_bytes=1_000_000,
    )

    url = "https://www.python.org/"

    print("Fetching:")
    print(url)

    page = await fetcher.fetch(
        url
    )

    print("\nStatus code:")
    print(page.status_code)

    print("\nContent type:")
    print(page.content_type)

    print("\nTitle:")
    print(page.title)

    print("\nExtracted characters:")
    print(len(page.text))

    print("\nFirst 500 characters:")
    print(page.text[:500])

    if (
        page.status_code == 200
        and len(page.text) > 0
    ):
        print(
            "\nWeb source fetching: OK"
        )
    else:
        print(
            "\nWeb source fetching: FAILED"
        )


if __name__ == "__main__":
    asyncio.run(main())