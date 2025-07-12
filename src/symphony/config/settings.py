"""Symphony API configuration settings."""

import os
from functools import lru_cache
from typing import Any

from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # API Settings
    api_v1_str: str = "/api/v1"
    project_name: str = "Symphony API"
    debug: bool = False

    # Database Settings
    postgres_server: str
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str
    database_url: PostgresDsn | None = None
    
    # Demo Settings
    demo_mode: bool = False
    demo_database_url: str = "sqlite+aiosqlite:///:memory:"

    # Security Settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 8  # 8 days

    # CORS Settings
    backend_cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        postgres_server = info.data.get("postgres_server")
        postgres_port = info.data.get("postgres_port", 5432)
        postgres_user = info.data.get("postgres_user")
        postgres_password = info.data.get("postgres_password")
        postgres_db = info.data.get("postgres_db")

        if all([postgres_server, postgres_user, postgres_password, postgres_db]):
            return f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"
        return v

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()  # type: ignore[call-arg]
