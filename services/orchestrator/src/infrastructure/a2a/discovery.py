"""A2A Discovery Service - Agent Discovery and Registration"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import httpx
from pydantic import BaseModel

from .protocol import (
    AgentInfo,
    AgentType,
    DiscoverRequest,
    DiscoverResponse,
    HandshakeRequest,
    HandshakeResponse,
    JSONRPCRequest,
    JSONRPCResponse,
    A2ASession,
)


class A2ADiscoveryService:
    """Service for agent discovery and handshake management"""

    def __init__(self) -> None:
        self._registry: dict[str, AgentInfo] = {}
        self._sessions: dict[str, A2ASession] = {}
        self._lock = asyncio.Lock()

    async def register_agent(self, agent_info: AgentInfo) -> None:
        """Register an agent in the discovery registry"""
        async with self._lock:
            self._registry[agent_info.agent_id] = agent_info

    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the registry"""
        async with self._lock:
            self._registry.pop(agent_id, None)

    async def discover_agents(
        self, agent_type: AgentType | None = None, capability: str | None = None
    ) -> list[AgentInfo]:
        """Discover agents by type or capability"""
        agents = list(self._registry.values())

        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]

        if capability:
            agents = [
                a
                for a in agents
                if any(cap.name == capability for cap in a.capabilities)
            ]

        return agents

    async def initiate_handshake(
        self, initiator: AgentInfo, target_endpoint: str
    ) -> A2ASession:
        """Initiate A2A handshake with another agent"""
        request = JSONRPCRequest[HandshakeRequest](
            method="handshake",
            params=HandshakeRequest(
                agent_info=initiator,
                protocol_version="1.0",
            ),
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{target_endpoint}/a2a/handshake",
                json=request.model_dump(),
            )
            response.raise_for_status()
            
            rpc_response = JSONRPCResponse[HandshakeResponse](**response.json())
            
            if rpc_response.error:
                raise RuntimeError(
                    f"Handshake failed: {rpc_response.error.message}"
                )
            
            if not rpc_response.result or not rpc_response.result.accepted:
                raise RuntimeError("Handshake rejected by target agent")

            # Create session
            now = datetime.now(timezone.utc).isoformat()
            session = A2ASession(
                session_id=rpc_response.result.session_id,
                initiator=initiator,
                responder=rpc_response.result.agent_info,
                established_at=now,
                last_activity=now,
            )

            async with self._lock:
                self._sessions[session.session_id] = session

            return session

    async def accept_handshake(
        self, request: HandshakeRequest, responder: AgentInfo
    ) -> HandshakeResponse:
        """Accept incoming handshake request"""
        import uuid

        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        session = A2ASession(
            session_id=session_id,
            initiator=request.agent_info,
            responder=responder,
            established_at=now,
            last_activity=now,
        )

        async with self._lock:
            self._sessions[session_id] = session

        return HandshakeResponse(
            agent_info=responder,
            accepted=True,
            session_id=session_id,
            message="Handshake accepted successfully",
        )

    async def get_session(self, session_id: str) -> A2ASession | None:
        """Get session by ID"""
        return self._sessions.get(session_id)

    async def update_session_activity(self, session_id: str) -> None:
        """Update last activity timestamp for a session"""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.last_activity = datetime.now(timezone.utc).isoformat()

    def get_all_agents(self) -> list[AgentInfo]:
        """Get all registered agents"""
        return list(self._registry.values())
