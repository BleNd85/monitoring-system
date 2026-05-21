import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def warmup() -> None:
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": "",
                    "keep_alive": "10m",
                },
            )
            response.raise_for_status()
        logger.info("Ollama model %s warmed up", settings.OLLAMA_MODEL)
    except Exception as e:
        logger.warning("Ollama warmup failed: %s", e)


# TODO change prompt
async def interpret(
    agent_id: str,
    anomaly_type: str,
    affected_metrics: dict,
    expected_values: dict,
    actual_values: dict,
    deviation_score: float,
) -> str | None:
    prompt = f"""You are a senior DevOps engineer. Analyze this server anomaly and respond ONLY in English.

Agent: {agent_id}
Anomaly type: {anomaly_type}
Deviation score: {deviation_score:.2f}

Baseline (expected): {expected_values}
Current (actual): {actual_values}
Affected metrics: {affected_metrics}

Context: Linux server running Docker containers (SpringBoot services, PostgreSQL).
Metrics disk_read_bytes/disk_write_bytes/net_sent_bytes/net_received_bytes are cumulative since boot — a sharp drop means restart, not anomaly.

Instructions:
- Pick ONE most likely root cause based on which specific metrics deviated most from baseline.
- Do NOT list all possible causes — commit to the most probable one given the data.
- Suggest ONE concrete investigation command using docker logs, docker stats, or standard Linux tools.
- If deviation_score >= 0.9, treat as confirmed anomaly requiring immediate action.
- If deviation_score < 0.7, suggest passive monitoring only.
- Max 3 sentences total.

Format:
Root cause: <one specific cause>
Action: <one concrete command>"""

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 500,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
    except Exception as e:
        logger.error("Failed to get LLM interpretation: %s", e)
        return None
