import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from fastapi.responses import ORJSONResponse

from core.models import db_helper
from core.config import settings
from api import router

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    #shutdown
    await db_helper.dispose()

app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan = lifespan
)

app.include_router(
    router,
    prefix=settings.api.prefix
)


if __name__ == "__main__":
    uvicorn.run(
        app="main:app", 
        host=settings.run.host,
        port=settings.run.port,
        reload=True)

