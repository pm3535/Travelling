from os import name

from back.services.weather import get_weather
from back.services.destinations import search_destinations
 
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for available flights between two airports",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "IATA airport code e.g. CDG"},
                    "destination": {"type": "string", "description": "IATA airport code e.g. JFK"},
                    "departure_date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "adults": {"type": "integer", "default": 1},
                },
                "required": ["origin", "destination", "departure_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": "Search for hotels in a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_code": {"type": "string", "description": "IATA city code e.g. PAR"},
                    "check_in": {"type": "string", "description": "YYYY-MM-DD"},
                    "check_out": {"type": "string", "description": "YYYY-MM-DD"},
                    "adults": {"type": "integer", "default": 1},
                },
                "required": ["city_code", "check_in", "check_out"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_destinations",
            "description": "Search travel destinations by name or country",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        },
    },
]
 
async def execute_tool(tool_name: str, parameters: dict) -> dict:
    try:
        if name == "search_flights":
            from back.schemas.schemas import FlightSearchRequest
            from back.services.amadeus import search_flights
            req = FlightSearchRequest(**parameters)
            return await search_flights(req)
        elif name == "search_hotels":
            from back.schemas.schemas import HotelSearchRequest
            from back.services.amadeus import search_hotels
            req = HotelSearchRequest(**parameters)
            return await search_hotels(req)
        elif name == "get_weather":
            city = parameters["city"]
            return await get_weather(city)
        elif name == "search_destinations":
            results = await search_destinations(parameters["query"])
            return {"results": results}
        
        return {"error": f"Unknown tool: {name}"}
    except Exception as e:
         return {"error": str(e)}
          
