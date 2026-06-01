"""
Application configuration.
Uses pydantic-settings for env-var based configuration.
"""

import sys
from pathlib import Path
from typing import List, Optional

# Ensure ml_engine is importable
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(Path(__file__).parent.parent / ".env"), env_file_encoding="utf-8", extra="ignore", protected_namespaces=('settings_',))

    # App
    app_name: str = "Terra API"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./app.db"

    # Redis (for caching / background jobs)
    redis_url: str = "redis://localhost:6379/0"

    # ML
    model_dir: str = "./models"
    default_domain: str = "film_tv"

    # CORS
    cors_origins: List[str] = ["*"]

    # Auth
    secret_key: str = "dev-secret-change-in-production"



settings = Settings()
