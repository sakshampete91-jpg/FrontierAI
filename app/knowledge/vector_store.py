import json
import math
import sqlite3
from pathlib import Path

from app.knowledge.base import KnowledgeChunk


class SQLiteVectorStore:
    """Persistent SQLite storage for knowledge chunk embeddings."""

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
                CREATE TABLE IF NOT EXISTS knowledge_embeddings (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_knowledge_embeddings_document
                ON knowledge_embeddings(document_id)
                """
            )

            connection.commit()

    def add_embedding(
        self,
        chunk: KnowledgeChunk,
        embedding: list[float],
    ) -> None:
        if not embedding:
            raise ValueError(
                "Embedding cannot be empty."
            )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO knowledge_embeddings
                (
                    chunk_id,
                    document_id,
                    content,
                    metadata,
                    embedding
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    chunk.chunk_id,
                    chunk.document_id,
                    chunk.content,
                    json.dumps(chunk.metadata),
                    json.dumps(embedding),
                ),
            )

            connection.commit()

    def add_embeddings(
        self,
        items: list[
            tuple[KnowledgeChunk, list[float]]
        ],
    ) -> None:
        if not items:
            return

        with self._connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO knowledge_embeddings
                (
                    chunk_id,
                    document_id,
                    content,
                    metadata,
                    embedding
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.chunk_id,
                        chunk.document_id,
                        chunk.content,
                        json.dumps(chunk.metadata),
                        json.dumps(embedding),
                    )
                    for chunk, embedding in items
                ],
            )

            connection.commit()

    def get_embedding(
        self,
        chunk_id: str,
    ) -> tuple[KnowledgeChunk, list[float]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    content,
                    metadata,
                    embedding
                FROM knowledge_embeddings
                WHERE chunk_id = ?
                """,
                (chunk_id,),
            ).fetchone()

        if row is None:
            raise ValueError(
                f"Embedding not found: {chunk_id}"
            )

        chunk = KnowledgeChunk(
            chunk_id=row["chunk_id"],
            document_id=row["document_id"],
            content=row["content"],
            metadata=json.loads(
                row["metadata"]
            ),
        )

        embedding = [
            float(value)
            for value in json.loads(
                row["embedding"]
            )
        ]

        return chunk, embedding

    def list_embeddings(
        self,
    ) -> list[
        tuple[KnowledgeChunk, list[float]]
    ]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    content,
                    metadata,
                    embedding
                FROM knowledge_embeddings
                ORDER BY chunk_id ASC
                """
            ).fetchall()

        results = []

        for row in rows:
            chunk = KnowledgeChunk(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                content=row["content"],
                metadata=json.loads(
                    row["metadata"]
                ),
            )

            embedding = [
                float(value)
                for value in json.loads(
                    row["embedding"]
                )
            ]

            results.append(
                (
                    chunk,
                    embedding,
                )
            )

        return results

    def delete_document_embeddings(
        self,
        document_id: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM knowledge_embeddings
                WHERE document_id = ?
                """,
                (document_id,),
            )

            connection.commit()

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM knowledge_embeddings
                """
            ).fetchone()

        return int(row["total"])

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM knowledge_embeddings"
            )

            connection.commit()


def cosine_similarity(
    first: list[float],
    second: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if not first or not second:
        return 0.0

    if len(first) != len(second):
        raise ValueError(
            "Embedding dimensions do not match."
        )

    dot_product = sum(
        a * b
        for a, b in zip(first, second)
    )

    first_norm = math.sqrt(
        sum(a * a for a in first)
    )

    second_norm = math.sqrt(
        sum(b * b for b in second)
    )

    if first_norm == 0 or second_norm == 0:
        return 0.0

    return (
        dot_product
        / (first_norm * second_norm)
    )