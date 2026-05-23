from fastapi import APIRouter
from app.model.metrics_schema import HostInfo, MetricsSnapshot
import app.service.metrics_service as service

router = APIRouter()


@router.get("/host", response_model=HostInfo)
async def get_host():
    return await service.collect_host_info()


@router.get("/metrics", response_model=MetricsSnapshot)
async def get_metrics():
    return await service.collect_metrics()


@router.get("/health")
async def get_health():
    return {"status": "ok"}
