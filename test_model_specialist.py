import asyncio

from app.core.container import create_orchestrator


async def main():
    orchestrator = create_orchestrator()

    result = await orchestrator.process(
        "Explain what a Python variable is.",
        conversation_id="model_specialist_test",
    )

    print("Intent:", result["intent"])
    print(
        "Selected specialist:",
        result["routing"]["specialist"],
    )

    print(
        "\nSpecialist response:"
    )
    print(
        result["specialist_response"]
    )

    print(
        "\nFinal response:"
    )
    print(
        result["response"]
    )

    print(
        "\nStatus:",
        result["status"]
    )


if __name__ == "__main__":
    asyncio.run(main())