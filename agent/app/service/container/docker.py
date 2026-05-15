import docker
import logging
from app.service.container.base import BaseContainerCollector
from app.models.metrics_schema import ContainerMetrics

logger = logging.getLogger(__name__)


class DockerContainerCollector(BaseContainerCollector):
    def collect(self) -> list[ContainerMetrics]:
        try:
            client = docker.from_env()
            containers = []
            for container in client.containers.list(all=True):
                stats = container.stats(stream=False)
                cpu_delta = (
                    stats["cpu_stats"]["cpu_usage"]["total_usage"]
                    - stats["precpu_stats"]["cpu_usage"]["total_usage"]
                )
                system_delta = (
                    stats["cpu_stats"]["system_cpu_usage"]
                    - stats["precpu_stats"]["system_cpu_usage"]
                )
                cpu_percent = (
                    (cpu_delta / system_delta) * 100 if system_delta > 0 else 0.0
                )

                mem = stats["memory_stats"]
                ram_used = mem.get("usage", 0) / 1024**2
                ram_limit = mem.get("limit", 0) / 1024**2

                containers.append(
                    ContainerMetrics(
                        name=container.name,
                        cpu_load_percent=round(cpu_percent, 2),
                        ram_usage_mb=round(ram_used, 2),
                        ram_limit_mb=round(ram_limit, 2),
                        status=container.status,
                    )
                )
            return containers
        except Exception as e:
            logger.error(f"Failed to collect container metrics: {e}")
            return []
