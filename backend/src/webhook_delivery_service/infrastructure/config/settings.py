from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Webhook Delivery Service"
    DEBUG: bool = False
    ENVIRONMENT: Literal[
        "development",
        "testing",
        "staging",
        "production",
    ] = "development"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str
    REDIS_STREAM_NAME: str = "webhook:deliveries"

    # Authentication
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, gt=0)

    # Webhook delivery
    WEBHOOK_TIMEOUT_SECONDS: int = Field(default=10, gt=0)
    MAX_RETRY_ATTEMPTS: int = Field(default=5, ge=0)

    # Frontend and observability
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    LOG_LEVEL: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
