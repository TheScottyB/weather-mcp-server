#!/usr/bin/env python3
"""
Simple MCP client to test the weather server
"""

import asyncio
import json
import subprocess
import sys
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def test_mcp_server():
    """Test the MCP weather server."""
    print("🧪 Testing Weather MCP Server via MCP Protocol...")
    print("=" * 60)
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["weather.py"],
        env=None
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ Server initialized successfully!")
                
                # List available tools
                print("\n🔧 Listing available tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # List available resources
                print("\n📦 Listing available resources:")
                resources = await session.list_resources()
                for resource in resources.resources:
                    print(f"  - {resource.name}: {resource.description}")
                
                # Test get_current_weather tool
                print("\n🌤️ Testing get_current_weather tool:")
                result = await session.call_tool(
                    "get_current_weather",
                    {"location": "Tokyo", "units": "metric"}
                )
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                
                # Test get_weather_forecast tool
                print("\n📈 Testing get_weather_forecast tool:")
                result = await session.call_tool(
                    "get_weather_forecast",
                    {"location": "London", "days": 2, "units": "imperial"}
                )
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                
                print("\n🎉 All MCP tests completed successfully!")
                
    except Exception as e:
        print(f"❌ Error during MCP test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
