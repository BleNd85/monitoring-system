from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, String, Float, BigInteger
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class MetricsRecord(Base):
    __tablename__ = "metrics"
    time = Column(TIMESTAMP(timezone=True), primary_key=True)
    agent_id = Column(String, primary_key=True)
    cpu_load_percent = Column(Float)
    load_avg_1m = Column(Float)
    load_avg_5m = Column(Float)
    load_avg_15m = Column(Float)
    ram_percent = Column(Float)
    ram_usage_mb = Column(Float)
    swap_percent = Column(Float)
    swap_usage_mb = Column(Float)
    disk_read_bytes = Column(BigInteger)
    disk_write_bytes = Column(BigInteger)
    net_sent_bytes = Column(BigInteger)
    net_received_bytes = Column(BigInteger)


class ContainerRecord(Base):
    __tablename__ = "container_metrics"

    time = Column(TIMESTAMP(timezone=True), primary_key=True)
    agent_id = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    cpu_load_percent = Column(Float)
    ram_usage_mb = Column(Float)
    ram_limit_mb = Column(Float)
    status = Column(String)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
