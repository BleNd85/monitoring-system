from fastapi import APIRouter
from app.model.schema import AnomalyDetected, IncidentResponse
from app.service import incident_service

internal_router = APIRouter()


@internal_router.post("/incidents", response_model=IncidentResponse)
async def create_incident(anomaly: AnomalyDetected):
    return await incident_service.create(anomaly)
