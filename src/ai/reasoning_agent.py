# src/ai/reasoning_agent.py
"""
ReasoningAgent
==============

Generates INSERT / DELETE instructions that transform *original code*
into an *AI-generated suggestion* using an OpenAI chat model.
"""
from __future__ import annotations

import textwrap          # ← NEW: required for _build_prompt
from functools import lru_cache
from typing import Final

import openai
from openai import APIError, APIConnectionError, APITimeoutError

from src.config.settings import get_settings, AppSettings
from src.utils.code_utils import add_line_numbers



_SYSTEM_PROMPT: Final[str] = (
    "You are a precise code-transformation instruction generator. "
    "Reply ONLY with the requested list of operations (or 'NO CHANGES')."
)


class ReasoningAgent:
    """Wrapper around an OpenAI chat model that returns merge instructions."""

    def __init__(self, settings: AppSettings | None = None) -> None:
        current_settings: AppSettings
        if settings is None:
            current_settings = get_settings()
        else:
            current_settings = settings

        if not current_settings.openai_api_key:
            raise ValueError("OpenAI API key not configured in settings.")

        self._client = openai.OpenAI(
            api_key=current_settings.openai_api_key,
            timeout=current_settings.timeout_seconds,
        )
        self._model_name: str = current_settings.openai_model

    # ------------------------------------------------------------------ #
    def get_instructions(self, original_code: str, ai_suggestion: str) -> str:
        """Return the LLM’s merge instructions—or an ``ERROR: …`` string."""
        numbered_orig = add_line_numbers(original_code)
        numbered_sugg = add_line_numbers(ai_suggestion)
        prompt = _build_prompt(numbered_orig, numbered_sugg)

        try:
            completion = self._client.chat.completions.create(
                model=self._model_name,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            content = completion.choices[0].message.content or ""
            return content.strip() or "ERROR: AI returned empty content."
        except APITimeoutError:
            return "ERROR: request to OpenAI timed out."
        except APIConnectionError as exc:
            return f"ERROR: failed to connect to OpenAI – {exc}"
        except APIError as exc:
            return f"ERROR: OpenAI API error – {exc}"
        except Exception as exc:  # noqa: BLE001
            return f"ERROR: unexpected exception – {exc}"


# ---------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _build_prompt(numbered_original: str, numbered_suggestion: str) -> str:
    """Build and memoise the single user prompt sent to the model."""
    return textwrap.dedent(
        f"""
        You are an expert *diff engine*.

        **Original Code** (1-indexed):
        ```text
        {numbered_original}
        ```

        **AI-Generated Suggestion** (1-indexed):
        ```text
        {numbered_suggestion}
        ```

        Produce the *minimal* set of operations to transform the Original Code
        into the AI-Generated Suggestion, using ONLY:

        1. Insert lines *from the suggestion* **before** a line in the original:  
           `INSERT <orig_line_before>: <exact_code_content>`

        2. Delete one line:  
           `DELETE <orig_line>`

        3. Delete a contiguous range:  
           `DELETE <start_orig_line>-<end_orig_line>`

        If nothing needs changing, reply exactly:
        NO CHANGES
        """
    ).strip()
