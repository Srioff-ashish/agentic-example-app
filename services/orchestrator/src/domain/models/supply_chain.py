"""Domain Models for Supply Chain"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ShipmentStatus(str, Enum):
    """Shipment status enumeration"""

    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class ComplianceStatus(str, Enum):
    """Compliance status enumeration"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_ACTION = "requires_action"


class Location(BaseModel):
    """Geographic location"""

    latitude: float
    longitude: float
    address: str
    city: str
    country: str


class Shipment(BaseModel):
    """Shipment domain model"""

    id: UUID = Field(default_factory=uuid4)
    tracking_number: str
    origin: Location
    destination: Location
    status: ShipmentStatus = ShipmentStatus.PENDING
    estimated_delivery: datetime
    actual_delivery: datetime | None = None
    carrier: str
    weight_kg: float
    value_usd: float
    contents: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class ComplianceCheck(BaseModel):
    """Compliance check domain model"""

    id: UUID = Field(default_factory=uuid4)
    shipment_id: UUID
    check_type: str
    status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW
    regulations: list[str]
    findings: list[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=lambda: datetime.now())
    checked_by: str = "compliance_agent"


class SupplyChainEvent(BaseModel):
    """Supply chain event for tracking"""

    id: UUID = Field(default_factory=uuid4)
    event_type: str
    shipment_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    location: Location | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    agent_id: str


class LogisticsTask(BaseModel):
    """Logistics task for the logistics agent"""

    id: UUID = Field(default_factory=uuid4)
    task_type: str
    shipment_id: UUID
    priority: int = 1
    status: str = "pending"
    assigned_to: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    completed_at: datetime | None = None
