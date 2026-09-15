import asyncio

from app.core.container import create_orchestrator


async def main():
    orchestrator = create_orchestrator()

    request = (
        "Research the Python programming language using "
        "web sources and provide citations."
    )

    print("REQUEST:")
    print(request)

    result = await orchestrator.process(
        request,
        conversation_id="research_debug_final",
    )

    routing = result.get(
        "routing",
        {},
    )

    research = result.get(
        "research"
    )

    print("\n" + "=" * 70)

    print("INTENT:")
    print(
        result.get("intent")
    )

    print("\nSPECIALIST:")
    print(
        routing.get("specialist")
    )

    print("\nRESEARCH OBJECT EXISTS:")
    print(
        research is not None
    )

    if research is not None:
        print("\nRESEARCH PROVIDER:")
        print(
            research.get(
                "search_provider"
            )
        )

        print("\nSOURCE COUNT:")
        print(
            research.get(
                "source_count"
            )
        )

        print("\nCITATION COUNT:")
        print(
            research.get(
                "citation_count"
            )
        )

        print("\nRESEARCH ERROR:")
        print(
            research.get(
                "error"
            )
        )

        print("\nSTRUCTURED SOURCES:")

        for source in research.get(
            "sources",
            [],
        ):
            print(
                "\nTitle:",
                source.get("title")
            )

            print(
                "URL:",
                source.get("url")
            )

            print(
                "Fetch:",
                source.get(
                    "fetch_success"
                )
            )

        print("\nSTRUCTURED CITATIONS:")

        for citation in research.get(
            "citations",
            [],
        ):
            print(
                citation.get(
                    "citation_id"
                ),
                "|",
                citation.get(
                    "title"
                ),
                "|",
                citation.get(
                    "url"
                ),
            )

    print("\n" + "=" * 70)

    print("MODEL RESPONSE:")
    print(
        result.get(
            "response"
        )
    )

    print("\n" + "=" * 70)

    print("DIAGNOSTIC RESULT:")

    routing_ok = (
        routing.get(
            "specialist"
        )
        == "research"
    )

    research_ok = (
        research is not None
    )

    source_ok = (
        research is not None
        and research.get(
            "source_count",
            0,
        ) > 0
    )

    citation_ok = (
        research is not None
        and research.get(
            "citation_count",
            0,
        ) > 0
    )

    print(
        "Research routing:",
        routing_ok,
    )

    print(
        "Research object:",
        research_ok,
    )

    print(
        "Real sources:",
        source_ok,
    )

    print(
        "Structured citations:",
        citation_ok,
    )

    if (
        routing_ok
        and research_ok
        and source_ok
        and citation_ok
    ):
        print(
            "\nRESEARCH PIPELINE: OK"
        )
    else:
        print(
            "\nRESEARCH PIPELINE: FAILED"
        )


if __name__ == "__main__":
    asyncio.run(main())