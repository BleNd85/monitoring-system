import asyncio
import httpx
import logging
from app.core.config import settings
from app.models.metrics_schema import MetricsSnapshot
from app.db.repository import save_snapshot
from app.service.agent_registry import agent_registry

logger = logging.getLogger(__name__)

client = httpx.AsyncClient(timeout=settings.AGENT_TIMEOUT)


async def poll_agent(agent) -> None:
    try:
        response = await client.get(
            f"{agent.url}/api/v1/metrics",
        )
        response.raise_for_status()
        snapshot = MetricsSnapshot(**response.json())
        await save_snapshot(snapshot)
    except httpx.TimeoutException:
        logger.error("Agent %s timeout", agent.agent_id)
    except httpx.HTTPStatusError as e:
        logger.error("Agent %s HTTP error: %s", agent.agent_id, e.response.status_code)
    except Exception as e:
        logger.error("Agent %s failed: %s", agent.agent_id, e)


async def polling_loop():
    logger.info("Polling loop started")
    while True:
        agents = agent_registry.get_all()
        if agents:
            await asyncio.gather(*[poll_agent(a) for a in agents])
        await asyncio.sleep(settings.POLL_INTERVAL)
