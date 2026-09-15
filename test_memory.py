from app.memory.conversation import InMemoryConversationStore


def main() -> None:
    memory = InMemoryConversationStore()

    memory.add(
        "user",
        "My name is Alex.",
    )

    memory.add(
        "assistant",
        "Nice to meet you, Alex.",
    )

    recent = memory.get_recent()

    print("Memory test: OK")
    print("Stored items:", len(recent))

    for item in recent:
        print(f"{item.role}: {item.content}")


if __name__ == "__main__":
    main()