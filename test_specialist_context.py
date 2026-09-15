import asyncio

from app.core.container import create_orchestrator


async def test_request(
    orchestrator,
    request: str,
    conversation_id: str,
) -> None:
    result = await orchestrator.process(
        request,
        conversation_id=conversation_id,
    )

    print("\n" + "=" * 60)
    print("Request:", request)
    print("Intent:", result["intent"])
    print(
        "Specialist:",
        result["routing"]["specialist"],
    )
    print(
        "Memory used:",
        result["memory_items_used"],
    )
    print(
        "Specialist response:",
        result["specialist_response"],
    )
    print(
        "Final response:",
        result["response"],
    )
    print(
        "Status:",
        result["status"],
    )


async def main():
    orchestrator = create_orchestrator()

    await test_request(
        orchestrator,
        "Explain what a Python variable is.",
        "specialist_context_coding",
    )

    await test_request(
        orchestrator,
        "What is 15% of 200?",
        "specialist_context_math",
    )

    await test_request(
        orchestrator,
        "Explain what artificial intelligence means.",
        "specialist_context_general",
    )

    await test_request(
        orchestrator,
        "Research the history of artificial intelligence.",
        "specialist_context_research",
    )


if __name__ == "__main__":
    asyncio.run(main())