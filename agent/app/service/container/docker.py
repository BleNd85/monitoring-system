import docker
import logging
from concurrent.futures import ThreadPoolExecutor
from app.service.container.base import BaseContainerCollector
from app.models.metrics_schema import ContainerMetrics

logger = logging.getLogger(__name__)


class DockerContainerCollector(BaseContainerCollector):

    def _collect_single(self, container) -> tuple[ContainerMetrics | None, int, int]:
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
            cpu_percent = (
                (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            )

            mem = stats.get("memory_stats", {})
            ram_used = mem.get("usage", 0) / 1024**2
            ram_limit = mem.get("limit", 0) / 1024**2

            networks = stats.get("networks", {})
            net_tx = sum(v.get("tx_bytes", 0) for v in networks.values())
            net_rx = sum(v.get("rx_bytes", 0) for v in networks.values())

            return (
                ContainerMetrics(
                    name=container.name,
                    cpu_load_percent=round(cpu_percent, 2),
                    ram_usage_mb=round(ram_used, 2),
                    ram_limit_mb=round(ram_limit, 2),
                    status=container.status,
                ),
                net_tx,
                net_rx,
            )

        except Exception as e:
            logger.warning("Skipping container %s: %s", container.name, e)
            return None, 0, 0

    def collect(self) -> list[ContainerMetrics]:
        containers, _, _ = self.collect_with_network()
        return containers

    def collect_with_network(self) -> tuple[list[ContainerMetrics], int, int]:
        try:
            client = docker.from_env()
            with ThreadPoolExecutor() as executor:
                results = list(
                    executor.map(self._collect_single, client.containers.list(all=True))
                )
            return (
                [r[0] for r in results if r[0] is not None],
                sum(r[1] for r in results),
                sum(r[2] for r in results),
            )
        except Exception as e:
            logger.error("Failed to collect container metrics: %s", e)
            return [], 0, 0
