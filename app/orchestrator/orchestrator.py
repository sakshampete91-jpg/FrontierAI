import uuid
from dataclasses import dataclass, field
from typing import Any

from app.context.manager import ContextManager
from app.execution.engine import ExecutionEngine
from app.intent.engine import IntentEngine
from app.intent.router import ModelRouter, RoutingDecision
from app.knowledge.retriever import KnowledgeRetriever
from app.memory.base import MemoryStore
from app.memory.retriever import MemoryRetriever
from app.models.gateway import ModelGateway
from app.observability.logger import get_logger, log_event
from app.observability.trace import ExecutionTrace
from app.planner.planner import TaskPlanner, TaskPlan
from app.research.pipeline import ResearchPipeline
from app.specialists.registry import SpecialistRegistry
from app.tools.registry import ToolRegistry
from app.tools.selection.selector import ToolSelection, ToolSelector
from app.verification.engine import VerificationEngine


@dataclass
class TaskContext:
    """Information carried through the orchestration pipeline."""

    user_input: str
    intent: str = "unknown"
    plan: TaskPlan | None = None
    routing: RoutingDecision | None = None
    tool_selection: ToolSelection | None = None
    specialist_response: str | None = None
    research_data: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None
    response: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class MasterOrchestrator:
    """Central coordinator for FrontierAI."""

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
        context_manager: ContextManager | None = None,
        tool_registry: ToolRegistry | None = None,
        tool_selector: ToolSelector | None = None,
        specialist_registry: SpecialistRegistry | None = None,
        knowledge_retriever: KnowledgeRetriever | None = None,
        research_pipeline: ResearchPipeline | None = None,
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
        self.verification_engine = (
            verification_engine
        )
        self.memory_store = memory_store

        self.memory_retriever = (
            memory_retriever or MemoryRetriever()
        )

        self.context_manager = (
            context_manager or ContextManager()
        )

        self.tool_registry = tool_registry

        self.tool_selector = (
            tool_selector
            or ToolSelector(
                tool_registry or ToolRegistry()
            )
        )

        self.specialist_registry = (
            specialist_registry
            or SpecialistRegistry()
        )

        self.knowledge_retriever = (
            knowledge_retriever
        )

        self.research_pipeline = (
            research_pipeline
        )

        self.logger = get_logger(
            "frontierai.orchestrator"
        )

    async def process(
        self,
        user_input: str,
        *,
        conversation_id: str = "default",
    ) -> dict[str, Any]:
        """
        Process a request with a global error boundary.

        Unexpected exceptions are captured, logged, traced,
        and converted into a structured failure response.
        """

        request_id = str(
            uuid.uuid4()
        )

        trace = ExecutionTrace(
            request_id
        )

        log_event(
            self.logger,
            20,
            "request_started",
            request_id=request_id,
            conversation_id=conversation_id,
            component="orchestrator",
        )

        try:
            return await self._process_internal(
                user_input=user_input,
                conversation_id=conversation_id,
                request_id=request_id,
                trace=trace,
            )

        except Exception as exc:
            error_type = type(exc).__name__
            error_message = str(exc)

            trace.add_event(
                "request_failed",
                error_type=error_type,
                error=error_message,
            )

            log_event(
                self.logger,
                40,
                "request_failed",
                request_id=request_id,
                conversation_id=conversation_id,
                component="orchestrator",
                error_type=error_type,
                error=error_message,
                elapsed_ms=round(
                    trace.elapsed_ms(),
                    3,
                ),
            )

            return {
                "request_id": request_id,
                "input": user_input,
                "response": (
                    "I couldn't complete this request "
                    "because an internal processing error occurred."
                ),
                "intent": "unknown",
                "confidence": 0.0,
                "conversation_id": conversation_id,
                "memory_items_available": 0,
                "memory_items_used": 0,
                "knowledge_items_used": 0,
                "routing": {
                    "model_tier": None,
                    "specialist": None,
                    "reasoning_required": False,
                    "complexity": None,
                    "tool_required": False,
                },
                "specialist_response": None,
                "research": None,
                "tool_selection": {
                    "tool_name": None,
                    "reason": None,
                    "confidence": None,
                },
                "plan": [],
                "requires_tools": False,
                "requires_retrieval": False,
                "requires_verification": False,
                "execution": None,
                "verification": None,
                "status": "failed",
                "error": {
                    "type": error_type,
                    "message": error_message,
                },
                "trace": trace.to_dict(),
            }

    async def _process_internal(
        self,
        user_input: str,
        conversation_id: str,
        request_id: str,
        trace: ExecutionTrace,
    ) -> dict[str, Any]:

        context = TaskContext(
            user_input=user_input
        )

        # -------------------------------------------------
        # 1. Retrieve conversation memory
        # -------------------------------------------------
        all_memory = []

        if self.memory_store is not None:
            all_memory = self.memory_store.get_recent(
                limit=50,
                conversation_id=conversation_id,
            )

        trace.add_event(
            "memory_loaded",
            available=len(all_memory),
        )

        # -------------------------------------------------
        # 2. Retrieve relevant memories
        # -------------------------------------------------
        relevant_memory = (
            self.memory_retriever.retrieve(
                user_input,
                all_memory,
                limit=5,
            )
        )

        trace.add_event(
            "memory_retrieved",
            used=len(relevant_memory),
        )

        # -------------------------------------------------
        # 3. Retrieve knowledge
        # -------------------------------------------------
        relevant_knowledge = []

        if self.knowledge_retriever is not None:
            relevant_knowledge = (
                self.knowledge_retriever.search(
                    user_input,
                    limit=5,
                )
            )

        trace.add_event(
            "knowledge_retrieved",
            used=len(relevant_knowledge),
        )

        # -------------------------------------------------
        # 4. Store user message
        # -------------------------------------------------
        if self.memory_store is not None:
            self.memory_store.add(
                "user",
                user_input,
                conversation_id=conversation_id,
            )

        # -------------------------------------------------
        # 5. Understand intent
        # -------------------------------------------------
        intent_result = self.intent_engine.classify(
            user_input
        )

        context.intent = intent_result.intent

        trace.add_event(
            "intent_classified",
            intent=intent_result.intent,
            confidence=intent_result.confidence,
        )

        log_event(
            self.logger,
            20,
            "intent_classified",
            request_id=request_id,
            intent=intent_result.intent,
            confidence=intent_result.confidence,
        )

        # -------------------------------------------------
        # 6. Route task
        # -------------------------------------------------
        context.routing = self.model_router.route(
            intent_result
        )

        trace.add_event(
            "task_routed",
            model_tier=context.routing.model_tier,
            specialist=context.routing.specialist,
            complexity=context.routing.complexity,
            tool_required=context.routing.tool_required,
        )

        log_event(
            self.logger,
            20,
            "task_routed",
            request_id=request_id,
            specialist=context.routing.specialist,
            model_tier=context.routing.model_tier,
            complexity=context.routing.complexity,
        )

        # -------------------------------------------------
        # 7. Create plan
        # -------------------------------------------------
        context.plan = self.task_planner.create_plan(
            intent_result
        )

        trace.add_event(
            "plan_created",
            steps=context.plan.steps,
        )

        # -------------------------------------------------
        # 8. Select tool
        # -------------------------------------------------
        context.tool_selection = (
            self.tool_selector.select(
                intent=context.intent,
                user_input=user_input,
            )
        )

        trace.add_event(
            "tool_selected",
            tool=context.tool_selection.tool_name,
            confidence=context.tool_selection.confidence,
        )

        # -------------------------------------------------
        # 9. Run research pipeline
        # -------------------------------------------------
        if (
            context.routing.specialist == "research"
            and self.research_pipeline is not None
        ):
            try:
                context.research_data = (
                    await self.research_pipeline.research(
                        user_input,
                        search_limit=5,
                        fetch_limit=3,
                    )
                )

                source_count = len(
                    context.research_data.get(
                        "sources",
                        [],
                    )
                )

                citation_count = len(
                    context.research_data.get(
                        "citations",
                        [],
                    )
                )

                trace.add_event(
                    "research_completed",
                    sources=source_count,
                    citations=citation_count,
                )

                log_event(
                    self.logger,
                    20,
                    "research_completed",
                    request_id=request_id,
                    sources=source_count,
                    citations=citation_count,
                    provider=(
                        context.research_data.get(
                            "search_provider"
                        )
                    ),
                )

            except Exception as exc:
                context.research_data = {
                    "query": user_input,
                    "search_provider": "unknown",
                    "search_results": [],
                    "sources": [],
                    "citations": [],
                    "citation_text": "",
                    "error": str(exc),
                }

                trace.add_event(
                    "research_error",
                    error=str(exc),
                )

                log_event(
                    self.logger,
                    40,
                    "research_failed",
                    request_id=request_id,
                    error_type=type(exc).__name__,
                    error=str(exc),
                )

        # -------------------------------------------------
        # 10. Dispatch specialist
        # -------------------------------------------------
        if (
            context.routing.specialist
            in self.specialist_registry.list_specialists()
        ):
            specialist_context = {
                "intent": context.intent,
                "conversation_id": conversation_id,
                "memory": relevant_memory,
                "knowledge": relevant_knowledge,
                "routing": context.routing,
            }

            if context.research_data is not None:
                specialist_context[
                    "research_data"
                ] = context.research_data

            try:
                context.specialist_response = (
                    await self.specialist_registry.handle(
                        context.routing.specialist,
                        user_input,
                        specialist_context,
                    )
                )

                trace.add_event(
                    "specialist_handled",
                    specialist=context.routing.specialist,
                )

                log_event(
                    self.logger,
                    20,
                    "specialist_handled",
                    request_id=request_id,
                    specialist=context.routing.specialist,
                )

            except Exception as exc:
                trace.add_event(
                    "specialist_error",
                    specialist=context.routing.specialist,
                    error=str(exc),
                )

                log_event(
                    self.logger,
                    40,
                    "specialist_failed",
                    request_id=request_id,
                    specialist=context.routing.specialist,
                    error_type=type(exc).__name__,
                    error=str(exc),
                )

        # -------------------------------------------------
        # 11. Execute selected tool
        # -------------------------------------------------
        if (
            context.tool_selection.tool_name is not None
            and self.execution_engine is not None
        ):
            tool_name = (
                context.tool_selection.tool_name
            )

            if tool_name == "calculator":
                expression = self._extract_expression(
                    user_input
                )

                if expression:
                    try:
                        context.execution = (
                            await self.execution_engine.execute_tool(
                                tool_name,
                                expression=expression,
                            )
                        )

                        trace.add_event(
                            "tool_executed",
                            tool=tool_name,
                            status=context.execution.get(
                                "status"
                            ),
                        )

                        log_event(
                            self.logger,
                            20,
                            "tool_executed",
                            request_id=request_id,
                            tool=tool_name,
                            status=context.execution.get(
                                "status"
                            ),
                        )

                    except Exception as exc:
                        context.execution = {
                            "status": "failed",
                            "error": str(exc),
                        }

                        trace.add_event(
                            "tool_error",
                            tool=tool_name,
                            error=str(exc),
                        )

                        log_event(
                            self.logger,
                            40,
                            "tool_failed",
                            request_id=request_id,
                            tool=tool_name,
                            error_type=type(exc).__name__,
                            error=str(exc),
                        )

                    # -------------------------------------------------
                    # 12. Verify calculation
                    # -------------------------------------------------
                    if (
                        context.execution.get(
                            "status"
                        )
                        == "success"
                        and self.verification_engine is not None
                    ):
                        try:
                            verification = (
                                self.verification_engine.verify_calculation(
                                    expression=expression,
                                    actual_result=(
                                        context.execution[
                                            "result"
                                        ]
                                    ),
                                )
                            )

                            context.verification = {
                                "verified": verification.verified,
                                "message": verification.message,
                                "expected": verification.expected,
                                "actual": verification.actual,
                            }

                            trace.add_event(
                                "verification_completed",
                                verified=verification.verified,
                            )

                            log_event(
                                self.logger,
                                20,
                                "verification_completed",
                                request_id=request_id,
                                verified=verification.verified,
                            )

                        except Exception as exc:
                            context.verification = {
                                "verified": False,
                                "message": str(exc),
                                "expected": None,
                                "actual": context.execution.get(
                                    "result"
                                ),
                            }

                            trace.add_event(
                                "verification_error",
                                error=str(exc),
                            )

                            log_event(
                                self.logger,
                                40,
                                "verification_failed",
                                request_id=request_id,
                                error_type=type(exc).__name__,
                                error=str(exc),
                            )

                    if (
                        context.execution.get(
                            "status"
                        )
                        == "success"
                    ):
                        context.response = str(
                            context.execution["result"]
                        )

        # -------------------------------------------------
        # 13. Use specialist response
        # -------------------------------------------------
        if (
            context.response is None
            and context.specialist_response is not None
        ):
            context.response = (
                context.specialist_response
            )

        # -------------------------------------------------
        # 14. Fallback model response
        # -------------------------------------------------
        if context.response is None:
            context_bundle = (
                self.context_manager.build(
                    user_input,
                    relevant_memory=relevant_memory,
                    relevant_knowledge=relevant_knowledge,
                )
            )

            trace.add_event(
                "context_built",
                memory_items=(
                    context_bundle.memory_items_used
                ),
                knowledge_items=(
                    context_bundle.knowledge_items_used
                ),
            )

            try:
                context.response = (
                    await self.model_gateway.generate(
                        context_bundle.messages
                    )
                )

                trace.add_event(
                    "model_response_generated"
                )

                log_event(
                    self.logger,
                    20,
                    "model_response_generated",
                    request_id=request_id,
                )

            except Exception as exc:
                trace.add_event(
                    "model_error",
                    error_type=type(exc).__name__,
                    error=str(exc),
                )

                log_event(
                    self.logger,
                    40,
                    "model_generation_failed",
                    request_id=request_id,
                    error_type=type(exc).__name__,
                    error=str(exc),
                )

                raise

        # -------------------------------------------------
        # 15. Store assistant response
        # -------------------------------------------------
        if (
            self.memory_store is not None
            and context.response is not None
        ):
            self.memory_store.add(
                "assistant",
                context.response,
                conversation_id=conversation_id,
            )

        # -------------------------------------------------
        # 16. Determine status
        # -------------------------------------------------
        verified = (
            context.verification is not None
            and context.verification["verified"]
        )

        if context.execution:
            execution_status = (
                context.execution.get(
                    "status"
                )
            )

            if execution_status == "timeout":
                status = "execution_timeout"

            elif execution_status == "failed":
                status = "tool_failed"

            elif not verified:
                status = "verification_failed"

            else:
                status = "verified"

        else:
            status = "completed"

        trace.add_event(
            "request_completed",
            status=status,
        )

        log_event(
            self.logger,
            20,
            "request_completed",
            request_id=request_id,
            status=status,
            intent=context.intent,
            specialist=(
                context.routing.specialist
                if context.routing
                else None
            ),
            elapsed_ms=round(
                trace.elapsed_ms(),
                3,
            ),
        )

        # -------------------------------------------------
        # 17. Build structured research output
        # -------------------------------------------------
        research_output = None

        if context.research_data is not None:
            research_output = {
                "query": context.research_data.get(
                    "query"
                ),
                "search_provider": (
                    context.research_data.get(
                        "search_provider"
                    )
                ),
                "source_count": len(
                    context.research_data.get(
                        "sources",
                        [],
                    )
                ),
                "citation_count": len(
                    context.research_data.get(
                        "citations",
                        [],
                    )
                ),
                "sources": [
                    {
                        "source_id": source.source_id,
                        "title": source.title,
                        "url": source.url,
                        "fetch_success": source.metadata.get(
                            "fetch_success",
                            False,
                        ),
                    }
                    for source in context.research_data.get(
                        "sources",
                        []
                    )
                ],
                "citations": [
                    {
                        "citation_id": citation.citation_id,
                        "title": citation.title,
                        "url": citation.url,
                    }
                    for citation in context.research_data.get(
                        "citations",
                        []
                    )
                ],
                "citation_text": (
                    context.research_data.get(
                        "citation_text",
                        "",
                    )
                ),
                "error": context.research_data.get(
                    "error"
                ),
            }

        return {
            "request_id": request_id,
            "input": context.user_input,
            "response": context.response,
            "intent": context.intent,
            "confidence": intent_result.confidence,
            "conversation_id": conversation_id,
            "memory_items_available": len(
                all_memory
            ),
            "memory_items_used": len(
                relevant_memory
            ),
            "knowledge_items_used": len(
                relevant_knowledge
            ),
            "routing": {
                "model_tier": (
                    context.routing.model_tier
                ),
                "specialist": (
                    context.routing.specialist
                ),
                "reasoning_required": (
                    context.routing.reasoning_required
                ),
                "complexity": (
                    context.routing.complexity
                ),
                "tool_required": (
                    context.routing.tool_required
                ),
            },
            "specialist_response": (
                context.specialist_response
            ),
            "research": research_output,
            "tool_selection": {
                "tool_name": (
                    context.tool_selection.tool_name
                    if context.tool_selection
                    else None
                ),
                "reason": (
                    context.tool_selection.reason
                    if context.tool_selection
                    else None
                ),
                "confidence": (
                    context.tool_selection.confidence
                    if context.tool_selection
                    else None
                ),
            },
            "plan": (
                context.plan.steps
                if context.plan
                else []
            ),
            "requires_tools": (
                context.plan.requires_tools
                if context.plan
                else False
            ),
            "requires_retrieval": (
                context.plan.requires_retrieval
                if context.plan
                else False
            ),
            "requires_verification": (
                context.plan.requires_verification
                if context.plan
                else False
            ),
            "execution": context.execution,
            "verification": context.verification,
            "status": status,
            "trace": trace.to_dict(),
        }

    def _extract_expression(
        self,
        text: str,
    ) -> str | None:
        expression = text.lower().strip()

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

        if expression and all(
            char in allowed
            for char in expression
        ):
            return expression

        return None