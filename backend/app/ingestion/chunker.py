"""Heading-aware chunking of the Markdown knowledge files.

Strategy (see README for the reasoning):
  * A level-2 section ("## ...") is the natural unit; it is kept whole if it fits CHUNK_MAX_TOKENS.
  * Larger sections are split at level-3 headings ("### ..."), each keeping its parent heading.
  * Sections smaller than CHUNK_MIN_TOKENS are merged with the next unit when the result still fits.
  * A single unit that is still too large is split at paragraph/sentence boundaries with a small
    overlap (CHUNK_OVERLAP_TOKENS). Overlap is used ONLY here; heading boundaries are clean cuts.
  * Every chunk is embedded with a "Document title > section" prefix so it makes sense alone.
Token counts are estimates (characters / 4) - the embedding model accepts far more than we send.
"""
from __future__ import annotations

import hashlib
import math
import re
import uuid
from dataclasses import dataclass, field

from app.ingestion import IngestionError
from app.schemas.knowledge import Chunk, ChunkMetadata, Manifest, ManifestDocument

_NAMESPACE = uuid.UUID("6f1c0b52-3c1e-4b8e-9d3a-5a1f0d7e2c11")  # fixed: keeps point IDs stable
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_NUMBER_PREFIX_RE = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+")
_FRONT_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.*?)\s*$")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def _clean_heading(raw: str) -> str:
    return _NUMBER_PREFIX_RE.sub("", raw).strip()


def _slug(raw: str, limit: int = 60) -> str:
    return re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")[:limit] or "section"


def _normalise(text: str) -> str:
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


@dataclass
class _Section:
    raw_h2: str
    intro: list[str] = field(default_factory=list)
    subs: list[tuple[str, list[str]]] = field(default_factory=list)  # (raw h3, body lines)

    def full_text(self) -> str:
        parts = ["\n".join(self.intro)] + [f"### {h}\n" + "\n".join(b) for h, b in self.subs]
        return _normalise(f"## {self.raw_h2}\n\n" + "\n\n".join(p for p in parts if p.strip()))


@dataclass
class _Unit:
    label: str  # human breadcrumb part, e.g. "Suit coordination > Shoes and belt"
    slug: str
    text: str
    h2: str

    @property
    def tokens(self) -> int:
        return estimate_tokens(self.text)


def parse_markdown(text: str) -> tuple[str, dict[str, str], list[_Section]]:
    """Return (document title, front-matter fields, level-2 sections)."""
    title, front, sections = "", {}, []
    current: _Section | None = None
    current_sub: list[str] | None = None
    in_fence = False
    for line in text.replace("\r\n", "\n").split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else _HEADING_RE.match(line)
        level = len(m.group(1)) if m else 0
        if level == 1 and not title:
            title = m.group(2).strip()
        elif level == 2:
            current = _Section(raw_h2=m.group(2).strip())
            sections.append(current)
            current_sub = None
        elif level == 3 and current is not None:
            current_sub = []
            current.subs.append((m.group(2).strip(), current_sub))
        elif current is None:
            fm = _FRONT_RE.match(line.strip())
            if fm:
                front[fm.group(1).strip().lower()] = fm.group(2).strip()
        elif current_sub is not None:
            current_sub.append(line)
        else:
            current.intro.append(line)
    if not title:
        raise IngestionError("Document has no '# Title' heading")
    return title, front, sections


def _split_long(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    """Split oversized text at paragraph, then sentence boundaries; add a small overlap."""
    pieces: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        if estimate_tokens(block) <= max_tokens:
            pieces.append(block)
            continue
        for line in block.split("\n"):
            if estimate_tokens(line) <= max_tokens:
                pieces.append(line)
                continue
            for sentence in _SENTENCE_RE.split(line):
                if estimate_tokens(sentence) <= max_tokens:
                    pieces.append(sentence)
                else:  # pathological: no punctuation at all - hard split
                    step = max_tokens * 4
                    pieces.extend(sentence[i : i + step] for i in range(0, len(sentence), step))
    chunks: list[str] = []
    buf: list[str] = []
    has_new = False  # True once buf holds text beyond the carried-over overlap
    for piece in pieces:
        if has_new and estimate_tokens("\n\n".join(buf + [piece])) > max_tokens:
            chunks.append("\n\n".join(buf))
            carried = _tail("\n\n".join(buf), overlap_tokens) if overlap_tokens else ""
            buf, has_new = ([carried] if carried else []), False
        buf.append(piece)
        has_new = True
    if buf and has_new:
        chunks.append("\n\n".join(buf))
    return chunks


def _tail(text: str, tokens: int) -> str:
    """Trailing text of about `tokens` tokens: whole sentences if they fit, else the last words."""
    out: list[str] = []
    for sentence in reversed(_SENTENCE_RE.split(text.strip())):
        if estimate_tokens(" ".join([sentence] + out)) > tokens:
            break
        out.insert(0, sentence)
    if out:
        return " ".join(out)
    tail = text.strip()[-tokens * 4 :]  # one huge sentence: keep only its last words
    return tail.split(" ", 1)[-1] if " " in tail else tail


def _units_for_section(sec: _Section, max_tokens: int, overlap: int) -> list[_Unit]:
    h2 = _clean_heading(sec.raw_h2)
    base_slug = _slug(sec.raw_h2)
    units: list[_Unit] = []
    full = sec.full_text()
    if estimate_tokens(full) <= max_tokens or not sec.subs:
        units.append(_Unit(h2, base_slug, full, h2))
    else:
        intro = _normalise("\n".join(sec.intro))
        if intro:
            units.append(_Unit(h2, base_slug, _normalise(f"## {sec.raw_h2}\n\n{intro}"), h2))
        for raw_h3, body in sec.subs:
            body_text = _normalise("\n".join(body))
            text = _normalise(f"## {sec.raw_h2}\n\n### {raw_h3}\n\n{body_text}")
            units.append(_Unit(f"{h2} > {_clean_heading(raw_h3)}", f"{base_slug}--{_slug(raw_h3)}", text, h2))
    # split any unit that is still too large
    result: list[_Unit] = []
    for u in units:
        if u.tokens <= max_tokens:
            result.append(u)
            continue
        for i, part in enumerate(_split_long(u.text, max_tokens, overlap), start=1):
            result.append(_Unit(u.label, f"{u.slug}-p{i}", part, u.h2))
    return result


def _merge_small(units: list[_Unit], min_tokens: int, max_tokens: int) -> list[_Unit]:
    merged: list[_Unit] = []
    i = 0
    while i < len(units):
        cur = units[i]
        while cur.tokens < min_tokens and i + 1 < len(units):
            nxt = units[i + 1]
            if estimate_tokens(cur.text + "\n\n" + nxt.text) > max_tokens:
                break
            cur = _Unit(f"{cur.label} + {nxt.label}", f"{cur.slug}_{nxt.slug}"[:90], cur.text + "\n\n" + nxt.text, cur.h2)
            i += 1
        merged.append(cur)
        i += 1
    return merged


def chunk_document(
    entry: ManifestDocument,
    text: str,
    manifest: Manifest,
    *,
    max_tokens: int,
    min_tokens: int,
    overlap_tokens: int,
) -> list[Chunk]:
    if overlap_tokens >= max_tokens:
        raise IngestionError("CHUNK_OVERLAP_TOKENS must be smaller than CHUNK_MAX_TOKENS")
    title, front, sections = parse_markdown(text)
    excluded = {h.strip().lower() for h in manifest.global_exclude_headings + entry.exclude_headings}

    units: list[_Unit] = []
    for sec in sections:
        if _clean_heading(sec.raw_h2).lower() in excluded:
            continue
        units.extend(_units_for_section(sec, max_tokens, overlap_tokens))
    units = _merge_small(units, min_tokens, max_tokens)
    if not units:
        raise IngestionError(f"{entry.file}: no indexable sections found")

    chunks: list[Chunk] = []
    seen: dict[str, int] = {}
    for index, u in enumerate(units):
        slug = u.slug
        seen[slug] = seen.get(slug, 0) + 1
        if seen[slug] > 1:
            slug = f"{slug}-{seen[slug]}"
        chunk_id = f"{entry.document_id}#{slug}"
        embed_text = f"{entry.title} > {u.label}\n\n{u.text}"
        metadata = ChunkMetadata(
            document_id=entry.document_id,
            chunk_id=chunk_id,
            source=entry.file,
            title=entry.title,
            section=u.label,
            category=entry.category,
            retrieval_role=entry.retrieval_role,
            audience=front.get("audience", ""),
            language=manifest.language,
            access_scope=manifest.access_scope,
            chunk_index=index,
            token_estimate=estimate_tokens(u.text),
            content_hash=hashlib.sha256(embed_text.encode("utf-8")).hexdigest(),
        )
        chunks.append(
            Chunk(
                point_id=str(uuid.uuid5(_NAMESPACE, chunk_id)),
                text=u.text,
                embed_text=embed_text,
                metadata=metadata,
            )
        )
    return chunks
