"""Groq chat completion. Isolated so the provider can be swapped by editing this file only."""
from __future__ import annotations

import logging

from groq import Groq

from app.core.config import get_settings
from app.core.errors import UpstreamError

logger = logging.getLogger(__name__)
_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=get_settings().groq_api_key, timeout=45.0, max_retries=1)
    return _client


def generate(messages: list[dict[str, str]]) -> str:
    """Return the assistant text, or raise UpstreamError (never returns a fake answer)."""
    s = get_settings()
    try:
        response = _get_client().chat.completions.create(
            model=s.llm_model,
            messages=messages,
            temperature=s.llm_temperature,
            max_tokens=s.llm_max_tokens,
        )
    except Exception as exc:
        logger.error("LLM call failed: %s: %s", type(exc).__name__, str(exc)[:400])
        raise UpstreamError("llm_unavailable", "The answer service is unavailable. Please try again.") from exc
    text = (response.choices[0].message.content or "").strip() if response.choices else ""
    if not text:
        raise UpstreamError("llm_empty", "The answer service returned an empty response. Please try again.")
    return text
