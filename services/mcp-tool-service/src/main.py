"""MCP Tool Service Main Application"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

from .infrastructure.a2a.protocol import (
    AgentCapability,
    AgentInfo,
    AgentType,
    HandshakeRequest,
    JSONRPCRequest,
    TaskRequest,
    TaskResponse,
    JSONRPCResponse,
)
from .infrastructure.config.settings import settings
from .infrastructure.mcp.registry import MCPTool, tool_registry
from .application.tools import supply_chain_tools

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifecycle manager"""
    # Startup
    logger.info("Starting MCP Tool Service...")
    
    # Register tools
    register_tools()
    
    # Register with orchestrator
    await register_with_orchestrator()
    
    yield
    
    # Shutdown
    logger.info("Shutting down MCP Tool Service...")


def register_tools() -> None:
    """Register all available tools"""
    tools = [
        (
            MCPTool(
                name="calculate_shipping_cost",
                description="Calculate shipping cost based on weight, distance, and priority",
                parameters={
                    "weight_kg": "number",
                    "distance_km": "number",
                    "priority": "string (standard|express|overnight)",
                },
                category="logistics",
                handler="calculate_shipping_cost",
            ),
            supply_chain_tools.calculate_shipping_cost,
        ),
        (
            MCPTool(
                name="estimate_delivery_time",
                description="Estimate delivery time based on distance and priority",
                parameters={
                    "distance_km": "number",
                    "priority": "string (standard|express|overnight)",
                },
                category="logistics",
                handler="estimate_delivery_time",
            ),
            supply_chain_tools.estimate_delivery_time,
        ),
        (
            MCPTool(
                name="validate_customs_documentation",
                description="Validate customs documentation for international shipments",
                parameters={"documents": "array of strings"},
                category="compliance",
                handler="validate_customs_documentation",
            ),
            supply_chain_tools.validate_customs_documentation,
        ),
        (
            MCPTool(
                name="check_compliance_status",
                description="Check compliance status for a shipment",
                parameters={
                    "shipment_type": "string",
                    "destination_country": "string",
                },
                category="compliance",
                handler="check_compliance_status",
            ),
            supply_chain_tools.check_compliance_status,
        ),
        (
            MCPTool(
                name="optimize_route",
                description="Optimize delivery route for multiple stops",
                parameters={"stops": "array of locations"},
                category="logistics",
                handler="optimize_route",
            ),
            supply_chain_tools.optimize_route,
        ),
        (
            MCPTool(
                name="track_shipment",
                description="Track shipment location and status",
                parameters={"tracking_number": "string"},
                category="logistics",
                handler="track_shipment",
            ),
            supply_chain_tools.track_shipment,
        ),
    ]
    
    for tool, handler in tools:
        tool_registry.register_tool(tool, handler)
    
    logger.info(f"Registered {len(tools)} tools")


async def register_with_orchestrator() -> None:
    """Register this service with the orchestrator"""
    try:
        # Create capabilities from registered tools
        capabilities = [
            AgentCapability(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters,
            )
            for tool in tool_registry.list_tools()
        ]
        
        agent_info = AgentInfo(
            agent_id=settings.agent_id,
            agent_type=AgentType.MCP_TOOL,
            name=settings.service_name,
            version=settings.service_version,
            capabilities=capabilities,
            endpoint=f"http://{settings.host}:{settings.port}",
        )
        
        request = JSONRPCRequest[HandshakeRequest](
            method="handshake",
            params=HandshakeRequest(agent_info=agent_info),
        )
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.orchestrator_url}/a2a/handshake",
                json=request.model_dump(),
            )
            response.raise_for_status()
            logger.info("Successfully registered with orchestrator")
    except Exception as e:
        logger.error(f"Failed to register with orchestrator: {e}")


app = FastAPI(
    title="Supply Chain MCP Tool Service",
    version=settings.service_version,
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"service": settings.service_name, "version": settings.service_version}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check"""
    return {"status": "healthy"}


@app.get("/tools")
async def list_tools(category: str | None = None) -> dict[str, list[dict[str, Any]]]:
    """List available tools"""
    tools = tool_registry.list_tools(category=category)
    return {"tools": [tool.model_dump() for tool in tools]}


class ToolExecutionRequest(BaseModel):
    """Tool execution request"""

    tool_name: str
    parameters: dict[str, Any]


@app.post("/tools/execute")
async def execute_tool(request: ToolExecutionRequest) -> dict[str, Any]:
    """Execute a tool"""
    try:
        result = await tool_registry.execute_tool(request.tool_name, request.parameters)
        return {"result": result, "status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/a2a/task")
async def handle_task(request: JSONRPCRequest[TaskRequest]) -> JSONRPCResponse[TaskResponse]:
    """Handle task requests from other agents"""
    try:
        logger.info(f"Received task: {request.params.task_type}")
        
        if request.params.task_type == "execute_tool":
            tool_name = request.params.payload.get("tool_name", "")
            parameters = request.params.payload.get("parameters", {})
            
            result = await tool_registry.execute_tool(tool_name, parameters)
            
            response = TaskResponse(
                task_type=request.params.task_type,
                result={"tool_result": result},
                status="completed",
                correlation_id=request.params.correlation_id,
            )
        elif request.params.task_type == "list_tools":
            category = request.params.payload.get("category")
            tools = tool_registry.list_tools(category=category)
            
            response = TaskResponse(
                task_type=request.params.task_type,
                result={"tools": [t.model_dump() for t in tools]},
                status="completed",
                correlation_id=request.params.correlation_id,
            )
        else:
            response = TaskResponse(
                task_type=request.params.task_type,
                result={"error": "Unknown task type"},
                status="failed",
                correlation_id=request.params.correlation_id,
            )
        
        return JSONRPCResponse[TaskResponse](result=response, id=request.id)
    except Exception as e:
        logger.error(f"Task error: {e}")
        from .infrastructure.a2a.protocol import A2AError
        return JSONRPCResponse[TaskResponse](
            error=A2AError(code=-32000, message=str(e)),
            id=request.id,
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
