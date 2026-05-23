from pydantic import BaseModel, Field
from datetime import datetime


class CPUMetrics(BaseModel):
    load_percent: float = Field(..., ge=0, le=100)
    load_avg_1m: float = Field(..., ge=0)
    load_avg_5m: float = Field(..., ge=0)
    load_avg_15m: float = Field(..., ge=0)


class MemoryMetrics(BaseModel):
    ram_percent: float = Field(..., ge=0, le=100)
    ram_usage_mb: float = Field(..., ge=0)
    swap_percent: float = Field(..., ge=0, le=100)
    swap_usage_mb: float = Field(..., ge=0)


class DiskMetrics(BaseModel):
    read_bytes: int = Field(..., ge=0)
    write_bytes: int = Field(..., ge=0)


class NetworkMetrics(BaseModel):
    sent_bytes: int = Field(..., ge=0)
    received_bytes: int = Field(..., ge=0)


class ContainerMetrics(BaseModel):
    name: str = Field(..., min_length=1)
    cpu_load_percent: float = Field(..., ge=0, le=100)
    ram_usage_mb: float = Field(..., ge=0)
    ram_limit_mb: float = Field(..., ge=0)
    status: str = Field(...)


class MetricsSnapshot(BaseModel):
    agent_id: str = Field(...)
    timestamp: datetime = Field(...)
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics
    containers: list[ContainerMetrics] = Field(default_factory=list)


class HostInfo(BaseModel):
    agent_id: str = Field(...)
    host: str = Field(...)
    ram_total_mb: float = Field(..., ge=0)
    cpu_count: int = Field(..., ge=1)
    os: str = Field(...)


class AgentInfo(BaseModel):
    agent_id: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class AgentRegisterRequest(BaseModel):
    url: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
