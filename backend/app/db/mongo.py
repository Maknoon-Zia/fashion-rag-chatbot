"""MongoDB connection (one shared client) and index setup."""
from __future__ import annotations

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database

from app.core.config import get_settings

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        s = get_settings()
        _client = MongoClient(
            s.mongodb_uri, tz_aware=True, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000
        )
    return _client


def get_db() -> Database:
    return get_client()[get_settings().mongodb_db_name]


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


def ensure_indexes(db: Database | None = None) -> None:
    """Idempotent. Creates the indexes required by the brief plus token-revocation indexes."""
    db = db if db is not None else get_db()
    db.users.create_index([("email", ASCENDING)], unique=True, name="uniq_email")
    db.conversations.create_index(
        [("user_id", ASCENDING), ("last_message_at", DESCENDING)], name="user_last_message"
    )
    db.messages.create_index(
        [("conversation_id", ASCENDING), ("created_at", ASCENDING)], name="conversation_created"
    )
    db.revoked_tokens.create_index([("jti", ASCENDING)], unique=True, name="uniq_jti")
    db.revoked_tokens.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0, name="ttl_expires")


def ping() -> None:
    get_client().admin.command("ping")
