"""Reads manifest.json and the Markdown files it lists. No chunking or embedding here."""
from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import ValidationError

from app.ingestion import IngestionError
from app.schemas.knowledge import Manifest, ManifestDocument

_DOC_ID_RE = re.compile(r"\*\*Document ID:\*\*\s*(\S+)")


def load_manifest(knowledge_dir: Path) -> Manifest:
    path = knowledge_dir / "manifest.json"
    if not path.is_file():
        raise IngestionError(f"manifest.json not found in {knowledge_dir}")
    try:
        return Manifest.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise IngestionError(f"manifest.json is invalid: {exc}") from exc


def load_documents(knowledge_dir: Path) -> tuple[Manifest, list[tuple[ManifestDocument, str]]]:
    """Return the manifest and (entry, markdown text) pairs, after consistency checks."""
    manifest = load_manifest(knowledge_dir)

    listed = {d.file for d in manifest.knowledge_documents}
    unlisted = sorted(p.name for p in knowledge_dir.glob("*.md") if p.name not in listed)
    if unlisted:
        raise IngestionError(f"Markdown files missing from manifest.json: {', '.join(unlisted)}")

    ids = [d.document_id for d in manifest.knowledge_documents]
    if len(ids) != len(set(ids)):
        raise IngestionError("manifest.json contains duplicate document_id values")

    docs: list[tuple[ManifestDocument, str]] = []
    for entry in manifest.knowledge_documents:
        path = knowledge_dir / entry.file
        if not path.is_file():
            raise IngestionError(f"File listed in manifest not found: {entry.file}")
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise IngestionError(f"File is empty: {entry.file}")
        match = _DOC_ID_RE.search(text)
        if match and match.group(1).strip() != entry.document_id:
            raise IngestionError(
                f"{entry.file}: Document ID in file ({match.group(1)}) differs from manifest ({entry.document_id})"
            )
        docs.append((entry, text))
    return manifest, docs
