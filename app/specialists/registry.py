from typing import Any

from app.specialists.base import Specialist


class SpecialistRegistry:
    """Stores and retrieves FrontierAI specialists."""

    def __init__(self) -> None:
        self._specialists: dict[str, Specialist] = {}

    def register(
        self,
        specialist: Specialist,
    ) -> None:
        if specialist.name in self._specialists:
            raise ValueError(
                f"Specialist already registered: {specialist.name}"
            )

        self._specialists[specialist.name] = specialist

    def get(
        self,
        name: str,
    ) -> Specialist:
        specialist = self._specialists.get(name)

        if specialist is None:
            raise ValueError(
                f"Unknown specialist: {name}"
            )

        return specialist

    def list_specialists(self) -> list[str]:
        return list(self._specialists.keys())

    async def handle(
        self,
        name: str,
        user_input: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        specialist = self.get(name)

        return await specialist.handle(
            user_input,
            context,
        )