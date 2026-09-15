from app.knowledge.base import KnowledgeChunk
from app.knowledge.retriever import KnowledgeSearchResult
from app.specialists.context import SpecialistContextBuilder


def main():
    chunk = KnowledgeChunk(
        chunk_id="rag-test-1",
        document_id="rag-doc-1",
        content=(
            "FrontierAI uses a Model Router to select "
            "an appropriate model based on task requirements."
        ),
        metadata={
            "title": "FrontierAI Architecture",
            "source": "local_test",
        },
    )

    result = KnowledgeSearchResult(
        chunk=chunk,
        score=0.92,
    )

    builder = SpecialistContextBuilder()

    messages = builder.build_messages(
        system_instruction=(
            "You are a test specialist."
        ),
        user_input=(
            "How does FrontierAI select a model?"
        ),
        context={
            "knowledge": [result],
            "intent": "general",
        },
    )

    for message in messages:
        print(
            f"\n[{message['role']}]"
        )
        print(
            message["content"]
        )

    combined = "\n".join(
        message["content"]
        for message in messages
    )

    if (
        "Model Router" in combined
        and "task requirements" in combined
        and "local_test" in combined
    ):
        print(
            "\nRAG context injection: OK"
        )
    else:
        print(
            "\nRAG context injection: FAILED"
        )


if __name__ == "__main__":
    main()