import asyncio

from app.models.gateway import ModelGateway
from app.models.mock import MockProvider
from app.orchestrator.orchestrator import MasterOrchestrator


async def main() -> None:
    gateway = ModelGateway()

    gateway.register_provider(
        "mock",
        MockProvider(),
        default=True,
    )

    orchestrator = MasterOrchestrator(gateway)

    result = await orchestrator.process(
        "Help me debug my Python program"
    )

    print("\nFrontierAI Orchestrator")
    print("=======================")
    print(f"Input: {result['input']}")
    print(f"Intent: {result['intent']}")
    print("Plan:")

    for step in result["plan"]:
        print(f"  → {step}")

    print(f"Status: {result['status']}")


if __name__ == "__main__":
    asyncio.run(main())