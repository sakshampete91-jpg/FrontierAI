from app.knowledge.base import KnowledgeChunk
from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore
from app.knowledge.retriever import KnowledgeRetriever


def main():
    store = SQLiteKnowledgeChunkStore(
        "data/test_retrieval_knowledge.db"
    )

    store.clear()

    store.add_chunks(
        [
            KnowledgeChunk(
                chunk_id="doc-1-chunk-1",
                document_id="doc-1",
                content=(
                    "FrontierAI uses model routing "
                    "to select an appropriate model."
                ),
                metadata={
                    "topic": "routing",
                },
            ),
            KnowledgeChunk(
                chunk_id="doc-1-chunk-2",
                document_id="doc-1",
                content=(
                    "FrontierAI stores persistent "
                    "conversation memory."
                ),
                metadata={
                    "topic": "memory",
                },
            ),
            KnowledgeChunk(
                chunk_id="doc-1-chunk-3",
                document_id="doc-1",
                content=(
                    "FrontierAI verifies calculator "
                    "results independently."
                ),
                metadata={
                    "topic": "verification",
                },
            ),
        ]
    )

    retriever = KnowledgeRetriever(store)

    results = retriever.search(
        "How does FrontierAI select a model?",
        limit=2,
    )

    print("Results:", len(results))

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
        and "model routing"
        in results[0].chunk.content.lower()
    ):
        print(
            "\nKnowledge retrieval: OK"
        )
    else:
        print(
            "\nKnowledge retrieval: FAILED"
        )


if __name__ == "__main__":
    main()