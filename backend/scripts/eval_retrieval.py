"""Measure retrieval quality against data/eval_questions.json using the REAL embedding model + Qdrant.

  python -m scripts.eval_retrieval

For in-scope questions: Recall@k (does ANY expected document appear in the top-k?) and the rank of the
first expected document (for MRR). For out-of-scope questions: the best raw similarity score.
It then suggests a MIN_RELEVANCE_SCORE between the two groups. Limitations: tiny hand-made question
set, document-level (not passage-level) judgements, and similarity scores are model-specific.
"""
from __future__ import annotations

import json
import sys

from app.core.config import BACKEND_DIR, get_settings
from app.db.qdrant import get_qdrant
from app.services import embedding_service


def main() -> int:
    s = get_settings()
    questions = json.loads((BACKEND_DIR / "data" / "eval_questions.json").read_text(encoding="utf-8"))["questions"]
    client = get_qdrant()
    k = s.retrieval_top_k
    in_top: list[float] = []
    out_top: list[float] = []
    hits_at_k, rr_sum, n_in = 0, 0.0, 0

    print(f"Model={s.embedding_model} dims={s.embedding_dimensions} top_k={k} threshold={s.min_relevance_score}\n")
    for item in questions:
        vec = embedding_service.embed_query(item["q"])
        res = client.query_points(s.qdrant_collection, query=vec, limit=s.retrieval_candidates, with_payload=True).points
        docs = [p.payload["document_id"] for p in res]
        best = res[0].score if res else 0.0
        if item["in_scope"]:
            n_in += 1
            in_top.append(best)
            rank = next((i + 1 for i, d in enumerate(docs) if d in item["expected_documents"]), None)
            hit = rank is not None and rank <= k
            hits_at_k += hit
            rr_sum += 1 / rank if rank else 0.0
            print(f"[{'HIT ' if hit else 'MISS'}] top={best:.3f} rank={rank}  {item['q']}")
        else:
            out_top.append(best)
            print(f"[out ] top={best:.3f}              {item['q']}")

    print(f"\nRecall@{k} (document-level): {hits_at_k}/{n_in} = {hits_at_k / n_in:.2f}")
    print(f"MRR: {rr_sum / n_in:.2f}")
    low_in, high_out = min(in_top), max(out_top)
    print(f"Lowest in-scope top score: {low_in:.3f} | highest out-of-scope top score: {high_out:.3f}")
    if low_in > high_out:
        print(f"Suggested MIN_RELEVANCE_SCORE ~ {(low_in + high_out) / 2:.2f} (midpoint of the gap)")
    else:
        print("Scores overlap: no clean threshold. Inspect the lists above; consider a lower-risk threshold "
              "and rely on the prompt's insufficient-evidence rule.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Evaluation failed ({type(exc).__name__}): {exc}", file=sys.stderr)
        sys.exit(1)
