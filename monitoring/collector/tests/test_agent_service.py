import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.service.agent_service import get_all, get_by_id, register, remove_by_id
from app.model.metrics_schema import AgentInfo, AgentRegisterRequest


def make_agent():
    return AgentInfo(
        agent_id="server-01",
        url="http://192.168.1.100:8200",
        name="Test Server",
    )


@pytest.mark.asyncio
async def test_get_all_returns_agents():
    agents = [make_agent()]
    with patch("app.service.agent_service.agent_registry") as mock_registry:
        mock_registry.get_all.return_value = agents
        result = await get_all()
    assert len(result) == 1
    assert result[0].agent_id == "server-01"


@pytest.mark.asyncio
async def test_get_by_id_returns_agent():
    agent = make_agent()
    with patch("app.service.agent_service.agent_registry") as mock_registry:
        mock_registry.get.return_value = agent
        result = await get_by_id("server-01")
    assert result.agent_id == "server-01"


@pytest.mark.asyncio
async def test_get_by_id_raises_404_when_not_found():
    with patch("app.service.agent_service.agent_registry") as mock_registry:
        mock_registry.get.return_value = None
        with pytest.raises(HTTPException) as exc:
            await get_by_id("unknown")
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_register_saves_agent():
    request = AgentRegisterRequest(url="http://192.168.1.100:8200", name="Test Server")
    host_info_data = {
        "agent_id": "server-01",
        "host": "test-host",
        "ram_total_mb": 8192.0,
        "cpu_count": 8,
        "os": "Linux",
    }

    mock_response = MagicMock()
    mock_response.json.return_value = host_info_data
    mock_response.raise_for_status = MagicMock()

    with patch("app.service.agent_service.httpx.AsyncClient") as mock_client, \
         patch("app.service.agent_service.repository.save_agent", AsyncMock()), \
         patch("app.service.agent_service.agent_registry") as mock_registry:

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        mock_registry.add = MagicMock()

        result = await register(request)

    assert result.agent_id == "server-01"
    assert result.name == "Test Server"
    mock_registry.add.assert_called_once()


@pytest.mark.asyncio
async def test_register_raises_400_when_agent_unreachable():
    request = AgentRegisterRequest(url="http://unreachable:8200", name="Bad Server")

    with patch("app.service.agent_service.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Connection refused")
        )
        with pytest.raises(HTTPException) as exc:
            await register(request)
        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_remove_by_id_removes_agent():
    with patch("app.service.agent_service.repository.delete_agent", AsyncMock(return_value=True)), \
         patch("app.service.agent_service.agent_registry") as mock_registry:

        mock_registry.remove = MagicMock()
        await remove_by_id("server-01")
        mock_registry.remove.assert_called_once_with("server-01")


@pytest.mark.asyncio
async def test_remove_by_id_raises_404_when_not_found():
    with patch("app.service.agent_service.repository.delete_agent", AsyncMock(return_value=False)):
        with pytest.raises(HTTPException) as exc:
            await remove_by_id("unknown")
        assert exc.value.status_code == 404