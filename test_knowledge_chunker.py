from app.knowledge.base import KnowledgeDocument
from app.knowledge.chunker import KnowledgeChunker


def main():
    document = KnowledgeDocument(
        document_id="doc-chunk-test",
        title="Chunking Test",
        content=(
            "FrontierAI is an AI orchestration platform. "
            "It coordinates models, memory, tools, specialists, "
            "retrieval, and verification. "
            "The knowledge system stores documents and splits "
            "them into smaller searchable chunks."
        ),
        source="chunk_test",
    )

    chunker = KnowledgeChunker(
        chunk_size=100,
        overlap=20,
    )

    chunks = chunker.chunk(document)

    print("Total chunks:", len(chunks))

    for chunk in chunks:
        print(
            "\nChunk ID:",
            chunk.chunk_id,
        )
        print(
            "Content:",
            chunk.content,
        )
        print(
            "Metadata:",
            chunk.metadata,
        )

    if chunks and all(
        chunk.document_id == document.document_id
        for chunk in chunks
    ):
        print("\nChunking: OK")
    else:
        print("\nChunking: FAILED")


if __name__ == "__main__":
    main()