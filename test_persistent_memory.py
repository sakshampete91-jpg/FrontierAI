from app.memory.sqlite import SQLiteConversationStore


DATABASE = "data/frontier_memory.db"


def main() -> None:
    memory = SQLiteConversationStore(DATABASE)

    memory.clear()

    memory.add(
        "user",
        "FrontierAI persistent memory test.",
    )

    print("Before restart:")
    for item in memory.get_recent():
        print(f"{item.role}: {item.content}")


if __name__ == "__main__":
    main()