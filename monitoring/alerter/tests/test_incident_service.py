import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from app.service.incident_service import create, get_all, get_by_agent, resolve
from app.model.schema import AnomalyDetected, IncidentResponse


def make_anomaly():
    return AnomalyDetected(
        agent_id="test-agent",
        timestamp=datetime.now(timezone.utc),
        severity="warning",
        anomaly_type="cpu_spike",
        affected_metrics={"cpu_load_percent": 90.0},
        expected_values={"cpu_load_percent": 40.0},
        actual_values={"cpu_load_percent": 90.0},
        deviation_score=0.82,
        llm_interpretation="High CPU load detected.",
    )


def make_record(anomaly: AnomalyDetected):
    record = MagicMock()
    record.id = uuid4()
    record.agent_id = anomaly.agent_id
    record.timestamp = anomaly.timestamp
    record.severity = anomaly.severity
    record.anomaly_type = anomaly.anomaly_type
    record.affected_metrics = anomaly.affected_metrics
    record.expected_values = anomaly.expected_values
    record.actual_values = anomaly.actual_values
    record.deviation_score = anomaly.deviation_score
    record.llm_interpretation = anomaly.llm_interpretation
    record.resolved_at = None
    return record


@pytest.mark.asyncio
async def test_create_saves_and_notifies():
    anomaly = make_anomaly()
    record = make_record(anomaly)

    with patch("app.service.incident_service.repository.save_incident", AsyncMock(return_value=record)), \
         patch("app.service.incident_service.notify_service.send_telegram", AsyncMock()) as mock_notify, \
         patch.object(IncidentResponse, "model_validate", return_value=MagicMock()):

        await create(anomaly)
        mock_notify.assert_called_once_with(anomaly)


@pytest.mark.asyncio
async def test_get_all_returns_list():
    anomaly = make_anomaly()
    records = [make_record(anomaly) for _ in range(3)]

    with patch("app.service.incident_service.repository.get_all_incidents", AsyncMock(return_value=records)), \
         patch.object(IncidentResponse, "model_validate", side_effect=lambda r: MagicMock()):

        result = await get_all(limit=100)
        assert len(result) == 3


@pytest.mark.asyncio
async def test_get_by_agent_returns_filtered_list():
    anomaly = make_anomaly()
    records = [make_record(anomaly)]

    with patch("app.service.incident_service.repository.get_by_agent_id", AsyncMock(return_value=records)), \
         patch.object(IncidentResponse, "model_validate", side_effect=lambda r: MagicMock()):

        result = await get_by_agent("test-agent", limit=50)
        assert len(result) == 1


@pytest.mark.asyncio
async def test_resolve_returns_response():
    anomaly = make_anomaly()
    record = make_record(anomaly)
    incident_id = record.id

    with patch("app.service.incident_service.repository.resolve_incident", AsyncMock(return_value=record)), \
         patch.object(IncidentResponse, "model_validate", return_value=MagicMock()):

        result = await resolve(incident_id)
        assert result is not None


@pytest.mark.asyncio
async def test_resolve_raises_404_when_not_found():
    with patch("app.service.incident_service.repository.resolve_incident", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await resolve(uuid4())
        assert exc.value.status_code == 404