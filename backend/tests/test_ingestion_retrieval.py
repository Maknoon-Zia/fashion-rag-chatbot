import shutil

import pytest

from app.core.config import get_settings
from app.core.errors import UpstreamError
from app.db.qdrant import get_qdrant
from app.ingestion import IngestionError
from app.ingestion.indexer import ingest
from app.services import embedding_service, retrieval_service


@pytest.fixture
def kb_copy(tmp_path, monkeypatch):
    dest = tmp_path / "kb"
    shutil.copytree(get_settings().knowledge_dir, dest)
    monkeypatch.setattr(get_settings(), "knowledge_dir", dest)
    return dest


def test_first_ingest_stores_every_chunk():
    report = ingest()
    assert report.embedded == report.chunks_total > 0 and report.skipped_unchanged == 0
    s = get_settings()
    assert get_qdrant().count(s.qdrant_collection).count == report.chunks_total
    point = get_qdrant().scroll(s.qdrant_collection, limit=1, with_payload=True)[0][0]
    for key in ("text", "document_id", "chunk_id", "source", "title", "section", "access_scope", "content_hash"):
        assert key in point.payload


def test_rerun_does_not_duplicate_or_reembed(monkeypatch):
    first = ingest()
    calls = []
    monkeypatch.setattr(embedding_service, "embed_documents", lambda t: calls.append(len(t)) or [[1.0] * 512 for _ in t])
    second = ingest()
    assert second.embedded == 0 and second.skipped_unchanged == first.chunks_total and calls == []
    assert get_qdrant().count(get_settings().qdrant_collection).count == first.chunks_total


def test_changed_section_is_reembedded_and_removed_section_is_deleted(kb_copy):
    first = ingest()
    f = kb_copy / "01_color_theory_and_coordination.md"
    text = f.read_text(encoding="utf-8")
    f.write_text(text.replace("burgundy tie use grey and white", "burgundy tie use grey and ivory"), encoding="utf-8")
    second = ingest()
    assert second.embedded == 1 and second.deleted_stale == 0

    f.write_text(f.read_text(encoding="utf-8").split("## 8. Personalization checklist")[0], encoding="utf-8")
    third = ingest()
    assert third.deleted_stale == 1 and third.embedded == 0
    assert get_qdrant().count(get_settings().qdrant_collection).count == first.chunks_total - 1


def test_dimension_mismatch_refuses_and_recreate_fixes(monkeypatch):
    ingest()
    monkeypatch.setattr(get_settings(), "embedding_dimensions", 32)
    monkeypatch.setattr(embedding_service, "embed_documents", lambda t: [[1.0] * 32 for _ in t])
    with pytest.raises(IngestionError, match="--recreate"):
        ingest()
    report = ingest(recreate=True)
    assert report.recreated and report.embedded == report.chunks_total


def test_dry_run_touches_nothing():
    report = ingest(dry_run=True)
    assert report.dry_run and not get_qdrant().collection_exists(get_settings().qdrant_collection)


def test_retrieval_finds_relevant_documents(indexed_kb):
    hits = retrieval_service.retrieve("What hijab or scarf color works with a black abaya?")
    assert hits and hits[0].score >= get_settings().min_relevance_score
    assert {"fashion-womenswear-004", "fashion-examples-008", "fashion-color-001", "fashion-complexion-002"} & {
        h.document_id for h in hits
    }
    assert all(h.title and h.section and h.source for h in hits)


def test_retrieval_respects_per_document_cap_top_k_and_no_duplicates(indexed_kb):
    s = get_settings()
    hits = retrieval_service.retrieve("outfit color coordination for office shirt trousers shoes belt")
    assert len(hits) <= s.retrieval_top_k
    for doc in {h.document_id for h in hits}:
        assert sum(h.document_id == doc for h in hits) <= s.retrieval_max_per_document
    assert len({h.chunk_id for h in hits}) == len(hits)


def test_metadata_filter_by_category(indexed_kb):
    hits = retrieval_service.retrieve("shirt trousers shoes belt tie", categories=["menswear"])
    assert hits and all(h.document_id == "fashion-menswear-003" for h in hits)


def test_unrelated_query_returns_nothing(indexed_kb):
    assert retrieval_service.retrieve("zxqv plorbat gnarfle wuzzle quixotic") == []


def test_missing_collection_raises_helpful_error():
    with pytest.raises(UpstreamError) as exc:
        retrieval_service.retrieve("black abaya hijab")
    assert exc.value.code == "knowledge_base_not_indexed"
