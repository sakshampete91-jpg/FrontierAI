from app.tools.registry import ToolDefinition, ToolRegistry


def test_permission_required():
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="protected_tool",
            description="Test tool requiring permission.",
            handler=lambda: "secret result",
            requires_permission=True,
        )
    )

    try:
        registry.execute("protected_tool")
        print("ERROR: Permission check failed.")
    except PermissionError as exc:
        print("Permission blocked: OK")
        print(exc)

    result = registry.execute(
        "protected_tool",
        permission_granted=True,
    )

    print("Permission granted result:", result)


if __name__ == "__main__":
    test_permission_required()