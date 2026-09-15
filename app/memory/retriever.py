import re
from datetime import datetime, timezone

from app.memory.base import MemoryItem


class MemoryRetriever:
    """Selects relevant conversation memories using relevance and recency."""

    def retrieve(
        self,
        query: str,
        memories: list[MemoryItem],
        *,
        limit: int = 5,
    ) -> list[MemoryItem]:
        if not query.strip() or not memories or limit <= 0:
            return []

        query_words = self._keywords(query)

        if not query_words:
            return memories[-limit:]

        scored: list[tuple[float, int, MemoryItem]] = []

        now = datetime.now(timezone.utc)

        for index, memory in enumerate(memories):
            memory_words = self._keywords(memory.content)

            overlap = len(query_words & memory_words)

            if overlap == 0:
                continue

            relevance_score = overlap / max(len(query_words), 1)

            age_seconds = max(
                (now - memory.timestamp).total_seconds(),
                0,
            )

            recency_score = 1 / (1 + age_seconds / 3600)

            final_score = (
                relevance_score * 0.8
                + recency_score * 0.2
            )

            scored.append(
                (
                    final_score,
                    index,
                    memory,
                )
            )

        scored.sort(
            key=lambda item: (item[0], item[1]),
            reverse=True,
        )

        return [
            item[2]
            for item in scored[:limit]
        ]

    def _keywords(self, text: str) -> set[str]:
        words = re.findall(
            r"[a-zA-Z0-9_]+",
            text.lower(),
        )

        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "what",
            "why",
            "how",
            "when",
            "where",
            "who",
            "my",
            "your",
            "you",
            "i",
            "me",
            "to",
            "of",
            "in",
            "on",
            "for",
            "and",
            "or",
            "it",
            "this",
            "that",
            "do",
            "does",
            "did",
            "can",
            "could",
            "would",
            "should",
        }

        return {
            word
            for word in words
            if word not in stop_words
            and len(word) > 2
        }