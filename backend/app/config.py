"""App configuration from environment."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. All from env with safe defaults for local run."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # CORS: comma-separated origins, e.g. "http://localhost:5173,https://app.example.com"
    cors_origins: str = "http://localhost:5173"
    # Max request body size for code (bytes). 100 KB default.
    max_code_length: int = 102400
    # PEP 8 source of truth (revision transparency per spec/update.txt).
    pep8_url: str = "https://peps.python.org/pep-0008/"
    pep8_date: str = "2021-11-01"  # Revision date shown in UI
    pep8_revision: str = "2021-11-01"  # Revision identifier (e.g. date or hash)

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
