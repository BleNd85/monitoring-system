import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from app.service.metrics_service import get_latest, get_range


@pytest.mark.asyncio
async def test_get_latest_returns_snapshot():
    mock_snapshot = {"agent_id": "server-01", "cpu": {"load_percent": 45.0}}

    with patch("app.service.metrics_service.repository.get_latest_snapshot", AsyncMock(return_value=mock_snapshot)):
        result = await get_latest("server-01")

    assert result["agent_id"] == "server-01"


@pytest.mark.asyncio
async def test_get_latest_raises_404_when_not_found():
    with patch("app.service.metrics_service.repository.get_latest_snapshot", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc:
            await get_latest("unknown")
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_range_returns_snapshots():
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=1)
    mock_snapshots = [{"agent_id": "server-01"}, {"agent_id": "server-01"}]

    with patch("app.service.metrics_service.repository.get_snapshot_range", AsyncMock(return_value=mock_snapshots)):
        result = await get_range("server-01", start, now)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_range_raises_400_when_start_after_end():
    now = datetime.now(timezone.utc)
    start = now + timedelta(hours=1)

    with pytest.raises(HTTPException) as exc:
        await get_range("server-01", start, now)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_get_range_raises_400_when_start_equals_end():
    now = datetime.now(timezone.utc)

    with pytest.raises(HTTPException) as exc:
        await get_range("server-01", now, now)
    assert exc.value.status_code == 400