"""Main Orchestrator Service Application"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.a2a.discovery import A2ADiscoveryService
from .infrastructure.a2a.protocol import (
    AgentCapability,
    AgentInfo,
    AgentType,
    DiscoverRequest,
    DiscoverResponse,
    HandshakeRequest,
    HandshakeResponse,
    JSONRPCRequest,
    JSONRPCResponse,
    TaskRequest,
    TaskResponse,
)
from .infrastructure.config.settings import settings
from .infrastructure.websocket.manager import manager
from .domain.models.supply_chain import (
    Shipment,
    ShipmentStatus,
    ComplianceCheck,
    ComplianceStatus,
    Location,
)

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Global discovery service
discovery_service = A2ADiscoveryService()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifecycle manager for the application"""
    # Startup
    logger.info("Starting Orchestrator Service...")
    
    # Register self
    orchestrator_info = AgentInfo(
        agent_id=settings.agent_id,
        agent_type=AgentType.ORCHESTRATOR,
        name=settings.service_name,
        version=settings.service_version,
        capabilities=[
            AgentCapability(
                name="orchestrate_shipment",
                description="Orchestrate shipment logistics and compliance",
                parameters={"shipment_id": "string"},
            ),
            AgentCapability(
                name="coordinate_agents",
                description="Coordinate between logistics and compliance agents",
            ),
        ],
        endpoint=f"http://{settings.host}:{settings.port}",
    )
    await discovery_service.register_agent(orchestrator_info)
    
    logger.info(f"Orchestrator registered: {orchestrator_info.agent_id}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Orchestrator Service...")
    await discovery_service.unregister_agent(settings.agent_id)


app = FastAPI(
    title="Supply Chain Orchestrator",
    version=settings.service_version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"service": settings.service_name, "version": settings.service_version}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


# A2A Protocol Endpoints
@app.post("/a2a/handshake")
async def handshake(request: JSONRPCRequest[HandshakeRequest]) -> JSONRPCResponse[HandshakeResponse]:
    """Handle A2A handshake requests"""
    try:
        logger.info(f"Received handshake from {request.params.agent_info.agent_id}")
        
        # Get orchestrator info
        orchestrator_info = AgentInfo(
            agent_id=settings.agent_id,
            agent_type=AgentType.ORCHESTRATOR,
            name=settings.service_name,
            version=settings.service_version,
            capabilities=[],
            endpoint=f"http://{settings.host}:{settings.port}",
        )
        
        response = await discovery_service.accept_handshake(
            request.params, orchestrator_info
        )
        
        # Broadcast handshake event
        await manager.broadcast_event("agent_connected", {
            "agent_id": request.params.agent_info.agent_id,
            "agent_type": request.params.agent_info.agent_type,
            "session_id": response.session_id,
        })
        
        return JSONRPCResponse[HandshakeResponse](
            result=response,
            id=request.id,
        )
    except Exception as e:
        logger.error(f"Handshake error: {e}")
        from .infrastructure.a2a.protocol import A2AError
        return JSONRPCResponse[HandshakeResponse](
            error=A2AError(code=-32000, message=str(e)),
            id=request.id,
        )


@app.post("/a2a/discover")
async def discover(request: JSONRPCRequest[DiscoverRequest]) -> JSONRPCResponse[DiscoverResponse]:
    """Handle agent discovery requests"""
    try:
        agents = await discovery_service.discover_agents(
            agent_type=request.params.agent_type,
            capability=request.params.capability,
        )
        
        response = DiscoverResponse(agents=agents)
        return JSONRPCResponse[DiscoverResponse](
            result=response,
            id=request.id,
        )
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        from .infrastructure.a2a.protocol import A2AError
        return JSONRPCResponse[DiscoverResponse](
            error=A2AError(code=-32000, message=str(e)),
            id=request.id,
        )


@app.post("/a2a/task")
async def handle_task(request: JSONRPCRequest[TaskRequest]) -> JSONRPCResponse[TaskResponse]:
    """Handle task requests from other agents"""
    try:
        logger.info(f"Received task: {request.params.task_type}")
        
        # Process task based on type
        result = {"status": "processed", "message": "Task completed"}
        
        response = TaskResponse(
            task_type=request.params.task_type,
            result=result,
            status="completed",
            correlation_id=request.params.correlation_id,
        )
        
        return JSONRPCResponse[TaskResponse](
            result=response,
            id=request.id,
        )
    except Exception as e:
        logger.error(f"Task error: {e}")
        from .infrastructure.a2a.protocol import A2AError
        return JSONRPCResponse[TaskResponse](
            error=A2AError(code=-32000, message=str(e)),
            id=request.id,
        )


# Supply Chain Endpoints
@app.post("/shipments")
async def create_shipment(shipment: Shipment) -> dict[str, Any]:
    """Create a new shipment"""
    logger.info(f"Creating shipment: {shipment.tracking_number}")
    
    # Broadcast shipment created event
    await manager.broadcast_event("shipment_created", {
        "shipment_id": str(shipment.id),
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
    })
    
    return {"shipment": shipment.model_dump(mode="json")}


@app.get("/shipments/{shipment_id}")
async def get_shipment(shipment_id: str) -> dict[str, Any]:
    """Get shipment details"""
    # Mock response for demo
    return {"shipment_id": shipment_id, "status": "pending"}


@app.get("/agents")
async def list_agents() -> dict[str, list[dict[str, Any]]]:
    """List all registered agents"""
    agents = discovery_service.get_all_agents()
    return {"agents": [agent.model_dump() for agent in agents]}


@app.post("/orchestrate")
async def orchestrate_shipment(shipment: Shipment) -> dict[str, Any]:
    """Orchestrate a shipment through logistics and compliance agents"""
    from .domain.services.logistics_agent import LogisticsAgent
    from .domain.services.compliance_agent import ComplianceAgent
    from .application.use_cases.supply_chain_orchestration import SupplyChainOrchestrationUseCase
    
    # Initialize agents
    logistics_agent = LogisticsAgent(
        agent_id="logistics-001",
        orchestrator_url=f"http://{settings.host}:{settings.port}",
        mcp_tool_url=settings.mcp_tool_service_url,
    )
    
    compliance_agent = ComplianceAgent(
        agent_id="compliance-001",
        orchestrator_url=f"http://{settings.host}:{settings.port}",
        mcp_tool_url=settings.mcp_tool_service_url,
        rag_agent_url=settings.rag_agent_url,
    )
    
    # Create use case
    use_case = SupplyChainOrchestrationUseCase(logistics_agent, compliance_agent)
    
    # Convert shipment to dict for processing
    shipment_data = shipment.model_dump(mode="json")
    shipment_data["id"] = str(shipment.id)
    shipment_data["distance_km"] = 500  # Mock distance
    shipment_data["priority"] = "standard"
    shipment_data["documents"] = ["commercial_invoice", "packing_list", "certificate_of_origin"]
    shipment_data["type"] = "general"
    shipment_data["destination_country"] = shipment.destination.country
    
    # Process shipment
    result = await use_case.process_new_shipment(shipment_data)
    
    return result


# WebSocket endpoint for real-time dashboard
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    logger.info("New WebSocket connection established")
    
    try:
        # Send initial connection message
        await manager.send_personal_message(
            {"type": "connected", "message": "Connected to orchestrator"},
            websocket,
        )
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")
            
            # Echo back for now
            await manager.send_personal_message(
                {"type": "echo", "data": data},
                websocket,
            )
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
