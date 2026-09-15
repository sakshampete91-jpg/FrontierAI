from dataclasses import dataclass

from app.intent.engine import IntentResult


@dataclass
class RoutingDecision:
    """Decision produced by FrontierAI's model routing layer."""

    intent: str
    model_tier: str
    specialist: str
    reasoning_required: bool
    complexity: str = "low"
    tool_required: bool = False


class ModelRouter:
    """
    Intelligent model and specialist router.

    Routing is based on:
    - detected intent
    - task complexity
    - reasoning requirements
    - tool requirements
    """

    def route(self, intent: IntentResult) -> RoutingDecision:
        intent_name = intent.intent
        complexity = intent.complexity
        tool_required = intent.tool_required

        # Mathematics
        if intent_name == "mathematics":
            return RoutingDecision(
                intent=intent_name,
                model_tier="fast" if complexity == "low" else "strong",
                specialist="mathematics",
                reasoning_required=True,
                complexity=complexity,
                tool_required=True,
            )

        # Coding
        if intent_name == "coding":
            if complexity == "high":
                model_tier = "strong"
            else:
                model_tier = "strong"

            return RoutingDecision(
                intent=intent_name,
                model_tier=model_tier,
                specialist="coding",
                reasoning_required=True,
                complexity=complexity,
                tool_required=tool_required,
            )

        # Research
        if intent_name == "research":
            return RoutingDecision(
                intent=intent_name,
                model_tier="strong",
                specialist="research",
                reasoning_required=True,
                complexity=complexity,
                tool_required=True,
            )

        # General tasks
        if complexity == "high":
            return RoutingDecision(
                intent="general",
                model_tier="strong",
                specialist="general",
                reasoning_required=True,
                complexity=complexity,
                tool_required=tool_required,
            )

        return RoutingDecision(
            intent="general",
            model_tier="fast",
            specialist="general",
            reasoning_required=False,
            complexity=complexity,
            tool_required=tool_required,
        )