"""RAG Agent Main Application"""
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
from .infrastructure.chromadb.service import ChromaDBService
from .infrastructure.config.settings import settings

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Global ChromaDB service
chroma_service: ChromaDBService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifecycle manager"""
    global chroma_service
    
    # Startup
    logger.info("Starting RAG Agent Service...")
    
    # Initialize ChromaDB
    chroma_service = ChromaDBService(
        persist_directory=settings.chroma_db_path,
        collection_name=settings.chroma_collection_name,
    )
    
    # Seed initial data
    await seed_initial_data()
    
    # Register with orchestrator
    await register_with_orchestrator()
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Agent Service...")


async def seed_initial_data() -> None:
    """Seed initial supply chain knowledge"""
    if chroma_service is None:
        return
        
    count = await chroma_service.count_documents()
    if count > 0:
        logger.info(f"Collection already has {count} documents")
        return
    
    documents = [
        "International shipping regulations require proper customs documentation including commercial invoice, packing list, and certificate of origin.",
        "Hazardous materials must be classified according to UN numbers and require special handling and documentation.",
        "Cross-border shipments must comply with import/export regulations including tariffs, duties, and trade agreements.",
        "Temperature-sensitive goods require controlled environment shipping with monitoring systems.",
        "Last-mile delivery optimization can reduce costs by 15-20% through route planning and consolidation.",
        "Supply chain visibility improves customer satisfaction and reduces support inquiries by 40%.",
        "Compliance with CTPAT (Customs-Trade Partnership Against Terrorism) provides expedited customs processing.",
        "Electronic data interchange (EDI) enables automated document exchange between supply chain partners.",
    ]
    
    metadatas = [
        {"category": "compliance", "region": "international"},
        {"category": "compliance", "type": "hazmat"},
        {"category": "compliance", "region": "cross-border"},
        {"category": "logistics", "type": "cold-chain"},
        {"category": "logistics", "optimization": "routing"},
        {"category": "logistics", "metric": "visibility"},
        {"category": "compliance", "program": "ctpat"},
        {"category": "logistics", "technology": "edi"},
    ]
    
    await chroma_service.add_documents(documents=documents, metadatas=metadatas)
    logger.info("Seeded initial knowledge base")


async def register_with_orchestrator() -> None:
    """Register this agent with the orchestrator"""
    try:
        agent_info = AgentInfo(
            agent_id=settings.agent_id,
            agent_type=AgentType.RAG,
            name=settings.service_name,
            version=settings.service_version,
            capabilities=[
                AgentCapability(
                    name="query_knowledge",
                    description="Query supply chain knowledge base",
                    parameters={"query": "string", "n_results": "integer"},
                ),
            ],
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
    title="Supply Chain RAG Agent",
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


class QueryRequest(BaseModel):
    """Query request model"""

    query: str
    n_results: int = 5
    category: str | None = None


@app.post("/query")
async def query_knowledge(request: QueryRequest) -> dict[str, Any]:
    """Query the knowledge base"""
    if chroma_service is None:
        raise HTTPException(status_code=500, detail="ChromaDB service not initialized")
    
    where = {"category": request.category} if request.category else None
    results = await chroma_service.query(
        query_text=request.query,
        n_results=request.n_results,
        where=where,
    )
    
    return {"results": results}


@app.post("/a2a/task")
async def handle_task(request: JSONRPCRequest[TaskRequest]) -> JSONRPCResponse[TaskResponse]:
    """Handle task requests from other agents"""
    try:
        logger.info(f"Received task: {request.params.task_type}")
        
        if request.params.task_type == "query_knowledge":
            query = request.params.payload.get("query", "")
            n_results = request.params.payload.get("n_results", 5)
            
            if chroma_service is None:
                raise RuntimeError("ChromaDB service not initialized")
            
            results = await chroma_service.query(query, n_results)
            
            response = TaskResponse(
                task_type=request.params.task_type,
                result={"results": results},
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
