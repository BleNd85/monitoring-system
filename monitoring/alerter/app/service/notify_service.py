import httpx
import logging
import html
from app.model.schema import AnomalyDetected
from app.core.config import settings

logger = logging.getLogger(__name__)

SEVERITY_EMOJI = {"warning": "🟡", "critical": "🔴"}


async def send_telegram(anomaly: AnomalyDetected) -> None:
    if not settings.TELEGRAM_CHAT_ID or not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot not configured, skipping notification.")
        return

    emoji = SEVERITY_EMOJI.get(anomaly.severity)

    metrics_text = "\n".join(
        f"- {html.escape(str(k))}: {html.escape(str(v))}"
        for k, v in anomaly.affected_metrics.items()
    )

    text = (
        f"{emoji} <b>{html.escape(anomaly.severity.upper())} — {html.escape(anomaly.anomaly_type)}</b>\n"
        f"Agent: <code>{html.escape(str(anomaly.agent_id))}</code>\n"
        f"Time: {anomaly.timestamp.strftime('%H:%M:%S %d-%m-%Y')}\n"
        f"Score: {anomaly.deviation_score:.2f}\n\n"
        f"<b>Affected metrics:</b>\n{metrics_text}\n"
    )

    if anomaly.llm_interpretation:
        text += f"\n<b>Analysis</b>\n{html.escape(anomaly.llm_interpretation)}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML",
                },
            )
            response.raise_for_status()

        logger.info("Telegram notification was sent for agent %s", anomaly.agent_id)

    except httpx.HTTPStatusError as e:
        logger.error(
            "Failed to send Telegram notification: %s — response: %s",
            e,
            e.response.text,
        )
    except Exception as e:
        logger.error("Failed to send Telegram notification: %s", e)
