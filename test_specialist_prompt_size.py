import asyncio


from app.core.container import create_orchestrator


async def main():
    orchestrator = create_orchestrator()

    request = (
        "Research the Python programming language "
        "using web sources and provide a concise summary."
    )

    print("Starting research pipeline...")

    research_data = (
        await orchestrator.research_pipeline.research(
            request,
            search_limit=5,
            fetch_limit=3,
        )
    )

    print(
        "Sources:",
        len(
            research_data.get(
                "sources",
                [],
            )
        ),
    )

    specialist = (
        orchestrator.specialist_registry.get(
            "research"
        )
    )

    # Replace the real model call with a diagnostic function.
    async def inspect_generate(messages):
        print("\n" + "=" * 70)
        print("ACTUAL MODEL MESSAGE ANALYSIS")
        print("=" * 70)

        total_chars = 0

        for index, message in enumerate(
            messages,
            start=1,
        ):
            content = str(
                message.get(
                    "content",
                    "",
                )
            )

            chars = len(content)

            total_chars += chars

            print(
                f"\nMessage {index}"
            )

            print(
                "Role:",
                message.get("role"),
            )

            print(
                "Characters:",
                chars,
            )

            print(
                "Approx tokens:",
                chars // 4,
            )

        print("\nTOTAL CHARACTERS:")
        print(total_chars)

        print(
            "TOTAL APPROX TOKENS:"
        )

        print(
            total_chars // 4
        )

        return "DIAGNOSTIC MODEL RESPONSE"

    original_generate = (
        specialist.model_gateway.generate
    )

    specialist.model_gateway.generate = (
        inspect_generate
    )

    try:
        context = {
            "intent": "research",
            "conversation_id": "prompt_size_test",
            "memory": [],
            "knowledge": [],
            "routing": None,
            "research_data": research_data,
        }

        await specialist.handle(
            request,
            context,
        )

    finally:
        specialist.model_gateway.generate = (
            original_generate
        )

    print(
        "\nPrompt measurement complete."
    )


if __name__ == "__main__":
    asyncio.run(main())