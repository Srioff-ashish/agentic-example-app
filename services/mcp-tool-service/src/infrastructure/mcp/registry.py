"""MCP Tool Registry and Discovery"""
from __future__ import annotations

from typing import Any, Callable, Awaitable
from pydantic import BaseModel


class MCPTool(BaseModel):
    """MCP Tool definition"""

    name: str
    description: str
    parameters: dict[str, Any]
    category: str
    handler: str  # Handler function name


class MCPToolRegistry:
    """Registry for MCP tools"""

    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}
        self._handlers: dict[str, Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]] = {}

    def register_tool(
        self,
        tool: MCPTool,
        handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
    ) -> None:
        """Register a tool with its handler"""
        self._tools[tool.name] = tool
        self._handlers[tool.name] = handler

    def get_tool(self, name: str) -> MCPTool | None:
        """Get a tool by name"""
        return self._tools.get(name)

    def list_tools(self, category: str | None = None) -> list[MCPTool]:
        """List all tools, optionally filtered by category"""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools

    async def execute_tool(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool"""
        if name not in self._handlers:
            raise ValueError(f"Tool not found: {name}")
        
        handler = self._handlers[name]
        return await handler(params)


# Global registry
tool_registry = MCPToolRegistry()
