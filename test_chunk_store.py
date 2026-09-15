from app.knowledge.base import KnowledgeChunk
from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore


def main():
    store = SQLiteKnowledgeChunkStore(
        "data/test_knowledge.db"
    )

    store.clear()

    chunks = [
        KnowledgeChunk(
            chunk_id="doc-001-chunk-1",
            document_id="doc-001",
            content="FrontierAI uses model routing.",
            metadata={
                "chunk_number": 1,
                "topic": "routing",
            },
        ),
        KnowledgeChunk(
            chunk_id="doc-001-chunk-2",
            document_id="doc-001",
            content="FrontierAI uses persistent memory.",
            metadata={
                "chunk_number": 2,
                "topic": "memory",
            },
        ),
    ]

    store.add_chunks(chunks)

    first = store.get_chunk(
        "doc-001-chunk-1"
    )

    document_chunks = store.get_document_chunks(
        "doc-001"
    )

    print("Retrieved chunk:")
    print(first.content)

    print("\nDocument chunk count:")
    print(len(document_chunks))

    print("\nTotal stored chunks:")
    print(store.count())

    if (
        first.content
        == "FrontierAI uses model routing."
        and len(document_chunks) == 2
        and store.count() == 2
    ):
        print("\nChunk persistence: OK")
    else:
        print("\nChunk persistence: FAILED")


if __name__ == "__main__":
    main()