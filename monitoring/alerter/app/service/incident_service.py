import logging
from uuid import UUID
from fastapi import HTTPException
from app.model.schema import AnomalyDetected, IncidentResponse
from app.db import repository
from app.service import notify_service

logger = logging.getLogger(__name__)


async def create(anomaly: AnomalyDetected) -> IncidentResponse:
    record = await repository.save_incident(anomaly)
    await notify_service.send_telegram(anomaly)
    return IncidentResponse.model_validate(record)


async def get_all(limit: int = 100) -> list[IncidentResponse]:
    records = await repository.get_all_incidents(limit)
    return [IncidentResponse.model_validate(r) for r in records]


async def get_by_agent(agent_id: str, limit: int = 100) -> list[IncidentResponse]:
    records = await repository.get_by_agent_id(agent_id, limit)
    return [IncidentResponse.model_validate(r) for r in records]

async def resolve(incident_id: UUID) -> IncidentResponse:
    record = await repository.resolve_incident(incident_id)
    if not record:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse.model_validate(record)
