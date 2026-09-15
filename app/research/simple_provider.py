import asyncio
import html
import re
import urllib.parse
import urllib.request

from app.research.web_base import (
    WebSearchProvider,
    WebSearchResult,
)


class SimpleWebSearchProvider(WebSearchProvider):
    """Basic DuckDuckGo HTML search provider."""

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

        if not query:
            return []

        if limit <= 0:
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
        url = "https://html.duckduckgo.com/html/"

        form_data = urllib.parse.urlencode(
            {
                "q": query,
                "b": "",
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=form_data,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/153.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://html.duckduckgo.com/",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                raw_html = response.read().decode(
                    "utf-8",
                    errors="replace",
                )

        except Exception as exc:
            raise ConnectionError(
                "DuckDuckGo web search failed."
            ) from exc

        return self._parse_results(
            raw_html,
            limit,
        )

    def _parse_results(
        self,
        raw_html: str,
        limit: int,
    ) -> list[WebSearchResult]:
        results: list[WebSearchResult] = []

        # DuckDuckGo result links.
        matches = re.findall(
            r'<a[^>]*class=["\'][^"\']*result__a[^"\']*["\'][^>]*'
            r'href=["\']([^"\']+)["\'][^>]*>'
            r'(.*?)</a>',
            raw_html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Some responses put href before class.
        if not matches:
            matches = re.findall(
                r'<a[^>]*href=["\']([^"\']+)["\'][^>]*'
                r'class=["\'][^"\']*result__a[^"\']*["\'][^>]*>'
                r'(.*?)</a>',
                raw_html,
                flags=re.IGNORECASE | re.DOTALL,
            )

        snippet_matches = re.findall(
            r'<(?:a|div)[^>]*class=["\'][^"\']*result__snippet[^"\']*["\'][^>]*>'
            r'(.*?)</(?:a|div)>',
            raw_html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        for index, (
            raw_url,
            raw_title,
        ) in enumerate(matches):
            if len(results) >= limit:
                break

            result_url = self._decode_url(
                raw_url
            )

            title = self._clean_text(
                raw_title
            )

            snippet = ""

            if index < len(
                snippet_matches
            ):
                snippet = self._clean_text(
                    snippet_matches[index]
                )

            if not title or not result_url:
                continue

            results.append(
                WebSearchResult(
                    title=title,
                    url=result_url,
                    snippet=snippet,
                    source="duckduckgo",
                )
            )

        return results[:limit]

    def _decode_url(
        self,
        raw_url: str,
    ) -> str:
        value = html.unescape(
            raw_url
        ).strip()

        if value.startswith(
            "//"
        ):
            return (
                "https:"
                + value
            )

        if value.startswith(
            "/l/?"
        ):
            parsed = urllib.parse.urlparse(
                "https://duckduckgo.com"
                + value
            )

            params = urllib.parse.parse_qs(
                parsed.query
            )

            encoded_target = params.get(
                "uddg"
            )

            if encoded_target:
                return urllib.parse.unquote(
                    encoded_target[0]
                )

        return value

    def _clean_text(
        self,
        value: str,
    ) -> str:
        value = re.sub(
            r"<[^>]+>",
            " ",
            value,
        )

        value = html.unescape(
            value
        )

        value = " ".join(
            value.split()
        )

        return value.strip()