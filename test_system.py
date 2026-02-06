#!/usr/bin/env python3
"""Test script to demonstrate the Supply Chain Multi-Agent system"""

import asyncio
import json
from datetime import datetime, timedelta

import httpx


async def main():
    """Run the complete workflow test"""
    print("🚀 Testing Supply Chain Multi-Agent System\n")
    print("=" * 60)
    
    # 1. Check service health
    print("\n1. Checking service health...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        orchestrator_health = await client.get("http://localhost:8000/health")
        mcp_health = await client.get("http://localhost:8002/health")
        
        print(f"   Orchestrator: {orchestrator_health.json()}")
        print(f"   MCP Tool Service: {mcp_health.json()}")
    
    # 2. List registered agents
    print("\n2. Listing registered agents...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("http://localhost:8000/agents")
        agents = response.json()["agents"]
        print(f"   Found {len(agents)} agent(s):")
        for agent in agents:
            print(f"   - {agent['name']} ({agent['agent_type']}) - {agent['agent_id']}")
    
    # 3. List MCP tools
    print("\n3. Listing MCP tools...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("http://localhost:8002/tools")
        tools = response.json()["tools"]
        print(f"   Found {len(tools)} tool(s):")
        for tool in tools:
            print(f"   - {tool['name']} ({tool['category']}): {tool['description']}")
    
    # 4. Execute a tool
    print("\n4. Testing tool execution (calculate_shipping_cost)...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "http://localhost:8002/tools/execute",
            json={
                "tool_name": "calculate_shipping_cost",
                "parameters": {
                    "weight_kg": 15.5,
                    "distance_km": 750,
                    "priority": "express"
                }
            }
        )
        result = response.json()
        print(f"   Result: {json.dumps(result, indent=2)}")
    
    # 5. Execute another tool
    print("\n5. Testing compliance validation...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "http://localhost:8002/tools/execute",
            json={
                "tool_name": "validate_customs_documentation",
                "parameters": {
                    "documents": ["commercial_invoice", "packing_list"]
                }
            }
        )
        result = response.json()
        print(f"   Result: {json.dumps(result, indent=2)}")
    
    # 6. Create a shipment
    print("\n6. Creating a shipment...")
    shipment_data = {
        "tracking_number": "TEST-001",
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
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "http://localhost:8000/shipments",
            json=shipment_data
        )
        shipment = response.json()
        print(f"   Created shipment: {shipment['shipment']['tracking_number']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("\n📊 Dashboard available at: http://localhost:3000")
    print("🔌 Orchestrator API: http://localhost:8000")
    print("🛠️  MCP Tool Service: http://localhost:8002")
    print("\nConnect to the dashboard to see real-time events!")


if __name__ == "__main__":
    asyncio.run(main())
