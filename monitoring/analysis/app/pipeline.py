import asyncio
import logging
from datetime import datetime, timezone, timedelta
from app.service import collector_client, trainer, analyzer
from app.core.config import settings

logger = logging.getLogger(__name__)

_last_training: dict[str, datetime] = {}
_last_anomaly: dict[str, datetime] = {}
_last_analyzed_ts: dict[str, datetime] = {}
_agents_cache: list = []
_agents_last_fetch: datetime | None = None

AGENTS_REFRESH_INTERVAL = settings.AGENTS_REFRESH_INTERVAL
ANOMALY_COOLDOWN = settings.ANOMALY_COOLDOWN


async def get_agents_cached() -> list:
    global _agents_cache, _agents_last_fetch
    now = datetime.now(timezone.utc)
    if (
        _agents_last_fetch is None
        or (now - _agents_last_fetch).total_seconds() > AGENTS_REFRESH_INTERVAL
    ):
        _agents_cache = await collector_client.get_agents()
        _agents_last_fetch = now
    return _agents_cache


async def should_train(agent_id: str) -> bool:
    now = datetime.now(timezone.utc)
    last = _last_training.get(agent_id)
    if last is None:
        return True
    return (now - last).total_seconds() > settings.RETRAIN_INTERVAL_HOURS * 3600


async def run_training(agent_id: str) -> None:
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=24)
    logger.info("Starting training for agent %s", agent_id)
    snapshots = await collector_client.get_range(agent_id, start, now)
    if not snapshots:
        logger.warning("No data for training agent %s", agent_id)
        _last_training[agent_id] = now
        return
    success = await trainer.train(agent_id, snapshots)
    _last_training[agent_id] = now
    if not success:
        logger.warning(
            "Training failed or skipped for agent %s, will retry in 23h", agent_id
        )


async def run_analysis(agent_id: str) -> None:
    snapshot = await collector_client.get_latest(agent_id)
    if not snapshot:
        return

    last_ts = _last_analyzed_ts.get(agent_id)
    if last_ts and snapshot.timestamp <= last_ts:
        logger.debug("Skipping already analyzed snapshot for agent %s", agent_id)
        return

    now = datetime.now(timezone.utc)
    last_anomaly = _last_anomaly.get(agent_id)

    if last_anomaly and (now - last_anomaly).total_seconds() < ANOMALY_COOLDOWN:
        await analyzer.analyze_silent(agent_id, snapshot)
    else:
        detected = await analyzer.analyze(agent_id, snapshot)
        if detected:
            _last_anomaly[agent_id] = now

    _last_analyzed_ts[agent_id] = snapshot.timestamp


async def _wait_for_agents() -> list:
    logger.info("Waiting for agents...")
    while True:
        try:
            agents = await collector_client.get_agents()
            if agents:
                logger.info("Found %d agent(s), starting pipeline", len(agents))
                return agents
            logger.info("No agents yet, retrying in 15s...")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error("Error fetching agents: %s", e)
        await asyncio.sleep(15)


async def pipeline_loop() -> None:
    logger.info("Pipeline loop started")
    await _wait_for_agents()

    while True:
        try:
            agents = await get_agents_cached()
            for agent in agents:
                if await should_train(agent.agent_id):
                    await run_training(agent.agent_id)
                await run_analysis(agent.agent_id)
        except asyncio.CancelledError:
            logger.info("Pipeline loop cancelled")
            raise
        except Exception as e:
            logger.error("Pipeline error: %s", e)
        await asyncio.sleep(settings.ANALYSIS_INTERVAL)
