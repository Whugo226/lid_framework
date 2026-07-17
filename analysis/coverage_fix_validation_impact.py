"""
coverage_fix_validation_impact.py

Quantifies how the 2026-07-16 coverage-guard fix (correct zero-shot language
inventories in recommender/model_language_coverage.py) changes the held-out
validation results, versus the numbers currently reported in Chapter 5.

WHY THIS EXISTS
---------------
`validate_recommendations.py` calls `recommend_from_profile()` WITHOUT
`user_iso_codes`, and that defaults to the profiled columns — so the language
coverage guard was ACTIVE when the committed `validation_report.json`
(timestamp 2026-05-14) was produced. That run used the OLD, buggy inventories,
which credited the three zero-shot models (lid.176, CLD3, XLM-V) with only the
languages of the benchmark corpus they were evaluated on, instead of their true
inventories (176 / ~100 / ~100). The fix corrects this.

This script re-runs the recommendation step on the SAME cached profiles
(`eval_profiles/*.pkl`; deterministic — seeded sampling) under the current
(fixed) code, and scores the result from the benchmark scores already stored in
the report, so the comparison isolates the code change with zero sampling noise.

It does NOT modify validation_report.json or the thesis. It writes a dated JSON
snapshot so the discrepancy is on record even after the report is regenerated.

Run (repo root, thesis_final):
    python analysis/coverage_fix_validation_impact.py
"""
from __future__ import annotations

import json
import statistics as st
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd  # noqa: E402
from lid_toolkit.recommender import Recommender  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def hypergeom_p(a: int, n_nz: int, K: int, N: int) -> float | None:
    """One-sided P(>= a correct in the n_nz non-zero-confidence draws)."""
    try:
        from scipy.stats import hypergeom
        return float(sum(hypergeom.pmf(i, N, K, n_nz) for i in range(a, min(K, n_nz) + 1)))
    except Exception:
        return None


def evaluate(rec, rep, metric, coverage_off: bool):
    rows = []
    for d in rep["per_dataset"]:
        prof = pd.read_pickle(REPO / "eval_profiles" / f"{d['dataset']}.pkl")
        fp = rec.store.builder.build(prof)
        uic = None if coverage_off else frozenset(prof.columns)
        r = rec.engine.query(fp, priority_metric=metric, user_iso_codes=uic)
        bench = d["all_benchmark_scores"]
        gt_score = max(bench.values())
        rec_score = bench.get(r.recommended_model, gt_score)
        rows.append({
            "dataset": d["dataset"],
            "recommended": r.recommended_model,
            "correct": r.recommended_model == d["ground_truth_model"],
            "confidence": round(r.confidence, 4),
            "regret": gt_score - rec_score,
        })
    n = len(rows)
    correct = sum(x["correct"] for x in rows)
    reg = [x["regret"] for x in rows]
    nz = [x for x in rows if x["confidence"] > 0]
    z = [x for x in rows if x["confidence"] == 0]
    nz_correct = sum(x["correct"] for x in nz)
    return {
        "top1": f"{correct}/{n}",
        "top1_acc": round(correct / n, 4),
        "mean_regret": round(st.mean(reg), 6),
        "max_regret": round(max(reg), 6),
        "confidence_split": f"{nz_correct}/{len(nz)} correct at non-zero conf "
                            f"vs {sum(x['correct'] for x in z)}/{len(z)} at zero conf",
        "confidence_p": hypergeom_p(nz_correct, len(nz), correct, n),
        "per_dataset": rows,
    }


def main() -> None:
    rep = json.load(open(REPO / "validation_report.json", encoding="utf-8"))
    metric = rep["priority_metric"]
    rec = Recommender.from_store(REPO / "mkb.pkl", k=3)

    old = {
        "top1": f"{rep['n_correct']}/{rep['n_total']}",
        "top1_acc": round(rep["recommendation_accuracy"], 4),
        "mean_regret": round(rep["performance_delta"]["mean"], 6),
        "max_regret": round(rep["performance_delta"]["max"], 6),
        "confidence_split": "2/2 correct at non-zero conf vs 1/15 at zero conf",
        "confidence_p": 0.0221,
        "note": "as reported in committed validation_report.json (buggy zero-shot coverage)",
    }
    new_on = evaluate(rec, rep, metric, coverage_off=False)
    new_off = evaluate(rec, rep, metric, coverage_off=True)

    out = {
        "generated": str(date.today()),
        "priority_metric": metric,
        "isolation": "same cached eval_profiles; only the coverage-inventory fix differs",
        "scenarios": {
            "OLD_buggy_coverage_guard_on": old,
            "corrected_coverage_guard_on": {k: v for k, v in new_on.items() if k != "per_dataset"},
            "corrected_coverage_guard_off": {k: v for k, v in new_off.items() if k != "per_dataset"},
        },
        "changed_recommendations_guard_on": [
            {"dataset": o["dataset"], "old": o_model, "new": nw["recommended"]}
            for o, nw in zip(rep["per_dataset"], new_on["per_dataset"])
            if (o_model := o["recommended_model"]) != nw["recommended"]
        ],
    }
    stamp = date.today().isoformat()
    dest = REPO / "analysis" / f"coverage_fix_validation_impact_{stamp}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(out["scenarios"], indent=2, ensure_ascii=False))
    print("changed (guard on):", out["changed_recommendations_guard_on"])
    print(f"\nsnapshot → {dest}")


if __name__ == "__main__":
    main()
