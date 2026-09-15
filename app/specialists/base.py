from abc import ABC, abstractmethod
from typing import Any


class Specialist(ABC):
    """Base interface for FrontierAI specialist components."""

    name: str

    @abstractmethod
    async def handle(
        self,
        user_input: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request assigned to this specialist."""
        raise NotImplementedError