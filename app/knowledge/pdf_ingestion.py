from pathlib import Path
from uuid import uuid4

import pymupdf

from app.knowledge.base import KnowledgeDocument
from app.knowledge.chunk_store import SQLiteKnowledgeChunkStore
from app.knowledge.chunker import KnowledgeChunker
from app.knowledge.embeddings import OllamaEmbeddingService
from app.knowledge.sqlite import SQLiteKnowledgeStore
from app.knowledge.vector_store import SQLiteVectorStore


class PDFKnowledgeIngestionService:
    """Extracts PDF text and stores searchable knowledge."""

    def __init__(
        self,
        document_store: SQLiteKnowledgeStore,
        chunk_store: SQLiteKnowledgeChunkStore,
        chunker: KnowledgeChunker | None = None,
        vector_store: SQLiteVectorStore | None = None,
        embedding_service: OllamaEmbeddingService | None = None,
    ) -> None:
        self.document_store = document_store
        self.chunk_store = chunk_store
        self.chunker = chunker or KnowledgeChunker()

        self.vector_store = vector_store
        self.embedding_service = embedding_service

        if (
            self.vector_store is not None
            and self.embedding_service is None
        ):
            raise ValueError(
                "An embedding service is required when "
                "a vector store is configured."
            )

    def ingest_pdf(
        self,
        file_path: str,
        *,
        source: str = "local_pdf",
        metadata: dict | None = None,
    ) -> KnowledgeDocument:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"PDF path is not a file: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "The supplied file must be a PDF."
            )

        text_parts: list[str] = []

        with pymupdf.open(path) as pdf:
            if len(pdf) == 0:
                raise ValueError(
                    "The PDF contains no pages."
                )

            for page_number, page in enumerate(
                pdf,
                start=1,
            ):
                page_text = page.get_text(
                    "text"
                ).strip()

                if page_text:
                    text_parts.append(
                        f"[Page {page_number}]\n"
                        f"{page_text}"
                    )

        content = "\n\n".join(
            text_parts
        ).strip()

        if not content:
            raise ValueError(
                "No extractable text was found in the PDF."
            )

        document = KnowledgeDocument(
            document_id=str(uuid4()),
            title=path.stem,
            content=content,
            source=source,
            metadata=metadata or {},
        )

        document.metadata.setdefault(
            "file_type",
            "pdf",
        )

        self.document_store.add_document(
            document
        )

        chunks = self.chunker.chunk(
            document
        )

        self.chunk_store.delete_document_chunks(
            document.document_id
        )

        self.vector_store_delete(
            document.document_id
        )

        if chunks:
            self.chunk_store.add_chunks(
                chunks
            )

        if (
            chunks
            and self.vector_store is not None
            and self.embedding_service is not None
        ):
            embedded_items = []

            for chunk in chunks:
                embedding = (
                    self.embedding_service.embed(
                        chunk.content
                    )
                )

                embedded_items.append(
                    (
                        chunk,
                        embedding,
                    )
                )

            self.vector_store.add_embeddings(
                embedded_items
            )

        return document

    def vector_store_delete(
        self,
        document_id: str,
    ) -> None:
        if self.vector_store is not None:
            self.vector_store.delete_document_embeddings(
                document_id
            )