from datetime import datetime, timezone

from app.memory.base import MemoryItem, MemoryStore


class InMemoryConversationStore(MemoryStore):
    """Simple conversation memory stored in application memory."""

    def __init__(self) -> None:
        self._memories: list[MemoryItem] = []

    def add(
        self,
        role: str,
        content: str,
        *,
        metadata: dict | None = None,
    ) -> MemoryItem:
        item = MemoryItem(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
        )

        self._memories.append(item)
        return item

    def get_recent(self, limit: int = 10) -> list[MemoryItem]:
        if limit <= 0:
            return []

        return self._memories[-limit:]

    def clear(self) -> None:
        self._memories.clear()