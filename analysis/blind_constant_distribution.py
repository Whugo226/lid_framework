"""
blind_constant_distribution.py

THE FULL DISTRIBUTION OF FIXED-MODEL CHOICES, NOT JUST ITS MEAN.

Chapter 5 reported the "single model, chosen blindly" baseline as a single
expected gap (0.3902).  That is a weak summary of a quantity whose outcomes
span 0.0127 to 0.8110: the choice of model matters far more than the fact that
the choice was uninformed, and no practitioner experiences the mean.

Unlike the random-selection baseline — which needs Monte Carlo because there
are 105^17 possible strategies — the fixed-choice baseline has exactly 105
possible outcomes.  Its distribution is therefore enumerable exactly, with no
sampling, no seed, and no simulation error.  This script enumerates it.

Two further facts fall out of the same regret matrix:

  * The old 0.3902 figure averaged over only the 103 candidates recorded under
    one portable key across all 17 datasets.  CLD3 and lid.176 are keyed per
    evaluation corpus (``cld3_<dataset>``), so a set intersection over key
    strings silently drops them.  Resolving the key per dataset recovers all
    105 and gives 0.3832.

  * That 0.3832 equals the analytic expected gap of random per-corpus selection
    exactly, and not by coincidence: both statistics are the grand mean of the
    same 17x105 regret matrix, summed in different orders (Fubini).  The two
    strategies differ in variance, not in expectation.

Reads only committed artifacts; writes a dated JSON snapshot. Modifies nothing.

Run (repo root, thesis_final):
    python analysis/blind_constant_distribution.py
"""
from __future__ import annotations

import json
import statistics as st
from datetime import date
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
BENCH_SOURCE = REPO / "validation_report.json"
FRAMEWORK_SOURCE = REPO / "analysis" / "reporting_measures_2026-07-21.json"
FRAMEWORK_CONDITION = "A_evaluation_splits_full_mkb"
THRESHOLDS = [0.02, 0.05, 0.10, 0.20]


def resolve(model: str, dataset: str, scores: dict[str, float]) -> str:
    """Zero-shot detectors are keyed per evaluation dataset; resolve per dataset."""
    return model if model in scores else f"{model}_{dataset}"


def main() -> None:
    report = json.loads(BENCH_SOURCE.read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    bench = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}
    datasets = sorted(bench)

    # Candidate names: the 103 sharing one portable key, plus the two zero-shot
    # detectors recovered by per-dataset key resolution.
    shared = set(bench[datasets[0]])
    for scores in bench.values():
        shared &= set(scores)
    models = sorted(shared) + ["cld3", "lid.176"]

    # Regret matrix R[dataset, model].
    R = np.array([
        [max(bench[d].values()) - bench[d][resolve(m, d, bench[d])] for m in models]
        for d in datasets
    ])
    gaps = R.mean(axis=0)  # one mean gap per candidate, averaged over the datasets
    order = np.argsort(gaps)

    # Framework, same condition and same 17 datasets.
    fw_rows = json.loads(FRAMEWORK_SOURCE.read_text(encoding="utf-8"))
    fw_rows = fw_rows["per_dataset"][FRAMEWORK_CONDITION]
    fw_regret = {r["dataset"]: r["regret"] for r in fw_rows}
    fw_mean = st.mean(fw_regret.values())

    # How many candidates beat the framework on each individual dataset?
    per_dataset = []
    for i, d in enumerate(datasets):
        n_better = int((R[i] < fw_regret[d]).sum())
        per_dataset.append({
            "dataset": d,
            "framework_regret": round(fw_regret[d], 6),
            "n_candidates_better": n_better,
            "framework_is_outright_best": fw_regret[d] == 0.0,
        })

    out = {
        "generated": str(date.today()),
        "priority_metric": metric,
        "question": (
            "What is the full distribution of fixed-model (constant policy) "
            "choices across the 17 evaluation datasets, and how does the "
            "framework sit within it?"
        ),
        "sources": {
            "benchmark_scores": str(BENCH_SOURCE.relative_to(REPO)),
            "framework_regret": (
                f"{FRAMEWORK_SOURCE.relative_to(REPO)} :: {FRAMEWORK_CONDITION}"
            ),
        },
        "n_datasets": len(datasets),
        "n_candidates": len(models),
        "n_candidates_sharing_portable_key": len(shared),
        "framework_mean_gap": round(fw_mean, 6),
        "distribution_of_constant_policies": {
            "mean": round(float(gaps.mean()), 6),
            "sd": round(float(gaps.std(ddof=1)), 6),
            **{
                f"p{q}": round(float(np.percentile(gaps, q)), 6)
                for q in (0, 5, 10, 25, 50, 75, 90, 95, 100)
            },
        },
        "n_beating_framework": int((gaps < fw_mean).sum()),
        "n_at_or_below_threshold": {
            f"{t:.2f}": int((gaps <= t).sum()) for t in THRESHOLDS
        },
        "best_constants": [
            {"model": models[i], "mean_gap": round(float(gaps[i]), 6)}
            for i in order[:8]
        ],
        "worst_constants": [
            {"model": models[i], "mean_gap": round(float(gaps[i]), 6)}
            for i in order[-3:]
        ],
        "per_dataset_candidates_beating_framework": {
            "mean": round(
                st.mean(r["n_candidates_better"] for r in per_dataset), 1
            ),
            "max": max(r["n_candidates_better"] for r in per_dataset),
            "n_datasets_with_at_least_one": sum(
                1 for r in per_dataset if r["n_candidates_better"] > 0
            ),
            "n_datasets_framework_outright_best": sum(
                1 for r in per_dataset if r["framework_is_outright_best"]
            ),
            "per_dataset": per_dataset,
        },
        "fubini_identity": {
            "note": (
                "Blind constant pick and random per-corpus selection are the "
                "grand mean of the same regret matrix summed in different "
                "orders, so their expectations are equal by construction."
            ),
            "blind_constant_mean_over_105": round(float(gaps.mean()), 6),
            "random_selection_analytic_mean": round(
                float(R.mean(axis=1).mean()), 6
            ),
            "superseded_mean_over_103_shared_keys": round(
                float(st.mean(
                    gaps[i] for i, m in enumerate(models) if m in shared
                )), 6
            ),
        },
    }

    dest = REPO / "analysis" / f"blind_constant_distribution_{date.today()}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    printable = dict(out)
    printable["per_dataset_candidates_beating_framework"] = {
        k: v for k, v in out["per_dataset_candidates_beating_framework"].items()
        if k != "per_dataset"
    }
    print(json.dumps(printable, indent=2, ensure_ascii=False))
    print(f"\nWrote {dest.relative_to(REPO)}")


if __name__ == "__main__":
    main()
