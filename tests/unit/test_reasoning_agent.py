# tests/unit/test_reasoning_agent.py
import pytest
from unittest.mock import MagicMock, patch
from src.ai.reasoning_agent import ReasoningAgent
from src.config.settings import AppSettings # Make sure this is imported
# If AppSettings is not directly in src.config.settings, adjust as needed
# based on your settings.py structure. It appears to be, from your files.


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


# Add this new test function:
def test_init_requires_api_key_with_direct_settings():
    """Test ReasoningAgent raises ValueError if API key is missing in direct settings."""
    # Create an AppSettings instance with an invalid API key
    # Ensure all fields AppSettings expects are provided, or they have defaults.
    # Based on your settings.py, openai_model and timeout_seconds have defaults.
    bad_settings = AppSettings(openai_api_key="", openai_model="test-model-bad")

    with pytest.raises(ValueError, match="OpenAI API key not configured in settings."):
        ReasoningAgent(settings=bad_settings)




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


# Add this new test function:
@patch("src.ai.reasoning_agent.openai.OpenAI")
def test_get_instructions_success_with_direct_settings(mock_openai_cls, fake_settings, monkeypatch):
    """Happy-path: AI returns an instruction list, agent uses direct settings."""
    mock_choice = MagicMock()
    mock_choice.message.content = "INSERT 1: print('hi direct')"
    mock_completion = MagicMock(choices=[mock_choice])

    mock_client = mock_openai_cls.return_value
    mock_client.chat.completions.create.return_value = mock_completion

    # Patch add_line_numbers as it's called by get_instructions
    monkeypatch.setattr("src.ai.reasoning_agent.add_line_numbers", lambda s: f"NUM_DIRECT:{s}")

    # Key change: Initialize ReasoningAgent with the fake_settings object directly
    agent = ReasoningAgent(settings=fake_settings)
    out = agent.get_instructions("orig_direct", "sugg_direct")

    assert out == "INSERT 1: print('hi direct')"
    mock_client.chat.completions.create.assert_called_once()
    # You can add more assertions here if needed, like checking call_args for the mock_client
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert "NUM_DIRECT:orig_direct" in messages[1]["content"]
    assert "NUM_DIRECT:sugg_direct" in messages[1]["content"]
    assert mock_client.chat.completions.create.call_args.kwargs["model"] == fake_settings.openai_model


# Add this new test function:
@patch("src.ai.reasoning_agent.openai.OpenAI")
def test_get_instructions_api_error_with_direct_settings(mock_openai_cls, fake_settings, monkeypatch):
    """Surface an APIError as a clean error string, agent uses direct settings."""
    from openai import APIError # Keep this import local if only for this test or move to top

    mock_client = mock_openai_cls.return_value
    mock_client.chat.completions.create.side_effect = APIError(
        message="boom direct",
        request=MagicMock(), # APIError constructor requires a request object
        body=None # And a body
    )

    monkeypatch.setattr("src.ai.reasoning_agent.add_line_numbers", lambda s: s)

    # Key change: Initialize ReasoningAgent with the fake_settings object directly
    agent = ReasoningAgent(settings=fake_settings)
    out = agent.get_instructions("a_direct", "b_direct")

    assert out.startswith("ERROR: OpenAI API error – boom direct")




# Add this new test function:
@patch("src.ai.reasoning_agent.openai.OpenAI") # We patch to avoid actual API calls
def test_init_with_direct_valid_settings(mock_openai_constructor, fake_settings):
    """Test ReasoningAgent initializes correctly when valid settings are passed directly."""
    # fake_settings fixture provides a valid AppSettings instance
    agent = ReasoningAgent(settings=fake_settings)

    # Check that the OpenAI client was attempted to be initialized with correct parameters
    mock_openai_constructor.assert_called_once_with(
        api_key=fake_settings.openai_api_key,
        timeout=fake_settings.timeout_seconds,
    )
    # Check that internal attributes are set from the passed settings
    assert agent._model_name == fake_settings.openai_model
    assert agent._client == mock_openai_constructor.return_value # Ensure the client instance was assigned




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
