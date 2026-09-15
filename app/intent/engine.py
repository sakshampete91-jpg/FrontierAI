from dataclasses import dataclass


@dataclass
class IntentResult:
    """Result produced by the intent understanding layer."""

    intent: str
    confidence: float
    reasoning_required: bool
    complexity: str = "low"
    tool_required: bool = False


class IntentEngine:
    """
    FrontierAI intent understanding layer.

    Uses rule-based semantic signals to classify requests without
    requiring an additional model call. This keeps routing fast
    while providing richer information to the orchestrator.
    """

    def classify(self, text: str) -> IntentResult:
        original = text.strip()
        normalized = original.lower()

        if not normalized:
            return IntentResult(
                intent="general",
                confidence=0.50,
                reasoning_required=False,
                complexity="low",
                tool_required=False,
            )

        coding_signals = [
            "write code",
            "generate code",
            "code",
            "program",
            "programming",
            "debug",
            "debugging",
            "fix this code",
            "python",
            "javascript",
            "typescript",
            "html",
            "css",
            "api",
            "function",
            "class",
            "script",
            "algorithm",
            "compile",
            "syntax error",
            "bug",
        ]

        research_signals = [
            "research",
            "latest",
            "current",
            "recent",
            "news",
            "investigate",
            "look up",
            "find information",
            "sources",
            "source",
            "according to",
            "compare",
            "comparison",
            "pros and cons",
            "evidence",
            "what happened",
            "who is",
            "what is the latest",
        ]

        math_signals = [
            "calculate",
            "calculator",
            "compute",
            "equation",
            "solve",
            "mathematical",
            "math",
            "percentage",
            "percent",
            "average",
            "sum",
            "difference",
            "multiply",
            "divide",
        ]

        tool_signals = [
            "calculate",
            "compute",
            "run",
            "execute",
            "search",
            "look up",
            "find",
            "analyze",
            "convert",
        ]

        high_complexity_signals = [
            "build",
            "develop",
            "create an application",
            "architecture",
            "system design",
            "full project",
            "production",
            "deploy",
            "investigate",
            "deep research",
            "comprehensive",
            "analyze deeply",
        ]

        coding_score = self._score(
            normalized,
            coding_signals,
        )

        research_score = self._score(
            normalized,
            research_signals,
        )

        math_score = self._score(
            normalized,
            math_signals,
        )

        tool_required = self._contains_any(
            normalized,
            tool_signals,
        )

        high_complexity = self._contains_any(
            normalized,
            high_complexity_signals,
        )

        # Explicit mathematical requests take priority.
        if math_score > 0:
            complexity = "high" if high_complexity else "medium"

            return IntentResult(
                intent="mathematics",
                confidence=min(0.99, 0.80 + math_score * 0.05),
                reasoning_required=True,
                complexity=complexity,
                tool_required=True,
            )

        # Research language should take priority over generic
        # programming words when the user explicitly asks for
        # current information, sources, or investigation.
        if research_score > 0:
            complexity = "high" if high_complexity else "medium"

            return IntentResult(
                intent="research",
                confidence=min(0.98, 0.78 + research_score * 0.04),
                reasoning_required=True,
                complexity=complexity,
                tool_required=True,
            )

        if coding_score > 0:
            complexity = "high" if high_complexity else "medium"

            return IntentResult(
                intent="coding",
                confidence=min(0.98, 0.80 + coding_score * 0.04),
                reasoning_required=True,
                complexity=complexity,
                tool_required=tool_required,
            )

        complexity = "high" if high_complexity else "low"

        return IntentResult(
            intent="general",
            confidence=0.70,
            reasoning_required=False,
            complexity=complexity,
            tool_required=tool_required,
        )

    def _score(
        self,
        text: str,
        signals: list[str],
    ) -> int:
        return sum(
            1
            for signal in signals
            if signal in text
        )

    def _contains_any(
        self,
        text: str,
        signals: list[str],
    ) -> bool:
        return any(
            signal in text
            for signal in signals
        )