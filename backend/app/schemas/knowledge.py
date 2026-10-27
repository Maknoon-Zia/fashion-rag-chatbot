"""Schemas for the knowledge base: manifest entries, chunks, retrieval results, ingestion report."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

RetrievalRole = Literal["knowledge", "example_library", "behavior_guidance"]


class ManifestDocument(BaseModel):
    file: str
    document_id: str
    title: str
    category: str
    retrieval_role: RetrievalRole = "knowledge"
    purpose: str = ""
    exclude_headings: list[str] = Field(default_factory=list)

    @field_validator("document_id", "title", "category", "file")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v


class Manifest(BaseModel):
    project: str
    language: str = "en"
    access_scope: str = "public"
    global_exclude_headings: list[str] = Field(default_factory=list)
    knowledge_documents: list[ManifestDocument]


class ChunkMetadata(BaseModel):
    """Payload stored next to every vector in Qdrant (besides `text`)."""

    document_id: str
    chunk_id: str
    source: str  # original file name
    title: str  # document title
    section: str  # heading breadcrumb, e.g. "Suit coordination > Shoes and belt"
    category: str
    retrieval_role: RetrievalRole
    audience: str = ""
    language: str = "en"
    access_scope: str = "public"
    chunk_index: int = Field(ge=0)
    token_estimate: int = Field(ge=1)
    content_hash: str


class Chunk(BaseModel):
    point_id: str  # deterministic UUID derived from chunk_id
    text: str  # raw section text shown to the LLM
    embed_text: str  # text actually embedded (breadcrumb + text)
    metadata: ChunkMetadata


class RetrievedChunk(BaseModel):
    text: str
    score: float
    document_id: str
    chunk_id: str
    title: str
    section: str
    source: str


class IngestReport(BaseModel):
    collection: str
    documents: int
    chunks_total: int
    embedded: int
    skipped_unchanged: int
    deleted_stale: int
    recreated: bool = False
    dry_run: bool = False
