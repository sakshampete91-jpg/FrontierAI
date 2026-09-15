import json
import urllib.error
import urllib.request


class OllamaEmbeddingService:
    """Creates text embeddings using a local Ollama embedding model."""

    def __init__(
        self,
        *,
        model: str = "nomic-embed-text",
        host: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.host = host.rstrip("/")

    def embed(
        self,
        text: str,
    ) -> list[float]:
        text = text.strip()

        if not text:
            raise ValueError(
                "Cannot create an embedding for empty text."
            )

        payload = json.dumps(
            {
                "model": self.model,
                "prompt": text,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{self.host}/api/embeddings",
            data=payload,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=60,
            ) as response:
                raw = response.read().decode(
                    "utf-8"
                )

        except urllib.error.URLError as exc:
            raise ConnectionError(
                "Failed to connect to Ollama embedding service."
            ) from exc

        data = json.loads(raw)

        embedding = data.get("embedding")

        if not isinstance(
            embedding,
            list,
        ):
            raise ValueError(
                "Ollama returned an invalid embedding."
            )

        if not embedding:
            raise ValueError(
                "Ollama returned an empty embedding."
            )

        return [
            float(value)
            for value in embedding
        ]