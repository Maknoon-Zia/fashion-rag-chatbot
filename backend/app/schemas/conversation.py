from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SourceRef(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    section: str
    score: float


class RetrievalInfo(BaseModel):
    grounded: bool
    sources: list[SourceRef] = Field(default_factory=list)
    model: str | None = None


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    status: Literal["pending", "answered", "failed", "ok"] = "ok"
    created_at: datetime
    retrieval: RetrievalInfo | None = None


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime


class ConversationList(BaseModel):
    items: list[ConversationOut]
    total: int
    limit: int
    offset: int


class ConversationDetail(BaseModel):
    conversation: ConversationOut
    messages: list[MessageOut]  # oldest -> newest
    has_more: bool
    next_before: str | None = None  # pass as ?before= to load older messages


class RenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def _clean(cls, v: str) -> str:
        v = " ".join(v.split())
        if not v:
            raise ValueError("Title must not be empty")
        return v
