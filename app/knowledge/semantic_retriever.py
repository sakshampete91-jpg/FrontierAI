from dataclasses import dataclass

from app.knowledge.base import KnowledgeChunk
from app.knowledge.embeddings import OllamaEmbeddingService
from app.knowledge.vector_store import (
    SQLiteVectorStore,
    cosine_similarity,
)


@dataclass
class SemanticSearchResult:
    """A knowledge chunk ranked by semantic similarity."""

    chunk: KnowledgeChunk
    score: float


class SemanticKnowledgeRetriever:
    """Retrieves knowledge using embedding similarity."""

    def __init__(
        self,
        vector_store: SQLiteVectorStore,
        embedding_service: OllamaEmbeddingService,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        min_score: float = 0.0,
    ) -> list[SemanticSearchResult]:
        if not query.strip():
            return []

        if limit <= 0:
            return []

        query_embedding = (
            self.embedding_service.embed(query)
        )

        stored_items = (
            self.vector_store.list_embeddings()
        )

        scored: list[
            tuple[float, KnowledgeChunk]
        ] = []

        for chunk, embedding in stored_items:
            score = cosine_similarity(
                query_embedding,
                embedding,
            )

            if score >= min_score:
                scored.append(
                    (
                        score,
                        chunk,
                    )
                )

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            SemanticSearchResult(
                chunk=chunk,
                score=score,
            )
            for score, chunk in scored[:limit]
        ]