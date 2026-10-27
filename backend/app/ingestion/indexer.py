"""Builds chunks from the knowledge folder and syncs them to Qdrant.

Idempotent: unchanged chunks are skipped (no re-embedding), changed chunks are updated in place,
chunks that no longer exist in the Markdown are deleted. Point IDs are deterministic.
"""
from __future__ import annotations

import logging
from collections.abc import Callable

from qdrant_client import QdrantClient, models

from app.core.config import Settings, get_settings
from app.db import qdrant as qdb
from app.ingestion import IngestionError
from app.ingestion.chunker import chunk_document
from app.ingestion.loader import load_documents
from app.schemas.knowledge import Chunk, IngestReport
from app.services import embedding_service

logger = logging.getLogger(__name__)


def build_chunks(settings: Settings | None = None) -> tuple[int, list[Chunk]]:
    """Read + chunk + validate every document. Returns (document count, chunks)."""
    s = settings or get_settings()
    manifest, docs = load_documents(s.knowledge_dir)
    chunks: list[Chunk] = []
    for entry, text in docs:
        chunks.extend(
            chunk_document(
                entry,
                text,
                manifest,
                max_tokens=s.chunk_max_tokens,
                min_tokens=s.chunk_min_tokens,
                overlap_tokens=s.chunk_overlap_tokens,
            )
        )
    ids = [c.point_id for c in chunks]
    if len(ids) != len(set(ids)):
        raise IngestionError("Duplicate chunk ids were generated - check for repeated headings")
    return len(docs), chunks


def _existing_state(client: QdrantClient, collection: str) -> dict[str, tuple]:
    """point id -> (content_hash, embedding_model, embedding_dimensions) for every stored point."""
    state: dict[str, tuple] = {}
    offset = None
    while True:
        points, offset = client.scroll(
            collection,
            limit=256,
            offset=offset,
            with_payload=["content_hash", "embedding_model", "embedding_dimensions"],
            with_vectors=False,
        )
        for p in points:
            pl = p.payload or {}
            state[str(p.id)] = (pl.get("content_hash"), pl.get("embedding_model"), pl.get("embedding_dimensions"))
        if offset is None:
            return state


def ingest(
    *,
    recreate: bool = False,
    dry_run: bool = False,
    client: QdrantClient | None = None,
    progress: Callable[[str], None] = lambda _msg: None,
) -> IngestReport:
    s = get_settings()
    doc_count, chunks = build_chunks(s)
    collection = s.qdrant_collection

    if dry_run:
        return IngestReport(
            collection=collection, documents=doc_count, chunks_total=len(chunks),
            embedded=0, skipped_unchanged=0, deleted_stale=0, dry_run=True,
        )

    client = client or qdb.get_qdrant()
    if recreate and client.collection_exists(collection):
        progress(f"Deleting collection '{collection}' (--recreate)")
        client.delete_collection(collection)

    size = qdb.collection_vector_size(client, collection)
    if size is None:
        progress(f"Creating collection '{collection}' ({s.embedding_dimensions} dims, cosine)")
        qdb.create_collection(client, collection, s.embedding_dimensions)
        existing: dict[str, tuple] = {}
    elif size != s.embedding_dimensions:
        raise IngestionError(
            f"Collection '{collection}' has {size}-dimensional vectors but EMBEDDING_DIMENSIONS="
            f"{s.embedding_dimensions}. Re-index safely with: python -m scripts.ingest --recreate"
        )
    else:
        existing = _existing_state(client, collection)

    signature = (s.embedding_model, s.embedding_dimensions)
    to_embed = [
        c for c in chunks
        if existing.get(c.point_id) != (c.metadata.content_hash, *signature)
    ]
    current_ids = {c.point_id for c in chunks}
    stale = [pid for pid in existing if pid not in current_ids]

    for start in range(0, len(to_embed), s.embed_batch_size):
        batch = to_embed[start : start + s.embed_batch_size]
        vectors = embedding_service.embed_documents([c.embed_text for c in batch])
        client.upsert(
            collection,
            wait=True,
            points=[
                models.PointStruct(
                    id=c.point_id,
                    vector=vec,
                    payload={
                        **c.metadata.model_dump(),
                        "text": c.text,
                        "embedding_model": signature[0],
                        "embedding_dimensions": signature[1],
                    },
                )
                for c, vec in zip(batch, vectors, strict=True)
            ],
        )
        progress(f"Embedded and stored {min(start + len(batch), len(to_embed))}/{len(to_embed)} chunks")

    if stale:
        client.delete(collection, points_selector=models.PointIdsList(points=stale), wait=True)

    return IngestReport(
        collection=collection, documents=doc_count, chunks_total=len(chunks),
        embedded=len(to_embed), skipped_unchanged=len(chunks) - len(to_embed),
        deleted_stale=len(stale), recreated=recreate,
    )
