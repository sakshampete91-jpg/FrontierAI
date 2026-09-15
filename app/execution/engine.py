import asyncio
from typing import Any

from app.tools.registry import ToolRegistry


class ExecutionEngine:
    """Executes approved tools with safety controls."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
    ) -> None:
        self.tool_registry = tool_registry

    async def execute_tool(
        self,
        tool_name: str,
        *,
        permission_granted: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        try:
            tool = self.tool_registry.get(tool_name)

            if not tool.enabled:
                raise RuntimeError(
                    f"Tool is disabled: {tool_name}"
                )

            if (
                tool.requires_permission
                and not permission_granted
            ):
                raise PermissionError(
                    f"Permission required to execute tool: "
                    f"{tool_name}"
                )

            self.tool_registry.validate_inputs(
                tool,
                kwargs,
            )

            result = await asyncio.wait_for(
                asyncio.to_thread(
                    tool.handler,
                    **kwargs,
                ),
                timeout=tool.timeout_seconds,
            )

            return {
                "tool": tool_name,
                "status": "success",
                "result": result,
            }

        except asyncio.TimeoutError:
            return {
                "tool": tool_name,
                "status": "timeout",
                "error": (
                    f"Tool execution exceeded "
                    f"the {tool.timeout_seconds}s timeout."
                ),
            }

        except Exception as exc:
            return {
                "tool": tool_name,
                "status": "error",
                "error": str(exc),
            }