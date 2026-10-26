"""Application settings."""

from __future__ import annotations

from pathlib import Path

from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "OnboardPilot"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = ""
    access_token_expire_minutes: int = 60 * 8
    operator_auth_required: bool = True
    database_url: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    data_dir: Path = Path("data")
    seed_on_startup: bool = False

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
        if not self.cors_origins.strip():
            return []
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_security(self) -> Settings:
        if self.app_env != "development":
            if not self.secret_key or self.secret_key == "change-me-in-production-please-use-env":
                raise ValueError("SECRET_KEY must be set to a non-default value outside development")
            if not self.operator_auth_required:
                raise ValueError("OPERATOR_AUTH_REQUIRED=false is only allowed in development")
            if self.cors_origins.strip() == "*":
                raise ValueError("CORS_ORIGINS must not be '*' outside development")
        return self


settings = Settings()
