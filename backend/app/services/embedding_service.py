"""Gemini embeddings. Documents and queries use the SAME model and dimensions (set in .env).

The provider is isolated in this file: to switch providers, replace `_embed` only.
"""
from __future__ import annotations

import logging
import math
import time

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.core.errors import UpstreamError

logger = logging.getLogger(__name__)
_client: genai.Client | None = None
_RETRYABLE = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 4


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=get_settings().gemini_api_key)
    return _client


def _normalise(vec: list[float]) -> list[float]:
    """Gemini only guarantees unit length at 3072 dims; normalise so cosine scores are consistent."""
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def _call(contents: list[str], task_type: str) -> list[list[float]]:
    s = get_settings()
    config = types.EmbedContentConfig(task_type=task_type, output_dimensionality=s.embedding_dimensions)
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            result = _get_client().models.embed_content(model=s.embedding_model, contents=contents, config=config)
            return [list(e.values) for e in result.embeddings]
        except Exception as exc:  # SDK raises several error types; classify by HTTP-like code
            code = getattr(exc, "code", None)
            if code in _RETRYABLE and attempt < _MAX_ATTEMPTS:
                delay = 2**attempt
                logger.warning("Embedding call failed (code %s), retrying in %ss", code, delay)
                time.sleep(delay)
                continue
            logger.error("Embedding call failed: %s (code=%s)", type(exc).__name__, code)
            raise UpstreamError("embedding_unavailable", "The embedding service is unavailable. Please try again.") from exc
    raise UpstreamError("embedding_unavailable", "The embedding service is unavailable. Please try again.")


def _embed(texts: list[str], task_type: str) -> list[list[float]]:
    vectors = _call(texts, task_type)
    if len(vectors) != len(texts):  # some deployments accept one text per request: fall back
        vectors = [v for t in texts for v in _call([t], task_type)]
    dims = get_settings().embedding_dimensions
    if any(len(v) != dims for v in vectors):
        raise UpstreamError("embedding_unavailable", "The embedding service returned an unexpected vector size.")
    return [_normalise(v) for v in vectors]


def embed_documents(texts: list[str]) -> list[list[float]]:
    return _embed(texts, "RETRIEVAL_DOCUMENT") if texts else []


def embed_query(text: str) -> list[float]:
    return _embed([text], "RETRIEVAL_QUERY")[0]
