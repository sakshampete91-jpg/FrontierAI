import asyncio

from app.core.container import create_orchestrator


async def main():
    orchestrator = create_orchestrator()

    result = await orchestrator.process(
        "calculate 25 * 4",
        conversation_id="tool_pipeline_test",
    )

    print("Response:", result["response"])
    print("Intent:", result["intent"])
    print("Selected tool:", result["tool_selection"]["tool_name"])
    print("Tool confidence:", result["tool_selection"]["confidence"])
    print("Execution:", result["execution"])
    print("Verification:", result["verification"])
    print("Status:", result["status"])


if __name__ == "__main__":
    asyncio.run(main())