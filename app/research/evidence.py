import re
from dataclasses import dataclass


@dataclass
class EvidenceBlock:
    """A relevant piece of text extracted from a source."""

    text: str
    score: float


class EvidenceSelector:
    """Selects query-relevant passages from retrieved web content."""

    def __init__(
        self,
        *,
        max_blocks: int = 6,
        max_chars: int = 6000,
        min_block_chars: int = 80,
    ) -> None:
        self.max_blocks = max_blocks
        self.max_chars = max_chars
        self.min_block_chars = min_block_chars

    def select(
        self,
        query: str,
        text: str,
    ) -> str:
        query_terms = self._terms(query)

        if not text.strip():
            return ""

        paragraphs = self._split_paragraphs(
            text
        )

        scored: list[EvidenceBlock] = []

        for paragraph in paragraphs:
            score = self._score(
                paragraph,
                query_terms,
            )

            if score > 0:
                scored.append(
                    EvidenceBlock(
                        text=paragraph,
                        score=score,
                    )
                )

        scored.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        selected: list[str] = []
        total_chars = 0

        for block in scored:
            if len(selected) >= self.max_blocks:
                break

            remaining = (
                self.max_chars
                - total_chars
            )

            if remaining <= 0:
                break

            text_block = block.text

            if len(text_block) > remaining:
                text_block = text_block[
                    :remaining
                ]

            if (
                len(text_block)
                < self.min_block_chars
            ):
                continue

            selected.append(
                text_block
            )

            total_chars += len(
                text_block
            )

        if not selected:
            return text[: self.max_chars]

        return "\n\n".join(
            selected
        )

    def _terms(
        self,
        query: str,
    ) -> set[str]:
        words = re.findall(
            r"[a-zA-Z0-9]{3,}",
            query.lower(),
        )

        stop_words = {
            "the",
            "and",
            "using",
            "with",
            "from",
            "that",
            "this",
            "what",
            "about",
            "provide",
            "please",
            "research",
            "sources",
            "source",
            "information",
        }

        return {
            word
            for word in words
            if word not in stop_words
        }

    def _split_paragraphs(
        self,
        text: str,
    ) -> list[str]:
        raw_parts = re.split(
            r"\n\s*\n|(?<=[.!?])\s{2,}",
            text,
        )

        paragraphs = []

        for part in raw_parts:
            cleaned = " ".join(
                part.split()
            )

            if (
                len(cleaned)
                >= self.min_block_chars
            ):
                paragraphs.append(
                    cleaned
                )

        return paragraphs

    def _score(
        self,
        paragraph: str,
        query_terms: set[str],
    ) -> float:
        paragraph_terms = set(
            re.findall(
                r"[a-zA-Z0-9]{3,}",
                paragraph.lower(),
            )
        )

        if not query_terms:
            return 0.0

        overlap = (
            query_terms
            & paragraph_terms
        )

        return (
            len(overlap)
            / len(query_terms)
        )