from typing import Any

from openai import AsyncOpenAI

from app.models.base import ModelProvider


class OpenAIProvider(ModelProvider):
    """OpenAI implementation of the FrontierAI model provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5",
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI API key is required.")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        response = await self.client.responses.create(
            model=self.model,
            input=messages,
            **kwargs,
        )

        return response.output_text