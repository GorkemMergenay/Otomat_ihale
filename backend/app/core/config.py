from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "turkiye-otomat-ihale-takip"
    environment: str = "dev"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/tender_tracker"
    )

    auth_disabled: bool = False
    auth_secret_key: str = "change-this-secret-in-production"
    auth_token_ttl_minutes: int = 720
    admin_token: str = "admin-token"
    analyst_token: str = "analyst-token"
    viewer_token: str = "viewer-token"

    scheduler_enabled: bool = True
    scheduler_interval_minutes: int = 30
    auto_purge_mock_data: bool = True

    scoring_high_threshold: float = 75.0
    scoring_relevant_threshold: float = 55.0
    scoring_maybe_threshold: float = 35.0
    notification_score_threshold: float = 80.0

    email_enabled: bool = False
    email_from: str = "alerts@example.com"
    smtp_host: str = "localhost"
    smtp_port: int = 25
    smtp_use_tls: bool = False
    smtp_username: str = ""
    smtp_password: str = ""

    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    notification_email_recipients: str = ""

    notification_cooldown_minutes: int = 120
    deadline_warning_days: str = "14,7,3"
    archive_no_deadline_after_days: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
