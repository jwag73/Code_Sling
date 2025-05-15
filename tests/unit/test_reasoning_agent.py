# tests/unit/test_reasoning_agent.py
import pytest
from unittest.mock import MagicMock, patch

from src.ai.reasoning_agent import ReasoningAgent


# ------------------------------------------------------------------------- #
@pytest.fixture
def fake_settings(monkeypatch):
    """Deterministic settings for each test."""
    from src.config.settings import AppSettings

    settings = AppSettings(
        openai_api_key="test-key",
        openai_model="test-model",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        "src.ai.reasoning_agent.get_settings",
        lambda: settings,
        raising=True,
    )
    return settings


# ------------------------------------------------------------------------- #
def test_init_requires_api_key(fake_settings):
    from src.config.settings import AppSettings

    bad_settings = AppSettings(openai_api_key="", openai_model="x")
    with patch("src.ai.reasoning_agent.get_settings", return_value=bad_settings), pytest.raises(
        ValueError
    ):
        ReasoningAgent()


@patch("src.ai.reasoning_agent.openai.OpenAI")
def test_get_instructions_success(mock_openai_cls, fake_settings, monkeypatch):
    """Happy-path: AI returns an instruction list."""
    mock_choice = MagicMock()
    mock_choice.message.content = "INSERT 1: print('hi')"
    mock_completion = MagicMock(choices=[mock_choice])

    mock_client = mock_openai_cls.return_value
    mock_client.chat.completions.create.return_value = mock_completion

    monkeypatch.setattr("src.ai.reasoning_agent.add_line_numbers", lambda s: f"NUM:{s}", raising=True)

    agent = ReasoningAgent()
    out = agent.get_instructions("orig", "sugg")

    assert out == "INSERT 1: print('hi')"
    mock_client.chat.completions.create.assert_called_once()
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert "NUM:orig" in messages[1]["content"]
    assert "NUM:sugg" in messages[1]["content"]


@patch("src.ai.reasoning_agent.openai.OpenAI")
def test_get_instructions_api_error(mock_openai_cls, fake_settings, monkeypatch):
    """Surface an APIError as a clean error string."""
    from openai import APIError
    from unittest.mock import MagicMock  # already imported earlier, but explicit here for clarity

    mock_client = mock_openai_cls.return_value
    # Construct APIError with required args (message + request + body)
    mock_client.chat.completions.create.side_effect = APIError(
        message="boom",
        request=MagicMock(),
        body=None,          # <— new: satisfies the signature
    )

    monkeypatch.setattr("src.ai.reasoning_agent.add_line_numbers", lambda s: s, raising=True)

    agent = ReasoningAgent()
    out = agent.get_instructions("a", "b")
    assert out.startswith("ERROR:")
