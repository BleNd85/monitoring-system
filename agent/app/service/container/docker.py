import docker
import logging
from concurrent.futures import ThreadPoolExecutor
from app.service.container.base import BaseContainerCollector
from app.models.metrics_schema import ContainerMetrics

logger = logging.getLogger(__name__)


class DockerContainerCollector(BaseContainerCollector):
    def _colect_single(self, container) -> ContainerMetrics | None:
        try:
            stats = container.stats(stream=False)

            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})

            cpu_delta = cpu_stats.get("cpu_usage", {}).get(
                "total_usage", 0
            ) - precpu_stats.get("cpu_usage", {}).get("total_usage", 0)

            system_delta = cpu_stats.get("system_cpu_usage", 0) - precpu_stats.get(
                "system_cpu_usage", 0
            )

            cpu_percent = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0.0

            mem = stats.get("memory_stats", {})
            ram_used = mem.get("usage", 0) / 1024**2
            ram_limit = mem.get("limit", 0) / 1024**2

            return ContainerMetrics(
                name=container.name,
                cpu_load_percent=round(cpu_percent, 2),
                ram_usage_mb=round(ram_used, 2),
                ram_limit_mb=round(ram_limit, 2),
                status=container.status,
            )

        except Exception as e:
            logger.warning(f"Skipping container {container.name}: {e}")
            return None

    def collect(self):
        try:
            client = docker.from_env()
            all_containers = client.containers.list(all=True)

            with ThreadPoolExecutor() as executor:
                results = list(executor.map(self._colect_single, all_containers))

            return [r for r in results if r is not None]
        except Exception as e:
            logger.error(f"Failed to collect container metrics: {e}")
            return []
