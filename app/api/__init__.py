from fastapi import APIRouter

from core.config import settings

from .weather import router as weather_router
from .user import router as user_router


router = APIRouter(
    prefix="/v1",
)
router.include_router(
    weather_router,
    prefix="/weather",
)
router.include_router(
    user_router,
    prefix="/user",
)