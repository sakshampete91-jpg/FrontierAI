from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore
from app.knowledge.chunker import KnowledgeChunker
from app.knowledge.pdf_ingestion import PDFKnowledgeIngestionService
from app.knowledge.sqlite import SQLiteKnowledgeStore


def main():
    database_path = "data/test_pdf_rag.db"

    document_store = SQLiteKnowledgeStore(
        database_path
    )

    chunk_store = SQLiteKnowledgeChunkStore(
        database_path
    )

    document_store.clear()
    chunk_store.clear()

    ingestion = PDFKnowledgeIngestionService(
        document_store=document_store,
        chunk_store=chunk_store,
        chunker=KnowledgeChunker(
            chunk_size=300,
            overlap=40,
        ),
    )

    document = ingestion.ingest_pdf(
        "frontierai_rag_test.pdf",
        source="pdf_test",
        metadata={
            "category": "rag",
        },
    )

    chunks = chunk_store.get_document_chunks(
        document.document_id
    )

    print("Document:", document.title)
    print("Document ID:", document.document_id)
    print("Source:", document.source)
    print("Extracted characters:", len(document.content))
    print("Chunks created:", len(chunks))

    print("\nFirst chunk:")
    if chunks:
        print(chunks[0].content)

    if (
        document.content.strip()
        and len(chunks) > 0
    ):
        print("\nPDF ingestion: OK")
    else:
        print("\nPDF ingestion: FAILED")


if __name__ == "__main__":
    main()