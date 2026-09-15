from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolDefinition:
    """Definition of a registered FrontierAI tool."""

    name: str
    description: str
    handler: Callable[..., Any]

    input_schema: dict[str, type] = field(
        default_factory=dict
    )

    requires_permission: bool = False
    timeout_seconds: float = 10.0
    enabled: bool = True


class ToolRegistry:
    """Stores and safely manages tools available to FrontierAI."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        tool: ToolDefinition,
    ) -> None:
        if tool.name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool.name}"
            )

        self._tools[tool.name] = tool

    def get(
        self,
        name: str,
    ) -> ToolDefinition:
        tool = self._tools.get(name)

        if tool is None:
            raise ValueError(
                f"Unknown tool: {name}"
            )

        return tool

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def validate_inputs(
        self,
        tool: ToolDefinition,
        kwargs: dict[str, Any],
    ) -> None:
        if not tool.input_schema:
            return

        expected = set(tool.input_schema.keys())
        provided = set(kwargs.keys())

        missing = expected - provided
        unexpected = provided - expected

        if missing:
            raise ValueError(
                f"Missing tool arguments: "
                f"{sorted(missing)}"
            )

        if unexpected:
            raise ValueError(
                f"Unexpected tool arguments: "
                f"{sorted(unexpected)}"
            )

        for name, expected_type in tool.input_schema.items():
            value = kwargs[name]

            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Invalid type for '{name}': "
                    f"expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

    def execute(
        self,
        name: str,
        *,
        permission_granted: bool = False,
        **kwargs: Any,
    ) -> Any:
        tool = self.get(name)

        if not tool.enabled:
            raise RuntimeError(
                f"Tool is disabled: {name}"
            )

        if (
            tool.requires_permission
            and not permission_granted
        ):
            raise PermissionError(
                f"Permission required to execute tool: {name}"
            )

        self.validate_inputs(
            tool,
            kwargs,
        )

        return tool.handler(**kwargs)