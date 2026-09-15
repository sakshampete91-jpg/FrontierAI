import asyncio
import json
import urllib.parse
import urllib.request

from app.research.web_base import (
    WebSearchProvider,
    WebSearchResult,
)


class FreeSearchProvider(WebSearchProvider):
    """
    Free, no-API-key search provider.

    Uses Wikipedia search plus curated authoritative
    sources for common technical topics.
    """

    def __init__(
        self,
        *,
        timeout: int = 15,
    ) -> None:
        self.timeout = timeout

    async def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[WebSearchResult]:
        query = query.strip()

        if not query or limit <= 0:
            return []

        return await asyncio.to_thread(
            self._search_sync,
            query,
            limit,
        )

    def _search_sync(
        self,
        query: str,
        limit: int,
    ) -> list[WebSearchResult]:
        results: list[WebSearchResult] = []

        # Add authoritative sources first for Python queries.
        if self._is_python_query(query):
            results.extend(
                self._python_sources(query)
            )

        # Fill remaining slots with Wikipedia search.
        remaining = max(
            limit - len(results),
            0,
        )

        if remaining > 0:
            results.extend(
                self._wikipedia_search(
                    query,
                    remaining,
                )
            )

        # Deduplicate by URL.
        unique: list[WebSearchResult] = []
        seen: set[str] = set()

        for result in results:
            if result.url in seen:
                continue

            seen.add(result.url)
            unique.append(result)

            if len(unique) >= limit:
                break

        return unique

    def _is_python_query(
        self,
        query: str,
    ) -> bool:
        text = query.lower()

        return (
            "python" in text
            and (
                "programming" in text
                or "language" in text
                or "python" in text
            )
        )

    def _python_sources(
        self,
        query: str,
    ) -> list[WebSearchResult]:
        return [
            WebSearchResult(
                title="Python Official Documentation",
                url="https://docs.python.org/3/",
                snippet=(
                    "Official documentation for the Python "
                    "programming language, including tutorials, "
                    "library reference, and language reference."
                ),
                source="python.org",
            ),
            WebSearchResult(
                title="Python.org",
                url="https://www.python.org/",
                snippet=(
                    "Official Python website with information "
                    "about the language, downloads, documentation, "
                    "community, and projects."
                ),
                source="python.org",
            ),
            WebSearchResult(
                title="Python Language Reference",
                url="https://docs.python.org/3/reference/",
                snippet=(
                    "Official Python language reference covering "
                    "syntax and core language behavior."
                ),
                source="python.org",
            ),
        ]

    def _wikipedia_search(
        self,
        query: str,
        limit: int,
    ) -> list[WebSearchResult]:
        params = urllib.parse.urlencode(
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "format": "json",
            }
        )

        url = (
            "https://en.wikipedia.org/w/api.php?"
            + params
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "FrontierAI/1.0 "
                    "(local research assistant)"
                ),
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                data = json.loads(
                    response.read().decode(
                        "utf-8",
                        errors="replace",
                    )
                )

        except Exception:
            return []

        results: list[WebSearchResult] = []

        items = (
            data.get(
                "query",
                {},
            ).get(
                "search",
                [],
            )
        )

        for item in items:
            title = item.get(
                "title",
                "",
            ).strip()

            page_id = item.get(
                "pageid"
            )

            if not title or not page_id:
                continue

            page_url = (
                "https://en.wikipedia.org/wiki/"
                + urllib.parse.quote(
                    title.replace(
                        " ",
                        "_",
                    )
                )
            )

            snippet = (
                item.get(
                    "snippet",
                    "",
                )
                .replace(
                    '<span class="searchmatch">',
                    "",
                )
                .replace(
                    "</span>",
                    "",
                )
            )

            results.append(
                WebSearchResult(
                    title=title,
                    url=page_url,
                    snippet=snippet,
                    source="wikipedia",
                    metadata={
                        "page_id": page_id,
                    },
                )
            )

        return results[:limit]