import asyncio
from time import perf_counter

from app.core.config import settings
from app.models.ollama import OllamaProvider


async def main():
    print("Starting direct Qwen3 test...")

    provider = OllamaProvider(
        model=settings.ollama_model,
        host=settings.ollama_host,
    )

    messages = [
        {
            "role": "user",
            "content": "Reply with exactly: QWEN3 OK",
        }
    ]

    start = perf_counter()

    print("Calling Ollama...")

    try:
        response = await provider.generate(
            messages
        )

        elapsed = perf_counter() - start

        print("\nResponse:")
        print(response)

        print(
            "\nGeneration time:",
            round(elapsed, 2),
            "seconds",
        )

        if response:
            print(
                "\nDirect Qwen3 test: OK"
            )
        else:
            print(
                "\nDirect Qwen3 test: FAILED"
            )

    except Exception as exc:
        elapsed = perf_counter() - start

        print(
            "\nQwen3 ERROR:",
            type(exc).__name__,
        )

        print(
            "Message:",
            str(exc),
        )

        print(
            "Elapsed:",
            round(elapsed, 2),
            "seconds",
        )


if __name__ == "__main__":
    asyncio.run(main())