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
                    "keep_alive": "-1",
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
    severity_hint = (
        "CRITICAL — immediate action required"
        if deviation_score >= settings.ANOMALY_THRESHOLD_CRITICAL
        else "WARNING — investigation required"
    )

    prompt = f"""You are a senior DevOps/SRE engineer performing root cause analysis.
        Respond ONLY in English. Be precise and concise.

        === ANOMALY REPORT ===
        Agent: {agent_id}
        Detected anomaly type: {anomaly_type}
        Severity: {severity_hint} (score={deviation_score:.2f})

        === METRICS ===
        Baseline (Prophet seasonal forecast):
        {expected_values}

        Actual (current values):
        {actual_values}

        Affected metrics (deviated most from baseline):
        {affected_metrics}

        Running containers:
        {containers}

        === CONTEXT ===
        - Linux server with Docker containers (web apps, PostgreSQL).
        - disk_read_bytes / disk_write_bytes / net_sent_bytes / net_received_bytes are per-poll-interval deltas (not cumulative).
        - Anomaly type "{anomaly_type}" was determined by rule-based logic AFTER ML detection.
        - Focus your analysis on the anomaly type and affected metrics listed above.
        - Do NOT speculate about metrics that are NOT in "Affected metrics".

        === INSTRUCTIONS ===
        1. Root cause MUST match the anomaly type: "{anomaly_type}".
        2. Base your reasoning on "Affected metrics" only and {anomaly_type} is a main priority.
        3. ONE root cause. No alternatives in main analysis.
        4. Suggest 1-3 concrete Linux/Docker investigation commands relevant to "{anomaly_type}".
        5. If deviation_score >= {settings.ANOMALY_THRESHOLD_CRITICAL:.2f} → treat as confirmed incident.

        === OUTPUT FORMAT (follow exactly) ===
        Root cause: <one specific cause matching anomaly type "{anomaly_type}">
        Evidence: <1-2 sentences using only affected metrics data>
        Action:
        <command 1>
        <command 2 if needed>
        <command 3 if needed>
        Rejected alternatives: <one sentence on why other causes are less likely>"""

    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 400,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
    except Exception as e:
        logger.error("Failed to get LLM interpretation: %s", e)
        return None
