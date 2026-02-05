# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites

- Python 3.12+
- Poetry (will be installed if not present)
- Node.js 18+
- npm

### Step 1: Install Dependencies

```bash
# Install Python dependencies for all services
cd services/orchestrator && poetry install && cd ../..
cd services/mcp-tool-service && poetry install && cd ../..
# cd services/rag-agent && poetry install && cd ../..  # Optional - requires more time

# Install dashboard dependencies
cd dashboard && npm install && cd ..
```

### Step 2: Start Services

Open 3 separate terminals:

**Terminal 1 - Orchestrator:**
```bash
cd services/orchestrator
PYTHONPATH=$(pwd) poetry run python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - MCP Tool Service:**
```bash
cd services/mcp-tool-service
PYTHONPATH=$(pwd) poetry run python -m uvicorn src.main:app --host 0.0.0.0 --port 8002
```

**Terminal 3 - Dashboard:**
```bash
cd dashboard
npm run dev
```

**Optional - RAG Agent (Terminal 4):**
```bash
cd services/rag-agent
PYTHONPATH=$(pwd) poetry run python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### Step 3: Access the Application

- **Dashboard**: http://localhost:3000
- **Orchestrator API**: http://localhost:8000/docs
- **MCP Tool Service API**: http://localhost:8002/docs
- **RAG Agent API** (if running): http://localhost:8001/docs

### Step 4: Test the System

Run the test script:

```bash
python3 test_system.py
```

## 🎯 Quick API Examples

### List Available Tools

```bash
curl http://localhost:8002/tools
```

### Execute a Tool

```bash
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

### Create a Shipment

```bash
curl -X POST http://localhost:8000/shipments \
  -H "Content-Type: application/json" \
  -d '{
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
    "estimated_delivery": "2026-02-08T00:00:00",
    "carrier": "FastShip",
    "weight_kg": 15.5,
    "value_usd": 1200.00,
    "contents": ["Electronics"]
  }'
```

### List Registered Agents

```bash
curl http://localhost:8000/agents
```

## 🔍 Monitoring Real-time Events

1. Open the dashboard at http://localhost:3000
2. The WebSocket connection will automatically establish
3. Create shipments or execute tools to see real-time events
4. Watch agents collaborate in real-time!

## 🛠️ Key Features Demonstrated

- ✅ **A2A Protocol**: Agents communicate via JSON-RPC 2.0
- ✅ **MCP Tool Discovery**: Dynamic tool registration and discovery
- ✅ **WebSocket Updates**: Real-time dashboard notifications
- ✅ **Clean Architecture**: DDD and separation of concerns
- ✅ **Async Operations**: Full async/await support
- ✅ **Type Safety**: PEP 695 type syntax with strict typing

## 📊 Architecture Diagram

```
┌─────────────────┐      WebSocket      ┌──────────────┐
│   Dashboard     │◄────────────────────┤              │
│   (React)       │                     │ Orchestrator │
└─────────────────┘                     │   Service    │
                                        │   (8000)     │
                                        └──────┬───────┘
                                               │
                               ┌───────────────┼───────────────┐
                               │               │               │
                        A2A Protocol    A2A Protocol    A2A Protocol
                               │               │               │
                         ┌─────▼────┐   ┌─────▼────┐   ┌─────▼────┐
                         │   RAG    │   │   MCP    │   │ Logistics│
                         │  Agent   │   │   Tool   │   │ & Compli │
                         │  (8001)  │   │ Service  │   │  Agents  │
                         └──────────┘   │  (8002)  │   └──────────┘
                                        └──────────┘
                                             │
                                        6 Tools:
                                        - calculate_shipping_cost
                                        - estimate_delivery_time
                                        - validate_customs_docs
                                        - check_compliance_status
                                        - optimize_route
                                        - track_shipment
```

## 🔧 Troubleshooting

### Services Won't Start

- Ensure ports 8000, 8001, 8002, and 3000 are not in use
- Check that Poetry is installed: `poetry --version`
- Verify Python version: `python3 --version` (should be 3.12+)

### WebSocket Connection Issues

- Ensure Orchestrator is running on port 8000
- Check browser console for WebSocket errors
- Verify CORS settings in orchestrator settings.py

### Import Errors

- Make sure to use `PYTHONPATH=$(pwd)` when running services
- Ensure all `__init__.py` files are present
- Run from the service directory, not the root

## 📚 Next Steps

1. **Explore the Code**: Check out the Clean Architecture structure
2. **Add Custom Tools**: Create new tools in `mcp-tool-service/src/application/tools/`
3. **Enhance Agents**: Add new agent capabilities
4. **Extend Dashboard**: Add more visualizations and metrics
5. **Deploy**: Containerize with Docker for production

## 🤝 Contributing

See the main README.md for contribution guidelines.

## 📄 License

MIT License
