from app.execution.engine import ExecutionEngine
from app.models.gateway import ModelGateway
from app.models.mock import MockProvider
from app.orchestrator.orchestrator import MasterOrchestrator
from app.tools.calculator import calculate
from app.tools.registry import ToolDefinition, ToolRegistry


def create_orchestrator() -> MasterOrchestrator:
    """Create and configure FrontierAI's core dependencies."""

    # Model system
    gateway = ModelGateway()

    gateway.register_provider(
        "mock",
        MockProvider(),
        default=True,
    )

    # Tool system
    tool_registry = ToolRegistry()

    tool_registry.register(
        ToolDefinition(
            name="calculator",
            description="Safely performs basic mathematical calculations.",
            handler=calculate,
        )
    )

    execution_engine = ExecutionEngine(tool_registry)

    # Orchestrator
    return MasterOrchestrator(
        gateway,
        execution_engine=execution_engine,
    )