"""Compliance Agent Implementation"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from ..infrastructure.a2a.protocol import (
    AgentCapability,
    AgentInfo,
    AgentType,
    JSONRPCRequest,
    JSONRPCResponse,
    TaskRequest,
    TaskResponse,
)

logger = logging.getLogger(__name__)


class ComplianceAgent:
    """Compliance Agent for regulatory checks"""

    def __init__(
        self,
        agent_id: str,
        orchestrator_url: str,
        mcp_tool_url: str,
        rag_agent_url: str,
    ) -> None:
        self.agent_id = agent_id
        self.orchestrator_url = orchestrator_url
        self.mcp_tool_url = mcp_tool_url
        self.rag_agent_url = rag_agent_url
        self.agent_info = AgentInfo(
            agent_id=agent_id,
            agent_type=AgentType.COMPLIANCE,
            name="Compliance Agent",
            version="0.1.0",
            capabilities=[
                AgentCapability(
                    name="validate_documentation",
                    description="Validate customs and compliance documentation",
                ),
                AgentCapability(
                    name="check_regulations",
                    description="Check compliance with regulations",
                ),
            ],
            endpoint="",
        )

    async def validate_documentation(
        self, shipment_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate customs documentation"""
        logger.info(f"Validating documentation for shipment: {shipment_data.get('id')}")
        
        documents = shipment_data.get("documents", [])
        
        # Call MCP Tool Service to validate
        request = JSONRPCRequest[TaskRequest](
            method="task",
            params=TaskRequest(
                task_type="execute_tool",
                payload={
                    "tool_name": "validate_customs_documentation",
                    "parameters": {"documents": documents},
                },
            ),
        )
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.mcp_tool_url}/a2a/task",
                json=request.model_dump(),
            )
            result = JSONRPCResponse[TaskResponse](**response.json())
        
        return result.result.result if result.result else {}

    async def check_compliance(self, shipment_data: dict[str, Any]) -> dict[str, Any]:
        """Check compliance status"""
        logger.info(f"Checking compliance for shipment: {shipment_data.get('id')}")
        
        # First, query RAG agent for relevant regulations
        rag_request = JSONRPCRequest[TaskRequest](
            method="task",
            params=TaskRequest(
                task_type="query_knowledge",
                payload={
                    "query": f"compliance requirements for {shipment_data.get('type', 'general')} shipment to {shipment_data.get('destination_country', 'US')}",
                    "n_results": 3,
                },
            ),
        )
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Query RAG agent
            response = await client.post(
                f"{self.rag_agent_url}/a2a/task",
                json=rag_request.model_dump(),
            )
            rag_result = JSONRPCResponse[TaskResponse](**response.json())
            
            # Check compliance with MCP tool
            compliance_request = JSONRPCRequest[TaskRequest](
                method="task",
                params=TaskRequest(
                    task_type="execute_tool",
                    payload={
                        "tool_name": "check_compliance_status",
                        "parameters": {
                            "shipment_type": shipment_data.get("type", "general"),
                            "destination_country": shipment_data.get(
                                "destination_country", "US"
                            ),
                        },
                    },
                ),
            )
            
            response = await client.post(
                f"{self.mcp_tool_url}/a2a/task",
                json=compliance_request.model_dump(),
            )
            compliance_result = JSONRPCResponse[TaskResponse](**response.json())
        
        return {
            "compliance_check": compliance_result.result.result if compliance_result.result else {},
            "knowledge_base": rag_result.result.result if rag_result.result else {},
        }

    async def get_compliance_guidance(self, query: str) -> dict[str, Any]:
        """Get compliance guidance from knowledge base"""
        logger.info(f"Getting compliance guidance: {query}")
        
        request = JSONRPCRequest[TaskRequest](
            method="task",
            params=TaskRequest(
                task_type="query_knowledge",
                payload={"query": query, "n_results": 5},
            ),
        )
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.rag_agent_url}/a2a/task",
                json=request.model_dump(),
            )
            result = JSONRPCResponse[TaskResponse](**response.json())
        
        return result.result.result if result.result else {}
