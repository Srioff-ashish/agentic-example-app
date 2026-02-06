"""A2A (Agent-to-Agent) Protocol Implementation using JSON-RPC 2.0"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of agents in the supply chain system"""

    ORCHESTRATOR = "orchestrator"
    LOGISTICS = "logistics"
    COMPLIANCE = "compliance"
    RAG = "rag"
    MCP_TOOL = "mcp_tool"


class MessageType(str, Enum):
    """A2A Message Types"""

    HANDSHAKE = "handshake"
    DISCOVER = "discover"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class A2AError(BaseModel):
    """JSON-RPC Error Object"""

    code: int
    message: str
    data: dict[str, Any] | None = None


class AgentCapability(BaseModel):
    """Capability that an agent can provide"""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    requires_auth: bool = False


class AgentInfo(BaseModel):
    """Agent information for discovery"""

    agent_id: str
    agent_type: AgentType
    name: str
    version: str
    capabilities: list[AgentCapability]
    endpoint: str
    status: str = "active"


T = TypeVar("T")


class JSONRPCRequest(BaseModel, Generic[T]):
    """JSON-RPC 2.0 Request"""

    jsonrpc: str = "2.0"
    method: str
    params: T
    id: str = Field(default_factory=lambda: str(uuid4()))


class JSONRPCResponse(BaseModel, Generic[T]):
    """JSON-RPC 2.0 Response"""

    jsonrpc: str = "2.0"
    result: T | None = None
    error: A2AError | None = None
    id: str


class HandshakeRequest(BaseModel):
    """Handshake request payload"""

    agent_info: AgentInfo
    protocol_version: str = "1.0"


class HandshakeResponse(BaseModel):
    """Handshake response payload"""

    agent_info: AgentInfo
    accepted: bool
    session_id: str
    message: str | None = None


class DiscoverRequest(BaseModel):
    """Discovery request to find agents"""

    agent_type: AgentType | None = None
    capability: str | None = None


class DiscoverResponse(BaseModel):
    """Discovery response with available agents"""

    agents: list[AgentInfo]


class TaskRequest(BaseModel):
    """Generic task request"""

    task_type: str
    payload: dict[str, Any]
    correlation_id: str | None = None


class TaskResponse(BaseModel):
    """Generic task response"""

    task_type: str
    result: dict[str, Any]
    status: str
    correlation_id: str | None = None


@dataclass
class A2ASession:
    """A2A Session between agents"""

    session_id: str
    initiator: AgentInfo
    responder: AgentInfo
    established_at: str
    last_activity: str
