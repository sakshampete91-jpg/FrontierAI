import asyncio


from app.core.container import create_orchestrator


async def main():
    orchestrator = create_orchestrator()

    request = (
        "Research the Python programming language "
        "using web sources and provide a concise summary."
    )

    print("Creating research data...")

    research_data = (
        await orchestrator.research_pipeline.research(
            request,
            search_limit=5,
            fetch_limit=3,
        )
    )

    print(
        "\nSources:",
        len(
            research_data.get(
                "sources",
                [],
            )
        ),
    )

    total_chars = 0

    for index, source in enumerate(
        research_data.get(
            "sources",
            [],
        ),
        start=1,
    ):
        text = getattr(
            source,
            "extracted_text",
            "",
        )

        chars = len(text)

        total_chars += chars

        print(
            f"Source {index} characters:",
            chars,
        )

    print(
        "\nTotal source characters:",
        total_chars,
    )

    print(
        "Approximate tokens:",
        total_chars // 4,
    )

    specialist = (
        orchestrator.specialist_registry.get(
            "research"
        )
    )

    context = {
        "intent": "research",
        "conversation_id": "context_size_test",
        "memory": [],
        "knowledge": [],
        "routing": None,
        "research_data": research_data,
    }

    print(
        "\nBuilding specialist context..."
    )

    # This exercises the same specialist path,
    # but we do not call the model.
    if research_data.get("sources"):
        blocks = []

        for source in research_data["sources"]:
            text = getattr(
                source,
                "extracted_text",
                "",
            )

            blocks.append(
                text[:8000]
            )

        combined = "\n\n".join(
            blocks
        )

        print(
            "Specialist source context characters:",
            len(combined),
        )

        print(
            "Approximate context tokens:",
            len(combined) // 4,
        )

    print(
        "\nContext measurement complete."
    )


if __name__ == "__main__":
    asyncio.run(main())