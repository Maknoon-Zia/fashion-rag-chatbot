from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings
from app.schemas.conversation import ConversationOut, MessageOut


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1)
    # Set when retrying a message whose answer failed: reuses the saved user message.
    retry_message_id: str | None = None

    @field_validator("content")
    @classmethod
    def _validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message must not be empty")
        limit = get_settings().max_message_chars
        if len(v) > limit:
            raise ValueError(f"Message is too long (maximum {limit} characters)")
        return v


class SendMessageResponse(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
    conversation: ConversationOut
