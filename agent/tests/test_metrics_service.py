import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.service.metrics_service import collect_host_info, collect_metrics, _cpu_percent


def test_cpu_percent_returns_zero_when_prev_is_none():
    curr = MagicMock()
    assert _cpu_percent(None, curr) == 0.0


def test_cpu_percent_returns_zero_when_no_diff():
    prev = MagicMock()
    curr = MagicMock()
    prev.__iter__ = MagicMock(return_value=iter([100, 50, 50]))
    curr.__iter__ = MagicMock(return_value=iter([100, 50, 50]))
    with patch("builtins.sum", side_effect=[200, 200]):
        result = _cpu_percent(prev, curr)
    assert result == 0.0


def test_cpu_percent_calculates_correctly():
    prev = MagicMock(idle=50.0)
    curr = MagicMock(idle=60.0)
    with patch("builtins.sum", side_effect=[250.0, 200.0]):
        result = _cpu_percent(prev, curr)
    assert result == 80.0


@pytest.mark.asyncio
async def test_collect_host_info_returns_host_info():
    with patch("app.service.metrics_service.psutil.virtual_memory") as mock_vm, patch(
        "app.service.metrics_service.psutil.cpu_count", return_value=8
    ), patch(
        "app.service.metrics_service.platform.system", return_value="Linux"
    ), patch(
        "app.service.metrics_service.agent_id", "test-agent"
    ), patch(
        "app.service.metrics_service.agent_host", "test-host"
    ):

        mock_vm.return_value = MagicMock(total=8 * 1024**3)
        result = await collect_host_info()

    assert result.agent_id == "test-agent"
    assert result.host == "test-host"
    assert result.cpu_count == 8
    assert result.os == "Linux"
    assert result.ram_total_mb == pytest.approx(8192.0, rel=1e-3)


@pytest.mark.asyncio
async def test_collect_metrics_returns_snapshot():
    mock_cpu_times = MagicMock(idle=100.0)
    mock_vm = MagicMock(percent=55.0, used=4 * 1024**3)
    mock_swap = MagicMock(percent=10.0, used=512 * 1024**2)
    mock_disk = MagicMock(read_bytes=2000, write_bytes=3000)

    # реальний ContainerMetrics замість MagicMock
    from app.model.metrics_schema import ContainerMetrics

    mock_containers = [
        ContainerMetrics(
            name="test-container",
            cpu_load_percent=5.0,
            ram_usage_mb=128.0,
            ram_limit_mb=512.0,
            status="running",
        )
    ]

    with patch(
        "app.service.metrics_service.psutil.cpu_times", return_value=mock_cpu_times
    ), patch(
        "app.service.metrics_service.psutil.getloadavg", return_value=(1.0, 0.8, 0.5)
    ), patch(
        "app.service.metrics_service.psutil.virtual_memory", return_value=mock_vm
    ), patch(
        "app.service.metrics_service.psutil.swap_memory", return_value=mock_swap
    ), patch(
        "app.service.metrics_service.psutil.disk_io_counters", return_value=mock_disk
    ), patch(
        "app.service.metrics_service.collect_containers"
    ) as mock_collector, patch(
        "app.service.metrics_service._prev_disk", mock_disk
    ), patch(
        "app.service.metrics_service._prev_net", {"sent": 1000, "recv": 500}
    ), patch(
        "app.service.metrics_service._prev_cpu_times", mock_cpu_times
    ):

        mock_collector.collect_with_network.return_value = (mock_containers, 2000, 1500)
        result = await collect_metrics()

    assert result.cpu.load_avg_1m == 1.0
    assert result.memory.ram_percent == 55.0
    assert result.memory.swap_percent == 10.0
    assert result.network.sent_bytes == 1000
    assert result.network.received_bytes == 1000
    assert len(result.containers) == 1
    assert result.containers[0].name == "test-container"
