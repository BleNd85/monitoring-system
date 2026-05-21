import asyncio
import logging
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.pipeline import pipeline_loop
from app.core.config import settings
from app.service import llm_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ML service...")
    await llm_service.warmup()
    task = asyncio.create_task(pipeline_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Pipeline stopped")


app = FastAPI(title="ML Service", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}
