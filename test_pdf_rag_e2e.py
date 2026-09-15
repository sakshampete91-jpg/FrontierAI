import asyncio

from app.core.container import create_orchestrator
from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore
from app.knowledge.pdf_ingestion import PDFKnowledgeIngestionService
from app.knowledge.sqlite import SQLiteKnowledgeStore


async def main():
    database_path = "data/test_pdf_e2e.db"

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
    )

    document = ingestion.ingest_pdf(
        "frontierai_rag_test.pdf",
        source="pdf_e2e_test",
        metadata={
            "category": "rag",
        },
    )

    orchestrator = create_orchestrator()

    orchestrator.knowledge_retriever.chunk_store = (
        chunk_store
    )

    result = await orchestrator.process(
        "According to the PDF, what is the secret test phrase?",
        conversation_id="pdf_rag_e2e",
    )

    print("Document:", document.title)

    print(
        "\nKnowledge items used:",
        result["knowledge_items_used"],
    )

    print(
        "\nRetrieved knowledge:"
    )

    knowledge_results = (
        orchestrator.knowledge_retriever.search(
            "What is the secret test phrase in the PDF?",
            limit=3,
        )
    )

    for item in knowledge_results:
        print(
            "\nScore:",
            item.score,
        )
        print(
            item.chunk.content
        )

    print(
        "\nSpecialist:",
        result["routing"]["specialist"],
    )

    print(
        "\nSpecialist response:"
    )
    print(
        result["specialist_response"]
    )

    print(
        "\nFinal response:"
    )
    print(
        result["response"]
    )

    if (
        result["knowledge_items_used"] > 0
        and "84721" in result["response"]
    ):
        print(
            "\nPDF → RAG → Qwen3: OK"
        )
    else:
        print(
            "\nPDF → RAG → Qwen3: FAILED"
        )


if __name__ == "__main__":
    asyncio.run(main())