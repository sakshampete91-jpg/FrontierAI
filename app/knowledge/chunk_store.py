import json
import sqlite3
from pathlib import Path

from app.knowledge.base import KnowledgeChunk


class SQLiteKnowledgeChunkStore:
    """Persistent storage for searchable knowledge chunks."""

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
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_knowledge_chunks_document
                ON knowledge_chunks(document_id)
                """
            )

            connection.commit()

    def add_chunk(
        self,
        chunk: KnowledgeChunk,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO knowledge_chunks
                (
                    chunk_id,
                    document_id,
                    content,
                    metadata
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    chunk.chunk_id,
                    chunk.document_id,
                    chunk.content,
                    json.dumps(chunk.metadata),
                ),
            )

            connection.commit()

    def add_chunks(
        self,
        chunks: list[KnowledgeChunk],
    ) -> None:
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO knowledge_chunks
                (
                    chunk_id,
                    document_id,
                    content,
                    metadata
                )
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        chunk.chunk_id,
                        chunk.document_id,
                        chunk.content,
                        json.dumps(chunk.metadata),
                    )
                    for chunk in chunks
                ],
            )

            connection.commit()

    def get_chunk(
        self,
        chunk_id: str,
    ) -> KnowledgeChunk:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    content,
                    metadata
                FROM knowledge_chunks
                WHERE chunk_id = ?
                """,
                (chunk_id,),
            ).fetchone()

        if row is None:
            raise ValueError(
                f"Knowledge chunk not found: {chunk_id}"
            )

        return KnowledgeChunk(
            chunk_id=row["chunk_id"],
            document_id=row["document_id"],
            content=row["content"],
            metadata=json.loads(
                row["metadata"]
            ),
        )

    def get_document_chunks(
        self,
        document_id: str,
    ) -> list[KnowledgeChunk]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    content,
                    metadata
                FROM knowledge_chunks
                WHERE document_id = ?
                ORDER BY chunk_id ASC
                """,
                (document_id,),
            ).fetchall()

        return [
            KnowledgeChunk(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                content=row["content"],
                metadata=json.loads(
                    row["metadata"]
                ),
            )
            for row in rows
        ]

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM knowledge_chunks
                """
            ).fetchone()

        return int(row["total"])

    def delete_document_chunks(
        self,
        document_id: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM knowledge_chunks
                WHERE document_id = ?
                """,
                (document_id,),
            )

            connection.commit()

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM knowledge_chunks"
            )

            connection.commit()