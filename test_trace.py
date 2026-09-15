import asyncio

from app.core.container import create_orchestrator


async def main():
    orchestrator = create_orchestrator()

    result = await orchestrator.process(
        "calculate 25 * 4",
        conversation_id="trace_test",
    )

    trace = result["trace"]

    print("Request ID:", trace["request_id"])

    print("\nTrace events:")

    for event in trace["events"]:
        print("-", event["name"])

    expected_events = {
        "request_received",
        "memory_loaded",
        "memory_retrieved",
        "intent_classified",
        "task_routed",
        "plan_created",
        "tool_selected",
        "tool_executed",
        "verification_completed",
        "request_completed",
    }

    actual_events = {
        event["name"]
        for event in trace["events"]
    }

    missing = expected_events - actual_events

    if not missing:
        print("\nTrace verification: OK")
    else:
        print("\nMissing events:", sorted(missing))


if __name__ == "__main__":
    asyncio.run(main())