from pydantic import BaseModel, Field
from datetime import datetime


class MetricsSnapshot(BaseModel):
    agent_id: str
    timestamp: datetime
    cpu: dict
    memory: dict
    disk: dict
    network: dict
    containers: list[dict] = Field(default_factory=list)


class AnomalyDetected(BaseModel):
    agent_id: str
    timestamp: datetime
    severity: str
    anomaly_type: str
    affected_metrics: dict
    expected_values: dict
    actual_values: dict
    deviation_score: float = Field(..., ge=0.0, le=1.0)
    llm_interpretation: str | None = None


class AgentInfo(BaseModel):
    agent_id: str
    url: str
    name: str
