from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, String, Float, Text, Index
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSONB
import uuid
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class IncidentRecord(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String, nullable=False, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    severity = Column(String, nullable=False)
    anomaly_type = Column(String, nullable=False)
    affected_metrics = Column(JSONB, nullable=False)
    expected_values = Column(JSONB, nullable=True)
    actual_values = Column(JSONB, nullable=True)
    deviation_score = Column(Float, nullable=True)
    llm_interpretation = Column(String, nullable=False)
    resolved_at = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
    Index("ix_incidents_agent_timestamp", "agent_id", "timestamp"),
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
