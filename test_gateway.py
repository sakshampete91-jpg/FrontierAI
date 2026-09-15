import asyncio

from app.models.gateway import ModelGateway
from app.models.mock import MockProvider


async def main() -> None:
    gateway = ModelGateway()

    gateway.register_provider(
        "mock",
        MockProvider(),
        default=True,
    )

    response = await gateway.generate(
        [
            {
                "role": "user",
                "content": "Hello FrontierAI",
            }
        ]
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())