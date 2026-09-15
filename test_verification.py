from app.verification.engine import VerificationEngine


engine = VerificationEngine()

result = engine.verify_calculation(
    expression="25 * 18",
    actual_result=450,
)

print(result)