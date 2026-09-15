from dataclasses import dataclass

from app.tools.registry import ToolRegistry


@dataclass
class ToolSelection:
    """Decision about whether a tool should be used."""

    tool_name: str | None
    reason: str
    confidence: float


class ToolSelector:
    """Selects an appropriate registered tool for a task."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
    ) -> None:
        self.tool_registry = tool_registry

    def select(
        self,
        *,
        intent: str,
        user_input: str,
    ) -> ToolSelection:
        text = user_input.lower().strip()

        available_tools = set(
            self.tool_registry.list_tools()
        )

        if (
            intent == "mathematics"
            and "calculator" in available_tools
            and self._looks_like_calculation(text)
        ):
            return ToolSelection(
                tool_name="calculator",
                reason="The request contains a mathematical expression.",
                confidence=0.98,
            )

        return ToolSelection(
            tool_name=None,
            reason="No currently registered tool is required.",
            confidence=0.90,
        )

    def _looks_like_calculation(
        self,
        text: str,
    ) -> bool:
        calculation_words = {
            "calculate",
            "compute",
            "solve",
        }

        if any(
            word in text
            for word in calculation_words
        ):
            return True

        mathematical_symbols = set(
            "0123456789+-*/%.()"
        )

        return any(
            character in mathematical_symbols
            for character in text
        )