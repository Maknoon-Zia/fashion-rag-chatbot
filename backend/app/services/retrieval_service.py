"""Semantic retrieval from Qdrant: embed the query, search, filter weak/duplicate hits."""
from __future__ import annotations

import logging
import re

from qdrant_client import QdrantClient, models

from app.core.config import get_settings
from app.core.errors import UpstreamError
from app.db.qdrant import get_qdrant
from app.schemas.knowledge import RetrievedChunk
from app.services import embedding_service

logger = logging.getLogger(__name__)
_SHORT_QUERY_WORDS = 8


def build_query(content: str, previous_user_text: str | None) -> str:
    """Short follow-ups ("what about shoes?") are searched together with the previous question."""
    if previous_user_text and len(content.split()) < _SHORT_QUERY_WORDS:
        return f"{previous_user_text}\n{content}"
    return content


def _norm(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()


def retrieve(
    query: str,
    *,
    categories: list[str] | None = None,
    client: QdrantClient | None = None,
) -> list[RetrievedChunk]:
    """Return up to RETRIEVAL_TOP_K relevant chunks scoring >= MIN_RELEVANCE_SCORE ([] if none)."""
    s = get_settings()
    vector = embedding_service.embed_query(query)  # raises UpstreamError on failure

    must = [models.FieldCondition(key="access_scope", match=models.MatchValue(value="public"))]
    if categories:
        must.append(models.FieldCondition(key="category", match=models.MatchAny(any=categories)))

    client = client or get_qdrant()
    try:
        response = client.query_points(
            collection_name=s.qdrant_collection,
            query=vector,
            limit=s.retrieval_candidates,
            score_threshold=s.min_relevance_score,
            query_filter=models.Filter(must=must),
            with_payload=True,
        )
    except Exception as exc:
        logger.error("Qdrant search failed: %s", type(exc).__name__)
        try:
            missing = not client.collection_exists(s.qdrant_collection)
        except Exception:
            missing = False
        if missing:
            raise UpstreamError(
                "knowledge_base_not_indexed",
                "The fashion knowledge base has not been indexed yet. Run: python -m scripts.ingest",
            ) from exc
        raise UpstreamError("knowledge_base_unavailable", "The knowledge base is unavailable. Please try again.") from exc

    selected: list[RetrievedChunk] = []
    per_doc: dict[str, int] = {}
    seen_text: set[str] = set()
    for hit in sorted(response.points, key=lambda p: p.score, reverse=True):
        p = hit.payload or {}
        doc_id, text = p.get("document_id", ""), p.get("text", "")
        if not text or per_doc.get(doc_id, 0) >= s.retrieval_max_per_document or _norm(text) in seen_text:
            continue
        per_doc[doc_id] = per_doc.get(doc_id, 0) + 1
        seen_text.add(_norm(text))
        selected.append(
            RetrievedChunk(
                text=text, score=float(hit.score), document_id=doc_id, chunk_id=p.get("chunk_id", ""),
                title=p.get("title", ""), section=p.get("section", ""), source=p.get("source", ""),
            )
        )
        if len(selected) >= s.retrieval_top_k:
            break
    return selected
