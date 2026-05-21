import httpx
import logging
from datetime import datetime, timezone
from app.model.schema import MetricsSnapshot, AgentInfo
from app.core.config import settings

logger = logging.getLogger(__name__)

_agents_cache: list[AgentInfo] = []
_agents_last_fetched: datetime | None = None


async def get_agents() -> list[AgentInfo]:
    global _agents_cache, _agents_last_fetched

    now = datetime.now(timezone.utc)
    elapsed = (
        (now - _agents_last_fetched).total_seconds()
        if _agents_last_fetched is not None
        else float("inf")
    )

    if elapsed >= settings.AGENTS_REFRESH_INTERVAL:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.COLLECTOR_URL}/api/v1/agents",
                    timeout=10,
                )
                response.raise_for_status()
                _agents_cache = [AgentInfo(**a) for a in response.json()]
                _agents_last_fetched = now
                logger.info("Agents list refreshed: %d agents", len(_agents_cache))
        except Exception as e:
            logger.error("Failed to refresh agents list: %s", e)

    return _agents_cache


async def get_latest(agent_id: str) -> MetricsSnapshot | None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.COLLECTOR_URL}/api/v1/metrics/{agent_id}/latest",
                timeout=10,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return MetricsSnapshot(**response.json())
    except Exception as e:
        logger.error("Failed to get latest metrics for %s: %s", agent_id, e)
        return None


async def get_range(
    agent_id: str,
    start: datetime,
    end: datetime,
) -> list[MetricsSnapshot]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.COLLECTOR_URL}/api/v1/metrics/{agent_id}/range",
                params={
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
                timeout=30,
            )
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return [MetricsSnapshot(**s) for s in response.json()]
    except Exception as e:
        logger.error("Failed to get range metrics for %s: %s", agent_id, e)
        return []