"""Index the Markdown knowledge base into Qdrant.

  python -m scripts.ingest              # create/update (safe to re-run; unchanged chunks are skipped)
  python -m scripts.ingest --dry-run    # show chunks only; needs no network or API keys
  python -m scripts.ingest --recreate   # drop and rebuild the collection (after changing model/dimensions)
"""
from __future__ import annotations

import argparse
import sys

from app.ingestion import IngestionError
from app.ingestion.indexer import build_chunks, ingest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--recreate", action="store_true", help="delete and rebuild the collection")
    parser.add_argument("--dry-run", action="store_true", help="chunk only; do not call Qdrant or the embedding API")
    args = parser.parse_args()

    try:
        if args.dry_run:
            _, chunks = build_chunks()
            for c in chunks:
                m = c.metadata
                print(f"{m.token_estimate:4d} tok  {m.chunk_id:70.70}  {m.section[:60]}")
        report = ingest(recreate=args.recreate, dry_run=args.dry_run, progress=print)
    except IngestionError as exc:
        print(f"Ingestion problem: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # connection/auth problems etc. - message only, no secrets
        print(f"Ingestion failed ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 2

    print("\n" + report.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
