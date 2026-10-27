"""Qdrant client (one shared instance) and collection helpers."""
from __future__ import annotations

from qdrant_client import QdrantClient, models

from app.core.config import get_settings

_client: QdrantClient | None = None

KEYWORD_INDEX_FIELDS = ("document_id", "category", "retrieval_role", "access_scope")


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        s = get_settings()
        _client = QdrantClient(url=s.qdrant_url, api_key=s.qdrant_api_key or None, timeout=30)
    return _client


def close_qdrant() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


def collection_vector_size(client: QdrantClient, name: str) -> int | None:
    """Vector size of an existing collection, or None if the collection does not exist."""
    if not client.collection_exists(name):
        return None
    vectors = client.get_collection(name).config.params.vectors
    return getattr(vectors, "size", None)


def create_collection(client: QdrantClient, name: str, size: int) -> None:
    client.create_collection(
        collection_name=name,
        vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE),
    )
    for field in KEYWORD_INDEX_FIELDS:
        client.create_payload_index(name, field_name=field, field_schema=models.PayloadSchemaType.KEYWORD)
