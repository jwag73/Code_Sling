# tests/unit/test_settings.py
import os
import pytest
from pydantic_settings import SettingsConfigDict # Your import
from src.config.settings import AppSettings, get_settings # Your imports


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    s = AppSettings()  # direct construction
    assert s.openai_api_key == "dummy_key"
    assert s.openai_model == "test-model"


def test_singleton_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()  # <<<<<<<<<<< ****** ADD THIS LINE HERE ******
    monkeypatch.setenv("OPENAI_API_KEY", "cache_key")
    # If your AppSettings requires other env vars for successful instantiation,
    # ensure they are set here too, e.g., if OPENAI_MODEL didn't have a default.
    # monkeypatch.setenv("OPENAI_MODEL", "some_default_for_cache_test") 
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

    original_model_config_env_file = AppSettings.model_config.get('env_file')
    original_model_config_case_sensitive = AppSettings.model_config.get('case_sensitive', False) # Get current or default
    original_model_config_encoding = AppSettings.model_config.get('env_file_encoding', 'utf-8') # Get current or default


    # Temporarily modify model_config to disable .env file loading for this specific test
    test_specific_config = SettingsConfigDict(
        env_file=(), # Disable .env file loading for this instance
        env_file_encoding=original_model_config_encoding,
        case_sensitive=original_model_config_case_sensitive
        # Include other relevant original model_config settings if they exist and are needed
    )
    
    # Use monkeypatch to temporarily change the class's model_config
    # This is better than direct assignment if you want it reverted.
    monkeypatch.setattr(AppSettings, 'model_config', test_specific_config)
    
    settings = AppSettings()
    assert settings.deepseek_api_key is None

    # monkeypatch automatically reverts AppSettings.model_config after the test.
    # If you weren't using monkeypatch.setattr, you'd need to manually restore:
    # AppSettings.model_config['env_file'] = original_model_config_env_file
    # AppSettings.model_config['case_sensitive'] = original_model_config_case_sensitive
    # AppSettings.model_config['env_file_encoding'] = original_model_config_encoding