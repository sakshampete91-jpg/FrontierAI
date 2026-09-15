from app.knowledge.embeddings import OllamaEmbeddingService


def main():
    service = OllamaEmbeddingService()

    text = (
        "FrontierAI uses model routing to select "
        "an appropriate processing path."
    )

    print("Generating embedding...")

    embedding = service.embed(text)

    print("Embedding dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])

    if embedding:
        print("\nEmbedding generation: OK")
    else:
        print("\nEmbedding generation: FAILED")


if __name__ == "__main__":
    main()