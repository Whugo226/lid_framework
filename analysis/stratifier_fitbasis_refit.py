"""
stratifier_fitbasis_refit.py

WHAT THIS TESTS
---------------
MKBStore.finalise() pools every dataset's language columns and then drops
duplicate column labels:

    all_profiles = pd.concat(list(self._raw_profiles.values()), axis=1)
    all_profiles = all_profiles.loc[:, ~all_profiles.columns.duplicated()]

Because pandas keeps the FIRST occurrence of each label, and because
exorde-social-media-december-2024-week1 is first in insertion order and
carries all 24 ISO codes, the stratifier's PCA is fitted on 24 language
vectors drawn entirely from that one corpus. The other sixteen contribute
nothing to the projection basis. The build log records this verbatim:

    build_mkb.log:96900
    "Fitting stratifier on 24 pooled language samples from 18 datasets."

The dedup is defensible in intent (one row per language stops corpora with
many languages from dominating the basis), but the tie-break is arbitrary:
every language is represented by its social-media rendering purely because
of dict ordering.

This script measures whether that choice matters. It refits the stratifier
on the FULL 236 language-dataset observations (no dedup), rebuilds all 17
MKB fingerprints and all 17 query fingerprints from that basis, and re-runs
Condition A. Everything downstream of the representation -- k=3, the IDW
vote, the coverage guard, the priority metric, the scoring -- is untouched.

READ-ONLY with respect to every existing artifact. Nothing under src/ is
modified; the alternative basis is built through the public API
(FeatureStratifier.fit / FingerprintBuilder) on a deep copy of the store.
mkb.pkl is never rewritten. Writes one dated JSON snapshot.

Run (repo root, thesis_final):
    python analysis/stratifier_fitbasis_refit.py
"""
from __future__ import annotations

import copy
import itertools
import json
import statistics as st
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "analysis"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from lid_toolkit.recommender import Recommender  # noqa: E402
from lid_toolkit.recommender.mkb_store import MKBStore  # noqa: E402
from lid_toolkit.recommender.feature_stratifier import FeatureStratifier  # noqa: E402
from lid_toolkit.recommender.fingerprint_builder import FingerprintBuilder  # noqa: E402

# Reuse the reporting harness verbatim -- do not reimplement the measures.
from reporting_measures import measures, score_row  # noqa: E402

K = 3
# Condition A, analysis/reporting_measures_2026-08-04.json
BASELINE_OF_RECORD = {
    "mean_regret": 0.007287,
    "mean_range_capture_pct": 99.18,
    "top1_fraction": "2/17",
}


def paired_sign_flip(a_rows: list[dict], b_rows: list[dict]) -> dict:
    """
    Exact paired sign-flip permutation test on per-dataset regret.
    Positive difference = arm B has HIGHER regret (i.e. arm A is better).
    Two-sided, since neither direction is privileged here.
    """
    by_a = {r["dataset"]: r["regret"] for r in a_rows}
    diffs = [by_a[r["dataset"]] - r["regret"] for r in b_rows]  # +ve = refit better
    nz = [x for x in diffs if abs(x) > 1e-9]
    k = len(nz)
    obs = abs(sum(nz))
    if k == 0:
        p = 1.0
    elif k > 22:
        p = None
    else:
        hits = sum(
            1
            for signs in itertools.product([1, -1], repeat=k)
            if abs(sum(v * s for v, s in zip(nz, signs))) >= obs - 1e-12
        )
        p = hits / 2 ** k
    return {
        "refit_better": sum(1 for x in diffs if x > 1e-9),
        "original_better": sum(1 for x in diffs if x < -1e-9),
        "ties": sum(1 for x in diffs if abs(x) <= 1e-9),
        "informative_pairs": k,
        "mean_regret_difference": round(st.mean(diffs), 6) if diffs else None,
        "two_sided_p": round(p, 4) if p is not None else None,
    }


def run_condition_a(rec: Recommender, bench: dict, metric: str) -> tuple[list[dict], dict]:
    """Query the 17 evaluation splits; return (scored rows, retrieval diagnostics)."""
    rows, nn1 = [], Counter()
    self_top1 = self_top3 = 0
    for name in bench:
        profile = pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        r = rec.recommend_from_profile(profile, priority_metric=metric)
        rows.append(score_row(name, r.recommended_model, bench[name]))
        top3 = [nb.dataset_name for nb in r.neighbours[:3]]
        nn1[top3[0]] += 1
        self_top1 += top3[0] == name
        self_top3 += name in top3
    diag = {
        "nearest_neighbour_distribution": dict(nn1.most_common()),
        "self_retrieval_top1": f"{self_top1}/{len(rows)}",
        "self_retrieval_top3": f"{self_top3}/{len(rows)}",
    }
    return rows, diag


def main() -> None:
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    bench = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}
    print(f"priority metric: {metric}   datasets: {len(bench)}   k: {K}\n")

    # ── Arm 1: the shipped framework, untouched ──────────────────────────────
    print("=" * 78)
    print("ARM 1  original basis (24 rows, dedup, all from exorde)")
    print("=" * 78)
    store = MKBStore.load(REPO / "mkb.pkl")
    rec_orig = Recommender.from_store(REPO / "mkb.pkl", k=K)
    rows_orig, diag_orig = run_condition_a(rec_orig, bench, metric)
    m_orig = measures(rows_orig)
    print(json.dumps(m_orig, indent=2))

    drift = {
        key: {"reproduced": m_orig[key], "of_record": val}
        for key, val in BASELINE_OF_RECORD.items()
        if m_orig[key] != val
    }
    print("\nreproduction check vs reporting_measures_2026-08-04.json:",
          "EXACT" if not drift else f"DRIFT -> {drift}")

    # ── Build the alternative fit basis: all 236 language-dataset rows ───────
    print("\n" + "=" * 78)
    print("REFIT  pooling all language-dataset observations (no dedup)")
    print("=" * 78)
    raw = store._raw_profiles

    # Label each column uniquely as "<iso>@<dataset>" so no dedup can occur and
    # the provenance of every row stays inspectable.
    frames = []
    for ds_name, df in raw.items():
        renamed = df.copy()
        renamed.columns = [f"{iso}@{ds_name}" for iso in df.columns]
        frames.append(renamed)
    pooled = pd.concat(frames, axis=1)
    print(f"pooled matrix: {pooled.shape}  (features x language-dataset observations)")

    provenance = Counter(c.split("@", 1)[1] for c in pooled.columns)
    print(f"contributing corpora: {len(provenance)}  "
          f"(original basis: 1 -- exorde only)")

    # Features absent from some corpora (the conditional paragraph-level
    # variants) arrive as NaN. The stratifier's own validity filter drops them:
    # std of a NaN column is NaN, and NaN > 0 is False.
    n_nan_cols = int(pooled.isna().any(axis=1).sum())
    print(f"features with NaN in >=1 observation: {n_nan_cols} "
          f"(dropped by the stratifier's std>0 validity filter)")

    strat_new = FeatureStratifier(variance_threshold=0.95, max_components=20)
    strat_new.fit(pooled)
    print("\nrefitted stratum summary:")
    print(strat_new.stratum_summary())
    print(f"total PCs: {strat_new.total_pcs}   (original: {store.stratifier.total_pcs})")

    # ── Arm 2: same stratified design, refitted basis ────────────────────────
    print("\n" + "=" * 78)
    print("ARM 2  refitted basis (236 rows, all 17 corpora)")
    print("=" * 78)
    alt_store = copy.deepcopy(store)
    alt_store._stratifier = strat_new
    alt_store._builder = FingerprintBuilder(strat_new)
    for ds_name, df in alt_store._raw_profiles.items():
        alt_store._entries[ds_name].fingerprint = alt_store._builder.build(df)

    n_dims = len(next(iter(alt_store._entries.values())).fingerprint)
    print(f"fingerprint dimensions: {n_dims}  "
          f"(original: {len(store.get_entry(store.datasets[0]).fingerprint)})")

    # Recommender.recommend_from_profile() calls store.builder.build(), so the
    # query fingerprints are rebuilt on the new basis automatically.
    rec_refit = Recommender(alt_store, k=K)
    rows_refit, diag_refit = run_condition_a(rec_refit, bench, metric)
    m_refit = measures(rows_refit)
    print(json.dumps(m_refit, indent=2))

    # ── Comparison ───────────────────────────────────────────────────────────
    paired = paired_sign_flip(rows_orig, rows_refit)
    print("\n" + "=" * 78)
    print("COMPARISON")
    print("=" * 78)
    hdr = f"{'measure':30s} {'original':>14s} {'refit':>14s}"
    print(hdr); print("-" * len(hdr))
    for key in ("top1_fraction", "mean_regret", "median_regret", "max_regret",
                "mean_rank", "top3_hit", "top10_hit",
                "mean_range_capture_pct", "min_range_capture_pct"):
        print(f"{key:30s} {str(m_orig[key]):>14s} {str(m_refit[key]):>14s}")
    print(f"\n{'self-retrieval top-1':30s} "
          f"{diag_orig['self_retrieval_top1']:>14s} {diag_refit['self_retrieval_top1']:>14s}")
    print(f"{'self-retrieval top-3':30s} "
          f"{diag_orig['self_retrieval_top3']:>14s} {diag_refit['self_retrieval_top3']:>14s}")
    print("\npaired sign-flip permutation test on per-dataset regret:")
    print(json.dumps(paired, indent=2))

    out = {
        "generated": str(date.today()),
        "question": (
            "Does the stratifier's PCA fit basis matter? MKBStore.finalise() "
            "deduplicates pooled language columns and so fits on 24 vectors, all "
            "from exorde-social-media-december-2024-week1. This refits on all 236 "
            "language-dataset observations and re-runs Condition A."
        ),
        "priority_metric": metric,
        "k": K,
        "basis": {
            "original": {
                "n_rows": int(store.stratifier._fits[
                    store.stratifier.stratum_names[0]].scaler.n_samples_seen_),
                "contributing_corpora": 1,
                "total_pcs": store.stratifier.total_pcs,
                "stratum_pcs": {s: f.n_components
                                for s, f in store.stratifier._fits.items()},
            },
            "refit": {
                "n_rows": int(pooled.shape[1]),
                "contributing_corpora": len(provenance),
                "total_pcs": strat_new.total_pcs,
                "stratum_pcs": {s: f.n_components for s, f in strat_new._fits.items()},
                "features_with_nan_dropped": n_nan_cols,
            },
        },
        "conditions": {
            "A_original_basis": m_orig,
            "A_refit_basis": m_refit,
        },
        "retrieval_diagnostics": {
            "A_original_basis": diag_orig,
            "A_refit_basis": diag_refit,
        },
        "reproduction_check": {
            "of_record": BASELINE_OF_RECORD,
            "status": "EXACT" if not drift else "DRIFT",
            "drift": drift,
        },
        "paired_regret_test": paired,
        "per_dataset": {
            "A_original_basis": rows_orig,
            "A_refit_basis": rows_refit,
        },
    }
    dest = REPO / "analysis" / f"stratifier_fitbasis_refit_{date.today().isoformat()}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
