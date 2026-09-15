import json
import sqlite3
from pathlib import Path

from app.knowledge.base import KnowledgeDocument, KnowledgeStore


class SQLiteKnowledgeStore(KnowledgeStore):
    """Persistent knowledge storage backed by SQLite."""

    def __init__(
        self,
        database_path: str = "data/frontier_knowledge.db",
    ) -> None:
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path
        )
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

    def add_document(
        self,
        document: KnowledgeDocument,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO documents
                (
                    document_id,
                    title,
                    content,
                    source,
                    metadata,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    document.document_id,
                    document.title,
                    document.content,
                    document.source,
                    json.dumps(document.metadata),
                    document.created_at.isoformat(),
                ),
            )

            connection.commit()

    def get_document(
        self,
        document_id: str,
    ) -> KnowledgeDocument:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    document_id,
                    title,
                    content,
                    source,
                    metadata,
                    created_at
                FROM documents
                WHERE document_id = ?
                """,
                (document_id,),
            ).fetchone()

        if row is None:
            raise ValueError(
                f"Knowledge document not found: {document_id}"
            )

        from datetime import datetime

        return KnowledgeDocument(
            document_id=row["document_id"],
            title=row["title"],
            content=row["content"],
            source=row["source"],
            metadata=json.loads(row["metadata"]),
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
        )

    def list_documents(
        self,
    ) -> list[KnowledgeDocument]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    document_id,
                    title,
                    content,
                    source,
                    metadata,
                    created_at
                FROM documents
                ORDER BY created_at ASC
                """
            ).fetchall()

        from datetime import datetime

        return [
            KnowledgeDocument(
                document_id=row["document_id"],
                title=row["title"],
                content=row["content"],
                source=row["source"],
                metadata=json.loads(row["metadata"]),
                created_at=datetime.fromisoformat(
                    row["created_at"]
                ),
            )
            for row in rows
        ]

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM documents"
            )
            connection.commit()