"""
reporting_measures.py

Produces the full set of reporting measures for Chapter 5, under all three
evaluation conditions, plus every baseline policy — including the two zero-shot
detectors the existing Table 5.x footnote says "cannot be expressed as constant
policies in this bookkeeping."  They can: their benchmark records are keyed per
evaluation dataset (``cld3_<dataset>``), so a constant policy over them is
resolved key-by-key rather than by a single shared variant name.

WHY THIS EXISTS
---------------
Chapter 5 currently leads with strict top-1 exact-match accuracy.  That is a
harsher yardstick than the thesis's stated aim, which is NEAR-optimal selection
(introduction_chapter.tex:63).  Exact match penalises recommending a model
0.0001 below the winner exactly as hard as one 0.5 below it.

This script computes the measures that match the stated aim:

  * regret            — gap in the priority metric to the best available model
  * rank              — position of the recommendation among all candidates
  * range capture     — recommended score as a %% of the achievable
                        [worst, best] span on that dataset

alongside top-1, so the chapter can lead with the aim-matching measures and keep
exact match as a secondary strictness check.

THE THREE CONDITIONS
--------------------
  A  evaluation splits, full MKB          — the recorded protocol (in-scope use case)
  B  reserved validation splits, full MKB — the confirmatory run (read from artifact)
  C  leave-one-corpus-out WITH refit      — unseen corpus (read from artifact)

A is recomputed here under the corrected coverage guard, ACTIVE on the
profile-derived language set, mirroring what recommend_from_profile() actually
does.  B and C are read from their own dated snapshots.

BASIS NOTE: A and C score against the evaluation-side benchmark archive
(validation_report.json); B scores against the validation-side archive.  Range
capture and rank are therefore comparable in kind but not computed from an
identical candidate pool.  Do not present B's rank as directly commensurable
with A's without stating this.

Reads only committed artifacts; writes a dated JSON snapshot. Modifies nothing.

Run (repo root, thesis_final):
    python analysis/reporting_measures.py
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
K = 3


def measures(per_dataset: list[dict]) -> dict:
    """Summarise a list of {regret, rank, range_capture_pct, is_correct} rows."""
    n = len(per_dataset)
    regrets = [r["regret"] for r in per_dataset]
    ranks = [r["rank"] for r in per_dataset]
    caps = [r["range_capture_pct"] for r in per_dataset]
    correct = sum(r["is_correct"] for r in per_dataset)
    return {
        "n": n,
        "top1_fraction": f"{correct}/{n}",
        "top1_accuracy_pct": round(100 * correct / n, 1),
        "mean_regret": round(st.mean(regrets), 6),
        "median_regret": round(st.median(regrets), 6),
        "max_regret": round(max(regrets), 6),
        "mean_rank": round(st.mean(ranks), 1),
        "median_rank": st.median(ranks),
        "max_rank": max(ranks),
        "top3_hit": f"{sum(1 for r in ranks if r <= 3)}/{n}",
        "top10_hit": f"{sum(1 for r in ranks if r <= 10)}/{n}",
        "mean_range_capture_pct": round(st.mean(caps), 2),
        "min_range_capture_pct": round(min(caps), 2),
    }


def score_row(dataset: str, recommended: str, scores: dict[str, float]) -> dict:
    ranked = sorted(scores.values(), reverse=True)
    best, worst = ranked[0], ranked[-1]
    rec_score = scores[recommended]
    gt = max(scores, key=scores.__getitem__)
    return {
        "dataset": dataset,
        "recommended_model": recommended,
        "is_correct": recommended == gt,
        "regret": round(best - rec_score, 6),
        "rank": sum(1 for v in ranked if v > rec_score + 1e-12) + 1,
        "range_capture_pct": round(
            100 * ((rec_score - worst) / (best - worst) if best > worst else 1.0), 4
        ),
    }


def constant_policy(prefix: str, bench: dict[str, dict[str, float]]) -> dict:
    """
    Regret of always choosing one model. Zero-shot detectors are recorded under
    per-evaluation-dataset keys, so resolve the key per dataset.
    """
    rows = []
    for d, scores in bench.items():
        key = prefix if prefix in scores else f"{prefix}_{d}"
        if key not in scores:
            return {}
        rows.append(score_row(d, key, scores))
    return measures(rows)


def paired_vs_policy(
    framework_rows: list[dict],
    prefix: str,
    bench: dict[str, dict[str, float]],
) -> dict:
    """
    Exact paired sign-flip permutation test of framework regret against a
    constant policy, over the same datasets. One-sided in the framework's
    favour. Ties (identical regret) carry no sign and are excluded.
    """
    import itertools

    diffs = []
    for r in framework_rows:
        d = r["dataset"]
        scores = bench[d]
        key = prefix if prefix in scores else f"{prefix}_{d}"
        policy_regret = max(scores.values()) - scores[key]
        diffs.append(policy_regret - r["regret"])  # positive = framework better

    nz = [x for x in diffs if abs(x) > 1e-9]
    k = len(nz)
    obs = sum(nz)
    if k == 0:
        p = 1.0
    elif k > 22:  # exhaustive enumeration would be prohibitive
        p = None
    else:
        hits = sum(
            1
            for signs in itertools.product([1, -1], repeat=k)
            if sum(v * s for v, s in zip(nz, signs)) >= obs - 1e-12
        )
        p = hits / 2 ** k
    return {
        "wins": sum(1 for x in diffs if x > 1e-9),
        "losses": sum(1 for x in diffs if x < -1e-9),
        "ties": sum(1 for x in diffs if abs(x) <= 1e-9),
        "informative_pairs": k,
        "one_sided_p": round(p, 4) if p is not None else None,
    }


def main() -> None:
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    bench = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}

    # ── Condition A: evaluation splits, full MKB, coverage guard ACTIVE ──────
    rec = Recommender.from_store(REPO / "mkb.pkl", k=K)
    rows_a = []
    for d in report["per_dataset"]:
        name = d["dataset"]
        profile = pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        r = rec.recommend_from_profile(profile, priority_metric=metric)
        rows_a.append(score_row(name, r.recommended_model, bench[name]))

    # ── Conditions B and C: read from their dated snapshots ─────────────────
    conf_path = REPO / "validation_confirmatory_report.json"
    rows_b = []
    if conf_path.exists():
        conf = json.loads(conf_path.read_text(encoding="utf-8"))
        for r in conf["per_dataset"]:
            rows_b.append(score_row(r["dataset"], r["benchmark_key"], r["all_benchmark_scores"]))

    loo_files = sorted((REPO / "analysis").glob("corpus_exclusion_refit_*.json"))
    loo = json.loads(loo_files[-1].read_text(encoding="utf-8")) if loo_files else None

    # ── Baseline policies, on the evaluation-split basis ─────────────────────
    baselines = {}
    for label, prefix in [
        ("zero-shot lid.176", "lid.176"),
        ("zero-shot CLD3", "cld3"),
        ("zero-shot XLM-V Base", "xlm_v_base_language_id"),
        ("best constant (ORACLE, hindsight-chosen)",
         "fasttext_subword_exorde-social-media-december-2024-week1"),
    ]:
        m = constant_policy(prefix, bench)
        if m:
            baselines[label] = m

    # Expected regret of picking a constant policy blindly (uniform over those
    # variants scored on every evaluation dataset).
    common = set(bench[next(iter(bench))])
    for s in bench.values():
        common &= set(s)
    blind = st.mean(
        st.mean(max(s.values()) - s[v] for s in bench.values()) for v in common
    )

    # ── Paired tests: framework vs each policy, under A and under C ─────────
    policy_prefixes = {
        "zero-shot lid.176": "lid.176",
        "zero-shot CLD3": "cld3",
        "zero-shot XLM-V Base": "xlm_v_base_language_id",
        "best constant (ORACLE, hindsight-chosen)":
            "fasttext_subword_exorde-social-media-december-2024-week1",
    }
    paired = {"A_evaluation_splits_full_mkb": {}, "C_leave_one_corpus_out_refit": {}}
    for label, prefix in policy_prefixes.items():
        paired["A_evaluation_splits_full_mkb"][label] = paired_vs_policy(rows_a, prefix, bench)
        if loo:
            paired["C_leave_one_corpus_out_refit"][label] = paired_vs_policy(
                loo["per_dataset"], prefix, bench
            )

    # ── LLM baseline (if the run exists) — measures + paired test vs framework ─
    llm_summary = None
    llm_path = REPO / "llm_baseline_results.json"
    if llm_path.exists():
        import itertools
        llm = json.loads(llm_path.read_text(encoding="utf-8"))
        llm_gap = {r["dataset"]: r["gap"] for r in llm["per_dataset"]
                   if r.get("gap") is not None}
        fw_gap = {r["dataset"]: r["regret"] for r in rows_a}
        shared = [d for d in fw_gap if d in llm_gap]
        diffs = [llm_gap[d] - fw_gap[d] for d in shared]  # +ve = framework better
        nz = [x for x in diffs if abs(x) > 1e-9]
        obs = sum(nz)
        p = (sum(1 for s in itertools.product([1, -1], repeat=len(nz))
                 if sum(v * sg for v, sg in zip(nz, s)) >= obs - 1e-12) / 2 ** len(nz)
             if 0 < len(nz) <= 22 else None)
        llm_summary = {
            "provider": llm.get("provider"),
            "model": llm.get("model"),
            "open_weights": llm.get("open_weights"),
            "temperature": llm.get("temperature"),
            "repeats_per_dataset": llm.get("repeats_per_dataset"),
            "total_api_calls": llm.get("total_api_calls"),
            "n_datasets_scored": len(shared),
            "mean_gap": round(st.mean(llm_gap[d] for d in shared), 6),
            "median_gap": round(st.median(llm_gap[d] for d in shared), 6),
            "max_gap": round(max(llm_gap[d] for d in shared), 6),
            "mean_exact_match_rate": llm.get("mean_exact_match_rate"),
            "mean_self_consistency": llm.get("mean_self_consistency"),
            "paired_vs_framework_A": {
                "framework_mean_gap": round(st.mean(fw_gap[d] for d in shared), 6),
                "llm_mean_gap": round(st.mean(llm_gap[d] for d in shared), 6),
                "framework_better": sum(1 for x in diffs if x > 1e-9),
                "llm_better": sum(1 for x in diffs if x < -1e-9),
                "ties": sum(1 for x in diffs if abs(x) <= 1e-9),
                "informative_pairs": len(nz),
                "one_sided_p": round(p, 6) if p is not None else None,
            },
        }

    out = {
        "generated": str(date.today()),
        "priority_metric": metric,
        "k": K,
        "n_candidates_per_dataset": len(bench[next(iter(bench))]),
        "basis_note": (
            "Conditions A and C score against the evaluation-side benchmark "
            "archive; condition B against the validation-side archive. Rank and "
            "range capture are comparable in kind, not from an identical pool."
        ),
        "conditions": {
            "A_evaluation_splits_full_mkb": measures(rows_a),
            "B_confirmatory_validation_splits": measures(rows_b) if rows_b else None,
            "C_leave_one_corpus_out_refit": {
                k: loo[k] for k in (
                    "top1_fraction", "mean_regret", "median_regret", "max_regret",
                    "mean_rank", "median_rank", "max_rank", "top3_hit_rate",
                    "top10_hit_rate", "mean_range_capture_pct", "min_range_capture_pct",
                ) if k in loo
            } if loo else None,
        },
        "baseline_policies_evaluation_basis": baselines,
        "llm_baseline": llm_summary,
        "paired_framework_vs_policy": paired,
        "blind_constant_pick_expected_regret": round(blind, 6),
        "per_dataset": {
            "A_evaluation_splits_full_mkb": rows_a,
            "B_confirmatory_validation_splits": rows_b,
        },
    }

    stamp = date.today().isoformat()
    dest = REPO / "analysis" / f"reporting_measures_{stamp}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    printable = {k: v for k, v in out.items() if k != "per_dataset"}
    print(json.dumps(printable, indent=2, ensure_ascii=False))
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
