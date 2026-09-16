from typing import Any

from app.core.config import settings
from app.models.base import ModelProvider


class OllamaProvider(ModelProvider):
    """
    CHOKO AI provider.

    AI_PROVIDER=gemini
        Uses Google Gemini.

    AI_PROVIDER=ollama
        Uses local Ollama / Qwen3.
    """

    def __init__(
        self,
        model: str | None = None,
        host: str | None = None,
    ) -> None:
        self.model = model
        self.host = host

        self.provider = settings.ai_provider.strip().lower()

        self._ollama_client = None
        self._gemini_client = None

    async def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:

        if self.provider == "gemini":
            return await self._generate_gemini(
                messages,
                **kwargs,
            )

        if self.provider == "ollama":
            return await self._generate_ollama(
                messages,
                **kwargs,
            )

        raise RuntimeError(
            f"Unsupported AI_PROVIDER: {self.provider}"
        )

    async def _generate_gemini(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:

        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        from google import genai

        if self._gemini_client is None:
            self._gemini_client = genai.Client(
                api_key=settings.gemini_api_key
            )

        system_instruction = None
        interaction_input: list[dict[str, Any]] = []

        for message in messages:

            role = message.get("role", "user")
            content = str(message.get("content", ""))

            if not content.strip():
                continue

            if role == "system":

                if system_instruction is None:
                    system_instruction = content
                else:
                    system_instruction += (
                        "\n\n" + content
                    )

            elif role == "assistant":

                interaction_input.append(
                    {
                        "type": "model_output",
                        "content": [
                            {
                                "type": "text",
                                "text": content,
                            }
                        ],
                    }
                )

            else:

                interaction_input.append(
                    {
                        "type": "user_input",
                        "content": [
                            {
                                "type": "text",
                                "text": content,
                            }
                        ],
                    }
                )

        # IMPORTANT:
        # Gemini mode ALWAYS uses the Gemini model.
        # Never use self.model here because that could
        # accidentally contain the Ollama model qwen3:8b.

        gemini_model = settings.gemini_model.strip()

        if not gemini_model.startswith("gemini-"):
            raise RuntimeError(
                f"Invalid GEMINI_MODEL: {gemini_model}"
            )

        create_args: dict[str, Any] = {
            "model": gemini_model,
            "input": interaction_input,
        }

        if system_instruction:
            create_args["system_instruction"] = system_instruction

        interaction = await self._gemini_client.aio.interactions.create(
            **create_args
        )

        text = interaction.output_text

        if not text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text

    async def _generate_ollama(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:

        from ollama import AsyncClient

        if self._ollama_client is None:
            self._ollama_client = AsyncClient(
                host=self.host or settings.ollama_host
            )

        ollama_model = (
            self.model
            or settings.ollama_model
        )

        response = await self._ollama_client.chat(
            model=ollama_model,
            messages=messages,
            **kwargs,
        )

        return response["message"]["content"]