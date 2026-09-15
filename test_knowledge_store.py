from app.knowledge.base import KnowledgeDocument
from app.knowledge.sqlite import SQLiteKnowledgeStore


def main():
    store = SQLiteKnowledgeStore(
        "data/test_knowledge.db"
    )

    store.clear()

    document = KnowledgeDocument(
        document_id="doc-001",
        title="FrontierAI Test Document",
        content=(
            "FrontierAI is a local AI orchestration platform "
            "designed to coordinate models, memory, tools, "
            "retrieval, specialists, and verification."
        ),
        source="local_test",
        metadata={
            "category": "architecture",
            "test": True,
        },
    )

    store.add_document(document)

    retrieved = store.get_document(
        "doc-001"
    )

    print("Document ID:", retrieved.document_id)
    print("Title:", retrieved.title)
    print("Content:", retrieved.content)
    print("Source:", retrieved.source)
    print("Metadata:", retrieved.metadata)

    documents = store.list_documents()

    print("\nTotal documents:", len(documents))

    if (
        retrieved.document_id == "doc-001"
        and retrieved.title == "FrontierAI Test Document"
        and len(documents) == 1
    ):
        print("\nKnowledge persistence: OK")
    else:
        print("\nKnowledge persistence: FAILED")


if __name__ == "__main__":
    main()