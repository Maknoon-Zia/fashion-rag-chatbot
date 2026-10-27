"""Verify MongoDB, Qdrant, Gemini and Groq credentials one by one.

  python -m scripts.check_connections
Prints OK/FAIL per service (never prints secrets). Creates MongoDB indexes if MongoDB is reachable.
"""
from __future__ import annotations

import sys

from app.core.config import get_settings


def _run(name: str, fn) -> bool:
    try:
        detail = fn()
        print(f"[ OK ] {name}" + (f" - {detail}" if detail else ""))
        return True
    except Exception as exc:
        print(f"[FAIL] {name}: {type(exc).__name__}: {str(exc)[:200]}")
        return False


def main() -> int:
    try:
        s = get_settings()
    except Exception as exc:
        print(f"[FAIL] .env configuration: {exc}")
        return 1

    def mongo_check() -> str:
        from app.db import mongo

        mongo.ping()
        mongo.ensure_indexes()
        return f"database '{s.mongodb_db_name}', indexes ensured"

    def qdrant_check() -> str:
        from app.db.qdrant import get_qdrant

        c = get_qdrant()
        if not c.collection_exists(s.qdrant_collection):
            return f"reachable, collection '{s.qdrant_collection}' not created yet (run python -m scripts.ingest)"
        return f"collection '{s.qdrant_collection}' has {c.count(s.qdrant_collection).count} points"

    def gemini_check() -> str:
        from app.services import embedding_service

        vec = embedding_service.embed_query("navy blazer with grey trousers")
        return f"embedding returned {len(vec)} dimensions (expected {s.embedding_dimensions})"

    def groq_check() -> str:
        from app.services import llm_service

        return "reply: " + llm_service.generate([{"role": "user", "content": "Reply with the single word: ready"}])[:40]

    results = [
        _run("MongoDB Atlas", mongo_check),
        _run("Qdrant", qdrant_check),
        _run("Gemini embeddings", gemini_check),
        _run("Groq LLM", groq_check),
    ]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
