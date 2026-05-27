import logging
import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier

from app.model.schema import MetricsSnapshot
from app.service import model_manager
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


def snapshots_to_df(snapshots: list[MetricsSnapshot]) -> pd.DataFrame:
    rows = []

    for s in snapshots:
        rows.append(
            {
                "timestamp": s.timestamp.replace(tzinfo=None),
                "cpu_load_percent": s.cpu.get("load_percent", 0),
                "load_avg_1m": s.cpu.get("load_avg_1m", 0),
                "ram_percent": s.memory.get("ram_percent", 0),
                "ram_usage_mb": s.memory.get("ram_usage_mb", 0),
                "swap_percent": s.memory.get("swap_percent", 0),
                "disk_read_bytes": s.disk.get("read_bytes", 0),
                "disk_write_bytes": s.disk.get("write_bytes", 0),
                "net_sent_bytes": s.network.get("sent_bytes", 0),
                "net_received_bytes": s.network.get("received_bytes", 0),
            }
        )

    return pd.DataFrame(rows)


def _fit_prophet(df: pd.DataFrame, col: str) -> Prophet:
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=False,
        changepoint_prior_scale=0.05,
    )

    prophet_df = df[["timestamp", col]].rename(columns={"timestamp": "ds", col: "y"})

    model.fit(prophet_df)

    return model


def _get_prophet_predictions(
    df: pd.DataFrame,
    models: dict[str, Prophet],
) -> pd.DataFrame:

    future = pd.DataFrame({"ds": df["timestamp"]})

    result = {}

    for col, model in models.items():
        forecast = model.predict(future)
        result[f"expected_{col}"] = forecast["yhat"].values

    return pd.DataFrame(result, index=df.index)


def _build_deviation_matrix(
    df: pd.DataFrame,
    expected_df: pd.DataFrame,
) -> np.ndarray:

    deviations = pd.DataFrame(
        {
            "dev_cpu_load_percent": (
                df["cpu_load_percent"] - expected_df["expected_cpu_load_percent"]
            ),
            "dev_ram_percent": (
                df["ram_percent"] - expected_df["expected_ram_percent"]
            ),
            "dev_disk_read_bytes": (
                df["disk_read_bytes"] - expected_df["expected_disk_read_bytes"]
            ),
            "dev_disk_write_bytes": (
                df["disk_write_bytes"] - expected_df["expected_disk_write_bytes"]
            ),
            "dev_net_sent_bytes": (
                df["net_sent_bytes"] - expected_df["expected_net_sent_bytes"]
            ),
            "dev_net_received_bytes": (
                df["net_received_bytes"] - expected_df["expected_net_received_bytes"]
            ),
            "load_avg_1m": df["load_avg_1m"],
            "ram_usage_mb": df["ram_usage_mb"],
            "swap_percent": df["swap_percent"],
        }
    )

    return deviations[DEVIATION_FEATURES].values


def _build_xgb_matrix(
    df: pd.DataFrame,
    deviation_matrix: np.ndarray,
) -> np.ndarray:

    extra = df[
        [
            "cpu_load_percent",
            "ram_percent",
            "ram_usage_mb",
            "swap_percent",
            "load_avg_1m",
        ]
    ].values

    return np.concatenate([deviation_matrix, extra], axis=1)


async def train(
    agent_id: str,
    snapshots: list[MetricsSnapshot],
) -> bool:
    if len(snapshots) < settings.MIN_TRAINING_SAMPLES:
        logger.warning(
            "Not enough samples for agent %s: %d < %d",
            agent_id,
            len(snapshots),
            settings.MIN_TRAINING_SAMPLES,
        )
        return False

    df = snapshots_to_df(snapshots)
    df = df.sort_values("timestamp").drop_duplicates("timestamp")

    try:
        prophet_models: dict[str, Prophet] = {}

        for col in PROPHET_TARGETS:
            logger.info(
                "Fitting Prophet for %s / agent %s",
                col,
                agent_id,
            )

            model = _fit_prophet(df, col)

            model_manager.save_model(
                agent_id,
                f"prophet_{col}",
                model,
            )

            prophet_models[col] = model

        expected_df = _get_prophet_predictions(
            df,
            prophet_models,
        )

        X_dev = _build_deviation_matrix(
            df,
            expected_df,
        )

        iso_forest = IsolationForest(
            contamination=settings.ISO_CONTAMINATION,
            random_state=42,
            n_estimators=100,
        )

        iso_forest.fit(X_dev)

        model_manager.save_model(
            agent_id,
            "isolation_forest",
            iso_forest,
        )

        raw_scores = iso_forest.decision_function(X_dev)

        score_bounds = {
            "min": float(raw_scores.min()),
            "max": float(raw_scores.max()),
        }

        model_manager.save_model(
            agent_id,
            "if_score_bounds",
            score_bounds,
        )

        score_range = raw_scores.max() - raw_scores.min()

        if score_range == 0:
            normalized_scores = np.zeros_like(raw_scores)
        else:
            normalized_scores = 1.0 - (raw_scores - raw_scores.min()) / score_range

        X_full = _build_xgb_matrix(df, X_dev)

        X_labeled_full = []
        labels = []

        for i, score in enumerate(normalized_scores):

            if score >= settings.ANOMALY_THRESHOLD_CRITICAL:
                labels.append(2)
                X_labeled_full.append(X_full[i])

            elif score >= settings.ANOMALY_THRESHOLD_WARNING:
                labels.append(1)
                X_labeled_full.append(X_full[i])

            elif score < 0.40:
                labels.append(0)
                X_labeled_full.append(X_full[i])

        if len(X_labeled_full) > 50 and len(set(labels)) >= 2:

            xgb = XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
                eval_metric="mlogloss",
            )

            xgb.fit(
                np.array(X_labeled_full),
                np.array(labels),
            )

            model_manager.save_model(
                agent_id,
                "xgboost",
                xgb,
            )

            model_manager.save_model(
                agent_id,
                "xgb_feature_dim",
                X_full.shape[1],
            )

            logger.info(
                "XGBoost trained for agent %s: "
                "%d samples, labels=%s, feature_dim=%d",
                agent_id,
                len(X_labeled_full),
                sorted(set(labels)),
                X_full.shape[1],
            )

        else:
            logger.info(
                "Skipping XGBoost for agent %s: " "not enough labeled samples (%d)",
                agent_id,
                len(X_labeled_full),
            )

        model_manager.invalidate_cache(agent_id)
        logger.info(
            "Training complete for agent %s",
            agent_id,
        )

        return True

    except Exception as e:
        logger.exception(
            "Training failed for agent %s: %s",
            agent_id,
            e,
        )

        return False
