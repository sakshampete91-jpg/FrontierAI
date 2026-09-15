from typing import Any

from app.models.base import ModelProvider


class MockProvider(ModelProvider):
    """Temporary provider used for local architecture testing."""

    async def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        last_message = messages[-1]["content"]

        return f"Mock response received: {last_message}"