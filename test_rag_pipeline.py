import asyncio

from app.core.container import create_orchestrator
from app.knowledge.base import KnowledgeChunk
from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore
from app.knowledge.retriever import KnowledgeRetriever


async def main():
    orchestrator = create_orchestrator()

    test_store = SQLiteKnowledgeChunkStore(
        "data/test_rag_pipeline.db"
    )

    test_store.clear()

    test_store.add_chunk(
        KnowledgeChunk(
            chunk_id="rag-e2e-001",
            document_id="rag-e2e-doc",
            content=(
                "FrontierAI internal test code is "
                "84721. This value exists only in the "
                "local knowledge base for RAG testing."
            ),
            metadata={
                "title": "RAG End-to-End Test",
                "source": "local_rag_test",
                "topic": "testing",
            },
        )
    )

    orchestrator.knowledge_retriever = (
        KnowledgeRetriever(test_store)
    )

    result = await orchestrator.process(
        "According to the knowledge base, "
        "what is the FrontierAI internal test code?",
        conversation_id="rag_e2e_test",
    )

    print("Knowledge items used:")
    print(result["knowledge_items_used"])

    print("\nSelected specialist:")
    print(result["routing"]["specialist"])

    print("\nSpecialist response:")
    print(result["specialist_response"])

    print("\nFinal response:")
    print(result["response"])

    print("\nStatus:")
    print(result["status"])

    if result["knowledge_items_used"] > 0:
        print("\nRAG retrieval into pipeline: OK")
    else:
        print("\nRAG retrieval into pipeline: FAILED")


if __name__ == "__main__":
    asyncio.run(main())