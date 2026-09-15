from typing import Any

from ollama import AsyncClient

from app.core.config import settings
from app.models.base import ModelProvider


class OllamaProvider(ModelProvider):
    """Ollama implementation of the FrontierAI model provider."""

    def __init__(
        self,
        model: str | None = None,
        host: str | None = None,
    ) -> None:
        self.model = model or settings.ollama_model

        self.client = AsyncClient(
            host=host or settings.ollama_host
        )

    async def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        options = dict(
            kwargs.pop(
                "options",
                {}
            )
        )

        # Keep research/general responses concise by default.
        options.setdefault(
            "num_predict",
            256,
        )

        # Small context window is sufficient for our current
        # research prompts and helps CPU inference.
        options.setdefault(
            "num_ctx",
            4096,
        )

        # Slightly deterministic output is better for research.
        options.setdefault(
            "temperature",
            0.2,
        )

        response = await self.client.chat(
            model=self.model,
            messages=messages,
            options=options,
            **kwargs,
        )

        return response["message"]["content"]