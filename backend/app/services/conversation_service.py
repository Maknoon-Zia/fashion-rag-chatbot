"""MongoDB access for conversations and messages. Every query is scoped to the owning user."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import DESCENDING

from app.core.config import get_settings
from app.core.errors import AppError, NotFoundError
from app.db.mongo import get_db
from app.schemas.conversation import ConversationOut, MessageOut, RetrievalInfo

DEFAULT_TITLE = "New chat"


def utcnow() -> datetime:
    # MongoDB stores milliseconds; truncate so values compare equal after a round trip.
    now = datetime.now(timezone.utc)
    return now.replace(microsecond=now.microsecond // 1000 * 1000)


def parse_object_id(value: str, what: str = "Conversation") -> ObjectId:
    """Invalid ids are reported as 404 so that probing ids reveals nothing."""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError) as exc:
        raise NotFoundError(f"{what} not found.") from exc


def derive_title(content: str) -> str:
    """Short title from the first user message: whitespace collapsed, cut at a word boundary."""
    limit = 50
    text = " ".join(content.split())
    if len(text) <= limit:
        return text or DEFAULT_TITLE
    cut = text[:limit].rsplit(" ", 1)[0] or text[:limit]
    return cut.rstrip(".,;:!?-") + "…"


# ---------- serialisation ----------
def to_conversation_out(doc: dict[str, Any]) -> ConversationOut:
    return ConversationOut(
        id=str(doc["_id"]), title=doc["title"], created_at=doc["created_at"],
        updated_at=doc["updated_at"], last_message_at=doc["last_message_at"],
    )


def to_message_out(doc: dict[str, Any]) -> MessageOut:
    retrieval = RetrievalInfo.model_validate(doc["retrieval"]) if doc.get("retrieval") else None
    return MessageOut(
        id=str(doc["_id"]), conversation_id=str(doc["conversation_id"]), role=doc["role"],
        content=doc["content"], status=doc.get("status", "ok"), created_at=doc["created_at"], retrieval=retrieval,
    )


# ---------- conversations ----------
def create_conversation(user_id: ObjectId) -> dict[str, Any]:
    now = utcnow()
    doc = {
        "user_id": user_id, "title": DEFAULT_TITLE, "title_source": "default",
        "created_at": now, "updated_at": now, "last_message_at": now,
    }
    doc["_id"] = get_db().conversations.insert_one(doc).inserted_id
    return doc


def get_owned_conversation(user_id: ObjectId, conversation_id: str) -> dict[str, Any]:
    oid = parse_object_id(conversation_id)
    doc = get_db().conversations.find_one({"_id": oid, "user_id": user_id})
    if doc is None:
        raise NotFoundError("Conversation not found.")
    return doc


def list_conversations(user_id: ObjectId, limit: int, offset: int) -> tuple[list[dict[str, Any]], int]:
    col = get_db().conversations
    cursor = col.find({"user_id": user_id}).sort([("last_message_at", DESCENDING), ("_id", DESCENDING)])
    return list(cursor.skip(offset).limit(limit)), col.count_documents({"user_id": user_id})


def rename_conversation(user_id: ObjectId, conversation_id: str, title: str) -> dict[str, Any]:
    conv = get_owned_conversation(user_id, conversation_id)
    get_db().conversations.update_one(
        {"_id": conv["_id"], "user_id": user_id},
        {"$set": {"title": title, "title_source": "user", "updated_at": utcnow()}},
    )
    return get_owned_conversation(user_id, conversation_id)


def delete_conversation(user_id: ObjectId, conversation_id: str) -> None:
    conv = get_owned_conversation(user_id, conversation_id)
    db = get_db()
    db.messages.delete_many({"conversation_id": conv["_id"], "user_id": user_id})
    db.conversations.delete_one({"_id": conv["_id"], "user_id": user_id})


def touch_conversation(conv: dict[str, Any], when: datetime, first_message: str | None = None) -> None:
    """Bump activity time; set the auto title from the first user message if none was chosen."""
    update: dict[str, Any] = {"last_message_at": when, "updated_at": when}
    if first_message is not None and conv.get("title_source") == "default":
        update.update(title=derive_title(first_message), title_source="auto")
    get_db().conversations.update_one({"_id": conv["_id"], "user_id": conv["user_id"]}, {"$set": update})


# ---------- messages ----------
def insert_message(
    conv: dict[str, Any], role: str, content: str, status: str, retrieval: dict | None = None
) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "conversation_id": conv["_id"], "user_id": conv["user_id"], "role": role,
        "content": content, "status": status, "created_at": utcnow(),
    }
    if retrieval is not None:
        doc["retrieval"] = retrieval
    doc["_id"] = get_db().messages.insert_one(doc).inserted_id
    return doc


def set_message_status(message_id: ObjectId, status: str) -> dict[str, Any]:
    get_db().messages.update_one({"_id": message_id}, {"$set": {"status": status}})
    return get_db().messages.find_one({"_id": message_id})


def get_page(conv: dict[str, Any], limit: int, before: str | None) -> tuple[list[dict[str, Any]], bool]:
    """Newest `limit` messages (optionally older than message id `before`), returned oldest-first."""
    query: dict[str, Any] = {"conversation_id": conv["_id"], "user_id": conv["user_id"]}
    if before:
        anchor = get_db().messages.find_one({**query, "_id": parse_object_id(before, "Message")})
        if anchor is None:
            raise NotFoundError("Message not found.")
        query["$or"] = [
            {"created_at": {"$lt": anchor["created_at"]}},
            {"created_at": anchor["created_at"], "_id": {"$lt": anchor["_id"]}},
        ]
    rows = list(
        get_db().messages.find(query).sort([("created_at", DESCENDING), ("_id", DESCENDING)]).limit(limit + 1)
    )
    has_more = len(rows) > limit
    return list(reversed(rows[:limit])), has_more


def get_retryable_user_message(conv: dict[str, Any], message_id: str) -> dict[str, Any]:
    """The message must belong to this conversation, be unanswered, and be the latest message."""
    msg = get_db().messages.find_one(
        {"_id": parse_object_id(message_id, "Message"), "conversation_id": conv["_id"], "user_id": conv["user_id"]}
    )
    if msg is None or msg["role"] != "user":
        raise NotFoundError("Message not found.")
    latest = get_db().messages.find_one(
        {"conversation_id": conv["_id"]}, sort=[("created_at", DESCENDING), ("_id", DESCENDING)]
    )
    if msg["status"] not in ("pending", "failed") or latest["_id"] != msg["_id"]:
        raise AppError(409, "not_retryable", "That message was already answered or is no longer the latest.")
    return msg


def recent_history(conv: dict[str, Any], exclude_id: ObjectId) -> list[dict[str, Any]]:
    """Previous answered turns (oldest first) used as conversational context for the LLM."""
    limit = get_settings().history_messages
    if limit == 0:
        return []
    rows = get_db().messages.find(
        {
            "conversation_id": conv["_id"], "user_id": conv["user_id"], "_id": {"$ne": exclude_id},
            "$or": [{"role": "assistant"}, {"role": "user", "status": "answered"}],
        }
    ).sort([("created_at", DESCENDING), ("_id", DESCENDING)]).limit(limit)
    return list(reversed(list(rows)))
