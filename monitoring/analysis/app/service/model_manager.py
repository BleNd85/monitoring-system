import os
import pickle
import logging
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

_cache: dict[str, object] = {}

_PROPHET_MODELS = [
    "prophet_cpu_load_percent",
    "prophet_ram_percent",
    "prophet_disk_read_bytes",
    "prophet_disk_write_bytes",
    "prophet_net_sent_bytes",
    "prophet_net_received_bytes",
]

_REQUIRED_MODELS = _PROPHET_MODELS + ["isolation_forest", "if_score_bounds"]


def _cache_key(agent_id: str, model_name: str) -> str:
    return f"{agent_id}:{model_name}"


def get_model_path(agent_id: str, model_name: str) -> Path:
    agent_dir = Path(settings.MODELS_DIR) / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir / f"{model_name}.pkl"


def save_model(agent_id: str, model_name: str, model) -> None:
    path = get_model_path(agent_id, model_name)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    _cache[_cache_key(agent_id, model_name)] = model
    logger.info("Saved model %s for agent %s", model_name, agent_id)


def load_model(agent_id: str, model_name: str):
    key = _cache_key(agent_id, model_name)

    if key in _cache:
        return _cache[key]

    path = get_model_path(agent_id, model_name)
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            model = pickle.load(f)
        _cache[key] = model
        logger.info("Loaded model %s for agent %s", model_name, agent_id)
        return model
    except Exception as e:
        logger.error(
            "Failed to load model %s for agent %s: %s", model_name, agent_id, e
        )
        return None


def invalidate_cache(agent_id: str) -> None:
    keys = [k for k in _cache if k.startswith(f"{agent_id}:")]
    for k in keys:
        del _cache[k]
    logger.info("Cache invalidated for agent %s", agent_id)


def models_exist(agent_id: str) -> bool:
    return all(get_model_path(agent_id, m).exists() for m in _REQUIRED_MODELS)
