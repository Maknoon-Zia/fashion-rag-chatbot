from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.deps import require_user
from app.schemas.chat import SendMessageRequest, SendMessageResponse
from app.services import chat_service

router = APIRouter(prefix="/api/conversations", tags=["chat"])


@router.post("/{conversation_id}/messages", response_model=SendMessageResponse)
def send_message(
    conversation_id: str, body: SendMessageRequest, user: dict[str, Any] = Depends(require_user)
) -> SendMessageResponse:
    return chat_service.send_message(user, conversation_id, body.content, body.retry_message_id)
