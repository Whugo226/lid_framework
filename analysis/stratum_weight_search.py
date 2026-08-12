"""
stratum_weight_search.py

Does tuning the S1-S6 stratum weights improve recommendation quality, and does
any improvement survive out-of-sample selection?

WHY THIS EXISTS
---------------
The framework ships with equal stratum weights (all 1.0).  Chapter 3 defers
empirical weight refinement as under-powered at 17 corpora; Chapter 4 justifies
retaining the redundant heterogeneity statistic partly on the grounds that
weighting is not where the headroom lies; Chapter 5 lists weight refinement as a
mitigation for the generalist-neighbour failure mode.  None of those three
positions was backed by a measurement.  This script supplies one.

THE TWO EXPERIMENTS
-------------------
  IN-SAMPLE     Random search over weight vectors, scored on all 17 evaluation
                splits.  Answers: can ANY weighting beat equal weights when the
                same data chooses the weights and grades them?

  OUT-OF-SAMPLE Leave-one-corpus-out weight SELECTION.  For each corpus i, pick
                the best draw by mean regret over the other 16, then score that
                draw on i alone.  Answers: does a weighting chosen without
                seeing corpus i help on corpus i?

The gap between the two is the quantity of interest.  In-sample gains that do
not reproduce out-of-sample are overfitting to a 17-point sample, not headroom.

SCOPE NOTE — this is NOT the corpus-exclusion refit of condition C.  The MKB is
held FIXED at all 17 corpora throughout; only the weight-tuning signal is held
out.  Every query therefore runs against the same knowledge base as condition A
(evaluation splits, full MKB), and the two are directly comparable.  Do not
present this as an unseen-corpus result.

Reads only committed artifacts; writes a dated JSON snapshot. Modifies nothing.

Run (repo root, thesis_final):
    python analysis/stratum_weight_search.py [--draws 200] [--seed 20260805]
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from lid_toolkit.recommender import Recommender  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
K = 3
STRATA = [
    "S1_morphological",
    "S2_lexical_diversity",
    "S3_structural",
    "S4_info_theoretic",
    "S5_cross_level",
    "cat",
]
EQUAL_WEIGHTS = {s: 1.0 for s in STRATA}


def score_row(dataset: str, recommended: str, scores: dict[str, float]) -> dict:
    """Identical bookkeeping to reporting_measures.score_row (kept in step)."""
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


def measures(rows: list[dict]) -> dict:
    n = len(rows)
    return {
        "n": n,
        "top1_fraction": f"{sum(r['is_correct'] for r in rows)}/{n}",
        "mean_regret": round(st.mean(r["regret"] for r in rows), 6),
        "median_regret": round(st.median(r["regret"] for r in rows), 6),
        "max_regret": round(max(r["regret"] for r in rows), 6),
        "mean_rank": round(st.mean(r["rank"] for r in rows), 1),
        "mean_range_capture_pct": round(st.mean(r["range_capture_pct"] for r in rows), 2),
    }


def sample_weights(rng: np.random.Generator) -> dict[str, float]:
    """
    Log-uniform draw over [0.1, 10] per stratum, then rescaled to mean 1.0.

    Log-uniform spans two orders of magnitude symmetrically about 1.0, so a
    stratum is as likely to be suppressed as amplified.  The mean-1.0 rescale
    matches the normalisation learn_weights() applies, and is harmless anyway:
    the composite distance divides by the weight sum, so only RELATIVE weights
    affect the ranking.
    """
    w = np.exp(rng.uniform(np.log(0.1), np.log(10.0), size=len(STRATA)))
    w = w / w.mean()
    return {s: float(v) for s, v in zip(STRATA, w)}


def evaluate(rec, weights: dict[str, float], queries: list[tuple], bench: dict,
             metric: str) -> list[dict]:
    """Score one weight vector across every evaluation split."""
    rec.engine.stratum_weights = dict(weights)
    rows = []
    for name, fp, iso in queries:
        r = rec.engine.query(fp, priority_metric=metric, user_iso_codes=iso)
        rows.append(score_row(name, r.recommended_model, bench[name]))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260805)
    args = ap.parse_args()

    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    bench = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}

    rec = Recommender.from_store(REPO / "mkb.pkl", k=K)
    builder = rec.store.builder

    # Fingerprints depend only on the profile and the fitted stratifier, not on
    # the weights — build once and reuse for every draw.
    queries: list[tuple] = []
    for d in report["per_dataset"]:
        name = d["dataset"]
        profile = pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        queries.append((name, builder.build(profile), frozenset(profile.columns)))
    names = [q[0] for q in queries]

    # ── Reference policies ───────────────────────────────────────────────────
    equal_rows = evaluate(rec, EQUAL_WEIGHTS, queries, bench, metric)

    learned = Recommender.from_store(REPO / "mkb.pkl", k=K).learn_weights(
        priority_metric=metric
    )
    learned = {s: float(learned.get(s, 1.0)) for s in STRATA}
    learned_rows = evaluate(rec, learned, queries, bench, metric)

    # ── One pass of random draws, scored on every corpus, cached ─────────────
    rng = np.random.default_rng(args.seed)
    draws: list[dict] = [EQUAL_WEIGHTS] + [sample_weights(rng) for _ in range(args.draws)]
    # per_draw[d][name] = row  (draw d, corpus name)
    per_draw: list[dict[str, dict]] = []
    for w in draws:
        per_draw.append({r["dataset"]: r for r in evaluate(rec, w, queries, bench, metric)})

    # ── IN-SAMPLE: best draw by mean regret over all 17 ──────────────────────
    def mean_regret_over(d_idx: int, subset: list[str]) -> float:
        return st.mean(per_draw[d_idx][n]["regret"] for n in subset)

    best_in = min(range(len(draws)), key=lambda i: mean_regret_over(i, names))
    in_sample_rows = [per_draw[best_in][n] for n in names]

    # ── OUT-OF-SAMPLE: leave-one-corpus-out weight SELECTION ────────────────
    loo_rows: list[dict] = []
    loo_choice: list[dict] = []
    for held in names:
        train = [n for n in names if n != held]
        pick = min(range(len(draws)), key=lambda i: mean_regret_over(i, train))
        loo_rows.append(per_draw[pick][held])
        loo_choice.append({
            "held_out": held,
            "chosen_draw": pick,
            "chose_equal_weights": pick == 0,
            "train_mean_regret": round(mean_regret_over(pick, train), 6),
            "weights": {s: round(draws[pick][s], 4) for s in STRATA},
        })

    # ── Spread across the whole draw population ──────────────────────────────
    # How sensitive is the framework to weighting at all?  If most of a wide
    # random sweep lands near the equal-weight result, the weight vector is not
    # a lever worth pulling, whatever the best draw happens to score.
    draw_regrets = [mean_regret_over(i, names) for i in range(1, len(draws))]
    draw_top1 = [
        sum(per_draw[i][n]["is_correct"] for n in names) for i in range(1, len(draws))
    ]
    equal_regret = mean_regret_over(0, names)
    distribution = {
        "n_draws_scored": len(draw_regrets),
        "equal_weight_mean_regret": round(equal_regret, 6),
        "draw_mean_regret_min": round(min(draw_regrets), 6),
        "draw_mean_regret_median": round(st.median(draw_regrets), 6),
        "draw_mean_regret_max": round(max(draw_regrets), 6),
        "n_draws_beating_equal": sum(1 for r in draw_regrets if r < equal_regret - 1e-9),
        "pct_draws_beating_equal": round(
            100 * sum(1 for r in draw_regrets if r < equal_regret - 1e-9) / len(draw_regrets), 1
        ),
        "best_draw_improvement_vs_equal_pct": round(
            100 * (equal_regret - min(draw_regrets)) / equal_regret, 1
        ),
        "top1_min": min(draw_top1),
        "top1_max": max(draw_top1),
        "n_draws_exceeding_equal_top1": sum(
            1 for t in draw_top1 if t > sum(r["is_correct"] for r in equal_rows)
        ),
    }

    # ── Best constant policy, for scale ──────────────────────────────────────
    common = set(bench[names[0]])
    for s in bench.values():
        common &= set(s)
    const = {
        v: st.mean(max(s.values()) - s[v] for s in bench.values()) for v in common
    }
    best_const = min(const, key=const.__getitem__) if const else None

    out = {
        "generated": str(date.today()),
        "priority_metric": metric,
        "k": K,
        "seed": args.seed,
        "n_random_draws": args.draws,
        "search_space": "log-uniform [0.1, 10] per stratum, rescaled to mean 1.0",
        "scope_note": (
            "MKB held FIXED at all 17 corpora. Only the weight-tuning signal is "
            "held out in the leave-one-corpus-out condition. This is a test of "
            "weight-selection generalisation, NOT an unseen-corpus test — it is "
            "not comparable to the corpus-exclusion refit of condition C."
        ),
        "policies": {
            "equal_weights_published": measures(equal_rows),
            "learn_weights_shipped_method": measures(learned_rows),
            "best_in_sample_draw": measures(in_sample_rows),
            "leave_one_corpus_out_selection": measures(loo_rows),
        },
        "draw_distribution": distribution,
        "best_in_sample_weights": {s: round(draws[best_in][s], 4) for s in STRATA},
        "best_in_sample_is_equal_weights": best_in == 0,
        "learned_weights": {s: round(learned[s], 4) for s in STRATA},
        "best_constant_policy": {
            "variant": best_const,
            "mean_regret": round(const[best_const], 6) if best_const else None,
        },
        "loo_selection_detail": loo_choice,
        "per_dataset": {
            "equal_weights_published": equal_rows,
            "best_in_sample_draw": in_sample_rows,
            "leave_one_corpus_out_selection": loo_rows,
        },
    }

    stamp = date.today().isoformat()
    dest = REPO / "analysis" / f"stratum_weight_search_{stamp}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    printable = {k: v for k, v in out.items() if k not in ("per_dataset", "loo_selection_detail")}
    print(json.dumps(printable, indent=2, ensure_ascii=False))
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
