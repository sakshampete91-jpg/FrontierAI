from dataclasses import dataclass

from app.intent.engine import IntentResult


@dataclass
class RoutingDecision:
    """Decision about how a request should be processed."""

    intent: str
    model_tier: str
    specialist: str
    reasoning_required: bool
    complexity: str
    tool_required: bool


class ModelRouter:
    """Selects a model tier and specialist based on task characteristics."""

    def route(
        self,
        intent: IntentResult,
    ) -> RoutingDecision:
        routing = {
            "coding": {
                "model_tier": "strong",
                "specialist": "coding",
                "complexity": "high",
                "tool_required": True,
            },
            "research": {
                "model_tier": "strong",
                "specialist": "research",
                "complexity": "high",
                "tool_required": True,
            },
            "mathematics": {
                "model_tier": "fast",
                "specialist": "mathematics",
                "complexity": "medium",
                "tool_required": True,
            },
            "general": {
                "model_tier": "fast",
                "specialist": "general",
                "complexity": "low",
                "tool_required": False,
            },
        }

        selected = routing.get(
            intent.intent,
            routing["general"],
        )

        model_tier = selected["model_tier"]

        if intent.reasoning_required and selected["complexity"] == "high":
            model_tier = "strong"

        return RoutingDecision(
            intent=intent.intent,
            model_tier=model_tier,
            specialist=selected["specialist"],
            reasoning_required=intent.reasoning_required,
            complexity=selected["complexity"],
            tool_required=selected["tool_required"],
        )