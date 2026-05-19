from uuid import UUID
from fastapi import APIRouter, Query
from app.model.schema import IncidentResponse
from app.service import incident_service

router = APIRouter()


@router.get("/incidents", response_model=list[IncidentResponse])
async def get_all(limit: int = Query(100, ge=1, le=1000)):
    return await incident_service.get_all(limit)


@router.get("/incidents/{agent_id}", response_model=list[IncidentResponse])
async def get_by_agent_id(agent_id: str, limit: int = Query(100, ge=1, le=1000)):
    return await incident_service.get_by_agent(agent_id, limit)


@router.patch("/incidents/{incident_id}", response_model=IncidentResponse)
async def resolve(incident_id: UUID):
    return await incident_service.resolve(incident_id)


@router.get("/health")
async def health():
    return {"status": "ok"}
