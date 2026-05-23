import logging
from datetime import datetime, timezone
from app.db.database import (
    AsyncSessionLocal,
    MetricsRecord,
    ContainerRecord,
    AgentRecord,
)
from sqlalchemy import select, desc
from app.model.metrics_schema import MetricsSnapshot, AgentInfo

logger = logging.getLogger(__name__)


async def save_agent(agent: AgentInfo) -> None:
    async with AsyncSessionLocal() as session:
        try:
            existing = await session.get(AgentRecord, agent.agent_id)
            if existing:
                existing.url = agent.url
                existing.name = agent.name
            else:
                record = AgentRecord(
                    agent_id=agent.agent_id,
                    url=agent.url,
                    name=agent.name,
                    registered_at=datetime.now(timezone.utc),
                )
                session.add(record)
            await session.commit()
            logger.info("Saved agent: %s", agent.agent_id)
        except Exception as e:
            await session.rollback()
            logger.error("Failed to save agent: %s", e)


async def delete_agent(agent_id: str) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            record = await session.get(AgentRecord, agent_id)
            if not record:
                return False
            await session.delete(record)
            await session.commit()
            logger.info("Deleted agent: %s", agent_id)
            return True
        except Exception as e:
            await session.rollback()
            logger.error("Failed to delete agent: %s", e)
            raise


async def get_all_agents() -> list[AgentInfo]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AgentRecord))
        records = list(result.scalars().all())
        return [AgentInfo(agent_id=r.agent_id, url=r.url, name=r.name) for r in records]


async def get_agent(agent_id: str) -> AgentInfo | None:
    async with AsyncSessionLocal() as session:
        record = await session.get(AgentRecord, agent_id)
        if not record:
            return None
        return AgentInfo(agent_id=record.agent_id, url=record.url, name=record.name)


async def save_snapshot(snapshot: MetricsSnapshot):
    async with AsyncSessionLocal() as session:
        try:
            record = MetricsRecord(
                time=snapshot.timestamp,
                agent_id=snapshot.agent_id,
                cpu_load_percent=snapshot.cpu.load_percent,
                load_avg_1m=snapshot.cpu.load_avg_1m,
                load_avg_5m=snapshot.cpu.load_avg_5m,
                load_avg_15m=snapshot.cpu.load_avg_15m,
                ram_percent=snapshot.memory.ram_percent,
                ram_usage_mb=snapshot.memory.ram_usage_mb,
                swap_percent=snapshot.memory.swap_percent,
                swap_usage_mb=snapshot.memory.swap_usage_mb,
                disk_read_bytes=snapshot.disk.read_bytes,
                disk_write_bytes=snapshot.disk.write_bytes,
                net_sent_bytes=snapshot.network.sent_bytes,
                net_received_bytes=snapshot.network.received_bytes,
            )
            session.add(record)

            for container in snapshot.containers:
                c_record = ContainerRecord(
                    time=snapshot.timestamp,
                    agent_id=snapshot.agent_id,
                    name=container.name,
                    cpu_load_percent=container.cpu_load_percent,
                    ram_usage_mb=container.ram_usage_mb,
                    ram_limit_mb=container.ram_limit_mb,
                    status=container.status,
                )
                session.add(c_record)

            await session.commit()
            logger.info("Saved snapshot for agent: %s", snapshot.agent_id)
        except Exception as e:
            await session.rollback()
            logger.error("Failed to save snapshot: %s", e)
            raise


async def get_latest_snapshot(agent_id: str) -> dict | None:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(MetricsRecord)
                .where(MetricsRecord.agent_id == agent_id)
                .order_by(desc(MetricsRecord.time))
                .limit(1)
            )
            record = result.scalar_one_or_none()
            if not record:
                logger.warning("No snapshot found for agent: %s", agent_id)
                return None

            containers_result = await session.execute(
                select(ContainerRecord).where(
                    ContainerRecord.agent_id == agent_id,
                    ContainerRecord.time == record.time,
                )
            )
            containers = list(containers_result.scalars().all())

            return _build_snapshot(record, containers)
    except Exception as e:
        logger.error(
            "Failed to fetch latest snapshot for agent %s: %s",
            agent_id,
            e,
        )
        raise


async def get_snapshot_range(
    agent_id: str,
    start: datetime,
    end: datetime,
) -> list[dict]:
    async with AsyncSessionLocal() as session:
        metrics_result = await session.execute(
            select(MetricsRecord)
            .where(
                MetricsRecord.agent_id == agent_id,
                MetricsRecord.time >= start,
                MetricsRecord.time <= end,
            )
            .order_by(MetricsRecord.time)
        )
        records = list(metrics_result.scalars().all())
        if not records:
            return []

        timestamps = [r.time for r in records]
        containers_result = await session.execute(
            select(ContainerRecord)
            .where(
                ContainerRecord.agent_id == agent_id,
                ContainerRecord.time.in_(timestamps),
            )
            .order_by(ContainerRecord.time)
        )
        all_containers = list(containers_result.scalars().all())

        containers_by_time = {}
        for c in all_containers:
            containers_by_time.setdefault(c.time, []).append(c)

        return [_build_snapshot(r, containers_by_time.get(r.time, [])) for r in records]


def _build_snapshot(record: MetricsRecord, containers: list) -> dict:
    return {
        "agent_id": record.agent_id,
        "timestamp": record.time,
        "cpu": {
            "load_percent": record.cpu_load_percent,
            "load_avg_1m": record.load_avg_1m,
            "load_avg_5m": record.load_avg_5m,
            "load_avg_15m": record.load_avg_15m,
        },
        "memory": {
            "ram_percent": record.ram_percent,
            "ram_usage_mb": record.ram_usage_mb,
            "swap_percent": record.swap_percent,
            "swap_usage_mb": record.swap_usage_mb,
        },
        "disk": {
            "read_bytes": record.disk_read_bytes,
            "write_bytes": record.disk_write_bytes,
        },
        "network": {
            "sent_bytes": record.net_sent_bytes,
            "received_bytes": record.net_received_bytes,
        },
        "containers": [
            {
                "name": c.name,
                "cpu_load_percent": c.cpu_load_percent,
                "ram_usage_mb": c.ram_usage_mb,
                "ram_limit_mb": c.ram_limit_mb,
                "status": c.status,
            }
            for c in containers
        ],
    }
