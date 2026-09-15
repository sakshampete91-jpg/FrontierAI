from app.memory.sqlite import SQLiteConversationStore


def main() -> None:
    memory = SQLiteConversationStore(
        "data/test_isolation.db"
    )

    memory.clear()

    memory.add(
        "user",
        "Secret from conversation A.",
        conversation_id="conversation_a",
    )

    memory.add(
        "user",
        "Secret from conversation B.",
        conversation_id="conversation_b",
    )

    conversation_a = memory.get_recent(
        conversation_id="conversation_a"
    )

    conversation_b = memory.get_recent(
        conversation_id="conversation_b"
    )

    print("Memory isolation test: OK")
    print()
    print("Conversation A:")

    for item in conversation_a:
        print(f"{item.role}: {item.content}")

    print()
    print("Conversation B:")

    for item in conversation_b:
        print(f"{item.role}: {item.content}")


if __name__ == "__main__":
    main()