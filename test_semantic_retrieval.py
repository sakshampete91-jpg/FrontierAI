from app.knowledge.base import KnowledgeChunk
from app.knowledge.embeddings import OllamaEmbeddingService
from app.knowledge.semantic_retriever import (
    SemanticKnowledgeRetriever,
)
from app.knowledge.vector_store import SQLiteVectorStore


def main():
    database_path = "data/test_semantic.db"

    vector_store = SQLiteVectorStore(
        database_path
    )

    vector_store.clear()

    embedding_service = OllamaEmbeddingService()

    chunks = [
        KnowledgeChunk(
            chunk_id="semantic-1",
            document_id="semantic-doc",
            content=(
                "FrontierAI uses a Model Router to "
                "choose an appropriate model for a task."
            ),
            metadata={
                "topic": "routing",
            },
        ),
        KnowledgeChunk(
            chunk_id="semantic-2",
            document_id="semantic-doc",
            content=(
                "FrontierAI stores conversation history "
                "using persistent memory."
            ),
            metadata={
                "topic": "memory",
            },
        ),
        KnowledgeChunk(
            chunk_id="semantic-3",
            document_id="semantic-doc",
            content=(
                "FrontierAI independently verifies "
                "important calculator results."
            ),
            metadata={
                "topic": "verification",
            },
        ),
    ]

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

    retriever = SemanticKnowledgeRetriever(
        vector_store,
        embedding_service,
    )

    print("Searching...")

    results = retriever.search(
        "How does FrontierAI decide which model to use?",
        limit=3,
    )

    print(
        "\nResults:",
        len(results),
    )

    for result in results:
        print(
            "\nScore:",
            result.score,
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
            "\nSemantic retrieval: OK"
        )
    else:
        print(
            "\nSemantic retrieval: FAILED"
        )


if __name__ == "__main__":
    main()