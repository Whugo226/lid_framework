"""
stratum_share_of_distance.py

PANEL FINDING M1 — equal nominal weights are not equal influence.

The composite distance weights every stratum at w_s = 1.0 by default. That is
equal NOMINAL weight, not equal contribution: the five continuous terms are
Euclidean norms over stratum slices of differing dimensionality (S4 retains 5
components, S1 and S3 retain 16), and a norm grows with the dimensionality it
is taken over, while the S6 term is a bounded Hamming FRACTION on [0, 1]
averaged in with unbounded continuous norms.

conclusion.tex:220 (Limitation 6) states this mechanism. What did not exist
until now is the measurement behind it. This script supplies it: each
stratum's share of the composite numerator, measured over the 17 evaluation
queries under the deployed protocol.

    D(q, h) = ( SUM_s w_s * d_s ) / SUM_s w_s

    share_s = w_s * d_s / SUM_s w_s * d_s        (the numerator's composition)

Two populations are reported, because they answer different questions:

  ALL PAIRS  17 queries x 17 candidates = 289. How the distance function
             behaves in general.
  TOP-3      the 51 query-candidate pairs actually retrieved into the
             neighbourhoods that produce the recommendations. What the
             composition is where it matters.

Distances come from SimilarityEngine._stratum_distances, i.e. the deployed
code path, not a reimplementation.

READ-ONLY. Nothing under src/ is modified; mkb.pkl is never rewritten. Writes
one dated JSON snapshot.

Run (repo root, thesis_final):
    python analysis/stratum_share_of_distance.py
"""
from __future__ import annotations

import json
import statistics as st
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import pandas as pd  # noqa: E402

from lid_toolkit.recommender import Recommender  # noqa: E402
from lid_toolkit.recommender.mkb_store import MKBStore  # noqa: E402
from lid_toolkit.recommender.mkb_similarity import SimilarityEngine  # noqa: E402

K = 3
LABELS = {
    "S1_morphological": "S1 Morphological richness",
    "S2_lexical_diversity": "S2 Lexical diversity",
    "S3_structural": "S3 Structural / syntactic",
    "S4_info_theoretic": "S4 Information-theoretic",
    "S5_cross_level": "S5 Cross-level cohesion",
    "cat": "S6 Typological flags",
}


def summarise(rows: list[dict], keys: list[str]) -> dict:
    """Per-stratum share statistics over a population of query-candidate pairs."""
    out = {}
    for s in keys:
        shares = [r["shares"][s] * 100 for r in rows]
        dists = [r["distances"][s] for r in rows]
        out[s] = {
            "label": LABELS.get(s, s),
            "mean_share_pct": round(st.mean(shares), 2),
            "median_share_pct": round(st.median(shares), 2),
            "min_share_pct": round(min(shares), 2),
            "max_share_pct": round(max(shares), 2),
            "mean_distance": round(st.mean(dists), 4),
        }
    return out


def main() -> None:
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    names = [d["dataset"] for d in report["per_dataset"]]

    store = MKBStore.load(REPO / "mkb.pkl")
    engine = SimilarityEngine(store, k=K)
    rec = Recommender.from_store(REPO / "mkb.pkl", k=K)

    keys = list(store.stratifier.stratum_names) + ["cat"]
    n_pcs = {s: store.stratifier._fits[s].n_components
             for s in store.stratifier.stratum_names}
    n_pcs["cat"] = None  # not PCA'd

    all_pairs: list[dict] = []
    top3_pairs: list[dict] = []

    for q in names:
        profile = pd.read_pickle(REPO / "eval_profiles" / f"{q}.pkl")
        q_fp = store.builder.build(profile)

        # Which candidates were actually retrieved for this query?
        r = rec.recommend_from_profile(profile, priority_metric=metric)
        retrieved = {nb.dataset_name for nb in r.neighbours[:K]}

        for cand in store.datasets:
            d = engine._stratum_distances(q_fp, store.get_entry(cand).fingerprint)
            numer = sum(engine.stratum_weights.get(s, 1.0) * d[s] for s in keys)
            if numer <= 0:
                continue
            row = {
                "query": q,
                "candidate": cand,
                "distances": {s: float(d[s]) for s in keys},
                "shares": {s: engine.stratum_weights.get(s, 1.0) * d[s] / numer
                           for s in keys},
                "composite_D": numer / sum(engine.stratum_weights.get(s, 1.0) for s in keys),
            }
            all_pairs.append(row)
            if cand in retrieved:
                top3_pairs.append(row)

    stats_all = summarise(all_pairs, keys)
    stats_top3 = summarise(top3_pairs, keys)

    # Order the report by contribution, largest first.
    order = sorted(keys, key=lambda s: -stats_all[s]["mean_share_pct"])

    hdr = f"{'stratum':30s} {'PCs':>4s} {'mean %':>8s} {'min %':>7s} {'max %':>7s} {'top-3 %':>9s}"
    print(f"Per-stratum share of the composite numerator "
          f"({len(all_pairs)} query-candidate pairs; {len(top3_pairs)} retrieved)\n")
    print(hdr)
    print("-" * len(hdr))
    for s in order:
        a, t = stats_all[s], stats_top3[s]
        pcs = "--" if n_pcs[s] is None else str(n_pcs[s])
        print(f"{a['label']:30s} {pcs:>4s} {a['mean_share_pct']:>8.2f} "
              f"{a['min_share_pct']:>7.2f} {a['max_share_pct']:>7.2f} "
              f"{t['mean_share_pct']:>9.2f}")
    print("-" * len(hdr))
    print(f"{'equal nominal weight would be':30s} {'':>4s} {100/len(keys):>8.2f}")

    # Does dimensionality explain the ordering?
    cont = [s for s in keys if n_pcs[s] is not None]
    xs = [n_pcs[s] for s in cont]
    ys = [stats_all[s]["mean_share_pct"] for s in cont]
    mx, my = st.mean(xs), st.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    pearson = num / den if den else float("nan")
    print(f"\nPearson r between retained components and mean share "
          f"(five continuous strata): {pearson:.3f}")

    ratio = (max(stats_all[s]['mean_share_pct'] for s in cont) /
             min(stats_all[s]['mean_share_pct'] for s in cont))
    print(f"Largest / smallest continuous share: {ratio:.2f}x")
    print(f"S6 share relative to an equal sixth: "
          f"{stats_all['cat']['mean_share_pct'] / (100/len(keys)):.4f}x")

    out = {
        "generated": str(date.today()),
        "panel_finding": "M1 (equal nominal stratum weights are not equal influence)",
        "source_artifact": "mkb.pkl",
        "basis": "17 evaluation-split queries against the 17-corpus MKB, equal weights",
        "priority_metric": metric,
        "k": K,
        "n_pairs_all": len(all_pairs),
        "n_pairs_retrieved": len(top3_pairs),
        "retained_components": n_pcs,
        "equal_nominal_share_pct": round(100 / len(keys), 2),
        "share_all_pairs": stats_all,
        "share_retrieved_only": stats_top3,
        "dimensionality_correlation": {
            "pearson_r_components_vs_share": round(pearson, 4),
            "note": "five continuous strata only; S6 is not PCA-projected",
        },
        "largest_over_smallest_continuous": round(ratio, 3),
        "per_pair": [
            {"query": r["query"], "candidate": r["candidate"],
             "composite_D": round(r["composite_D"], 4),
             "shares_pct": {s: round(v * 100, 3) for s, v in r["shares"].items()}}
            for r in all_pairs
        ],
    }
    dest = REPO / "analysis" / f"stratum_share_of_distance_{date.today().isoformat()}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
