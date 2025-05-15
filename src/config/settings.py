# src/config/settings.py
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Central configuration object.
    Values are loaded, in order of precedence, from:
      1. explicit constructor args
      2. environment variables
      3. a `.env` file in the project root
      4. default values below
    """

    # --- Required -----------------------------------------------------------
    openai_api_key: str

    # --- Optional / defaults ------------------------------------------------
    deepseek_api_key: str | None = None  # <-- ADD THIS LINE
    openai_model: str = "gpt-4o-mini"
    indentation_model_name: str | None = None

    # General behaviour
    timeout_seconds: int = 60
    log_level: str = "INFO"

    # Paths
    data_dir: Path = Path("data")

    # Pydantic-settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False, # Pydantic converts env var names to lowercase by default anyway
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """
    Return a cached instance of `AppSettings`.
    """
    return AppSettings()