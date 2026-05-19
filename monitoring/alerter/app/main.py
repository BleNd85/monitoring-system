import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import router
from app.api.internal_router import internal_router
from app.db.database import init_db
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting alerter service...")
    await init_db()
    yield


app = FastAPI(title="Alerter Service", lifespan=lifespan)
app.include_router(router, prefix=settings.API_V1_STR)
app.include_router(internal_router, prefix="/internal")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app"
    )
