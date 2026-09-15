from app.research.evidence import EvidenceSelector


def main():
    selector = EvidenceSelector(
        max_blocks=3,
        max_chars=1000,
    )

    query = (
        "Python programming language "
        "machine learning"
    )

    text = """
    This paragraph talks about cooking recipes
    and kitchen equipment. It is unrelated to
    programming.

    Python is a high-level programming language
    widely used in software development, data
    science, and machine learning.

    The weather forecast predicts rain tomorrow.
    This has nothing to do with Python.

    Python supports machine learning through
    libraries and frameworks used for artificial
    intelligence and data analysis.
    """

    result = selector.select(
        query,
        text,
    )

    print("Selected evidence:")
    print(result)

    print(
        "\nCharacters:",
        len(result),
    )

    if (
        "Python is a high-level programming language"
        in result
        and "machine learning" in result.lower()
        and "weather forecast" not in result
    ):
        print(
            "\nEvidence selector: OK"
        )
    else:
        print(
            "\nEvidence selector: FAILED"
        )


if __name__ == "__main__":
    main()