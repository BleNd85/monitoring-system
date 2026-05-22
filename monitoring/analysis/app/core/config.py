from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    COLLECTOR_URL: str = "http://collector:8001"
    ALERTER_URL: str = "http://alerter:8002"
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = ""

    ANALYSIS_INTERVAL: int = 10
    AGENTS_REFRESH_INTERVAL: int = 60
    ANOMALY_COOLDOWN: int = 60
    RETRAIN_INTERVAL_HOURS: int = 23

    TRAINING_WINDOW_HOURS: int = 24
    MIN_TRAINING_SAMPLES: int = 100000

    ANOMALY_THRESHOLD_WARNING: float = 0.70
    ANOMALY_THRESHOLD_CRITICAL: float = 0.85
    ISO_CONTAMINATION: float = 0.01

    MODELS_DIR: str = "/app/models"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"


settings = Settings()
