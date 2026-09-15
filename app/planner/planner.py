from dataclasses import dataclass

from app.intent.engine import IntentResult


@dataclass
class TaskPlan:
    """Execution plan generated for a user request."""

    steps: list[str]
    requires_tools: bool = False
    requires_retrieval: bool = False
    requires_verification: bool = True


class TaskPlanner:
    """Creates an execution plan based on detected intent."""

    def create_plan(self, intent: IntentResult) -> TaskPlan:

        if intent.intent == "coding":
            return TaskPlan(
                steps=[
                    "understand coding task",
                    "inspect relevant context",
                    "generate or modify solution",
                    "run tests or checks",
                    "verify result",
                ],
                requires_tools=True,
                requires_verification=True,
            )

        if intent.intent == "research":
            return TaskPlan(
                steps=[
                    "understand research question",
                    "retrieve relevant information",
                    "evaluate sources",
                    "compare evidence",
                    "synthesize findings",
                    "verify important claims",
                ],
                requires_tools=True,
                requires_retrieval=True,
                requires_verification=True,
            )

        if intent.intent == "mathematics":
            return TaskPlan(
                steps=[
                    "understand mathematical problem",
                    "solve problem",
                    "verify calculation",
                ],
                requires_verification=True,
            )

        return TaskPlan(
            steps=[
                "understand request",
                "generate response",
                "verify response",
            ],
            requires_verification=True,
        )