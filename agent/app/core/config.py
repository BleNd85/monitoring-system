from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    AGENT_ID: str = "unknown-agent"
    AGENT_HOST: str = "localhost"


settings = Settings()
