import psutil
import platform
from datetime import datetime, timezone
from app.core.config import settings
from app.service.container.docker import DockerContainerCollector
from app.models.metrics_schema import (
    MetricsSnapshot,
    HostInfo,
    NetworkMetrics,
    DiskMetrics,
    MemoryMetrics,
    CPUMetrics,
)

agent_id = settings.AGENT_ID
agent_host = settings.AGENT_HOST

_prev_disk = None
_prev_net = None
_prev_cpu_times = None

collect_containers = DockerContainerCollector()


async def collect_host_info() -> HostInfo:
    return HostInfo(
        agent_id=agent_id,
        host=agent_host,
        ram_total_mb=psutil.virtual_memory().total / 1024**2,
        cpu_count=psutil.cpu_count(),
        os=platform.system(),
    )


def _cpu_percent(prev, curr) -> float:
    if prev is None:
        return 0.0
    total_diff = sum(curr) - sum(prev)
    if total_diff == 0:
        return 0.0
    return round((1.0 - (curr.idle - prev.idle) / total_diff) * 100.0, 2)


async def collect_metrics() -> MetricsSnapshot:
    global _prev_disk, _prev_net, _prev_cpu_times

    cpu_times = psutil.cpu_times()
    cpu = _cpu_percent(_prev_cpu_times, cpu_times)
    _prev_cpu_times = cpu_times

    load = psutil.getloadavg()
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()

    disk = psutil.disk_io_counters()
    disk_read  = max(0, disk.read_bytes  - _prev_disk.read_bytes)  if _prev_disk else 0
    disk_write = max(0, disk.write_bytes - _prev_disk.write_bytes) if _prev_disk else 0
    _prev_disk = disk

    containers, net_tx, net_rx = collect_containers.collect_with_network()
    net_sent  = max(0, net_tx - _prev_net["sent"])  if _prev_net else 0
    net_recv  = max(0, net_rx - _prev_net["recv"])  if _prev_net else 0
    _prev_net = {"sent": net_tx, "recv": net_rx}

    return MetricsSnapshot(
        agent_id=agent_id,
        timestamp=datetime.now(timezone.utc),
        cpu=CPUMetrics(
            load_percent=cpu,
            load_avg_1m=load[0],
            load_avg_5m=load[1],
            load_avg_15m=load[2],
        ),
        memory=MemoryMetrics(
            ram_percent=ram.percent,
            ram_usage_mb=round(ram.used / 1024**2, 2),
            swap_percent=swap.percent,
            swap_usage_mb=round(swap.used / 1024**2, 2),
        ),
        disk=DiskMetrics(read_bytes=disk_read, write_bytes=disk_write),
        network=NetworkMetrics(sent_bytes=net_sent, received_bytes=net_recv),
        containers=containers,
    )