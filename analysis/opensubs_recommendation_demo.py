"""
Experiment A — framework recommendation on realistic OpenSubtitles input.

Feeds the framework a natural-proportion random sample of unlabelled subtitle
text (realistic_sample.csv, built by stage_opensubtitles.py --realistic-only)
and records the recommendation it makes. This DECIDES the model that
Experiments B (scalability) and C (LLM head-to-head) benchmark.

Configuration matches the Chapter 5 validation exactly: the default path of
`recommend_from_profile` (language-coverage guard ACTIVE via the profiled
columns; no strict mode, no census-detected override). On the in-scope
24-language corpus the guard is inert (coverage factor = 1.0), so the
recommendation isolates the similarity retrieval and IDW aggregation.

The `label` column of the input is used ONLY for a post-hoc realism check
(what the framework detected vs what is actually present) — never fed in.

Run (toolkit repo root, thesis_final):
    python analysis/opensubs_recommendation_demo.py \
        --input <path>/realistic_sample.csv
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

TK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TK / "src"))

import pandas as pd  # noqa: E402
from lid_toolkit.recommender import Recommender  # noqa: E402
from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler  # noqa: E402

DEFAULT_INPUT = ("c:/Users/User/OneDrive/Masters/industry_partner/"
                 "opensubtitles_staging/realistic_sample.csv")

_ZERO_SHOT = ("lid.176", "cld3", "xlm_v_base_language_id")


def model_family(variant: str) -> str:
    """Coarse family label for readability (e.g. fasttext_subword, lid.176)."""
    for p in _ZERO_SHOT:
        if variant == p or variant.startswith(p + "_"):
            return p
    # trained variants carry a training-corpus suffix; strip the longest match
    return variant.rsplit("_", 1)[0] if "_" in variant else variant


def capture(rec: Recommender, profile, metric: str) -> dict:
    """Run one single-metric query (guard on / default) and serialise it."""
    r = rec.recommend_from_profile(profile, priority_metric=metric)
    ranked = sorted(r.all_model_scores.items(), key=lambda kv: -kv[1])
    return {
        "priority_metric": metric,
        "recommended_model": r.recommended_model,
        "recommended_family": model_family(r.recommended_model),
        "confidence": round(r.confidence, 4),
        "neighbours": [
            {"dataset": nb.dataset_name, "similarity_pct": nb.similarity_pct,
             "best_model": nb.best_model, "score": round(nb.best_score, 4)}
            for nb in r.neighbours
        ],
        "idw_ranking_top10": [{"model": m, "score": round(s, 4)} for m, s in ranked[:10]],
        "explanation": r.explanation,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=DEFAULT_INPUT, help="realistic_sample.csv")
    ap.add_argument("--out", default=None, help="output JSON (default: alongside input)")
    ap.add_argument("--metric", default="f1_weighted", help="deciding priority metric")
    ap.add_argument("--text-col", default="text")
    ap.add_argument("--label-col", default="label")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    texts = df[args.text_col].dropna().astype(str)
    true_labels = df[args.label_col] if args.label_col in df.columns else None
    print(f"loaded {len(texts)} rows from {args.input}")

    # ── Profile (user mode: unlabelled discovery, census + ≤100/lang) ─────────
    prof = DeepProfiler()
    t0 = time.perf_counter()
    profile = prof.run_profile("user", text_series=texts)
    t_prof = time.perf_counter() - t0
    profiled = sorted(profile.columns)
    detected = sorted(profile.attrs.get("detected_languages", []))
    det_counts = profile.attrs.get("detected_language_counts", {})
    print(f"profiled {len(profiled)} in-scope languages in {t_prof:.0f}s: {profiled}")

    rec = Recommender.from_store(TK / "mkb.pkl", k=3)

    # THE deciding query (feeds B and C)
    decision = capture(rec, profile, args.metric)
    print(f"\n=== DECISION ({args.metric}, guard on / default path) ===")
    print(f"recommended : {decision['recommended_model']}  "
          f"[{decision['recommended_family']}]  confidence {decision['confidence']}")
    for nb in decision["neighbours"]:
        print(f"   neighbour : {nb['dataset']} ({nb['similarity_pct']}%)  best={nb['best_model']}")

    # Reference only (NOT the decision): what a speed priority would pick
    speed = capture(rec, profile, "throughput_samples_per_sec")
    print(f"\n[reference] speed-priority pick: {speed['recommended_model']} "
          f"[{speed['recommended_family']}]")

    # ── Realism check: what the framework saw vs what is actually present ─────
    realism = None
    if true_labels is not None:
        true_dist = Counter(true_labels.dropna())
        realism = {
            "true_language_distribution": dict(true_dist.most_common()),
            "n_true_languages": len(true_dist),
            "profiled_languages": profiled,
            "census_detected_languages": detected,
            "true_langs_present_but_not_profiled": sorted(set(true_dist) - set(profiled)),
        }
        print(f"\nrealism: {len(true_dist)} languages present, "
              f"{len(profiled)} profiled; dropped (too rare to detect): "
              f"{realism['true_langs_present_but_not_profiled']}")

    out = Path(args.out) if args.out else Path(args.input).with_name("experiment_A_result.json")
    out.write_text(json.dumps({
        "input": str(args.input), "n_rows": int(len(texts)),
        "profile_seconds": round(t_prof, 1),
        "profiled_languages": profiled,
        "census_detected_languages": detected,
        "census_detected_counts": det_counts,
        "decision_query": decision,
        "reference_speed_query": speed,
        "realism_check": realism,
        "config_note": "recommend_from_profile default path — coverage guard active via "
                       "profiled columns, no strict mode, no detected-coverage override "
                       "(identical to Ch5 validation).",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nsaved → {out}")
    print(f"\n>>> MODEL FOR EXPERIMENTS B AND C: {decision['recommended_model']}")


if __name__ == "__main__":
    main()
