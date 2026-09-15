import asyncio

from app.core.container import create_orchestrator


async def main() -> None:
    orchestrator = create_orchestrator()

    print("=== Message 1 ===")

    result1 = await orchestrator.process(
        "My favorite programming language is Python."
    )

    print("Response:", result1["response"])
    print("Memory used:", result1["memory_items_used"])

    print()
    print("=== Message 2 ===")

    result2 = await orchestrator.process(
        "What is my favorite programming language?"
    )

    print("Response:", result2["response"])
    print("Memory used:", result2["memory_items_used"])


if __name__ == "__main__":
    asyncio.run(main())