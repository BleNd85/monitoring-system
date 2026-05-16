from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.service import service as metrics_service
from app.models.metrics_schema import AgentInfo, AgentRegisterRequest
from app.service.agent_registry import agent_registry

router = APIRouter()


@router.get("/agents", response_model=list[AgentInfo])
async def get_all():
    return agent_registry.get_all()


@router.post("/agents", response_model=AgentInfo)
async def add(request: AgentRegisterRequest):
    agent = AgentInfo(agent_id=request.agent_id, url=request.url, name=request.name)
    agent_registry.add(agent)
    return agent


@router.delete("/agents/{agent_id}")
async def remove(agent_id: str):
    if not agent_registry.remove(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "ok"}


@router.get("/health")
async def health():
    return {"status": "ok", "agents": agent_registry.count()}


@router.get("/metrics/{agent_id}/latest")
async def get_latest(agent_id: str):
    return await metrics_service.get_latest(agent_id)


@router.get("/metrics/{agent_id}/range")
async def get_range(
    agent_id: str, start: datetime = Query(...), end: datetime = Query(...)
):
    return await metrics_service.get_range(agent_id=agent_id, start=start, end=end)
