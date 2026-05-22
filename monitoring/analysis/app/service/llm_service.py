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


async def interpret(
    agent_id: str,
    anomaly_type: str,
    affected_metrics: dict,
    expected_values: dict,
    actual_values: dict,
    deviation_score: float,
    containers: list[dict],
) -> str | None:
    prompt = f"""You are a senior DevOps engineer. Analyze this server anomaly and respond ONLY in English.

Agent: {agent_id}
Anomaly type: {anomaly_type}
Deviation score: {deviation_score:.2f}

Pipeline context:
- Prophet defines expected seasonal baseline (normal behavior model)
- Deviation vector = actual - Prophet expected values
- Isolation Forest detects anomaly in multivariate deviation space
- XGBoost confirms severity class (0 = normal, 1 = warning, 2 = critical)
- This analysis is performed AFTER detection, not during real-time monitoring
Important:
- If there is conflict between Baseline and Current, ALWAYS trust Current as ground truth.
- Affected metrics contain only the most anomaly-contributing features.
Baseline (expected from Prophet): {expected_values}
Current (actual): {actual_values}
Affected metrics: {affected_metrics}

Containers list: {containers}

Context:
Linux server running Docker containers (SpringBoot services, PostgreSQL).
disk_read_bytes/disk_write_bytes/net_sent_bytes/net_received_bytes are per-interval deltas.

Instructions:
- Pick ONE most likely root cause.
- Do NOT list multiple hypotheses.
- Use pipeline context when reasoning.
- Suggest few concrete investigation commands.
- If deviation_score >= 0.9 → treat as critical incident.

Format:
Root cause: <one cause>
Explanation:
<1-3 sentences>
Evidence:
<1-3 sentences>
Rejected alternatives:
<1-2 sentences>
Action:
<1-5 commands>
Monitoring:
<one metric>"""

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
