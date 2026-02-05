# Supply Chain Multi-Agent Microservices Application

A comprehensive supply chain management system built with multi-agent architecture using Python 3.12+, FastAPI, React, and ChromaDB.

## 🏗️ Architecture

This application follows **Clean Architecture** and **Domain-Driven Design (DDD)** principles with three main microservices:

### Services

1. **Orchestrator Service** (Port 8000)
   - Coordinates agent collaboration
   - Manages A2A (Agent-to-Agent) handshakes
   - Provides WebSocket real-time updates
   - Orchestrates supply chain workflows

2. **RAG Agent Service** (Port 8001)
   - Knowledge base with ChromaDB
   - Semantic search for compliance information
   - Provides regulatory guidance

3. **MCP Tool Service** (Port 8002)
   - Model Context Protocol (MCP) tool discovery
   - Supply chain utility tools
   - Logistics calculations
   - Compliance validation

### Agent Types

- **Orchestrator Agent**: Coordinates multi-agent workflows
- **Logistics Agent**: Handles shipping calculations, route optimization, tracking
- **Compliance Agent**: Validates documentation, checks regulations
- **RAG Agent**: Provides knowledge-based responses
- **MCP Tool Agent**: Exposes discoverable tools

## 🚀 Technology Stack

### Backend
- **Python 3.12+** with PEP 695 type syntax
- **FastAPI** for REST APIs and WebSocket
- **ChromaDB** for vector storage (RAG)
- **Poetry** for dependency management
- **Pydantic** for data validation
- **HTTPX** for async HTTP client

### Frontend
- **React 18** with Hooks
- **Vite** for build tooling
- **WebSocket** for real-time updates
- **Lucide React** for icons

### Communication
- **A2A Protocol**: JSON-RPC 2.0 for agent-to-agent communication
- **Fast MCP**: Model Context Protocol for tool discovery
- **WebSocket**: Real-time dashboard updates

## 📁 Project Structure

```
agentic-example-app/
├── services/
│   ├── orchestrator/
│   │   ├── src/
│   │   │   ├── domain/              # Domain models and business logic
│   │   │   │   ├── models/          # Domain entities
│   │   │   │   └── services/        # Domain services (agents)
│   │   │   ├── application/         # Application use cases
│   │   │   │   └── use_cases/
│   │   │   ├── infrastructure/      # Infrastructure layer
│   │   │   │   ├── a2a/            # A2A protocol implementation
│   │   │   │   ├── websocket/      # WebSocket manager
│   │   │   │   └── config/         # Configuration
│   │   │   └── presentation/        # API layer
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── rag-agent/
│   │   ├── src/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   ├── infrastructure/
│   │   │   │   ├── chromadb/       # ChromaDB integration
│   │   │   │   └── a2a/
│   │   │   └── presentation/
│   │   └── pyproject.toml
│   │
│   └── mcp-tool-service/
│       ├── src/
│       │   ├── domain/
│       │   ├── application/
│       │   │   └── tools/          # MCP tools
│       │   ├── infrastructure/
│       │   │   └── mcp/            # MCP registry
│       │   └── presentation/
│       └── pyproject.toml
│
└── dashboard/
    ├── src/
    │   ├── App.jsx                  # Main dashboard component
    │   ├── App.css
    │   ├── main.jsx
    │   └── index.css
    ├── package.json
    └── vite.config.js
```

## 🔧 Setup Instructions

### Prerequisites

- Python 3.12+
- Poetry
- Node.js 18+
- npm or yarn

### Backend Setup

#### 1. Orchestrator Service

```bash
cd services/orchestrator
poetry install
poetry run python src/main.py
```

The orchestrator will run on `http://localhost:8000`

#### 2. RAG Agent Service

```bash
cd services/rag-agent
poetry install
poetry run python src/main.py
```

The RAG agent will run on `http://localhost:8001`

#### 3. MCP Tool Service

```bash
cd services/mcp-tool-service
poetry install
poetry run python src/main.py
```

The MCP tool service will run on `http://localhost:8002`

### Frontend Setup

```bash
cd dashboard
npm install
npm run dev
```

The dashboard will run on `http://localhost:3000`

## 🔌 A2A Protocol (Agent-to-Agent Communication)

The A2A protocol uses **JSON-RPC 2.0** for inter-agent communication.

### Handshake Flow

1. **Agent Registration**: Agent registers with orchestrator
2. **Handshake Request**: JSON-RPC request with agent info
3. **Handshake Response**: Session ID and acceptance
4. **Session Establishment**: Active A2A session created

### Example Handshake Request

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
          "description": "Query supply chain knowledge base"
        }
      ],
      "endpoint": "http://localhost:8001"
    },
    "protocol_version": "1.0"
  },
  "id": "uuid-here"
}
```

### Discovery

Agents can discover other agents by type or capability:

```python
# Discover all logistics agents
agents = await discovery_service.discover_agents(agent_type=AgentType.LOGISTICS)

# Discover agents with specific capability
agents = await discovery_service.discover_agents(capability="calculate_shipping")
```

## 🛠️ MCP Tool Discovery

The MCP Tool Service provides discoverable tools following the Model Context Protocol.

### Available Tools

#### Logistics Tools
- `calculate_shipping_cost`: Calculate cost based on weight, distance, priority
- `estimate_delivery_time`: Estimate delivery time
- `optimize_route`: Optimize delivery routes
- `track_shipment`: Track shipment status

#### Compliance Tools
- `validate_customs_documentation`: Validate customs docs
- `check_compliance_status`: Check regulatory compliance

### Tool Discovery

```bash
# List all tools
curl http://localhost:8002/tools

# List tools by category
curl http://localhost:8002/tools?category=logistics

# Execute a tool
curl -X POST http://localhost:8002/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "calculate_shipping_cost",
    "parameters": {
      "weight_kg": 10,
      "distance_km": 500,
      "priority": "express"
    }
  }'
```

## 📊 API Endpoints

### Orchestrator (Port 8000)

- `GET /` - Service info
- `GET /health` - Health check
- `GET /agents` - List registered agents
- `POST /shipments` - Create shipment
- `POST /orchestrate` - Orchestrate shipment workflow
- `POST /a2a/handshake` - A2A handshake
- `POST /a2a/discover` - Agent discovery
- `POST /a2a/task` - Task execution
- `WS /ws` - WebSocket for real-time updates

### RAG Agent (Port 8001)

- `GET /` - Service info
- `GET /health` - Health check
- `POST /query` - Query knowledge base
- `POST /a2a/task` - Handle A2A tasks

### MCP Tool Service (Port 8002)

- `GET /` - Service info
- `GET /health` - Health check
- `GET /tools` - List tools
- `POST /tools/execute` - Execute tool
- `POST /a2a/task` - Handle A2A tasks

## 🎯 Usage Example

### Complete Workflow

```python
import httpx
from datetime import datetime, timedelta

# Create a shipment
shipment = {
    "tracking_number": "SHIP001",
    "origin": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "123 Main St",
        "city": "New York",
        "country": "US"
    },
    "destination": {
        "latitude": 34.0522,
        "longitude": -118.2437,
        "address": "456 Oak Ave",
        "city": "Los Angeles",
        "country": "US"
    },
    "status": "pending",
    "estimated_delivery": (datetime.now() + timedelta(days=3)).isoformat(),
    "carrier": "FastShip",
    "weight_kg": 15.5,
    "value_usd": 1200.00,
    "contents": ["Electronics", "Accessories"]
}

# Orchestrate the shipment
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/orchestrate",
        json=shipment
    )
    result = response.json()
    print(result)
```

## 🔒 Error Handling

All services implement robust error handling:

- **Async operations** with proper exception handling
- **JSON-RPC error responses** with error codes
- **Logging** at appropriate levels
- **Graceful degradation** when services are unavailable

## 🧪 Testing

```bash
# Run tests for each service
cd services/orchestrator
poetry run pytest

cd services/rag-agent
poetry run pytest

cd services/mcp-tool-service
poetry run pytest
```

## 📝 Code Quality

### Linting

```bash
poetry run black .
poetry run ruff check .
poetry run mypy .
```

### Type Checking

All code uses **PEP 695 type parameter syntax** and strict type checking with mypy.

## 🔄 Real-time Dashboard

The React dashboard connects via WebSocket to receive real-time updates:

- **Agent connections**: See when agents connect/disconnect
- **Shipment processing**: Track shipment workflow in real-time
- **Task execution**: Monitor agent task execution
- **Compliance checks**: View compliance validation results
- **Statistics**: Real-time metrics and counters

## 🌟 Features

- ✅ **Clean Architecture** with clear separation of concerns
- ✅ **Domain-Driven Design** with rich domain models
- ✅ **A2A Protocol** for agent communication
- ✅ **MCP Tool Discovery** for dynamic capabilities
- ✅ **WebSocket** for real-time updates
- ✅ **ChromaDB** for semantic search
- ✅ **Async/Await** throughout
- ✅ **PEP 695** type syntax
- ✅ **Robust error handling**
- ✅ **Comprehensive logging**

## 🚀 Deployment

### Docker (Future)

Each service can be containerized:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
CMD ["poetry", "run", "python", "src/main.py"]
```

### Environment Variables

Create `.env` files for each service:

```env
# Orchestrator
HOST=0.0.0.0
PORT=8000
RAG_AGENT_URL=http://localhost:8001
MCP_TOOL_SERVICE_URL=http://localhost:8002

# RAG Agent
HOST=0.0.0.0
PORT=8001
ORCHESTRATOR_URL=http://localhost:8000

# MCP Tool Service
HOST=0.0.0.0
PORT=8002
ORCHESTRATOR_URL=http://localhost:8000
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)

## 🤝 Contributing

1. Follow Clean Architecture principles
2. Maintain type safety with mypy
3. Write tests for new features
4. Use async/await for I/O operations
5. Follow existing code style

## 📄 License

MIT License

## 🔗 Contact

For questions or support, please open an issue on GitHub.
