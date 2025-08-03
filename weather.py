#!/usr/bin/env python3
"""
Weather MCP Server

A Model Context Protocol server that provides weather information using a weather API.
"""

import asyncio
import logging
from typing import Any, Sequence

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities, ResourcesCapability, ToolsCapability
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-server")

# Weather API configuration
WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
API_KEY = "your_api_key_here"  # Replace with actual API key or use environment variable

class WeatherServer:
    def __init__(self):
        self.server = Server("weather-server")
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available weather resources."""
            return [
                Resource(
                    uri=AnyUrl("weather://current"),
                    name="Current Weather",
                    description="Get current weather information for a location",
                    mimeType="application/json",
                ),
                Resource(
                    uri=AnyUrl("weather://forecast"),
                    name="Weather Forecast",
                    description="Get weather forecast for a location",
                    mimeType="application/json",
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: AnyUrl) -> str:
            """Read weather resource content."""
            if str(uri) == "weather://current":
                return "Current weather data resource - use get_current_weather tool"
            elif str(uri) == "weather://forecast":
                return "Weather forecast data resource - use get_weather_forecast tool"
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available weather tools."""
            return [
                Tool(
                    name="get_current_weather",
                    description="Get current weather information for a specific location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city name or coordinates (lat,lon)"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial", "kelvin"],
                                "default": "metric",
                                "description": "Temperature units"
                            }
                        },
                        "required": ["location"]
                    }
                ),
                Tool(
                    name="get_weather_forecast",
                    description="Get weather forecast for a specific location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city name or coordinates (lat,lon)"
                            },
                            "days": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                                "default": 3,
                                "description": "Number of forecast days"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["metric", "imperial", "kelvin"],
                                "default": "metric",
                                "description": "Temperature units"
                            }
                        },
                        "required": ["location"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "get_current_weather":
                    return await self.get_current_weather(
                        arguments["location"],
                        arguments.get("units", "metric")
                    )
                elif name == "get_weather_forecast":
                    return await self.get_weather_forecast(
                        arguments["location"],
                        arguments.get("days", 3),
                        arguments.get("units", "metric")
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def get_current_weather(self, location: str, units: str = "metric") -> list[TextContent]:
        """Get current weather for a location."""
        async with httpx.AsyncClient() as client:
            try:
                # For demo purposes, using a mock response since we don't have an API key
                # In a real implementation, you would use:
                # url = f"{WEATHER_API_BASE}/weather"
                # params = {"q": location, "appid": API_KEY, "units": units}
                # response = await client.get(url, params=params)
                # data = response.json()
                
                # Mock weather data
                mock_data = {
                    "location": location,
                    "temperature": "22°C" if units == "metric" else "72°F",
                    "description": "Partly cloudy",
                    "humidity": "65%",
                    "wind_speed": "10 km/h" if units == "metric" else "6 mph",
                    "units": units
                }
                
                weather_text = f"""Current Weather for {location}:
🌡️ Temperature: {mock_data['temperature']}
☁️ Conditions: {mock_data['description']}
💧 Humidity: {mock_data['humidity']}
💨 Wind Speed: {mock_data['wind_speed']}"""
                
                return [TextContent(type="text", text=weather_text)]
                
            except Exception as e:
                logger.error(f"Error fetching weather data: {e}")
                return [TextContent(type="text", text=f"Failed to fetch weather data: {str(e)}")]
    
    async def get_weather_forecast(self, location: str, days: int = 3, units: str = "metric") -> list[TextContent]:
        """Get weather forecast for a location."""
        async with httpx.AsyncClient() as client:
            try:
                # Mock forecast data
                forecast_text = f"Weather Forecast for {location} ({days} days):\n\n"
                
                for i in range(days):
                    day = f"Day {i + 1}"
                    temp_high = 25 + i if units == "metric" else 77 + i * 2
                    temp_low = 15 + i if units == "metric" else 59 + i * 2
                    temp_unit = "°C" if units == "metric" else "°F"
                    
                    forecast_text += f"""📅 {day}:
   🌡️ High: {temp_high}{temp_unit}, Low: {temp_low}{temp_unit}
   ☁️ Conditions: {'Sunny' if i % 2 == 0 else 'Cloudy'}
   🌧️ Precipitation: {10 + i * 5}%

"""
                
                return [TextContent(type="text", text=forecast_text)]
                
            except Exception as e:
                logger.error(f"Error fetching forecast data: {e}")
                return [TextContent(type="text", text=f"Failed to fetch forecast data: {str(e)}")]
    
    async def run(self):
        """Run the server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="weather-server",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        resources=ResourcesCapability(subscribe=False, listChanged=False),
                        tools=ToolsCapability(listChanged=False)
                    )
                ),
            )

def main():
    """Main entry point."""
    weather_server = WeatherServer()
    asyncio.run(weather_server.run())

if __name__ == "__main__":
    main()
