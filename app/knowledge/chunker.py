from app.knowledge.base import KnowledgeChunk, KnowledgeDocument


class KnowledgeChunker:
    """Splits knowledge documents into manageable chunks."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if overlap < 0:
            raise ValueError(
                "overlap cannot be negative."
            )

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self,
        document: KnowledgeDocument,
    ) -> list[KnowledgeChunk]:
        text = document.content.strip()

        if not text:
            return []

        chunks: list[KnowledgeChunk] = []

        start = 0
        chunk_number = 1

        while start < len(text):
            end = min(
                start + self.chunk_size,
                len(text),
            )

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    KnowledgeChunk(
                        chunk_id=(
                            f"{document.document_id}"
                            f"-chunk-{chunk_number}"
                        ),
                        document_id=document.document_id,
                        content=chunk_text,
                        metadata={
                            "source": document.source,
                            "title": document.title,
                            "chunk_number": chunk_number,
                        },
                    )
                )

            if end >= len(text):
                break

            start = end - self.overlap
            chunk_number += 1

        return chunks