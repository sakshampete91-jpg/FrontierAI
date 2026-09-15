from dataclasses import dataclass

from app.knowledge.base import KnowledgeChunk
from app.knowledge.retriever import (
    KnowledgeRetriever,
)
from app.knowledge.semantic_retriever import (
    SemanticKnowledgeRetriever,
)


@dataclass
class HybridSearchResult:
    """A knowledge chunk ranked using combined retrieval signals."""

    chunk: KnowledgeChunk
    score: float
    keyword_score: float
    semantic_score: float


class HybridKnowledgeRetriever:
    """Combines keyword and semantic retrieval."""

    def __init__(
        self,
        keyword_retriever: KnowledgeRetriever,
        semantic_retriever: SemanticKnowledgeRetriever,
        *,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7,
    ) -> None:
        if keyword_weight < 0:
            raise ValueError(
                "keyword_weight cannot be negative."
            )

        if semantic_weight < 0:
            raise ValueError(
                "semantic_weight cannot be negative."
            )

        if (
            keyword_weight
            + semantic_weight
            <= 0
        ):
            raise ValueError(
                "At least one retrieval weight must be positive."
            )

        self.keyword_retriever = (
            keyword_retriever
        )

        self.semantic_retriever = (
            semantic_retriever
        )

        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[HybridSearchResult]:
        if not query.strip():
            return []

        if limit <= 0:
            return []

        keyword_results = (
            self.keyword_retriever.search(
                query,
                limit=max(limit * 3, 10),
            )
        )

        semantic_results = (
            self.semantic_retriever.search(
                query,
                limit=max(limit * 3, 10),
            )
        )

        keyword_scores = {
            result.chunk.chunk_id: result.score
            for result in keyword_results
        }

        semantic_scores = {
            result.chunk.chunk_id: result.score
            for result in semantic_results
        }

        chunks: dict[
            str,
            KnowledgeChunk,
        ] = {}

        for result in keyword_results:
            chunks[result.chunk.chunk_id] = (
                result.chunk
            )

        for result in semantic_results:
            chunks[result.chunk.chunk_id] = (
                result.chunk
            )

        combined: list[
            HybridSearchResult
        ] = []

        for chunk_id, chunk in chunks.items():
            keyword_score = (
                keyword_scores.get(
                    chunk_id,
                    0.0,
                )
            )

            semantic_score = (
                semantic_scores.get(
                    chunk_id,
                    0.0,
                )
            )

            score = (
                self.keyword_weight
                * keyword_score
                + self.semantic_weight
                * semantic_score
            )

            combined.append(
                HybridSearchResult(
                    chunk=chunk,
                    score=score,
                    keyword_score=keyword_score,
                    semantic_score=semantic_score,
                )
            )

        combined.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return combined[:limit]