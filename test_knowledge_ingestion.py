from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore
from app.knowledge.chunker import KnowledgeChunker
from app.knowledge.ingestion import KnowledgeIngestionService
from app.knowledge.sqlite import SQLiteKnowledgeStore


def main():
    document_store = SQLiteKnowledgeStore(
        "data/test_ingestion.db"
    )

    chunk_store = SQLiteKnowledgeChunkStore(
        "data/test_ingestion.db"
    )

    document_store.clear()
    chunk_store.clear()

    service = KnowledgeIngestionService(
        document_store=document_store,
        chunk_store=chunk_store,
        chunker=KnowledgeChunker(
            chunk_size=150,
            overlap=20,
        ),
    )

    document = service.ingest_text_file(
        "knowledge_test.txt",
        source="local_test_file",
        metadata={
            "category": "frontierai",
        },
    )

    chunks = chunk_store.get_document_chunks(
        document.document_id
    )

    print("Document ID:", document.document_id)
    print("Title:", document.title)
    print("Source:", document.source)
    print("Chunks created:", len(chunks))

    for chunk in chunks:
        print(
            "\nChunk:",
            chunk.chunk_id,
        )
        print(
            "Content:",
            chunk.content,
        )

    stored_document = document_store.get_document(
        document.document_id
    )

    if (
        stored_document.title
        == "knowledge_test"
        and stored_document.content
        == document.content
        and len(chunks) > 0
    ):
        print("\nKnowledge ingestion: OK")
    else:
        print("\nKnowledge ingestion: FAILED")


if __name__ == "__main__":
    main()