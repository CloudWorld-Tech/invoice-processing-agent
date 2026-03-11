"""Tests for the tool registry."""
import pytest

from src.tools.registry import ToolDefinition, ToolRegistry


class TestToolRegistry:
    def test_register_and_get(self):
        registry = ToolRegistry()

        async def dummy_handler(**kwargs):
            return "ok"

        registry.register("test_tool", "A test tool", dummy_handler)
        tool = registry.get("test_tool")
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"

    def test_get_missing_raises(self):
        registry = ToolRegistry()
        with pytest.raises(KeyError, match="not found"):
            registry.get("nonexistent")

    def test_list_tools(self):
        registry = ToolRegistry()

        async def h(**kw):
            return None

        registry.register("a", "Tool A", h)
        registry.register("b", "Tool B", h)
        tools = registry.list_tools()
        assert len(tools) == 2

    def test_tool_names(self):
        registry = ToolRegistry()

        async def h(**kw):
            return None

        registry.register("x", "X", h)
        registry.register("y", "Y", h)
        assert registry.tool_names == ["x", "y"]
