import asyncio
import time

from app.tools.registry import ToolDefinition, ToolRegistry
from app.execution.engine import ExecutionEngine


def slow_tool() -> str:
    time.sleep(3)
    return "finished"


async def main():
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="slow_tool",
            description="Test tool that intentionally runs slowly.",
            handler=slow_tool,
            timeout_seconds=1.0,
        )
    )

    engine = ExecutionEngine(registry)

    result = await engine.execute_tool(
        "slow_tool"
    )

    print("Execution result:", result)

    if result["status"] == "timeout":
        print("Timeout protection: OK")
    else:
        print("ERROR: Timeout protection failed.")


if __name__ == "__main__":
    asyncio.run(main())