import aiohttp  
from core.config import settings


API_KEY = settings.openweather_api_key
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

async def get_weather_from_api(city_name: str):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL, params=params) as response:
            data = await response.json() 
            if response.status == 200:
                return {
                    "city": data["name"],
                    "temperature": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                }
            else:
                error_message = data.get("message", "Unknown error")
                raise Exception(f"OpenWeatherMap API error: {error_message}")
