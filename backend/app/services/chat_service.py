"""One chat turn: save the user message, retrieve, generate, save the assistant message.

Failure policy: if retrieval or generation fails, the user's message stays saved (status "failed")
and NO assistant message is stored. The client can retry with retry_message_id.
"""
from __future__ import annotations

import logging
from typing import Any

from app.core.config import get_settings
from app.core.errors import UpstreamError
from app.schemas.chat import SendMessageResponse
from app.schemas.conversation import RetrievalInfo, SourceRef
from app.services import conversation_service as cs
from app.services import llm_service, prompts, retrieval_service

logger = logging.getLogger(__name__)
_HISTORY_CHAR_LIMIT = 1500


def _previous_user_text(history: list[dict[str, Any]]) -> str | None:
    for m in reversed(history):
        if m["role"] == "user":
            return m["content"][:_HISTORY_CHAR_LIMIT]
    return None


def _answer(content: str, history: list[dict[str, Any]]) -> tuple[str, RetrievalInfo]:
    """Return (assistant text, retrieval info). Raises UpstreamError on dependency failure."""
    s = get_settings()
    if prompts.is_small_talk(content):
        return prompts.GREETING_MESSAGE, RetrievalInfo(grounded=False)

    query = retrieval_service.build_query(content, _previous_user_text(history))
    chunks = retrieval_service.retrieve(query)
    if not chunks:
        return prompts.NO_ANSWER_MESSAGE, RetrievalInfo(grounded=False)

    turns = [{"role": m["role"], "content": m["content"][:_HISTORY_CHAR_LIMIT]} for m in history]
    text = llm_service.generate(prompts.build_messages(content, chunks, turns))
    sources = [
        SourceRef(document_id=c.document_id, chunk_id=c.chunk_id, title=c.title, section=c.section, score=round(c.score, 4))
        for c in chunks
    ]
    return text, RetrievalInfo(grounded=True, sources=sources, model=s.llm_model)


def send_message(
    user: dict[str, Any], conversation_id: str, content: str, retry_message_id: str | None = None
) -> SendMessageResponse:
    conv = cs.get_owned_conversation(user["_id"], conversation_id)

    if retry_message_id:
        user_msg = cs.get_retryable_user_message(conv, retry_message_id)
        content = user_msg["content"]  # trust the stored text, not the request body
    else:
        user_msg = cs.insert_message(conv, "user", content, "pending")
        cs.touch_conversation(conv, user_msg["created_at"], first_message=content)

    history = cs.recent_history(conv, exclude_id=user_msg["_id"])
    try:
        text, retrieval = _answer(content, history)
    except UpstreamError as exc:
        cs.set_message_status(user_msg["_id"], "failed")
        raise UpstreamError(exc.code, exc.message, user_message_id=str(user_msg["_id"])) from exc
    except Exception:
        cs.set_message_status(user_msg["_id"], "failed")
        raise

    assistant = cs.insert_message(conv, "assistant", text, "ok", retrieval.model_dump())
    user_msg = cs.set_message_status(user_msg["_id"], "answered")
    cs.touch_conversation(conv, assistant["created_at"])
    fresh_conv = cs.get_owned_conversation(user["_id"], conversation_id)
    return SendMessageResponse(
        user_message=cs.to_message_out(user_msg),
        assistant_message=cs.to_message_out(assistant),
        conversation=cs.to_conversation_out(fresh_conv),
    )
