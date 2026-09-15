from abc import ABC, abstractmethod
from typing import Any


class ModelProvider(ABC):
    """Base interface for every AI model provider."""

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Generate a response from the model."""
        raise NotImplementedError