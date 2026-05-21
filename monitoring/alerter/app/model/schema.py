from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class AnomalyDetected(BaseModel):
    agent_id: str = Field(...)
    timestamp: datetime = Field(...)
    severity: str = Field(...)
    anomaly_type: str = Field(...)
    affected_metrics: dict = Field(...)
    expected_values: dict = Field(default_factory=dict)
    actual_values: dict = Field(default_factory=dict)
    deviation_score: float = Field(..., ge=0.0, le=1.0)
    llm_interpretation: str | None = None


class IncidentResponse(BaseModel):
    id: UUID
    agent_id: str
    timestamp: datetime
    severity: str
    anomaly_type: str
    affected_metrics: dict
    expected_values: dict | None
    actual_values: dict | None
    deviation_score: float | None
    llm_interpretation: str | None
    resolved_at: datetime | None

    class Config:
        from_attributes = True
