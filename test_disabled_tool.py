from app.tools.registry import ToolDefinition, ToolRegistry


def test_disabled_tool():
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="disabled_tool",
            description="Test tool that is disabled.",
            handler=lambda: "should never execute",
            enabled=False,
        )
    )

    try:
        registry.execute("disabled_tool")
        print("ERROR: Disabled tool executed.")
    except RuntimeError as exc:
        print("Disabled tool blocked: OK")
        print(exc)


if __name__ == "__main__":
    test_disabled_tool()