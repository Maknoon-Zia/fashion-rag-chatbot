from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.db import mongo
from app.db.qdrant import get_qdrant

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict:
    """Reports dependency status without exposing any configuration values."""
    mongo_status, qdrant_status = "ok", "ok"
    try:
        mongo.ping()
    except Exception:
        mongo_status = "unreachable"
    try:
        client = get_qdrant()
        name = get_settings().qdrant_collection
        qdrant_status = "ok" if client.collection_exists(name) else "collection_missing (run ingestion)"
    except Exception:
        qdrant_status = "unreachable"
    overall = "ok" if mongo_status == "ok" and qdrant_status == "ok" else "degraded"
    return {"status": overall, "mongodb": mongo_status, "qdrant": qdrant_status}
