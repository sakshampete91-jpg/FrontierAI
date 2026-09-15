import asyncio

from app.core.container import create_orchestrator


async def main():
    orchestrator = create_orchestrator()

    requests = [
        "Write a Python program to reverse a string",
        "Calculate 25 * 4",
        "Tell me a joke",
    ]

    for request in requests:
        print("\n" + "=" * 60)
        print("Request:", request)

        result = await orchestrator.process(
            request,
            conversation_id="specialist_test",
        )

        print("Intent:", result["intent"])
        print(
            "Specialist:",
            result["routing"]["specialist"],
        )
        print(
            "Specialist response:",
            result["specialist_response"],
        )
        print(
            "Tool:",
            result["tool_selection"]["tool_name"],
        )
        print(
            "Final response:",
            result["response"],
        )


if __name__ == "__main__":
    asyncio.run(main())