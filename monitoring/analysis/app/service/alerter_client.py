import httpx
import logging
from app.model.schema import AnomalyDetected
from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_anomaly(anomaly: AnomalyDetected) -> None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ALERTER_URL}/internal/incidents",
                json=anomaly.model_dump(mode="json"),
                timeout=10,
            )
            response.raise_for_status()
            logger.info("Anomaly sent to alerter for agent: %s", anomaly.agent_id)
    except Exception as e:
        logger.error("Failed to send anomaly to alerter: %s", e)