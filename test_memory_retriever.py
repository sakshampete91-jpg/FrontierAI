from datetime import datetime, timezone

from app.memory.base import MemoryItem
from app.memory.retriever import MemoryRetriever


def main() -> None:
    memories = [
        MemoryItem(
            role="user",
            content="My favorite programming language is Python.",
            timestamp=datetime.now(timezone.utc),
            metadata={},
            conversation_id="test",
        ),
        MemoryItem(
            role="user",
            content="I enjoy playing guitar.",
            timestamp=datetime.now(timezone.utc),
            metadata={},
            conversation_id="test",
        ),
        MemoryItem(
            role="user",
            content="I am learning artificial intelligence.",
            timestamp=datetime.now(timezone.utc),
            metadata={},
            conversation_id="test",
        ),
    ]

    retriever = MemoryRetriever()

    results = retriever.retrieve(
        "What programming language do I like?",
        memories,
        limit=2,
    )

    print("Memory retriever test: OK")
    print("Relevant memories:", len(results))

    for item in results:
        print(f"{item.role}: {item.content}")


if __name__ == "__main__":
    main()
