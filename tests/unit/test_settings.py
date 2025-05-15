# tests/unit/test_settings.py
import os
import pytest
from pydantic_settings import SettingsConfigDict # <-- ADD THIS
from src.config.settings import AppSettings, get_settings




def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    s = AppSettings()  # direct construction
    assert s.openai_api_key == "dummy_key"
    assert s.openai_model == "test-model"


def test_singleton_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "cache_key")
    first = get_settings()
    second = get_settings()
    assert first is second
    assert first.openai_api_key == "cache_key"


def test_deepseek_key_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that DEEPSEEK_API_KEY is loaded from environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_openai_key_for_test") # Required for AppSettings instantiation
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dummy_deepseek_key_from_env")
    
    settings = AppSettings() # Re-instantiate to pick up monkeypatched env vars
    assert settings.deepseek_api_key == "dummy_deepseek_key_from_env"

def test_deepseek_key_is_none_if_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that deepseek_api_key is None if not set in environment and .env is ignored."""
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_openai_key_for_test") # Still required by AppSettings
    # Ensure DEEPSEEK_API_KEY is not in os.environ
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    # Temporarily modify model_config to disable .env file loading for this specific test
    # This ensures we're only testing settings from environment variables or defaults
    original_model_config = AppSettings.model_config.copy() # Keep a reference if needed, though monkeypatch handles restoration
    
    # Create a new config dict for this test, disabling env_file
    # Pydantic-settings expects env_file to be a tuple or None to disable it,
    # or a specific path. An empty tuple means no .env files.
    test_specific_config = SettingsConfigDict(
        env_file=(), # Disable .env file loading
        env_file_encoding=original_model_config.get('env_file_encoding', 'utf-8'),
        case_sensitive=original_model_config.get('case_sensitive', False)
        # Add any other relevant settings from your original model_config if necessary
    )
    
    monkeypatch.setattr(AppSettings, 'model_config', test_specific_config)

    settings = AppSettings()
    assert settings.deepseek_api_key is None

    # monkeypatch will automatically revert the change to AppSettings.model_config after the test