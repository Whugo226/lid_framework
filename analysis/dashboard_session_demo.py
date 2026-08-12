"""Capture the numbers behind the Ch5 interactive-explainer subsection
(Section 5.8.2, "The Interactive Explainer").

Runs the *same code path the Streamlit dashboard runs* — LID_Recommender.profile()
once, then LID_Recommender.explain_from_profile() per priority metric — over the
same 600-document WiLI-2018 sample used by analysis/walkthrough_demo.py, so the
two Ch5 subsections narrate one continuous session.

What it records, beyond walkthrough_results.json:
  * the profiler's language census (how many languages lid.176 saw at high
    confidence, and how many documents got an assignment) — the Corpus Profile
    panel's headline numbers;
  * the ranked top-5 shortlist with per-candidate coverage gaps — the
    Recommendation panel's shortlist table;
  * the MKB-query wall-clock, separately from the one-off profiling pass, which
    is the quantitative basis for the claim that re-querying is cheap.

Usage (from the toolkit repo root, thesis_final env):
    python analysis/dashboard_session_demo.py
Writes analysis/dashboard_session_<YYYY-MM-DD>.json.
"""
import datetime as _dt
import json
import sys
import time
from pathlib import Path

import pandas as pd

TK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TK / "src"))

CSV = TK / "test_examples" / "wili2018_walkthrough_600.csv"
OUT = Path(__file__).parent / f"dashboard_session_{_dt.date.today():%Y-%m-%d}.json"

METRICS = ("f1_weighted", "inference_time_ms_per_sample")


def _shortlist(rec, n=5):
    ranked = sorted(rec.all_model_scores.items(), key=lambda kv: -kv[1])[:n]
    rows = []
    for i, (model, score) in enumerate(ranked, 1):
        gaps = [len(nb.per_model_gaps.get(model, frozenset()))
                for nb in rec.neighbours if nb.per_model_gaps]
        rows.append({
            "rank": i,
            "model": model,
            "idw_score": round(score, 4),
            "neighbours_backing":
                f"{sum(nb.best_model == model for nb in rec.neighbours)}"
                f"/{len(rec.neighbours)}",
            "coverage_gap_langs": max(gaps) if gaps else 0,
        })
    return rows


def main() -> int:
    texts = pd.read_csv(CSV)["text"]

    from lid_toolkit import LID_Recommender
    lid = LID_Recommender(TK / "mkb.pkl")

    t0 = time.perf_counter()
    profile = lid.profile(texts)
    profile_s = time.perf_counter() - t0

    census = {str(k): int(v)
              for k, v in profile.attrs.get("detected_language_counts", {}).items()}
    out = {
        "corpus": CSV.name,
        "n_documents": int(len(texts)),
        "profile_seconds": round(profile_s, 1),
        "census_n_languages": len(census),
        "census_n_documents_assigned": int(sum(census.values())),
        "in_scope_languages": sorted(profile.columns),
        "n_in_scope_languages": int(profile.shape[1]),
        "n_features_per_language": int(profile.shape[0]),
        "census_counts": dict(sorted(census.items(), key=lambda kv: -kv[1])),
        "queries": {},
    }

    query_fp: dict = {}
    for metric in METRICS:
        t0 = time.perf_counter()
        rec, cfg = lid.explain_from_profile(profile, metric=metric)
        query_ms = (time.perf_counter() - t0) * 1000
        query_fp = cfg.trace.get("query_fingerprint", {}) or query_fp
        nn = rec.neighbours[0]
        rec_gap = next((nb.per_model_gaps.get(rec.recommended_model, frozenset())
                        for nb in rec.neighbours
                        if rec.recommended_model in nb.per_model_gaps), frozenset())
        out["queries"][metric] = {
            "query_ms": round(query_ms, 1),
            "recommended_model": rec.recommended_model,
            "consensus_confidence": round(rec.confidence, 4),
            "recommended_coverage_gap": sorted(rec_gap),
            "neighbours": [
                {"dataset": nb.dataset_name,
                 "similarity_pct": round(nb.similarity_pct, 1),
                 "best_model": nb.best_model,
                 "best_score": round(nb.best_score, 4)}
                for nb in rec.neighbours
            ],
            "nearest_neighbour_per_stratum_distance": {
                s: round(d, 4) for s, d in
                sorted(nn.per_stratum_distances.items(), key=lambda kv: kv[1])
            },
            "shortlist_top5": _shortlist(rec),
            "uncoverable_languages": sorted(rec.uncoverable_languages),
        }

    fp = out["queries"][METRICS[0]]
    # Same two S6 flags the dashboard renders as typological advisories.
    out["typological_advisories"] = {
        "n_tonal_languages": int(query_fp.get("cat__n_tonal", 0)),
        "cjk_script_detected": bool(int(query_fp.get("cat__has_cjk", 0))),
    }

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"profiled {out['n_documents']} docs in {out['profile_seconds']} s "
          f"({out['n_in_scope_languages']} in-scope of {out['census_n_languages']} "
          f"census languages)")
    for m, q in out["queries"].items():
        print(f"  {m}: {q['recommended_model']} "
              f"conf={q['consensus_confidence']} in {q['query_ms']} ms")
    print(f"nearest-neighbour strata: {fp['nearest_neighbour_per_stratum_distance']}")
    print(f"saved -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
