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
    Coding specialist for CHOKO.

    Compatible with the SpecialistRegistry interface.
    """

    name = "coding"

    def __init__(
        self,
        model_gateway: Any | None = None,
    ) -> None:
        self.model_gateway = model_gateway

    async def handle(
        self,
        user_input: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Handle a coding request through the specialist interface.
        """

        result = self.analyze(user_input)

        return result.response

    def analyze(
        self,
        user_input: str,
    ) -> CodingResult:
        """Analyze a coding request."""

        text = user_input.strip()
        normalized = text.lower()

        language = self._detect_language(
            normalized
        )

        requires_execution = any(
            phrase in normalized
            for phrase in [
                "run this",
                "execute this",
                "test this",
                "run the code",
                "execute the code",
                "run this code",
            ]
        )

        instructions = [
            "Act as CHOKO's coding specialist.",
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
                "The user appears to want code execution or testing. "
                "Only report execution results if an actual execution "
                "tool has been used."
            )

        response = "\n".join(
            f"- {instruction}"
            for instruction in instructions
        )

        return CodingResult(
            response=response,
            language=language,
            requires_execution=requires_execution,
            requires_verification=True,
            metadata={
                "specialist": self.name,
                "input_length": len(text),
                "gateway_available": (
                    self.model_gateway is not None
                ),
            },
        )

    def _detect_language(
        self,
        text: str,
    ) -> str | None:
        """Detect the likely programming language."""

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
                "node",
                "nodejs",
            ],
            "typescript": [
                "typescript",
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
            if any(
                signal in text
                for signal in signals
            ):
                return language

        return None