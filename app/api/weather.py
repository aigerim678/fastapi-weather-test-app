from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
import logging


from core.models import User, db_helper
from core.schemas import (
    WeatherRead,
    WeatherCreate,
    WeatherUpdate,
    Token
)
from .crud import weather as weather_crud
from .services.weather import get_weather_from_api 
from core.auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
)




router = APIRouter(tags=["Weather"])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@router.get("", response_model=list[WeatherRead])
async def get_weather(
    # session: AsyncSession = Depends(db_helper.session_getter),
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    weather = await weather_crud.get_all_weather(session=session)
    return weather


@router.post("", response_model=WeatherRead)
async def create_weather(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    weather_create: WeatherCreate,
):
    weather = await weather_crud.create_weather(
        session=session,
        weather_create=weather_create,
    )
    return weather



@router.post("/fetch", response_model=WeatherRead)
async def fetch_and_create_weather(
    city_name: str,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    try:
        # Fetch weather data from the external API
        weather_data = await get_weather_from_api(city_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


    weather_create = WeatherCreate(
        city=weather_data["city"],
        temperature=weather_data["temperature"],
        description=weather_data["description"],
    )

    weather = await weather_crud.create_weather(
        session=session,
        weather_create=weather_create,
    )
    return weather



@router.put("/{city_name}", response_model=WeatherRead)
async def update_weather(
    city_name: str,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    weather_update: WeatherUpdate,
    current_user: User = Depends(get_current_active_user) 
):
    existing_weather = await weather_crud.get_weather_by_city(
        session=session, city_name=city_name
    )
    if not existing_weather:
        raise HTTPException(status_code=404, detail="City not found")

    updated_weather = await weather_crud.update_weather(
        session=session,
        city_name=city_name,
        weather_update=weather_update,
    )
    return updated_weather



@router.get("/{city_name}", response_model=WeatherRead)
async def get_weather_by_city(
    city_name: str,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    weather = await weather_crud.get_weather_by_city(session=session, city_name=city_name)
    now = datetime.now(timezone.utc)
    cache_duration = timedelta(seconds=10)  

    if weather:
        # Проверяем, актуальны ли данные
        if now - weather.timestamp < cache_duration:
            logger.info(f"Returning cached weather data for city: {city_name}")
            return weather

        else:
            # Данные устарели, обращаемся к API
            try:
                weather_data = await get_weather_from_api(city_name)
                logger.info(f"Cached data expired for city: {city_name}. Fetching from API.")
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

            # Обновляем запись в базе данных
            weather_create = WeatherCreate(
                city=weather_data["city"],
                temperature=weather_data["temperature"],
                description=weather_data["description"],
            )
            weather = await weather_crud.create_or_update_weather(session=session, weather_create=weather_create)
            return weather
    else:
        # Данных нет в базе, обращаемся к API
        try:
            weather_data = await get_weather_from_api(city_name)
            logger.info(f"No cached data found for city: {city_name}. Fetching from API.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Создаём новую запись в базе данных
        weather_create = WeatherCreate(
            city=weather_data["city"],
            temperature=weather_data["temperature"],
            description=weather_data["description"],
        )
        weather = await weather_crud.create_or_update_weather(session=session, weather_create=weather_create)
        return weather
    




@router.post("/token", response_model=Token)
async def login_for_access_token(session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ], form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



