from typing import Any

from app.models.base import ModelProvider


class ModelGateway:
    """
    Central entry point for AI model calls.

    The rest of FrontierAI should communicate with models
    through this gateway rather than calling providers directly.
    """

    def __init__(self) -> None:
        self._providers: dict[str, ModelProvider] = {}
        self._default_provider: str | None = None

    def register_provider(
        self,
        name: str,
        provider: ModelProvider,
        *,
        default: bool = False,
    ) -> None:
        if name in self._providers:
            raise ValueError(f"Provider already registered: {name}")

        self._providers[name] = provider

        if default or self._default_provider is None:
            self._default_provider = name

    def get_provider(self, name: str | None = None) -> ModelProvider:
        provider_name = name or self._default_provider

        if provider_name is None:
            raise RuntimeError("No model provider has been registered.")

        provider = self._providers.get(provider_name)

        if provider is None:
            raise ValueError(f"Unknown model provider: {provider_name}")

        return provider

    async def generate(
        self,
        messages: list[dict[str, str]],
        *,
        provider: str | None = None,
        **kwargs: Any,
    ) -> str:
        model_provider = self.get_provider(provider)

        return await model_provider.generate(
            messages,
            **kwargs,
        )