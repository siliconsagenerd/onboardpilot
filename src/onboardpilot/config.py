"""Application settings."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "OnboardPilot"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "change-me-in-production-please-use-env"
    access_token_expire_minutes: int = 60 * 8
    operator_auth_required: bool = True
    database_url: str = ""
    cors_origins: str = "*"
    data_dir: Path = Path("data")
    seed_on_startup: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def db_url(self) -> str:
        if self.database_url:
            return self.database_url
        self.ensure_dirs()
        return f"sqlite:///{(self.data_dir / 'onboardpilot.db').resolve()}"

    @property
    def cors_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
if os.getenv("DATABASE_URL"):
    settings.database_url = os.getenv("DATABASE_URL", "")
if os.getenv("SECRET_KEY"):
    settings.secret_key = os.getenv("SECRET_KEY", settings.secret_key)
if os.getenv("OPERATOR_AUTH_REQUIRED"):
    settings.operator_auth_required = os.getenv("OPERATOR_AUTH_REQUIRED", "true").lower() == "true"
if os.getenv("SEED_ON_STARTUP"):
    settings.seed_on_startup = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"
if os.getenv("CORS_ORIGINS"):
    settings.cors_origins = os.getenv("CORS_ORIGINS", "*")
if os.getenv("DATA_DIR"):
    settings.data_dir = Path(os.getenv("DATA_DIR", "data"))
