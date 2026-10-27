from app.core.config import get_settings
from app.ingestion.chunker import chunk_document, estimate_tokens
from app.ingestion.indexer import build_chunks
from app.ingestion.loader import load_documents
from app.schemas.knowledge import Manifest, ManifestDocument


def test_all_ten_documents_are_read_and_chunked():
    docs, chunks = build_chunks()
    assert docs == 10
    assert {c.metadata.document_id for c in chunks} == {
        "fashion-color-001", "fashion-complexion-002", "fashion-menswear-003", "fashion-womenswear-004",
        "fashion-occasion-005", "fashion-wardrobe-006", "fashion-personalization-007",
        "fashion-examples-008", "fashion-traditional-009", "fashion-fabric-season-010",
    }
    assert 80 <= len(chunks) <= 130


def test_chunk_metadata_is_complete_and_valid():
    s = get_settings()
    _, chunks = build_chunks()
    for c in chunks:
        m = c.metadata
        assert m.document_id == m.document_id.strip() and m.chunk_id.startswith(m.document_id + "#")
        assert m.title and m.section and m.source.endswith(".md") and m.category and m.audience
        assert c.embed_text.startswith(f"{m.title} > ")
        assert m.token_estimate <= s.chunk_max_tokens + s.chunk_overlap_tokens + 20
        assert m.access_scope == "public" and len(m.content_hash) == 64


def test_ids_are_unique_and_stable_across_runs():
    _, a = build_chunks()
    _, b = build_chunks()
    assert [c.point_id for c in a] == [c.point_id for c in b]
    assert len({c.point_id for c in a}) == len(a)


def test_excluded_sections_are_not_indexed():
    _, chunks = build_chunks()
    joined_sections = " ".join(c.metadata.section.lower() for c in chunks)
    assert "retrieval summary" not in joined_sections
    assert "suggested evaluation questions" not in joined_sections
    assert "expected system behavior" not in joined_sections
    assert not any("Use this document for" in c.text for c in chunks)


def test_headings_stay_with_their_text():
    _, chunks = build_chunks()
    shoes = [c for c in chunks if c.metadata.section == "Suit coordination > Shoes and belt"]
    assert len(shoes) == 1 and "### 4.3 Shoes and belt" in shoes[0].text and "Black shoes" in shoes[0].text


def _entry():
    return ManifestDocument(file="x.md", document_id="doc-1", title="Doc", category="c")


def _manifest():
    return Manifest(project="t", knowledge_documents=[_entry()])


def test_long_section_is_split_with_overlap():
    sentences = [f"Sentence number {i} talks about outfit coordination and color balance." for i in range(60)]
    md = "# Doc\n\n**Audience:** all\n\n## 1. Big section\n\n" + " ".join(sentences) + "\n"
    chunks = chunk_document(_entry(), md, _manifest(), max_tokens=120, min_tokens=20, overlap_tokens=30)
    assert len(chunks) > 3
    assert all(estimate_tokens(c.text) <= 120 + 40 for c in chunks)
    import re
    last_in_first = re.findall(r"Sentence number \d+", chunks[0].text)[-1]
    assert last_in_first in chunks[1].text  # boundary sentence is repeated (overlap)
    assert chunks[1].text != chunks[0].text and all(c.text.strip() for c in chunks)


def test_tiny_sections_merge_but_never_exceed_max():
    md = "# Doc\n\n## 1. A\n\nShort one.\n\n## 2. B\n\nShort two.\n\n## 3. C\n\n" + ("word " * 300) + "\n"
    chunks = chunk_document(_entry(), md, _manifest(), max_tokens=150, min_tokens=40, overlap_tokens=10)
    assert len(chunks[0].text) < 200 and "Short one" in chunks[0].text and "Short two" in chunks[0].text
    assert all(estimate_tokens(c.text) <= 150 + 20 for c in chunks)


def test_manifest_id_mismatch_is_detected(tmp_path):
    import json, shutil
    import pytest
    from app.ingestion import IngestionError

    shutil.copytree(get_settings().knowledge_dir, tmp_path / "kb")
    m = json.loads((tmp_path / "kb" / "manifest.json").read_text())
    m["knowledge_documents"][0]["document_id"] = "wrong-id"
    (tmp_path / "kb" / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(IngestionError, match="differs from manifest"):
        load_documents(tmp_path / "kb")


def test_markdown_file_missing_from_manifest_is_reported(tmp_path):
    import shutil
    import pytest
    from app.ingestion import IngestionError

    shutil.copytree(get_settings().knowledge_dir, tmp_path / "kb")
    (tmp_path / "kb" / "99_extra.md").write_text("# Extra\n\n## 1. x\n\ntext\n")
    with pytest.raises(IngestionError, match="missing from manifest"):
        load_documents(tmp_path / "kb")
