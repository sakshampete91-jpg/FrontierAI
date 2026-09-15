from dataclasses import dataclass


@dataclass
class IntentResult:
    intent: str
    confidence: float
    reasoning_required: bool


class IntentEngine:
    """Classifies the user's request into a high-level task type."""

    def classify(
        self,
        text: str,
    ) -> IntentResult:
        text = text.lower().strip()

        # -----------------------------------------------------
        # Research has highest priority when explicitly requested.
        # This prevents words such as "python", "program", or
        # "code" inside a research request from forcing coding.
        # -----------------------------------------------------
        research_signals = [
            "research",
            "investigate",
            "latest",
            "recent",
            "current information",
            "news",
            "sources",
            "citations",
            "according to",
            "find information",
            "look up",
            "web search",
            "search the web",
            "study",
            "analyze the history",
            "literature review",
        ]

        if any(
            signal in text
            for signal in research_signals
        ):
            return IntentResult(
                intent="research",
                confidence=0.95,
                reasoning_required=True,
            )

        # -----------------------------------------------------
        # Coding
        # -----------------------------------------------------
        coding_signals = [
            "code",
            "python",
            "program",
            "programming",
            "debug",
            "javascript",
            "java",
            "c++",
            "c#",
            "html",
            "css",
            "function",
            "class",
            "variable",
            "loop",
            "algorithm",
            "syntax",
        ]

        if any(
            signal in text
            for signal in coding_signals
        ):
            return IntentResult(
                intent="coding",
                confidence=0.95,
                reasoning_required=True,
            )

        # -----------------------------------------------------
        # Mathematics
        # -----------------------------------------------------
        mathematics_signals = [
            "calculate",
            "calculation",
            "equation",
            "math",
            "mathematics",
            "solve",
            "percentage",
            "percent",
            "derivative",
            "integral",
            "algebra",
            "geometry",
            "probability",
        ]

        if any(
            signal in text
            for signal in mathematics_signals
        ):
            return IntentResult(
                intent="mathematics",
                confidence=0.95,
                reasoning_required=True,
            )

        # -----------------------------------------------------
        # General
        # -----------------------------------------------------
        return IntentResult(
            intent="general",
            confidence=0.70,
            reasoning_required=False,
        )