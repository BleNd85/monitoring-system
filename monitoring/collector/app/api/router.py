from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.service import metrics_service
from app.models.metrics_schema import AgentInfo, AgentRegisterRequest
from app.service import agent_service

router = APIRouter()


@router.get("/agents", response_model=list[AgentInfo])
async def get_all():
    return await agent_service.get_all()


@router.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent_by_id(agent_id: str):
    return await agent_service.get_by_id(agent_id)


@router.post("/agents", response_model=AgentInfo)
async def add(request: AgentRegisterRequest):
    return await agent_service.register(request)


@router.delete("/agents/{agent_id}")
async def delete_by_id(agent_id: str):
    await agent_service.remove_by_id(agent_id)
    return {"status": "ok"}


@router.get("/health")
async def health():
    return await agent_service.health()


@router.get("/metrics/{agent_id}/latest")
async def get_latest(agent_id: str):
    return await metrics_service.get_latest(agent_id)


@router.get("/metrics/{agent_id}/range")
async def get_range(
    agent_id: str, start: datetime = Query(...), end: datetime = Query(...)
):
    return await metrics_service.get_range(agent_id=agent_id, start=start, end=end)
