from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore
from app.knowledge.pdf_ingestion import PDFKnowledgeIngestionService
from app.knowledge.retriever import KnowledgeRetriever
from app.knowledge.sqlite import SQLiteKnowledgeStore
from app.knowledge.chunker import KnowledgeChunker


def main():
    database_path = "data/test_pdf_retrieval.db"

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

    retriever = KnowledgeRetriever(
        chunk_store
    )

    results = retriever.search(
        "What is the secret test phrase in the PDF?",
        limit=3,
    )

    print("Document:", document.title)
    print(
        "Retrieved results:",
        len(results),
    )

    for result in results:
        print("\nScore:", result.score)
        print(
            "Content:",
            result.chunk.content,
        )

    found_phrase = any(
        "ORBIT-84721"
        in result.chunk.content
        for result in results
    )

    if found_phrase:
        print(
            "\nPDF retrieval: OK"
        )
    else:
        print(
            "\nPDF retrieval: FAILED"
        )


if __name__ == "__main__":
    main()