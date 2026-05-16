import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import router
from app.db.database import init_db
from app.service.agent_poller import polling_loop
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting collector service...")
    await init_db()
    task = asyncio.create_task(polling_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Polling loop stopped")


app = FastAPI(title="Collector Service", lifespan=lifespan)
app.include_router(router=router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app"
    )