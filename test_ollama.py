import asyncio

from app.models.ollama import OllamaProvider


async def main() -> None:
    provider = OllamaProvider(
        model="qwen3:8b",
    )

    response = await provider.generate(
        [
            {
                "role": "user",
                "content": (
                    "Reply with exactly: "
                    "FrontierAI local model connected."
                ),
            }
        ]
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())