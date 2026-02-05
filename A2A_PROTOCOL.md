# A2A Protocol Documentation

## Agent-to-Agent Communication Protocol

This document describes the A2A (Agent-to-Agent) protocol implementation using JSON-RPC 2.0.

---

## Overview

The A2A protocol enables secure, typed communication between autonomous agents in the supply chain system. Built on JSON-RPC 2.0, it provides:

- **Handshake mechanism** for agent registration
- **Discovery service** for finding agents by type/capability
- **Task execution** with correlation IDs
- **Session management** for tracking agent relationships
- **Error handling** with standard error codes

---

## Architecture

```
┌─────────────┐         A2A Handshake        ┌─────────────┐
│   Agent A   │ ─────────────────────────► │   Agent B   │
│             │ ◄─────────────────────────  │             │
└─────────────┘      Session Created        └─────────────┘
       │                                            │
       │              A2A Task Request             │
       ├───────────────────────────────────────────►
       │                                            │
       │              A2A Task Response            │
       ◄───────────────────────────────────────────┤
       │                                            │
```

---

## JSON-RPC 2.0 Message Format

### Request

```json
{
  "jsonrpc": "2.0",
  "method": "string",
  "params": { ... },
  "id": "uuid"
}
```

### Response (Success)

```json
{
  "jsonrpc": "2.0",
  "result": { ... },
  "id": "uuid"
}
```

### Response (Error)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Error description",
    "data": { ... }
  },
  "id": "uuid"
}
```

---

## Protocol Methods

### 1. Handshake

**Purpose**: Establish a session between two agents

**Endpoint**: `POST /a2a/handshake`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "handshake",
  "params": {
    "agent_info": {
      "agent_id": "rag-agent-001",
      "agent_type": "rag",
      "name": "RAG Agent",
      "version": "0.1.0",
      "capabilities": [
        {
          "name": "query_knowledge",
          "description": "Query supply chain knowledge base",
          "parameters": {
            "query": "string",
            "n_results": "integer"
          },
          "requires_auth": false
        }
      ],
      "endpoint": "http://localhost:8001",
      "status": "active"
    },
    "protocol_version": "1.0"
  },
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "agent_info": {
      "agent_id": "orchestrator-001",
      "agent_type": "orchestrator",
      "name": "Supply Chain Orchestrator",
      "version": "0.1.0",
      "capabilities": [ ... ],
      "endpoint": "http://localhost:8000",
      "status": "active"
    },
    "accepted": true,
    "session_id": "abc123-def456-ghi789",
    "message": "Handshake accepted successfully"
  },
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Python Example**:
```python
from infrastructure.a2a.discovery import A2ADiscoveryService
from infrastructure.a2a.protocol import AgentInfo, HandshakeRequest

discovery = A2ADiscoveryService()

# Initiate handshake
session = await discovery.initiate_handshake(
    initiator=my_agent_info,
    target_endpoint="http://localhost:8001"
)
print(f"Session ID: {session.session_id}")
```

---

### 2. Discover

**Purpose**: Find agents by type or capability

**Endpoint**: `POST /a2a/discover`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "discover",
  "params": {
    "agent_type": "logistics",
    "capability": "calculate_shipping"
  },
  "id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "agents": [
      {
        "agent_id": "logistics-001",
        "agent_type": "logistics",
        "name": "Logistics Agent",
        "version": "0.1.0",
        "capabilities": [ ... ],
        "endpoint": "http://localhost:8003",
        "status": "active"
      }
    ]
  },
  "id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Python Example**:
```python
# Find all logistics agents
agents = await discovery.discover_agents(
    agent_type=AgentType.LOGISTICS
)

# Find agents with specific capability
agents = await discovery.discover_agents(
    capability="calculate_shipping"
)
```

---

### 3. Task

**Purpose**: Execute a task on another agent

**Endpoint**: `POST /a2a/task`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "task",
  "params": {
    "task_type": "query_knowledge",
    "payload": {
      "query": "What are customs requirements for electronics?",
      "n_results": 5
    },
    "correlation_id": "order-12345"
  },
  "id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "task_type": "query_knowledge",
    "result": {
      "documents": [ ... ],
      "metadatas": [ ... ],
      "distances": [ ... ]
    },
    "status": "completed",
    "correlation_id": "order-12345"
  },
  "id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Python Example**:
```python
import httpx
from infrastructure.a2a.protocol import JSONRPCRequest, TaskRequest

request = JSONRPCRequest[TaskRequest](
    method="task",
    params=TaskRequest(
        task_type="query_knowledge",
        payload={
            "query": "customs requirements",
            "n_results": 5
        },
        correlation_id="order-12345"
    )
)

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8001/a2a/task",
        json=request.model_dump()
    )
    result = response.json()
```

---

## Agent Types

| Type | Description | Example Capabilities |
|------|-------------|---------------------|
| `orchestrator` | Coordinates agent collaboration | orchestrate_shipment, coordinate_agents |
| `logistics` | Handles shipping operations | calculate_shipping, optimize_route, track_shipment |
| `compliance` | Validates regulations | validate_documentation, check_regulations |
| `rag` | Provides knowledge-based responses | query_knowledge, search_documents |
| `mcp_tool` | Exposes discoverable tools | Various supply chain tools |

---

## Capability Schema

```python
class AgentCapability(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    requires_auth: bool = False
```

**Example**:
```json
{
  "name": "calculate_shipping_cost",
  "description": "Calculate shipping cost based on weight, distance, and priority",
  "parameters": {
    "weight_kg": "number",
    "distance_km": "number",
    "priority": "string (standard|express|overnight)"
  },
  "requires_auth": false
}
```

---

## Session Management

### Session Lifecycle

1. **Initiation**: Agent A sends handshake to Agent B
2. **Acceptance**: Agent B accepts and creates session
3. **Active**: Agents exchange tasks using session context
4. **Timeout**: Session expires after inactivity (configurable)

### Session Object

```python
@dataclass
class A2ASession:
    session_id: str
    initiator: AgentInfo
    responder: AgentInfo
    established_at: str  # ISO 8601
    last_activity: str   # ISO 8601
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid Request | Invalid JSON-RPC request |
| -32601 | Method not found | Method doesn't exist |
| -32602 | Invalid params | Invalid method parameters |
| -32603 | Internal error | Internal JSON-RPC error |
| -32000 | Server error | Application-specific error |

---

## Security Considerations

### Current Implementation
- Internal network only (localhost)
- No authentication (trust-based)
- No encryption (HTTP)

### Production Recommendations
- **mTLS**: Mutual TLS for transport security
- **JWT**: Token-based authentication
- **Rate Limiting**: Prevent abuse
- **Audit Logging**: Track all A2A interactions
- **Network Segmentation**: Isolate agent networks

---

## Best Practices

### 1. Always Use Correlation IDs
```python
TaskRequest(
    task_type="process_order",
    payload={...},
    correlation_id=f"order-{order_id}"  # For tracing
)
```

### 2. Handle Errors Gracefully
```python
try:
    result = await agent.execute_task(...)
except httpx.HTTPError as e:
    logger.error(f"A2A communication failed: {e}")
    # Implement retry logic or fallback
```

### 3. Validate Responses
```python
response = JSONRPCResponse[TaskResponse](**raw_response)
if response.error:
    raise RuntimeError(f"Task failed: {response.error.message}")
```

### 4. Update Session Activity
```python
await discovery.update_session_activity(session_id)
```

### 5. Use Timeouts
```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(...)
```

---

## Example: Complete Agent Collaboration

### Scenario: Shipment Processing

```python
# 1. Orchestrator discovers logistics agent
logistics_agents = await discovery.discover_agents(
    agent_type=AgentType.LOGISTICS
)
logistics_agent = logistics_agents[0]

# 2. Orchestrator sends task to logistics agent
cost_request = JSONRPCRequest[TaskRequest](
    method="task",
    params=TaskRequest(
        task_type="calculate_shipping",
        payload={
            "weight_kg": 10,
            "distance_km": 500,
            "priority": "express"
        }
    )
)

async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{logistics_agent.endpoint}/a2a/task",
        json=cost_request.model_dump()
    )
    
# 3. Logistics agent executes via MCP tools
# 4. Returns result to orchestrator
# 5. Orchestrator aggregates and responds to client
```

---

## Implementation Files

- `services/orchestrator/src/infrastructure/a2a/protocol.py` - Protocol definitions
- `services/orchestrator/src/infrastructure/a2a/discovery.py` - Discovery service
- `services/orchestrator/src/domain/services/logistics_agent.py` - Logistics agent
- `services/orchestrator/src/domain/services/compliance_agent.py` - Compliance agent

---

## Testing A2A Protocol

### Unit Tests
```python
import pytest
from infrastructure.a2a.discovery import A2ADiscoveryService

@pytest.mark.asyncio
async def test_agent_registration():
    discovery = A2ADiscoveryService()
    await discovery.register_agent(my_agent_info)
    
    agents = await discovery.discover_agents()
    assert len(agents) == 1
    assert agents[0].agent_id == my_agent_info.agent_id
```

### Integration Tests
```bash
# Run test_system.py to verify A2A communication
python3 test_system.py
```

---

## Future Enhancements

1. **Authentication & Authorization**
   - OAuth 2.0 / JWT tokens
   - Role-based access control

2. **Encryption**
   - TLS/mTLS for transport
   - Message-level encryption for sensitive data

3. **Monitoring**
   - OpenTelemetry traces
   - Prometheus metrics

4. **Reliability**
   - Message queues (RabbitMQ/Kafka)
   - Retry mechanisms
   - Circuit breakers

5. **Protocol Extensions**
   - Streaming responses
   - Bidirectional tasks
   - Agent lifecycle events

---

## References

- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://docs.pydantic.dev/)

---

## Support

For questions or issues with the A2A protocol implementation, please refer to the main README.md or open an issue on GitHub.
