import httpx
from back.core.config import settings

async def get_weather(city: str) -> dict:
    if not settings.WEATHER_API_KEY:
        raise ValueError("Weather API key is not set in the configuration.")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": settings.WEATHER_API_KEY,
                "units": "metric"
            },
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "wind_speed": data["wind"]["speed"],
        }
        