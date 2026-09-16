from dataclasses import dataclass, field
from typing import Any

from app.execution.engine import ExecutionEngine
from app.intent.engine import IntentEngine
from app.intent.router import ModelRouter, RoutingDecision
from app.memory.base import MemoryStore
from app.memory.retriever import MemoryRetriever
from app.models.gateway import ModelGateway
from app.planner.planner import TaskPlanner, TaskPlan
from app.specialists.coding import CodingSpecialist
from app.verification.engine import VerificationEngine


@dataclass
class TaskContext:
    """Information carried through the CHOKO pipeline."""

    user_input: str

    intent: str = "unknown"
    plan: TaskPlan | None = None
    routing: RoutingDecision | None = None

    execution: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None

    response: str | None = None

    specialist: dict[str, Any] | None = None

    context: dict[str, Any] | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


class MasterOrchestrator:
    """
    Central coordinator for CHOKO.

    Pipeline:

    Context
    → Memory
    → Intent
    → Routing
    → Planning
    → Specialist
    → Tools
    → Verification
    → Model
    → Memory
    → Response
    """

    def __init__(
        self,
        model_gateway: ModelGateway,
        intent_engine: IntentEngine | None = None,
        model_router: ModelRouter | None = None,
        task_planner: TaskPlanner | None = None,
        execution_engine: ExecutionEngine | None = None,
        verification_engine: VerificationEngine | None = None,
        memory_store: MemoryStore | None = None,
        memory_retriever: MemoryRetriever | None = None,
        coding_specialist: CodingSpecialist | None = None,
        context_manager: Any | None = None,
        **kwargs: Any,
    ) -> None:
        self.model_gateway = model_gateway

        self.intent_engine = (
            intent_engine or IntentEngine()
        )

        self.model_router = (
            model_router or ModelRouter()
        )

        self.task_planner = (
            task_planner or TaskPlanner()
        )

        self.execution_engine = execution_engine
        self.verification_engine = verification_engine

        self.memory_store = memory_store

        self.memory_retriever = (
            memory_retriever or MemoryRetriever()
        )

        self.coding_specialist = (
            coding_specialist
            or CodingSpecialist(model_gateway)
        )

        self.context_manager = context_manager

        self.extra_dependencies = kwargs

    async def process(
        self,
        user_input: str,
        *,
        conversation_id: str = "default",
    ) -> dict[str, Any]:

        context = TaskContext(
            user_input=user_input
        )

        # --------------------------------------------------
        # CONTEXT MANAGER
        # --------------------------------------------------

        if self.context_manager is not None:
            try:
                context_result = await self._build_context(
                    user_input,
                    conversation_id,
                )

                if context_result is not None:
                    context.context = context_result

            except Exception:
                # Context management must never prevent
                # the main request pipeline from running.
                context.context = None

        # --------------------------------------------------
        # MEMORY
        # --------------------------------------------------

        all_memory = []

        if self.memory_store is not None:
            all_memory = self.memory_store.get_recent(
                limit=50,
                conversation_id=conversation_id,
            )

        relevant_memory = (
            self.memory_retriever.retrieve(
                user_input,
                all_memory,
                limit=5,
            )
        )

        if self.memory_store is not None:
            self.memory_store.add(
                "user",
                user_input,
                conversation_id=conversation_id,
            )

        # --------------------------------------------------
        # INTENT
        # --------------------------------------------------

        intent_result = (
            self.intent_engine.classify(
                user_input
            )
        )

        context.intent = intent_result.intent

        # --------------------------------------------------
        # ROUTING
        # --------------------------------------------------

        context.routing = (
            self.model_router.route(
                intent_result
            )
        )

        # --------------------------------------------------
        # PLANNING
        # --------------------------------------------------

        context.plan = (
            self.task_planner.create_plan(
                intent_result
            )
        )

        # --------------------------------------------------
        # SPECIALIST
        # --------------------------------------------------

        if (
            context.routing.specialist
            == "coding"
        ):
            coding_result = (
                self.coding_specialist.analyze(
                    user_input
                )
            )

            context.specialist = {
                "name": "coding",
                "language": coding_result.language,
                "requires_execution": (
                    coding_result.requires_execution
                ),
                "requires_verification": (
                    coding_result.requires_verification
                ),
                "metadata": (
                    coding_result.metadata
                ),
            }

        # --------------------------------------------------
        # MATHEMATICS TOOL PIPELINE
        # --------------------------------------------------

        if (
            context.intent == "mathematics"
            and self.execution_engine is not None
        ):
            expression = (
                self._extract_expression(
                    user_input
                )
            )

            if expression:
                context.execution = (
                    self.execution_engine.execute_tool(
                        "calculator",
                        expression=expression,
                    )
                )

                if (
                    context.execution.get(
                        "status"
                    ) == "success"
                    and self.verification_engine
                    is not None
                ):
                    verification = (
                        self.verification_engine
                        .verify_calculation(
                            expression=expression,
                            actual_result=(
                                context.execution[
                                    "result"
                                ]
                            ),
                        )
                    )

                    context.verification = {
                        "verified": (
                            verification.verified
                        ),
                        "message": (
                            verification.message
                        ),
                        "expected": (
                            verification.expected
                        ),
                        "actual": (
                            verification.actual
                        ),
                    }

                if (
                    context.execution.get(
                        "status"
                    ) == "success"
                ):
                    context.response = str(
                        context.execution[
                            "result"
                        ]
                    )

        # --------------------------------------------------
        # MODEL RESPONSE
        # --------------------------------------------------

        if context.response is None:

            system_prompt = (
                "You are CHOKO, a helpful AI assistant.\n\n"
                "Your name is CHOKO.\n"
                "If the user asks your name, identify yourself "
                "as CHOKO.\n"
                "Do not identify yourself as FrontierAI.\n"
                "Do not mention FrontierAI unless the user "
                "specifically asks about the project's old "
                "or internal name.\n\n"
                "Follow the user's request accurately.\n"
                "Use relevant conversation memory when "
                "provided.\n"
                "Do not claim to have used tools, sources, "
                "or executed code unless that actually "
                "happened.\n"
            )

            if (
                context.routing.specialist
                == "coding"
            ):
                system_prompt += (
                    "\nYou are handling this request "
                    "as the coding specialist.\n"
                    "Provide correct, runnable code when "
                    "code is requested.\n"
                    "Prefer simple and maintainable "
                    "solutions.\n"
                    "Explain important parts briefly.\n"
                    "Do not claim code execution unless "
                    "an execution tool actually ran.\n"
                )

                if context.specialist:
                    language = (
                        context.specialist.get(
                            "language"
                        )
                    )

                    if language:
                        system_prompt += (
                            f"\nDetected language: "
                            f"{language}\n"
                        )

            # Add context-manager information if available.
            if context.context:
                system_prompt += (
                    "\nRelevant context:\n"
                    f"{context.context}\n"
                )

            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                }
            ]

            for item in relevant_memory:
                messages.append(
                    {
                        "role": item.role,
                        "content": item.content,
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            context.response = (
                await self.model_gateway.generate(
                    messages
                )
            )

        # --------------------------------------------------
        # MEMORY UPDATE
        # --------------------------------------------------

        if (
            self.memory_store is not None
            and context.response is not None
        ):
            self.memory_store.add(
                "assistant",
                context.response,
                conversation_id=conversation_id,
            )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        verified = (
            context.verification is not None
            and context.verification.get(
                "verified"
            )
            is True
        )

        if (
            context.execution
            and not verified
        ):
            status = "verification_failed"

        elif verified:
            status = "verified"

        elif context.execution:
            status = "executed"

        else:
            status = "completed"

        # --------------------------------------------------
        # FINAL RESPONSE
        # --------------------------------------------------

        return {
            "input": context.user_input,

            "response": context.response,

            "intent": context.intent,

            "confidence": (
                intent_result.confidence
            ),

            "conversation_id": (
                conversation_id
            ),

            "memory_items_available": (
                len(all_memory)
            ),

            "memory_items_used": (
                len(relevant_memory)
            ),

            "context_available": (
                context.context is not None
            ),

            "routing": {
                "model_tier": (
                    context.routing.model_tier
                ),
                "specialist": (
                    context.routing.specialist
                ),
                "reasoning_required": (
                    context.routing
                    .reasoning_required
                ),
                "complexity": (
                    context.routing.complexity
                ),
                "tool_required": (
                    context.routing.tool_required
                ),
            },

            "specialist": (
                context.specialist
            ),

            "plan": (
                context.plan.steps
            ),

            "requires_tools": (
                context.plan.requires_tools
            ),

            "requires_retrieval": (
                context.plan.requires_retrieval
            ),

            "requires_verification": (
                context.plan
                .requires_verification
            ),

            "execution": (
                context.execution
            ),

            "verification": (
                context.verification
            ),

            "status": status,
        }

    async def _build_context(
        self,
        user_input: str,
        conversation_id: str,
    ) -> dict[str, Any] | None:
        """
        Safely obtain context from the ContextManager.

        Supports common async/sync context-manager interfaces
        without forcing the rest of CHOKO to depend on
        one specific implementation.
        """

        manager = self.context_manager

        method_names = [
            "build_context",
            "get_context",
            "create_context",
            "resolve",
        ]

        for method_name in method_names:

            method = getattr(
                manager,
                method_name,
                None,
            )

            if method is None:
                continue

            try:
                result = method(
                    user_input,
                    conversation_id=conversation_id,
                )
            except TypeError:
                try:
                    result = method(
                        user_input
                    )
                except TypeError:
                    continue

            if hasattr(result, "__await__"):
                result = await result

            if result is None:
                return None

            if isinstance(result, dict):
                return result

            return {
                "value": result
            }

        return None

    def _extract_expression(
        self,
        text: str,
    ) -> str | None:

        expression = (
            text.lower().strip()
        )

        for prefix in [
            "calculate",
            "compute",
            "solve",
        ]:
            if expression.startswith(prefix):
                expression = (
                    expression[
                        len(prefix):
                    ].strip()
                )
                break

        allowed = set(
            "0123456789+-*/%.() "
        )

        if (
            expression
            and all(
                char in allowed
                for char in expression
            )
        ):
            return expression

        return None