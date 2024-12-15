from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.models import Weather
from app.core.schemas import WeatherCreate, WeatherUpdate
from datetime import datetime, timezone


async def get_all_weather(
    session: AsyncSession,
) -> Sequence[Weather]:
    stmt = select(Weather).order_by(Weather.id)
    result = await session.scalars(stmt)
    return result.all()


async def create_weather(
    session: AsyncSession,
    weather_create: WeatherCreate,
) -> Weather:
    weather = Weather(**weather_create.model_dump())
    session.add(weather)
    await session.commit()
    return weather

async def get_weather_by_city(
    session: AsyncSession,
    city_name: str,
) -> Optional[Weather]:
    stmt = select(Weather).where(Weather.city.ilike(city_name))
    result = await session.scalars(stmt)
    return result.first()


async def update_weather(
    session: AsyncSession,
    city_name: str,
    weather_update: WeatherUpdate,
) -> Optional[Weather]:
    weather = await get_weather_by_city(session, city_name)
    if not weather:
        return None

    if weather_update.temperature is not None:
        weather.temperature = weather_update.temperature
    if weather_update.description is not None:
        weather.description = weather_update.description
    weather.timestamp = datetime.now(timezone.utc)

    await session.commit()
    # await session.refresh(weather)
    return weather


async def create_or_update_weather(session: AsyncSession, weather_create: WeatherCreate):
    weather = await get_weather_by_city(session, weather_create.city)
    if weather:
        weather.temperature = weather_create.temperature
        weather.description = weather_create.description
        weather.timestamp = datetime.now(timezone.utc)
    else:
        weather = Weather(
            city=weather_create.city,
            temperature=weather_create.temperature,
            description=weather_create.description,
            timestamp=datetime.now(timezone.utc)
        )
        session.add(weather)
    await session.commit()
    await session.refresh(weather)
    return weather