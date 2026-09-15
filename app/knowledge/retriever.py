import re
from dataclasses import dataclass

from app.knowledge.base import KnowledgeChunk
from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore


@dataclass
class KnowledgeSearchResult:
    """A knowledge chunk matched against a search query."""

    chunk: KnowledgeChunk
    score: float


class KnowledgeRetriever:
    """Retrieves relevant knowledge chunks using keyword overlap."""

    def __init__(
        self,
        chunk_store: SQLiteKnowledgeChunkStore,
    ) -> None:
        self.chunk_store = chunk_store

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[KnowledgeSearchResult]:
        if not query.strip() or limit <= 0:
            return []

        query_words = self._keywords(query)

        if not query_words:
            return []

        chunks = self._all_chunks()

        scored: list[
            tuple[float, int, KnowledgeChunk]
        ] = []

        for index, chunk in enumerate(chunks):
            chunk_words = self._keywords(
                chunk.content
            )

            overlap = len(
                query_words & chunk_words
            )

            if overlap == 0:
                continue

            score = overlap / max(
                len(query_words),
                1,
            )

            scored.append(
                (
                    score,
                    index,
                    chunk,
                )
            )

        scored.sort(
            key=lambda item: (
                item[0],
                item[1],
            ),
            reverse=True,
        )

        return [
            KnowledgeSearchResult(
                chunk=item[2],
                score=item[0],
            )
            for item in scored[:limit]
        ]

    def _all_chunks(
        self,
    ) -> list[KnowledgeChunk]:
        with self.chunk_store._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    content,
                    metadata
                FROM knowledge_chunks
                ORDER BY chunk_id ASC
                """
            ).fetchall()

        import json

        return [
            KnowledgeChunk(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                content=row["content"],
                metadata=json.loads(
                    row["metadata"]
                ),
            )
            for row in rows
        ]

    def _keywords(
        self,
        text: str,
    ) -> set[str]:
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
            "does",
            "do",
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