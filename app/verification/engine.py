from dataclasses import dataclass
from typing import Any

from app.tools.calculator import calculate


@dataclass
class VerificationResult:
    """Result produced by the verification engine."""

    verified: bool
    message: str
    expected: Any = None
    actual: Any = None


class VerificationEngine:
    """Independently verifies execution results."""

    def verify_calculation(
        self,
        expression: str,
        actual_result: Any,
    ) -> VerificationResult:
        try:
            expected_result = calculate(expression)

            verified = expected_result == actual_result

            if verified:
                return VerificationResult(
                    verified=True,
                    message="Calculation verified successfully.",
                    expected=expected_result,
                    actual=actual_result,
                )

            return VerificationResult(
                verified=False,
                message="Calculation result does not match verification.",
                expected=expected_result,
                actual=actual_result,
            )

        except Exception as exc:
            return VerificationResult(
                verified=False,
                message=f"Verification failed: {exc}",
                actual=actual_result,
            )