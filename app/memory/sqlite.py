import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.memory.base import MemoryItem, MemoryStore


class SQLiteConversationStore(MemoryStore):
    """Persistent conversation memory backed by SQLite."""

    def __init__(
        self,
        database_path: str = "data/frontier_memory.db",
    ) -> None:
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL DEFAULT 'default',
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )

            columns = connection.execute(
                "PRAGMA table_info(memories)"
            ).fetchall()

            column_names = {column["name"] for column in columns}

            if "conversation_id" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE memories
                    ADD COLUMN conversation_id
                    TEXT NOT NULL DEFAULT 'default'
                    """
                )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_memories_conversation
                ON memories(conversation_id, id)
                """
            )

            connection.commit()

    def add(
        self,
        role: str,
        content: str,
        *,
        conversation_id: str = "default",
        metadata: dict | None = None,
    ) -> MemoryItem:
        timestamp = datetime.now(timezone.utc)

        item = MemoryItem(
            role=role,
            content=content,
            timestamp=timestamp,
            metadata=metadata or {},
            conversation_id=conversation_id,
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories
                (
                    conversation_id,
                    role,
                    content,
                    timestamp,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    item.conversation_id,
                    item.role,
                    item.content,
                    item.timestamp.isoformat(),
                    json.dumps(item.metadata),
                ),
            )

            connection.commit()

        return item

    def get_recent(
        self,
        limit: int = 10,
        *,
        conversation_id: str = "default",
    ) -> list[MemoryItem]:
        if limit <= 0:
            return []

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    conversation_id,
                    role,
                    content,
                    timestamp,
                    metadata
                FROM memories
                WHERE conversation_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    conversation_id,
                    limit,
                ),
            ).fetchall()

        memories = []

        for row in reversed(rows):
            memories.append(
                MemoryItem(
                    role=row["role"],
                    content=row["content"],
                    timestamp=datetime.fromisoformat(
                        row["timestamp"]
                    ),
                    metadata=json.loads(row["metadata"]),
                    conversation_id=row["conversation_id"],
                )
            )

        return memories

    def clear(
        self,
        *,
        conversation_id: str | None = None,
    ) -> None:
        with self._connect() as connection:
            if conversation_id is None:
                connection.execute(
                    "DELETE FROM memories"
                )
            else:
                connection.execute(
                    """
                    DELETE FROM memories
                    WHERE conversation_id = ?
                    """,
                    (conversation_id,),
                )

            connection.commit()