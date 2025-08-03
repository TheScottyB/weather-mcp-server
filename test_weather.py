#!/usr/bin/env python3
"""
Test script for the Weather MCP Server
"""

import asyncio
import json
from weather import WeatherServer

async def test_weather_server():
    """Test the weather server functionality."""
    server = WeatherServer()
    
    print("🧪 Testing Weather MCP Server...")
    print("=" * 50)
    
    # Test current weather
    print("\n📍 Testing get_current_weather tool:")
    try:
        result = await server.get_current_weather("San Francisco", "metric")
        print("✅ Success!")
        print(result[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test weather forecast
    print("\n📍 Testing get_weather_forecast tool:")
    try:
        result = await server.get_weather_forecast("New York", 3, "imperial")
        print("✅ Success!")
        print(result[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test list tools
    print("\n🔧 Testing list_tools:")
    try:
        tools = await server.server._handlers['list_tools']()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test list resources
    print("\n📦 Testing list_resources:")
    try:
        resources = await server.server._handlers['list_resources']()
        print(f"✅ Found {len(resources)} resources:")
        for resource in resources:
            print(f"  - {resource.name}: {resource.description}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_weather_server())
