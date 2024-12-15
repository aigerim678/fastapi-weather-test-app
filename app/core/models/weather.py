from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, String, Float
from sqlalchemy import DateTime
from datetime import datetime, timezone

from .base import Base



class Weather(Base):
    __tablename__ = "weather_data"

    city: Mapped[str] = mapped_column(String)
    temperature: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False)

