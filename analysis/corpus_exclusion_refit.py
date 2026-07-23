"""
corpus_exclusion_refit.py

Simulates a genuinely UNSEEN corpus, correcting the leakage in the existing
corpus-exclusion diagnostic (analysis/paradigm_regret.py).

WHY THIS EXISTS
---------------
paradigm_regret.py's "corpus_excluded" scenario removes a dataset's entry from
the MKB before querying, but reuses the ORIGINAL FeatureStratifier — whose
StandardScaler and per-stratum PCA were fitted on all 17 pooled corpora
(mkb_store.py: MKBStore.finalise() pools every registered raw profile before
fitting). Excluding only the entry leaves the coordinate system itself fitted
with knowledge of the "excluded" corpus, so that diagnostic is optimistic about
generalisation to a corpus the framework has never seen.

This script refits the stratifier from scratch on the OTHER 16 corpora for each
of the 17 exclusions in turn, then projects the held-out corpus's evaluation
profile into that leave-one-out coordinate system before querying. This is the
honest version of "what happens on a corpus this framework has never seen."

PROTOCOL NOTE — this deliberately does NOT match paradigm_regret.py's own
guard-off diagnostic call (`engine.query(..., user_iso_codes=None)`, which
bypasses the coverage guard entirely). It instead mirrors the actual frozen
evaluation protocol: user_iso_codes = the profiled columns, exactly what
Recommender._resolve_iso_codes falls back to inside recommend_from_profile().
Numbers here are therefore not directly comparable to paradigm_regret.py's
"corpus_excluded" scenario; both the refit and the guard behaviour differ.

WHAT IS REPORTED
-----------------
Top-1 exact match is a strict yardstick the framework was never designed to
be judged on (see drafts/coverage_guard_iteration.tex handover notes). This
script reports the measures that match the stated aim of NEAR-optimal
selection: regret (gap to best), rank of the recommendation among all
candidate models, and range capture (recommended score as a % of the
achievable [worst, best] range) — alongside top-1 for continuity with the
rest of the evaluation chapter.

Reads only committed artifacts (mkb.pkl, eval_profiles/, validation_report.json
for ground-truth benchmark scores); writes a dated JSON snapshot. Modifies
nothing else. Refitting a PCA on cached profiles is cheap: no new data
collection or benchmarking is required.

Run (repo root, thesis_final):
    python analysis/corpus_exclusion_refit.py
"""
from __future__ import annotations

import json
import statistics as st
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd  # noqa: E402

from lid_toolkit.recommender.mkb_similarity import SimilarityEngine  # noqa: E402
from lid_toolkit.recommender.mkb_store import MKBStore  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
K = 3


def build_loo_store(full_store: MKBStore, excluded: str) -> MKBStore:
    """Refit stratifier + fingerprints on all datasets except `excluded`."""
    loo = MKBStore(
        variance_threshold=full_store._variance_threshold,
        max_pca_components=full_store._max_pca_components,
    )
    for name in full_store.datasets:
        if name == excluded:
            continue
        loo.add_raw_profile(name, full_store._raw_profiles[name])
    for name in full_store.datasets:
        if name == excluded:
            continue
        entry = full_store.get_entry(name)
        for variant, perfs in entry.performances.items():
            loo.add_performance(name, variant, perfs)
    loo.finalise()
    return loo


def main() -> None:
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    bench_by_ds = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}

    full_store = MKBStore.load(REPO / "mkb.pkl")
    datasets = full_store.datasets

    rows = []
    for i, name in enumerate(datasets, 1):
        print(f"[{i}/{len(datasets)}] refitting without '{name}' …", file=sys.stderr)
        loo_store = build_loo_store(full_store, name)
        engine = SimilarityEngine(loo_store, k=K)

        profile = pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        fp = loo_store.builder.build(profile)
        user_iso_codes = frozenset(profile.columns)  # mirrors Recommender._resolve_iso_codes

        rec = engine.query(fp, priority_metric=metric, user_iso_codes=user_iso_codes)

        scores = bench_by_ds[name]
        if rec.recommended_model not in scores:
            raise RuntimeError(
                f"[{name}] recommendation '{rec.recommended_model}' has no benchmark "
                f"record in validation_report.json — MKB/eval-benchmark naming has drifted."
            )
        ranked = sorted(scores.values(), reverse=True)
        best, worst = ranked[0], ranked[-1]
        rec_score = scores[rec.recommended_model]
        gt_model = max(scores, key=scores.__getitem__)
        rank = sum(1 for v in ranked if v > rec_score + 1e-12) + 1
        range_capture = (rec_score - worst) / (best - worst) if best > worst else 1.0

        rows.append({
            "dataset": name,
            "recommended_model": rec.recommended_model,
            "confidence": round(rec.confidence, 4),
            "ground_truth_model": gt_model,
            "is_correct": rec.recommended_model == gt_model,
            "best_score": round(best, 6),
            "worst_score": round(worst, 6),
            "recommended_score": round(rec_score, 6),
            "regret": round(best - rec_score, 6),
            "rank": rank,
            "n_candidates": len(ranked),
            "range_capture_pct": round(100 * range_capture, 4),
        })

    n = len(rows)
    correct = sum(r["is_correct"] for r in rows)
    regrets = [r["regret"] for r in rows]
    ranks = [r["rank"] for r in rows]
    caps = [r["range_capture_pct"] for r in rows]

    # Best constant policy on this same set of 17, for reference.
    common = set(bench_by_ds[datasets[0]])
    for d in datasets:
        common &= set(bench_by_ds[d])
    policy_regret = {
        v: st.mean(max(bench_by_ds[d].values()) - bench_by_ds[d][v] for d in datasets)
        for v in common
    }
    best_policy = min(policy_regret, key=policy_regret.get)

    summary = {
        "generated": str(date.today()),
        "priority_metric": metric,
        "k": K,
        "protocol": (
            "Leave-one-corpus-out WITH refit: for each of the 17 corpora, the "
            "StandardScaler + per-stratum PCA are refitted from scratch on the "
            "pooled profiles of the other 16 only, then the held-out corpus's "
            "evaluation profile is projected into that refit space before "
            "querying. Coverage guard active (profile-derived language set), "
            "matching the frozen evaluation protocol."
        ),
        "n_datasets": n,
        "top1_accuracy": round(correct / n, 4),
        "top1_fraction": f"{correct}/{n}",
        "mean_regret": round(st.mean(regrets), 6),
        "median_regret": round(st.median(regrets), 6),
        "max_regret": round(max(regrets), 6),
        "mean_rank": round(st.mean(ranks), 2),
        "median_rank": st.median(ranks),
        "max_rank": max(ranks),
        "n_candidates_typical": rows[0]["n_candidates"],
        "top3_hit_rate": f"{sum(1 for r in ranks if r <= 3)}/{n}",
        "top10_hit_rate": f"{sum(1 for r in ranks if r <= 10)}/{n}",
        "mean_range_capture_pct": round(st.mean(caps), 2),
        "min_range_capture_pct": round(min(caps), 2),
        "reference_best_constant_policy": {
            "policy": best_policy,
            "mean_regret": round(policy_regret[best_policy], 6),
        },
        "per_dataset": rows,
    }

    stamp = date.today().isoformat()
    dest = REPO / "analysis" / f"corpus_exclusion_refit_{stamp}.json"
    dest.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({k: v for k, v in summary.items() if k != "per_dataset"}, indent=2))
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
