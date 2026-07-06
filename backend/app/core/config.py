from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SACB_", extra="ignore")

    app_name: str = "Security Alert Case Builder"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://sacb:sacb@postgres:5432/sacb"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = Field(default="change-this-dev-secret")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    evidence_storage_path: Path = Path("/data/evidence")
    max_upload_bytes: int = 10 * 1024 * 1024
    seed_demo_data: bool = True
    seed_admin_email: str = "admin@example.com"
    seed_admin_password: str = "ChangeMe123!"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
