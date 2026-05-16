import logging
from app.db.database import AsyncSessionLocal, MetricsRecord, ContainerRecord
from app.models.metrics_schema import MetricsSnapshot

logger = logging.getLogger(__name__)


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
