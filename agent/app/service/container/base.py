from abc import ABC, abstractmethod
from app.models.metrics_schema import ContainerMetrics


class BaseContainerCollector(ABC):
    @abstractmethod
    def collect(self) -> list[ContainerMetrics]:
        pass
