import asyncio

from app.core.container import create_orchestrator


async def main():
    orchestrator = create_orchestrator()

    conversation_id = "memory_pipeline_test"

    first = await orchestrator.process(
        "My favorite programming language is Python.",
        conversation_id=conversation_id,
    )

    second = await orchestrator.process(
        "What is my favorite programming language?",
        conversation_id=conversation_id,
    )

    print("First response:")
    print(first["response"])

    print("\nSecond response:")
    print(second["response"])

    print("\nMemory used:")
    print(second["memory_items_used"])


if __name__ == "__main__":
    asyncio.run(main())