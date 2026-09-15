import asyncio
from time import perf_counter

from app.core.container import create_orchestrator


async def main():
    print("Creating FrontierAI orchestrator...")

    start = perf_counter()

    orchestrator = create_orchestrator()

    print(
        "Orchestrator created in:",
        round(
            perf_counter() - start,
            2,
        ),
        "seconds",
    )

    specialist = (
        orchestrator.specialist_registry.get(
            "research"
        )
    )

    print(
        "\nResearch specialist:",
        type(specialist).__name__,
    )

    request = (
        "Research the Python programming language "
        "using web sources and provide a concise summary."
    )

    print("\nRunning research specialist...")
    print(request)

    start = perf_counter()

    # First build research data explicitly.
    print("\n[1] Starting research pipeline...")

    research_data = (
        await orchestrator.research_pipeline.research(
            request,
            search_limit=5,
            fetch_limit=3,
        )
    )

    research_time = (
        perf_counter() - start
    )

    print(
        "[1] Research completed in:",
        round(
            research_time,
            2,
        ),
        "seconds",
    )

    print(
        "[1] Sources:",
        len(
            research_data.get(
                "sources",
                [],
            )
        ),
    )

    print(
        "[1] Citations:",
        len(
            research_data.get(
                "citations",
                [],
            )
        ),
    )

    # Now test only the specialist/model stage.
    specialist_context = {
        "intent": "research",
        "conversation_id": "specialist_timing_test",
        "memory": [],
        "knowledge": [],
        "routing": None,
        "research_data": research_data,
    }

    print(
        "\n[2] Starting ResearchSpecialist → Qwen3..."
    )

    start = perf_counter()

    response = await specialist.handle(
        request,
        specialist_context,
    )

    specialist_time = (
        perf_counter() - start
    )

    print(
        "[2] Specialist completed in:",
        round(
            specialist_time,
            2,
        ),
        "seconds",
    )

    print("\nResponse:")
    print(response)

    print("\n" + "=" * 60)
    print("TIMING SUMMARY")
    print("=" * 60)

    print(
        "Research pipeline:",
        round(
            research_time,
            2,
        ),
        "seconds",
    )

    print(
        "Specialist/Qwen3:",
        round(
            specialist_time,
            2,
        ),
        "seconds",
    )

    print(
        "Total:",
        round(
            research_time
            + specialist_time,
            2,
        ),
        "seconds",
    )

    if response:
        print(
            "\nSpecialist timing test: OK"
        )
    else:
        print(
            "\nSpecialist timing test: FAILED"
        )


if __name__ == "__main__":
    asyncio.run(main())