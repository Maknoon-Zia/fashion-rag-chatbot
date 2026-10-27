"""Environment-based settings. Every deployment-specific value lives here."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # MongoDB
    mongodb_uri: str
    mongodb_db_name: str = "fashion_chatbot"

    # Qdrant
    qdrant_url: str
    qdrant_api_key: str | None = None
    qdrant_collection: str = "fashion_knowledge"

    # Embeddings (Gemini)
    gemini_api_key: str
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = Field(768, ge=8, le=3072)

    # LLM (Groq)
    groq_api_key: str
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = Field(0.3, ge=0, le=1)
    llm_max_tokens: int = Field(900, ge=64, le=8000)

    # Auth
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(60, ge=1, le=1440)

    # HTTP
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Knowledge base / RAG
    knowledge_dir: Path = BACKEND_DIR / "data" / "knowledge"
    chunk_max_tokens: int = Field(400, ge=100)
    chunk_min_tokens: int = Field(80, ge=0)
    chunk_overlap_tokens: int = Field(40, ge=0)
    embed_batch_size: int = Field(16, ge=1, le=100)
    retrieval_top_k: int = Field(5, ge=1, le=20)
    retrieval_candidates: int = Field(10, ge=1, le=50)
    retrieval_max_per_document: int = Field(2, ge=1, le=10)
    min_relevance_score: float = Field(0.60, ge=0, le=1)
    history_messages: int = Field(6, ge=0, le=30)

    # Limits
    max_message_chars: int = Field(2000, ge=100, le=20000)
    max_title_chars: int = 120

    @field_validator("jwt_secret_key", "mongodb_uri", "qdrant_url", "gemini_api_key", "groq_api_key")
    @classmethod
    def _reject_placeholders(cls, v: str) -> str:
        v = v.strip()
        if not v or ("<" in v and ">" in v):
            raise ValueError("is empty or still a placeholder - edit your .env file")
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # raises a clear validation error if .env is incomplete
