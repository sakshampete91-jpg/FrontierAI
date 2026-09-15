import asyncio

from app.core.container import create_orchestrator


async def main():
    orchestrator = create_orchestrator()

    # Force an unexpected exception inside the internal pipeline.
    async def broken_internal(*args, **kwargs):
        raise RuntimeError(
            "Intentional test failure"
        )

    orchestrator._process_internal = (
        broken_internal
    )

    result = await orchestrator.process(
        "test error handling",
        conversation_id="error_test",
    )

    print("Status:")
    print(result["status"])

    print("\nError:")
    print(result["error"])

    print("\nTrace events:")

    for event in result["trace"]["events"]:
        print(
            "-",
            event["name"],
        )

    if (
        result["status"] == "failed"
        and result["error"]["type"] == "RuntimeError"
        and any(
            event["name"] == "request_failed"
            for event in result["trace"]["events"]
        )
    ):
        print(
            "\nGlobal error handling test: OK"
        )
    else:
        print(
            "\nGlobal error handling test: FAILED"
        )


if __name__ == "__main__":
    asyncio.run(main())