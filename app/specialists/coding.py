from dataclasses import dataclass
from typing import Any


@dataclass
class CodingResult:
    """Result produced by the coding specialist."""

    response: str
    language: str | None = None
    requires_execution: bool = False
    requires_verification: bool = True
    metadata: dict[str, Any] | None = None


class CodingSpecialist:
    """
    Handles coding-oriented requests.

    The specialist prepares structured instructions for the model
    and identifies whether the request may require code execution
    or verification.
    """

    def analyze(self, user_input: str) -> CodingResult:
        text = user_input.strip()
        normalized = text.lower()

        language = self._detect_language(normalized)

        requires_execution = any(
            phrase in normalized
            for phrase in [
                "run this",
                "execute this",
                "test this",
                "run the code",
                "execute the code",
            ]
        )

        requires_verification = True

        instructions = [
            "Act as FrontierAI's coding specialist.",
            "Understand the programming task before answering.",
            "Provide correct, runnable code when code is requested.",
            "Prefer simple and maintainable solutions.",
            "Explain important parts briefly.",
            "Do not claim that code was executed unless it was actually executed.",
            "Check syntax and obvious edge cases before responding.",
        ]

        if language:
            instructions.append(
                f"The detected programming language is {language}."
            )

        if requires_execution:
            instructions.append(
                "The user appears to want execution or testing. "
                "Only report execution results if a real execution tool "
                "is available and has actually been used."
            )

        response = "\n".join(
            f"- {instruction}"
            for instruction in instructions
        )

        return CodingResult(
            response=response,
            language=language,
            requires_execution=requires_execution,
            requires_verification=requires_verification,
            metadata={
                "specialist": "coding",
                "input_length": len(text),
            },
        )

    def _detect_language(self, text: str) -> str | None:
        language_signals = {
            "python": [
                "python",
                ".py",
                "pip",
                "django",
                "flask",
                "fastapi",
            ],
            "javascript": [
                "javascript",
                "js",
                "node",
                "nodejs",
            ],
            "typescript": [
                "typescript",
                "ts",
            ],
            "html": [
                "html",
                "webpage",
            ],
            "css": [
                "css",
                "stylesheet",
            ],
            "java": [
                "java",
                "spring boot",
            ],
            "cpp": [
                "c++",
                "cpp",
            ],
            "c": [
                "c language",
                "c programming",
            ],
        }

        for language, signals in language_signals.items():
            if any(signal in text for signal in signals):
                return language

        return None