"""
weight_insensitivity_diagnosis.py

WHY DOES REWEIGHTING THE STRATA BARELY MOVE THE RESULT?

stratum_weight_search.py established that stratum weights are a weak lever:
2,000 draws spanning two orders of magnitude move mean regret only within
[0.0067, 0.0118] and never improve strict top-1.  That is a suspicious finding
on its face — a parameter that does nothing is usually a symptom, not a
feature.  This script asks WHICH mechanism produces it.  Three candidates:

  (a) COLLINEARITY.  The six per-stratum distances are highly correlated
      across dataset pairs, so the composite is effectively one-dimensional
      and no reweighting can reorder the candidates.  If true, the
      stratification buys interpretability but little discriminative
      diversity.

  (b) SELF-MATCH DOMINANCE.  Each query re-identifies its own source corpus
      by a wide margin, so the nearest neighbour is fixed under any weighting
      and the retrieval problem is trivially easy in this protocol.

  (c) CEILING / TIE STRUCTURE.  The candidate models score so close together
      that almost any retrieval returns a near-optimal model, so regret is
      insensitive to retrieval quality — not merely to weights.

These are not mutually exclusive, and they have very different implications.
(a) is a design finding about the strata.  (b) is a protocol limitation the
thesis already partly concedes.  (c) would mean regret lacks the resolution to
detect retrieval differences at all, which would bound what ANY tuning
experiment on this knowledge base can show.

Measures, in order:
  1. Correlation matrix of per-stratum distances over all ordered pairs, plus
     the share of variance on the first principal component of that matrix.
  2. Retrieval churn under reweighting: how often the top-1 and top-3 change.
  3. Self-match margin: rank and relative gap of the query's own corpus.
  4. Score dispersion per dataset: how much regret is on the table at all.
  5. Recommendation diversity across queries and across weightings.

Reads only committed artifacts; writes a dated JSON snapshot. Modifies nothing.

Run (repo root, thesis_final):
    python analysis/weight_insensitivity_diagnosis.py [--draws 200]
"""
from __future__ import annotations

import argparse
import itertools
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
EQUAL = {s: 1.0 for s in STRATA}


def sample_weights(rng: np.random.Generator) -> dict[str, float]:
    w = np.exp(rng.uniform(np.log(0.1), np.log(10.0), size=len(STRATA)))
    return {s: float(v) for s, v in zip(STRATA, w / w.mean())}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    bench = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}

    rec = Recommender.from_store(REPO / "mkb.pkl", k=K)
    engine = rec.engine
    store = rec.store
    builder = store.builder

    # ── (1) Collinearity of the per-stratum distances ────────────────────────
    # Measured over all ordered MKB pairs — the same population the contrast
    # study uses, so the two are directly comparable.
    names_mkb = list(store.datasets)
    rows = []
    for a, b in itertools.permutations(names_mkb, 2):
        d = engine._stratum_distances(
            store.get_entry(a).fingerprint, store.get_entry(b).fingerprint
        )
        rows.append([d.get(s, 0.0) for s in STRATA])
    M = np.array(rows)
    corr = np.corrcoef(M.T)
    # PC1 share of the CORRELATION matrix = collinearity of the distance
    # components, independent of their differing scales.
    eig = np.sort(np.linalg.eigvalsh(corr))[::-1]
    pc1_share = float(eig[0] / eig.sum())

    collinearity = {
        "n_ordered_pairs": len(rows),
        "correlation_matrix": {
            STRATA[i]: {STRATA[j]: round(float(corr[i, j]), 3) for j in range(len(STRATA))}
            for i in range(len(STRATA))
        },
        "mean_offdiagonal_correlation": round(
            float(np.mean([corr[i, j] for i in range(6) for j in range(6) if i != j])), 3
        ),
        "max_offdiagonal_correlation": round(
            float(max(corr[i, j] for i in range(6) for j in range(6) if i != j)), 3
        ),
        "pc1_share_of_correlation_matrix": round(pc1_share, 3),
        "interpretation_note": (
            "pc1_share near 1.0 means the six stratum distances move together, "
            "so the composite is effectively one-dimensional and reweighting "
            "cannot reorder candidates. Near 1/6 = 0.167 means they are "
            "independent and weighting genuinely selects among them."
        ),
    }

    # ── Query fingerprints (built once) ──────────────────────────────────────
    queries = []
    for d in report["per_dataset"]:
        name = d["dataset"]
        profile = pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        queries.append((name, builder.build(profile), frozenset(profile.columns)))
    names = [q[0] for q in queries]

    def run(weights: dict[str, float]) -> dict[str, dict]:
        engine.stratum_weights = dict(weights)
        out = {}
        for name, fp, iso in queries:
            r = engine.query(fp, priority_metric=metric, user_iso_codes=iso)
            out[name] = {
                "top1_neighbour": r.neighbours[0].dataset_name,
                "top3": tuple(nb.dataset_name for nb in r.neighbours),
                "recommended": r.recommended_model,
                "distances": [nb.distance for nb in r.neighbours],
            }
        return out

    base = run(EQUAL)

    # ── (2) Retrieval churn under reweighting ────────────────────────────────
    rng = np.random.default_rng(args.seed)
    draws = [sample_weights(rng) for _ in range(args.draws)]
    n_top1_changed = 0
    n_top3_changed = 0
    n_rec_changed = 0
    total = 0
    recs_seen: dict[str, set[str]] = {n: set() for n in names}
    top1_seen: dict[str, set[str]] = {n: set() for n in names}
    for w in draws:
        res = run(w)
        for n in names:
            total += 1
            if res[n]["top1_neighbour"] != base[n]["top1_neighbour"]:
                n_top1_changed += 1
            if set(res[n]["top3"]) != set(base[n]["top3"]):
                n_top3_changed += 1
            if res[n]["recommended"] != base[n]["recommended"]:
                n_rec_changed += 1
            recs_seen[n].add(res[n]["recommended"])
            top1_seen[n].add(res[n]["top1_neighbour"])

    churn = {
        "n_draws": len(draws),
        "query_draw_pairs": total,
        "pct_top1_neighbour_changed": round(100 * n_top1_changed / total, 1),
        "pct_top3_set_changed": round(100 * n_top3_changed / total, 1),
        "pct_recommendation_changed": round(100 * n_rec_changed / total, 1),
        "mean_distinct_top1_neighbours_per_query": round(
            st.mean(len(v) for v in top1_seen.values()), 2
        ),
        "mean_distinct_recommendations_per_query": round(
            st.mean(len(v) for v in recs_seen.values()), 2
        ),
    }

    # ── (3) Self-match margin under equal weights ────────────────────────────
    engine.stratum_weights = dict(EQUAL)
    self_match = []
    for name, fp, iso in queries:
        r = engine.query(fp, priority_metric=metric, user_iso_codes=iso, k=len(names_mkb))
        order = [nb.dataset_name for nb in r.neighbours]
        dists = {nb.dataset_name: nb.distance for nb in r.neighbours}
        rank = order.index(name) + 1 if name in order else None
        d_self = dists.get(name)
        others = sorted(d for n2, d in dists.items() if n2 != name)
        self_match.append({
            "dataset": name,
            "self_rank": rank,
            "self_distance": round(d_self, 4) if d_self is not None else None,
            "nearest_other_distance": round(others[0], 4) if others else None,
            "margin_ratio": round(others[0] / d_self, 3) if d_self and others else None,
        })
    n_self_first = sum(1 for r in self_match if r["self_rank"] == 1)

    # ── (4) Score dispersion — how much regret is on the table ───────────────
    dispersion = []
    for n in names:
        vals = sorted(bench[n].values(), reverse=True)
        dispersion.append({
            "dataset": n,
            "n_candidates": len(vals),
            "best": round(vals[0], 6),
            "best_minus_second": round(vals[0] - vals[1], 6),
            "best_minus_worst": round(vals[0] - vals[-1], 6),
            "n_within_0.001_of_best": sum(1 for v in vals if vals[0] - v <= 0.001),
            "n_within_0.01_of_best": sum(1 for v in vals if vals[0] - v <= 0.01),
        })

    out = {
        "generated": str(date.today()),
        "priority_metric": metric,
        "k": K,
        "seed": args.seed,
        "question": (
            "Why is the framework insensitive to stratum weighting? Tests three "
            "mechanisms: (a) collinear stratum distances, (b) self-match "
            "dominance in retrieval, (c) ceiling/tie structure in the candidate "
            "scores."
        ),
        "a_collinearity": collinearity,
        "b_retrieval_churn_under_reweighting": churn,
        "b_self_match": {
            "n_self_retrieved_first": f"{n_self_first}/{len(names)}",
            "median_margin_ratio": round(
                st.median(r["margin_ratio"] for r in self_match
                          if r["margin_ratio"] is not None), 3
            ),
            "per_dataset": self_match,
        },
        "c_score_dispersion": {
            "median_best_minus_second": round(
                st.median(d["best_minus_second"] for d in dispersion), 6
            ),
            "median_best_minus_worst": round(
                st.median(d["best_minus_worst"] for d in dispersion), 6
            ),
            "median_n_within_0.001_of_best": st.median(
                d["n_within_0.001_of_best"] for d in dispersion
            ),
            "median_n_within_0.01_of_best": st.median(
                d["n_within_0.01_of_best"] for d in dispersion
            ),
            "per_dataset": dispersion,
        },
    }

    stamp = date.today().isoformat()
    dest = REPO / "analysis" / f"weight_insensitivity_diagnosis_{stamp}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    printable = json.loads(json.dumps(out))
    printable["b_self_match"].pop("per_dataset")
    printable["c_score_dispersion"].pop("per_dataset")
    printable["a_collinearity"].pop("correlation_matrix")
    print(json.dumps(printable, indent=2, ensure_ascii=False))
    print("\ncorrelation matrix:")
    print(pd.DataFrame(collinearity["correlation_matrix"]).round(2).to_string())
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
