from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status

from app.deps import require_user
from app.schemas.conversation import ConversationDetail, ConversationList, ConversationOut, RenameRequest
from app.services import conversation_service as cs

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(user: dict[str, Any] = Depends(require_user)) -> ConversationOut:
    return cs.to_conversation_out(cs.create_conversation(user["_id"]))


@router.get("", response_model=ConversationList)
def list_conversations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict[str, Any] = Depends(require_user),
) -> ConversationList:
    docs, total = cs.list_conversations(user["_id"], limit, offset)
    return ConversationList(items=[cs.to_conversation_out(d) for d in docs], total=total, limit=limit, offset=offset)


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    before: str | None = Query(None, description="Message id; returns messages older than it"),
    user: dict[str, Any] = Depends(require_user),
) -> ConversationDetail:
    conv = cs.get_owned_conversation(user["_id"], conversation_id)
    rows, has_more = cs.get_page(conv, limit, before)
    return ConversationDetail(
        conversation=cs.to_conversation_out(conv),
        messages=[cs.to_message_out(r) for r in rows],
        has_more=has_more,
        next_before=str(rows[0]["_id"]) if has_more and rows else None,
    )


@router.patch("/{conversation_id}", response_model=ConversationOut)
def rename_conversation(
    conversation_id: str, body: RenameRequest, user: dict[str, Any] = Depends(require_user)
) -> ConversationOut:
    return cs.to_conversation_out(cs.rename_conversation(user["_id"], conversation_id, body.title))


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: str, user: dict[str, Any] = Depends(require_user)) -> Response:
    cs.delete_conversation(user["_id"], conversation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
