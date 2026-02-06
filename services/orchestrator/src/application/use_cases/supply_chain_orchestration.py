"""Supply Chain Orchestration Use Case"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from ..domain.services.logistics_agent import LogisticsAgent
from ..domain.services.compliance_agent import ComplianceAgent
from ..infrastructure.websocket.manager import manager

logger = logging.getLogger(__name__)


class SupplyChainOrchestrationUseCase:
    """Use case for orchestrating supply chain operations"""

    def __init__(
        self,
        logistics_agent: LogisticsAgent,
        compliance_agent: ComplianceAgent,
    ) -> None:
        self.logistics_agent = logistics_agent
        self.compliance_agent = compliance_agent

    async def process_new_shipment(self, shipment_data: dict[str, Any]) -> dict[str, Any]:
        """Process a new shipment with logistics and compliance checks"""
        shipment_id = shipment_data.get("id", "unknown")
        logger.info(f"Processing new shipment: {shipment_id}")
        
        # Broadcast processing started
        await manager.broadcast_event("shipment_processing_started", {
            "shipment_id": shipment_id,
            "status": "processing",
        })
        
        try:
            # Step 1: Logistics Agent calculates shipping
            await manager.broadcast_event("agent_task_started", {
                "agent": "logistics",
                "task": "calculate_shipping",
                "shipment_id": shipment_id,
            })
            
            logistics_result = await self.logistics_agent.calculate_shipping(shipment_data)
            
            await manager.broadcast_event("agent_task_completed", {
                "agent": "logistics",
                "task": "calculate_shipping",
                "shipment_id": shipment_id,
                "result": logistics_result,
            })
            
            # Step 2: Compliance Agent validates documentation
            await manager.broadcast_event("agent_task_started", {
                "agent": "compliance",
                "task": "validate_documentation",
                "shipment_id": shipment_id,
            })
            
            doc_validation = await self.compliance_agent.validate_documentation(
                shipment_data
            )
            
            await manager.broadcast_event("agent_task_completed", {
                "agent": "compliance",
                "task": "validate_documentation",
                "shipment_id": shipment_id,
                "result": doc_validation,
            })
            
            # Step 3: Compliance Agent checks regulations
            await manager.broadcast_event("agent_task_started", {
                "agent": "compliance",
                "task": "check_compliance",
                "shipment_id": shipment_id,
            })
            
            compliance_result = await self.compliance_agent.check_compliance(
                shipment_data
            )
            
            await manager.broadcast_event("agent_task_completed", {
                "agent": "compliance",
                "task": "check_compliance",
                "shipment_id": shipment_id,
                "result": compliance_result,
            })
            
            # Combine results
            final_result = {
                "shipment_id": shipment_id,
                "status": "processed",
                "logistics": logistics_result,
                "documentation": doc_validation,
                "compliance": compliance_result,
                "approved": (
                    doc_validation.get("valid", False)
                    and compliance_result.get("compliance_check", {}).get("compliant", False)
                ),
            }
            
            # Broadcast completion
            await manager.broadcast_event("shipment_processing_completed", {
                "shipment_id": shipment_id,
                "status": "completed",
                "approved": final_result["approved"],
            })
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error processing shipment: {e}")
            await manager.broadcast_event("shipment_processing_failed", {
                "shipment_id": shipment_id,
                "error": str(e),
            })
            raise

    async def track_and_optimize(self, tracking_number: str) -> dict[str, Any]:
        """Track shipment and suggest optimizations"""
        logger.info(f"Tracking and optimizing: {tracking_number}")
        
        # Track shipment
        tracking_result = await self.logistics_agent.track_shipment(tracking_number)
        
        # Broadcast tracking update
        await manager.broadcast_event("shipment_tracked", {
            "tracking_number": tracking_number,
            "status": tracking_result.get("status"),
            "location": tracking_result.get("current_location"),
        })
        
        return {"tracking": tracking_result}
