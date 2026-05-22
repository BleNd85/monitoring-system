import logging
import numpy as np
import pandas as pd
from datetime import datetime
from app.model.schema import MetricsSnapshot, AnomalyDetected
from app.service import model_manager, llm_service, alerter_client
from app.core.config import settings

logger = logging.getLogger(__name__)

PROPHET_TARGETS = [
    "cpu_load_percent",
    "ram_percent",
    "disk_read_bytes",
    "disk_write_bytes",
    "net_sent_bytes",
    "net_received_bytes",
]

DEVIATION_FEATURES = [
    "dev_cpu_load_percent",
    "dev_ram_percent",
    "dev_disk_read_bytes",
    "dev_disk_write_bytes",
    "dev_net_sent_bytes",
    "dev_net_received_bytes",
    "load_avg_1m",
    "ram_usage_mb",
    "swap_percent",
]


def snapshot_to_raw_features(snapshot: MetricsSnapshot) -> dict:
    return {
        "cpu_load_percent": snapshot.cpu.get("load_percent", 0),
        "load_avg_1m": snapshot.cpu.get("load_avg_1m", 0),
        "ram_percent": snapshot.memory.get("ram_percent", 0),
        "ram_usage_mb": snapshot.memory.get("ram_usage_mb", 0),
        "swap_percent": snapshot.memory.get("swap_percent", 0),
        "disk_read_bytes": snapshot.disk.get("read_bytes", 0),
        "disk_write_bytes": snapshot.disk.get("write_bytes", 0),
        "net_sent_bytes": snapshot.network.get("sent_bytes", 0),
        "net_received_bytes": snapshot.network.get("received_bytes", 0),
    }


def get_expected_values(agent_id: str, timestamp: datetime) -> dict:
    naive_ts = timestamp.replace(tzinfo=None)
    future = pd.DataFrame({"ds": [naive_ts]})
    expected = {}

    for col in PROPHET_TARGETS:
        model = model_manager.load_model(agent_id, f"prophet_{col}")
        if model:
            forecast = model.predict(future)
            expected[col] = round(float(forecast["yhat"].iloc[0]), 4)

    return expected


def build_deviation_vector(raw_features: dict, expected: dict) -> np.ndarray:
    vector = [
        raw_features["cpu_load_percent"]
        - expected.get("cpu_load_percent", raw_features["cpu_load_percent"]),
        raw_features["ram_percent"]
        - expected.get("ram_percent", raw_features["ram_percent"]),
        raw_features["disk_read_bytes"]
        - expected.get("disk_read_bytes", raw_features["disk_read_bytes"]),
        raw_features["disk_write_bytes"]
        - expected.get("disk_write_bytes", raw_features["disk_write_bytes"]),
        raw_features["net_sent_bytes"]
        - expected.get("net_sent_bytes", raw_features["net_sent_bytes"]),
        raw_features["net_received_bytes"]
        - expected.get("net_received_bytes", raw_features["net_received_bytes"]),
        raw_features["load_avg_1m"],
        raw_features["ram_usage_mb"],
        raw_features["swap_percent"],
    ]
    return np.array([vector])


def build_xgb_vector(raw_features: dict, deviation_vector: np.ndarray) -> np.ndarray:
    extra = np.array(
        [
            [
                raw_features["cpu_load_percent"],
                raw_features["ram_percent"],
                raw_features["ram_usage_mb"],
                raw_features["swap_percent"],
                raw_features["load_avg_1m"],
            ]
        ]
    )
    return np.concatenate([deviation_vector, extra], axis=1)


def normalize_score(raw_score: float, bounds: dict) -> float:
    score_min = bounds.get("min", -0.5)
    score_max = bounds.get("max", 0.5)
    if score_max == score_min:
        return 0.0
    normalized = 1.0 - (raw_score - score_min) / (score_max - score_min)
    return float(max(0.0, min(1.0, normalized)))


def determine_anomaly_type(raw_features: dict, expected: dict) -> str:
    cpu_dev = raw_features["cpu_load_percent"] - expected.get(
        "cpu_load_percent", raw_features["cpu_load_percent"]
    )
    ram_dev = raw_features["ram_percent"] - expected.get(
        "ram_percent", raw_features["ram_percent"]
    )
    disk_r_dev = raw_features["disk_read_bytes"] - expected.get(
        "disk_read_bytes", raw_features["disk_read_bytes"]
    )
    disk_w_dev = raw_features["disk_write_bytes"] - expected.get(
        "disk_write_bytes", raw_features["disk_write_bytes"]
    )
    net_s_dev = raw_features["net_sent_bytes"] - expected.get(
        "net_sent_bytes", raw_features["net_sent_bytes"]
    )
    net_r_dev = raw_features["net_received_bytes"] - expected.get(
        "net_received_bytes", raw_features["net_received_bytes"]
    )

    if raw_features.get("swap_percent", 0) > 50:
        return "memory_swap"
    if ram_dev > 20:
        return "memory_anomaly"
    if cpu_dev > 30:
        return "cpu_spike"
    if disk_r_dev > 200_000_000 or disk_w_dev > 200_000_000:
        return "disk_io_spike"
    if net_s_dev > 50_000_000 or net_r_dev > 50_000_000:
        return "network_spike"
    return "general_anomaly"


async def analyze(agent_id: str, snapshot: MetricsSnapshot) -> bool:
    if not model_manager.models_exist(agent_id):
        return False

    iso_forest = model_manager.load_model(agent_id, "isolation_forest")
    if not iso_forest:
        return False

    raw_features = snapshot_to_raw_features(snapshot)
    expected = get_expected_values(agent_id, snapshot.timestamp)
    X_dev = build_deviation_vector(raw_features, expected)

    raw_score = float(iso_forest.decision_function(X_dev)[0])
    bounds = model_manager.load_model(agent_id, "if_score_bounds") or {}
    normalized = normalize_score(raw_score, bounds)

    logger.info(
        "IF score for agent %s: raw=%.4f normalized=%.4f",
        agent_id,
        raw_score,
        normalized,
    )

    if normalized < settings.ANOMALY_THRESHOLD_WARNING:
        return False

    severity = (
        "critical" if normalized >= settings.ANOMALY_THRESHOLD_CRITICAL else "warning"
    )

    xgb = model_manager.load_model(agent_id, "xgboost")
    if xgb:
        X_xgb = build_xgb_vector(raw_features, X_dev)
        xgb_pred = int(xgb.predict(X_xgb)[0])
        if xgb_pred == 0:
            return False
        severity = "critical" if xgb_pred == 2 else "warning"

    anomaly_type = determine_anomaly_type(raw_features, expected)
    affected = {
        k: raw_features[k]
        for k in [
            "cpu_load_percent",
            "ram_percent",
            "disk_read_bytes",
            "disk_write_bytes",
            "net_sent_bytes",
            "net_received_bytes",
        ]
        if k in expected and abs(raw_features[k] - expected[k]) > 10
    } or raw_features

    interpretation = await llm_service.interpret(
        agent_id=agent_id,
        anomaly_type=anomaly_type,
        affected_metrics=affected,
        expected_values=expected,
        actual_values=raw_features,
        deviation_score=normalized,
        containers=snapshot.containers,
    )

    anomaly = AnomalyDetected(
        agent_id=agent_id,
        timestamp=snapshot.timestamp,
        severity=severity,
        anomaly_type=anomaly_type,
        affected_metrics=affected,
        expected_values=expected,
        actual_values=raw_features,
        deviation_score=normalized,
        llm_interpretation=interpretation,
    )

    await alerter_client.send_anomaly(anomaly)
    logger.info(
        "Anomaly detected for agent %s: type=%s severity=%s score=%.2f",
        agent_id,
        anomaly_type,
        severity,
        normalized,
    )
    return True


async def analyze_silent(agent_id: str, snapshot: MetricsSnapshot) -> None:
    if not model_manager.models_exist(agent_id):
        return

    iso_forest = model_manager.load_model(agent_id, "isolation_forest")
    if not iso_forest:
        return

    raw_features = snapshot_to_raw_features(snapshot)
    expected = get_expected_values(agent_id, snapshot.timestamp)
    X_dev = build_deviation_vector(raw_features, expected)

    raw_score = float(iso_forest.decision_function(X_dev)[0])
    bounds = model_manager.load_model(agent_id, "if_score_bounds") or {}
    normalized = normalize_score(raw_score, bounds)

    if normalized >= settings.ANOMALY_THRESHOLD_WARNING:
        logger.debug(
            "Anomaly suppressed by cooldown for agent %s: score=%.2f",
            agent_id,
            normalized,
        )
