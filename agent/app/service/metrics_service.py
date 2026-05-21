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


async def collect_host_info() -> HostInfo:
    return HostInfo(
        agent_id=agent_id,
        host=agent_host,
        ram_total_mb=psutil.virtual_memory().total / 1024**2,
        cpu_count=psutil.cpu_count(),
        os=platform.system(),
    )


collect_containers = DockerContainerCollector()


async def collect_metrics() -> MetricsSnapshot:
    global _prev_disk, _prev_net

    cpu = psutil.cpu_percent()
    load = psutil.getloadavg()
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_io_counters()
    network = psutil.net_io_counters()

    if _prev_disk is None:
        disk_read = 0
        disk_write = 0
    else:
        disk_read = max(0, disk.read_bytes - _prev_disk.read_bytes)
        disk_write = max(0, disk.write_bytes - _prev_disk.write_bytes)

    if _prev_net is None:
        net_sent = 0
        net_recv = 0
    else:
        net_sent = max(0, network.bytes_sent - _prev_net.bytes_sent)
        net_recv = max(0, network.bytes_recv - _prev_net.bytes_recv)

    _prev_disk = disk
    _prev_net = network

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
        network=NetworkMetrics(
            sent_bytes=net_sent, received_bytes=net_recv
        ),
        containers=collect_containers.collect(),
    )
