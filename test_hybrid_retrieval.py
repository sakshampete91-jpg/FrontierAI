from app.knowledge.base import KnowledgeChunk
from app.knowledge.chunk_store import (
    SQLiteKnowledgeChunkStore,
)
from app.knowledge.embeddings import (
    OllamaEmbeddingService,
)
from app.knowledge.hybrid_retriever import (
    HybridKnowledgeRetriever,
)
from app.knowledge.retriever import (
    KnowledgeRetriever,
)
from app.knowledge.semantic_retriever import (
    SemanticKnowledgeRetriever,
)
from app.knowledge.vector_store import (
    SQLiteVectorStore,
)


def main():
    keyword_database = (
        "data/test_hybrid_keyword.db"
    )

    vector_database = (
        "data/test_hybrid_vector.db"
    )

    keyword_store = (
        SQLiteKnowledgeChunkStore(
            keyword_database
        )
    )

    vector_store = SQLiteVectorStore(
        vector_database
    )

    keyword_store.clear()
    vector_store.clear()

    chunks = [
        KnowledgeChunk(
            chunk_id="hybrid-1",
            document_id="hybrid-doc",
            content=(
                "FrontierAI uses a Model Router to "
                "select an appropriate model for each task."
            ),
            metadata={
                "topic": "routing",
            },
        ),
        KnowledgeChunk(
            chunk_id="hybrid-2",
            document_id="hybrid-doc",
            content=(
                "FrontierAI stores useful conversation "
                "history using persistent memory."
            ),
            metadata={
                "topic": "memory",
            },
        ),
        KnowledgeChunk(
            chunk_id="hybrid-3",
            document_id="hybrid-doc",
            content=(
                "FrontierAI verifies calculator results "
                "before marking a calculation verified."
            ),
            metadata={
                "topic": "verification",
            },
        ),
    ]

    keyword_store.add_chunks(
        chunks
    )

    embedding_service = (
        OllamaEmbeddingService()
    )

    embedded_items = []

    print("Creating embeddings...")

    for chunk in chunks:
        embedding = embedding_service.embed(
            chunk.content
        )

        embedded_items.append(
            (
                chunk,
                embedding,
            )
        )

    vector_store.add_embeddings(
        embedded_items
    )

    keyword_retriever = KnowledgeRetriever(
        keyword_store
    )

    semantic_retriever = (
        SemanticKnowledgeRetriever(
            vector_store,
            embedding_service,
        )
    )

    hybrid_retriever = (
        HybridKnowledgeRetriever(
            keyword_retriever,
            semantic_retriever,
        )
    )

    query = (
        "How does FrontierAI decide which AI model "
        "should handle a task?"
    )

    print("\nSearching:")
    print(query)

    results = hybrid_retriever.search(
        query,
        limit=3,
    )

    print(
        "\nHybrid results:",
        len(results),
    )

    for result in results:
        print(
            "\nCombined score:",
            round(
                result.score,
                4,
            ),
        )

        print(
            "Keyword score:",
            round(
                result.keyword_score,
                4,
            ),
        )

        print(
            "Semantic score:",
            round(
                result.semantic_score,
                4,
            ),
        )

        print(
            "Content:",
            result.chunk.content,
        )

    if (
        results
        and "model router"
        in results[0].chunk.content.lower()
    ):
        print(
            "\nHybrid retrieval: OK"
        )
    else:
        print(
            "\nHybrid retrieval: FAILED"
        )


if __name__ == "__main__":
    main()