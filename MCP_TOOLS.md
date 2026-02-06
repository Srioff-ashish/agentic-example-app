# MCP Tool Discovery Documentation

## Model Context Protocol (MCP) Tool Service

Fast MCP implementation for dynamic tool discovery and execution in the supply chain system.

---

## Overview

The MCP Tool Service provides a registry of discoverable tools that agents can query and execute. Tools are organized by category and expose standardized interfaces for:

- **Discovery**: Find tools by name or category
- **Metadata**: Get tool descriptions and parameters
- **Execution**: Run tools with typed parameters
- **Results**: Receive structured responses

---

## Architecture

```
┌──────────────┐
│   Agent      │
└──────┬───────┘
       │
       │ 1. List Tools (GET /tools?category=logistics)
       ▼
┌──────────────────────────────┐
│   MCP Tool Service           │
│   ┌────────────────────┐    │
│   │  Tool Registry     │    │
│   │  - Metadata        │    │
│   │  - Handlers        │    │
│   │  - Categories      │    │
│   └────────────────────┘    │
└──────────────────────────────┘
       │
       │ 2. Execute Tool (POST /tools/execute)
       ▼
┌──────────────────────────────┐
│   Tool Implementation        │
│   - calculate_shipping_cost  │
│   - estimate_delivery_time   │
│   - validate_customs_docs    │
│   - check_compliance_status  │
│   - optimize_route          │
│   - track_shipment          │
└──────────────────────────────┘
```

---

## Tool Schema

### Tool Definition

```python
class MCPTool(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]
    category: str
    handler: str
```

### Example Tool

```json
{
  "name": "calculate_shipping_cost",
  "description": "Calculate shipping cost based on weight, distance, and priority",
  "parameters": {
    "weight_kg": "number",
    "distance_km": "number",
    "priority": "string (standard|express|overnight)"
  },
  "category": "logistics",
  "handler": "calculate_shipping_cost"
}
```

---

## Available Tools

### Logistics Tools

#### 1. Calculate Shipping Cost

**Name**: `calculate_shipping_cost`

**Description**: Calculate shipping cost based on weight, distance, and priority

**Parameters**:
- `weight_kg` (number): Package weight in kilograms
- `distance_km` (number): Shipping distance in kilometers
- `priority` (string): Shipping priority - "standard", "express", or "overnight"

**Returns**:
```json
{
  "cost_usd": 112.5,
  "currency": "USD",
  "breakdown": {
    "weight_cost": 25.0,
    "distance_cost": 50.0,
    "priority_multiplier": 1.5
  }
}
```

**Example**:
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

---

#### 2. Estimate Delivery Time

**Name**: `estimate_delivery_time`

**Description**: Estimate delivery time based on distance and priority

**Parameters**:
- `distance_km` (number): Shipping distance in kilometers
- `priority` (string): Shipping priority

**Returns**:
```json
{
  "estimated_days": 2.5,
  "estimated_date": "2026-02-07T12:00:00",
  "confidence": 0.85
}
```

---

#### 3. Optimize Route

**Name**: `optimize_route`

**Description**: Optimize delivery route for multiple stops

**Parameters**:
- `stops` (array): Array of location objects

**Returns**:
```json
{
  "original_stops": 5,
  "optimized_stops": 5,
  "route": [...],
  "estimated_savings_km": 25,
  "optimization_id": "uuid"
}
```

---

#### 4. Track Shipment

**Name**: `track_shipment`

**Description**: Track shipment location and status

**Parameters**:
- `tracking_number` (string): Shipment tracking number

**Returns**:
```json
{
  "tracking_number": "SHIP001",
  "status": "in_transit",
  "current_location": {
    "city": "Chicago",
    "state": "IL",
    "country": "US"
  },
  "last_update": "2026-02-05T12:00:00",
  "estimated_delivery": "2026-02-07T12:00:00"
}
```

---

### Compliance Tools

#### 5. Validate Customs Documentation

**Name**: `validate_customs_documentation`

**Description**: Validate customs documentation for international shipments

**Parameters**:
- `documents` (array): Array of document names

**Required Documents**:
- `commercial_invoice`
- `packing_list`
- `certificate_of_origin`

**Returns**:
```json
{
  "valid": false,
  "missing_documents": ["certificate_of_origin"],
  "provided_documents": ["commercial_invoice", "packing_list"],
  "message": "Missing: certificate_of_origin"
}
```

**Example**:
```bash
curl -X POST http://localhost:8002/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "validate_customs_documentation",
    "parameters": {
      "documents": ["commercial_invoice", "packing_list"]
    }
  }'
```

---

#### 6. Check Compliance Status

**Name**: `check_compliance_status`

**Description**: Check compliance status for a shipment

**Parameters**:
- `shipment_type` (string): Type of shipment (e.g., "general", "hazmat")
- `destination_country` (string): Destination country code

**Returns**:
```json
{
  "compliant": true,
  "issues": [],
  "warnings": ["May require additional customs processing time"],
  "checked_at": "2026-02-05T12:00:00"
}
```

---

## API Endpoints

### List Tools

**Endpoint**: `GET /tools`

**Query Parameters**:
- `category` (optional): Filter by category ("logistics" or "compliance")

**Response**:
```json
{
  "tools": [
    {
      "name": "calculate_shipping_cost",
      "description": "...",
      "parameters": {...},
      "category": "logistics",
      "handler": "calculate_shipping_cost"
    },
    ...
  ]
}
```

**Examples**:
```bash
# List all tools
curl http://localhost:8002/tools

# List logistics tools only
curl http://localhost:8002/tools?category=logistics

# List compliance tools only
curl http://localhost:8002/tools?category=compliance
```

---

### Execute Tool

**Endpoint**: `POST /tools/execute`

**Request Body**:
```json
{
  "tool_name": "string",
  "parameters": {
    ...
  }
}
```

**Response (Success)**:
```json
{
  "result": {
    ...
  },
  "status": "success"
}
```

**Response (Error)**:
```json
{
  "detail": "Error message",
  "status": "error"
}
```

---

## Tool Registry Implementation

### Registering a Tool

```python
from infrastructure.mcp.registry import MCPTool, tool_registry

# Define tool metadata
tool = MCPTool(
    name="my_custom_tool",
    description="My custom supply chain tool",
    parameters={
        "param1": "type",
        "param2": "type"
    },
    category="logistics",
    handler="my_custom_tool"
)

# Define handler function
async def my_custom_tool(params: dict[str, Any]) -> dict[str, Any]:
    # Tool implementation
    result = process_params(params)
    return {"result": result}

# Register tool
tool_registry.register_tool(tool, my_custom_tool)
```

---

### Executing a Tool

```python
# Via API
result = await tool_registry.execute_tool(
    "calculate_shipping_cost",
    {
        "weight_kg": 10,
        "distance_km": 500,
        "priority": "express"
    }
)

# Or via HTTP
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8002/tools/execute",
        json={
            "tool_name": "calculate_shipping_cost",
            "parameters": {
                "weight_kg": 10,
                "distance_km": 500,
                "priority": "express"
            }
        }
    )
    result = response.json()
```

---

## A2A Integration

Tools can be invoked via the A2A protocol:

```python
from infrastructure.a2a.protocol import JSONRPCRequest, TaskRequest

request = JSONRPCRequest[TaskRequest](
    method="task",
    params=TaskRequest(
        task_type="execute_tool",
        payload={
            "tool_name": "calculate_shipping_cost",
            "parameters": {
                "weight_kg": 10,
                "distance_km": 500,
                "priority": "express"
            }
        }
    )
)

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8002/a2a/task",
        json=request.model_dump()
    )
```

---

## Tool Categories

| Category | Purpose | Example Tools |
|----------|---------|---------------|
| `logistics` | Shipping and delivery operations | calculate_cost, optimize_route, track |
| `compliance` | Regulatory and documentation | validate_docs, check_status |
| `inventory` | (Future) Inventory management | check_stock, reorder |
| `finance` | (Future) Financial operations | calculate_duties, process_payment |

---

## Error Handling

### Tool Not Found

```json
{
  "detail": "Tool not found: invalid_tool_name",
  "status": "error"
}
```

### Invalid Parameters

```json
{
  "detail": "Missing required parameter: weight_kg",
  "status": "error"
}
```

### Execution Error

```json
{
  "detail": "Tool execution failed: Division by zero",
  "status": "error"
}
```

---

## Best Practices

### 1. Parameter Validation

```python
async def my_tool(params: dict[str, Any]) -> dict[str, Any]:
    # Validate required parameters
    if "required_param" not in params:
        raise ValueError("Missing required parameter: required_param")
    
    # Validate types
    weight = float(params.get("weight_kg", 0))
    if weight <= 0:
        raise ValueError("Weight must be positive")
    
    return {"result": "success"}
```

### 2. Return Structured Data

```python
# Good - structured response
return {
    "cost_usd": 112.5,
    "currency": "USD",
    "breakdown": {...}
}

# Bad - unstructured
return {"message": "Cost is $112.50"}
```

### 3. Handle Edge Cases

```python
async def calculate_cost(params: dict[str, Any]) -> dict[str, Any]:
    distance = params.get("distance_km", 0)
    
    # Handle zero distance
    if distance == 0:
        return {
            "cost_usd": 0,
            "message": "Local pickup - no shipping cost"
        }
    
    # Calculate normally
    return {"cost_usd": calculate(distance)}
```

### 4. Use Type Hints

```python
from typing import Any

async def my_tool(params: dict[str, Any]) -> dict[str, Any]:
    """
    Tool implementation with proper typing
    
    Args:
        params: Tool parameters
        
    Returns:
        Tool execution result
    """
    pass
```

---

## Testing Tools

### Unit Testing

```python
import pytest
from application.tools.supply_chain_tools import calculate_shipping_cost

@pytest.mark.asyncio
async def test_calculate_shipping_cost():
    result = await calculate_shipping_cost({
        "weight_kg": 10,
        "distance_km": 500,
        "priority": "express"
    })
    
    assert "cost_usd" in result
    assert result["cost_usd"] > 0
    assert result["currency"] == "USD"
```

### Integration Testing

```bash
# Test via API
curl -X POST http://localhost:8002/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "calculate_shipping_cost", "parameters": {...}}'
```

---

## Adding New Tools

### Step 1: Define Tool Function

Create in `services/mcp-tool-service/src/application/tools/my_tools.py`:

```python
async def my_new_tool(params: dict[str, Any]) -> dict[str, Any]:
    """My new tool implementation"""
    param1 = params.get("param1")
    param2 = params.get("param2")
    
    # Tool logic here
    result = process(param1, param2)
    
    return {"result": result}
```

### Step 2: Register Tool

In `services/mcp-tool-service/src/main.py`:

```python
from application.tools.my_tools import my_new_tool

def register_tools():
    tools = [
        # ... existing tools ...
        (
            MCPTool(
                name="my_new_tool",
                description="Description of my new tool",
                parameters={
                    "param1": "type",
                    "param2": "type"
                },
                category="logistics",
                handler="my_new_tool"
            ),
            my_new_tool
        )
    ]
    
    for tool, handler in tools:
        tool_registry.register_tool(tool, handler)
```

### Step 3: Test

```bash
curl -X POST http://localhost:8002/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "my_new_tool",
    "parameters": {
      "param1": "value1",
      "param2": "value2"
    }
  }'
```

---

## Performance Considerations

- **Async Execution**: All tools use async/await
- **Timeouts**: Set appropriate timeouts for external calls
- **Caching**: Consider caching for expensive computations
- **Rate Limiting**: Implement if tools access external APIs

---

## Future Enhancements

1. **Tool Versioning**: Support multiple versions of the same tool
2. **Authentication**: Require auth for sensitive tools
3. **Quotas**: Rate limiting per agent
4. **Monitoring**: Track tool usage and performance
5. **Webhooks**: Async tool execution with callbacks

---

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)

---

## Support

For questions about MCP tools, see README.md or open a GitHub issue.
