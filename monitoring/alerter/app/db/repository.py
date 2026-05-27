import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, desc
from app.db.database import AsyncSessionLocal, IncidentRecord
from app.model.schema import AnomalyDetected

logger = logging.getLogger(__name__)


async def save_incident(anomaly: AnomalyDetected) -> IncidentRecord:
    async with AsyncSessionLocal() as session:
        try:
            record = IncidentRecord(
                agent_id=anomaly.agent_id,
                timestamp=anomaly.timestamp,
                severity=anomaly.severity,
                anomaly_type=anomaly.anomaly_type,
                affected_metrics=anomaly.affected_metrics,
                expected_values=anomaly.expected_values,
                actual_values=anomaly.actual_values,
                deviation_score=anomaly.deviation_score,
                llm_interpretation=anomaly.llm_interpretation,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            logger.info("Saved incident for agent: %s", anomaly.agent_id)
            return record
        except Exception as e:
            await session.rollback()
            logger.error("Failed to save incident: %s", e)
            raise


async def get_all_incidents(limit: int = 100) -> list[IncidentRecord]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IncidentRecord).order_by(desc(IncidentRecord.timestamp)).limit(limit)
        )
        return list(result.scalars().all())


async def get_by_agent_id(agent_id: str, limit=100) -> list[IncidentRecord]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IncidentRecord)
            .where(IncidentRecord.agent_id == agent_id)
            .order_by(desc(IncidentRecord.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())


async def resolve_incident(incident_id: UUID) -> IncidentRecord | None:
    async with AsyncSessionLocal() as session:
        try:
            record = await session.get(IncidentRecord, incident_id)
            if not record:
                return None
            record.resolved_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(record)
            return record
        except Exception as e:
            logger.error("Failed to resolve incident: %s", e)
            raise
