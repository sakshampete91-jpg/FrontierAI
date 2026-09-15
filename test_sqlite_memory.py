from app.memory.sqlite import SQLiteConversationStore


def main() -> None:
    memory = SQLiteConversationStore(
        "data/test_memory.db"
    )

    memory.clear()

    memory.add(
        "user",
        "My favorite language is Python.",
    )

    memory.add(
        "assistant",
        "Great choice!",
    )

    recent = memory.get_recent()

    print("SQLite memory test: OK")
    print("Stored items:", len(recent))

    for item in recent:
        print(f"{item.role}: {item.content}")


if __name__ == "__main__":
    main()