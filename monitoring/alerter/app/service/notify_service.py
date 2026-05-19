import httpx
import logging
from app.model.schema import AnomalyDetected
from app.core.config import settings

logger = logging.getLogger(__name__)

SEVERITY_EMOJI = {"warning": "🟡", "critical": "🔴"}


async def send_telegram(anomaly: AnomalyDetected) -> None:
    if not settings.TELEGRAM_CHAT_ID | settings.TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot not configured, skipping notification.")

    emoji = SEVERITY_EMOJI.get(anomaly.severity)
    metrics_text = "/n".join(f"-{k}: {v}" for k, v in anomaly.affected_metrics.items())

    text = (
        f"{emoji} *{anomaly.severity.upper()} — {anomaly.anomaly_type}*\n"
        f"Agent: `{anomaly.agent_id}`\n"
        f"Time: {anomaly.timestamp.strftime('%H:%M:%S %d-%m-%Y')}\n"
        f"Score: {anomaly.deviation_score:.2f}\n\n"
        f"*Affected metrics:*\n{metrics_text}\n"
    )

    if anomaly.llm_interpretation:
        text += f"\n*Analysis*\n{anomaly.llm_interpretation}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                    "text": text,
                    "parse_mode": "Markdown",
                },
            )

            response.raise_for_status()
        logger.info("Telegram notification was sent for agent %s", anomaly.agent_id)
    except Exception as e:
        logger.error("Failed to send Telegram notification: %s", e)
