"""Test setup. Tests NEVER touch real services: MongoDB is mongomock, Qdrant runs in memory,
embeddings and the LLM are replaced by deterministic fakes."""
from __future__ import annotations

import math
import os
import re
import zlib

# Settings must exist before the app modules are imported.
os.environ.update(
    MONGODB_URI="mongodb://localhost:27017",
    MONGODB_DB_NAME="fashion_test",
    QDRANT_URL="http://localhost:6333",
    QDRANT_COLLECTION="fashion_test",
    GEMINI_API_KEY="test-gemini-key",
    GROQ_API_KEY="test-groq-key",
    JWT_SECRET_KEY="test-secret-test-secret-test-secret-1234",
    EMBEDDING_DIMENSIONS="512",
    MIN_RELEVANCE_SCORE="0.25",
    CORS_ORIGINS="http://localhost:5173",
)

import mongomock  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from qdrant_client import QdrantClient  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.db import mongo as mongo_module  # noqa: E402
from app.db import qdrant as qdrant_module  # noqa: E402
from app.main import create_app  # noqa: E402
from app.services import embedding_service, llm_service  # noqa: E402


def fake_vector(text: str) -> list[float]:
    """Bag-of-words hashing embedding: texts sharing words get similar vectors."""
    dims = get_settings().embedding_dimensions
    vec = [0.0] * dims
    for word in re.findall(r"[a-z]{3,}", text.lower()):
        vec[zlib.crc32(word.encode()) % dims] += 1.0
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


class FakeLLM:
    def __init__(self) -> None:
        self.calls: list[list[dict]] = []
        self.error: Exception | None = None
        self.reply = "Try a cream hijab for contrast [1]."

    def generate(self, messages: list[dict]) -> str:
        self.calls.append(messages)
        if self.error:
            raise self.error
        return self.reply


@pytest.fixture(autouse=True)
def isolated_services(monkeypatch):
    mongo_module._client = mongomock.MongoClient(tz_aware=True)
    qdrant_module._client = QdrantClient(":memory:")
    monkeypatch.setattr(embedding_service, "embed_documents", lambda texts: [fake_vector(t) for t in texts])
    monkeypatch.setattr(embedding_service, "embed_query", fake_vector)
    yield
    mongo_module._client = None
    qdrant_module._client = None


@pytest.fixture
def llm(monkeypatch) -> FakeLLM:
    fake = FakeLLM()
    monkeypatch.setattr(llm_service, "generate", fake.generate)
    return fake


@pytest.fixture
def indexed_kb():
    from app.ingestion.indexer import ingest

    return ingest()


@pytest.fixture
def client():
    with TestClient(create_app()) as c:
        yield c


def make_user(client: TestClient, email: str = "a@example.com", name: str = "Alice") -> dict:
    """Register + login; returns auth headers."""
    body = {"name": name, "email": email, "password": "Passw0rdOK", "confirm_password": "Passw0rdOK"}
    assert client.post("/api/auth/register", json=body).status_code == 201
    r = client.post("/api/auth/login", json={"email": email, "password": "Passw0rdOK"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def alice(client):
    return make_user(client, "alice@example.com", "Alice")


@pytest.fixture
def bob(client):
    return make_user(client, "bob@example.com", "Bob")
