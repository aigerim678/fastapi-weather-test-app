from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WeatherBase(BaseModel):
    city: str

class WeatherCreate(WeatherBase):
    temperature: float
    description: str

class WeatherRead(BaseModel):
    id: int
    city: str
    temperature: float
    description: str
    timestamp: datetime

class WeatherUpdate(BaseModel):
    temperature: Optional[float] = None
    description: Optional[str] = None

