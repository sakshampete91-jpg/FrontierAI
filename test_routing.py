from app.intent.engine import IntentEngine
from app.intent.router import ModelRouter


def main():
    intent_engine = IntentEngine()
    router = ModelRouter()

    requests = [
        "Write a Python program to sort numbers",
        "Research the latest AI models",
        "Calculate 25 * 4",
        "Tell me a joke",
    ]

    for text in requests:
        intent = intent_engine.classify(text)
        decision = router.route(intent)

        print("\nRequest:", text)
        print("Intent:", decision.intent)
        print("Model tier:", decision.model_tier)
        print("Specialist:", decision.specialist)
        print("Complexity:", decision.complexity)
        print("Tool required:", decision.tool_required)
        print("Reasoning required:", decision.reasoning_required)


if __name__ == "__main__":
    main()