import asyncio
import html
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.research.url_security import URLSecurity


@dataclass
class FetchedWebPage:
    """A fetched and normalized webpage."""

    url: str
    title: str
    text: str
    status_code: int
    content_type: str
    metadata: dict[str, Any]


class _HTMLTextExtractor(HTMLParser):
    """Extract visible text and title from HTML."""

    def __init__(self) -> None:
        super().__init__()

        self.title_parts: list[str] = []
        self.text_parts: list[str] = []

        self._inside_title = False
        self._skip_depth = 0

        self._ignored_tags = {
            "script",
            "style",
            "noscript",
            "svg",
        }

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        tag = tag.lower()

        if tag == "title":
            self._inside_title = True

        if tag in self._ignored_tags:
            self._skip_depth += 1

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        tag = tag.lower()

        if tag == "title":
            self._inside_title = False

        if (
            tag in self._ignored_tags
            and self._skip_depth > 0
        ):
            self._skip_depth -= 1

    def handle_data(
        self,
        data: str,
    ) -> None:
        if self._skip_depth > 0:
            return

        cleaned = " ".join(
            html.unescape(data).split()
        )

        if not cleaned:
            return

        if self._inside_title:
            self.title_parts.append(cleaned)
        else:
            self.text_parts.append(cleaned)

    @property
    def title(self) -> str:
        return " ".join(
            self.title_parts
        ).strip()

    @property
    def text(self) -> str:
        return "\n".join(
            self.text_parts
        ).strip()


class WebSourceFetcher:
    """Fetch webpages with SSRF and response safety controls."""

    ALLOWED_CONTENT_TYPES = {
        "text/html",
        "application/xhtml+xml",
        "text/plain",
    }

    def __init__(
        self,
        *,
        timeout: int = 20,
        max_bytes: int = 2_000_000,
        max_text_characters: int = 500_000,
        url_security: URLSecurity | None = None,
    ) -> None:
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.max_text_characters = (
            max_text_characters
        )

        self.url_security = (
            url_security or URLSecurity()
        )

    async def fetch(
        self,
        url: str,
    ) -> FetchedWebPage:
        url = url.strip()

        if not url:
            raise ValueError(
                "URL cannot be empty."
            )

        self.url_security.validate(
            url
        )

        return await asyncio.to_thread(
            self._fetch_sync,
            url,
        )

    def _fetch_sync(
        self,
        url: str,
    ) -> FetchedWebPage:
        request = Request(
            url,
            headers={
                "User-Agent": (
                    "FrontierAI/1.0 "
                    "(research client)"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "text/plain;q=0.9"
                ),
            },
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                status_code = response.status

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    )
                )

                content_type_main = (
                    content_type.split(
                        ";",
                        1,
                    )[0]
                    .strip()
                    .lower()
                )

                content_length_header = (
                    response.headers.get(
                        "Content-Length"
                    )
                )

                if content_length_header:
                    try:
                        content_length = int(
                            content_length_header
                        )
                    except ValueError:
                        content_length = None

                    if (
                        content_length is not None
                        and content_length
                        > self.max_bytes
                    ):
                        raise ValueError(
                            "Webpage response exceeds the maximum allowed size."
                        )

                if (
                    content_type_main
                    and content_type_main
                    not in self.ALLOWED_CONTENT_TYPES
                ):
                    raise ValueError(
                        "Unsupported webpage content type: "
                        f"{content_type_main}"
                    )

                raw_bytes = response.read(
                    self.max_bytes + 1
                )

                final_url = response.geturl()

        except HTTPError as exc:
            raise ConnectionError(
                f"Webpage returned HTTP {exc.code}."
            ) from exc

        except URLError as exc:
            raise ConnectionError(
                "Failed to fetch webpage."
            ) from exc

        except TimeoutError as exc:
            raise ConnectionError(
                "Webpage fetch timed out."
            ) from exc

        if len(raw_bytes) > self.max_bytes:
            raise ValueError(
                "Webpage response exceeds the maximum allowed size."
            )

        if not raw_bytes:
            raise ValueError(
                "Webpage returned empty content."
            )

        if final_url != url:
            self.url_security.validate(
                final_url
            )

        charset = self._extract_charset(
            content_type
        )

        try:
            raw_text = raw_bytes.decode(
                charset,
                errors="replace",
            )
        except LookupError:
            raw_text = raw_bytes.decode(
                "utf-8",
                errors="replace",
            )

        if (
            "html" in content_type_main
            or "xhtml" in content_type_main
            or "<html" in raw_text[:1000].lower()
        ):
            parser = _HTMLTextExtractor()

            parser.feed(raw_text)

            title = parser.title
            text = parser.text
        else:
            title = ""
            text = raw_text.strip()

        if not text:
            raise ValueError(
                "No readable text was extracted from webpage."
            )

        if len(text) > self.max_text_characters:
            text = text[
                : self.max_text_characters
            ]

        return FetchedWebPage(
            url=final_url,
            title=title or final_url,
            text=text,
            status_code=status_code,
            content_type=content_type,
            metadata={
                "bytes_read": len(raw_bytes),
                "charset": charset,
                "redirected": final_url != url,
                "text_truncated": (
                    len(text)
                    >= self.max_text_characters
                ),
            },
        )

    def _extract_charset(
        self,
        content_type: str,
    ) -> str:
        parts = [
            part.strip()
            for part in content_type.split(";")
        ]

        for part in parts:
            if part.lower().startswith(
                "charset="
            ):
                charset = part.split(
                    "=",
                    1,
                )[1].strip()

                if charset:
                    return charset

        return "utf-8"