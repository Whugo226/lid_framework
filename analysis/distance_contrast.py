"""
Distance-concentration diagnostic for the stratified fingerprint space.

Chapter 4 justifies per-stratum Euclidean distance over global cosine partly by
appeal to concentration of measure: in very high-dimensional spaces pairwise
distances converge, destroying discriminative contrast. That argument is
testable on the fitted knowledge base, and this script tests it.

For every ordered pair of the 17 MKB datasets it computes the composite
distance D(q,h) and the per-stratum Euclidean distances, then reports the
standard concentration diagnostic, *relative contrast*:

    RC = (d_max - d_min) / d_min

measured within each query's own candidate set (which is exactly the set the
k-NN retrieval ranks over), plus the coefficient of variation of those
distances. Concentration of measure manifests as RC -> 0 and CV -> 0. Values
well away from zero mean the space still separates neighbours from
non-neighbours.

Read-only with respect to the MKB. Writes one JSON artifact next to itself.

Run from the repo root:
    python analysis/distance_contrast.py
"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, "src")

from lid_toolkit.recommender.mkb_similarity import SimilarityEngine  # noqa: E402
from lid_toolkit.recommender.mkb_store import MKBStore  # noqa: E402

OUT = Path("analysis") / f"distance_contrast_{date.today().isoformat()}.json"


def main() -> None:
    store = MKBStore.load("mkb.pkl")
    engine = SimilarityEngine(store)
    names = list(store.datasets)
    fps = {n: store.get_entry(n).fingerprint for n in names}

    composite_rc, composite_cv = [], []
    per_stratum_rc: dict[str, list[float]] = {}
    all_composite: list[float] = []

    for q in names:
        dists, strat_rows = [], []
        for h in names:
            if h == q:
                continue
            per_s = engine._stratum_distances(fps[q], fps[h])
            dists.append(engine._weighted_distance(per_s))
            strat_rows.append(per_s)

        all_composite.extend(dists)
        d_min, d_max = min(dists), max(dists)
        if d_min > 0:
            composite_rc.append((d_max - d_min) / d_min)
        composite_cv.append(statistics.stdev(dists) / statistics.mean(dists))

        for s in strat_rows[0]:
            vals = [row[s] for row in strat_rows]
            lo, hi = min(vals), max(vals)
            if lo > 0:
                per_stratum_rc.setdefault(s, []).append((hi - lo) / lo)

    result = {
        "generated": date.today().isoformat(),
        "n_datasets": len(names),
        "n_ordered_pairs": len(all_composite),
        "composite": {
            "relative_contrast_mean": statistics.mean(composite_rc),
            "relative_contrast_min": min(composite_rc),
            "relative_contrast_max": max(composite_rc),
            "cv_mean": statistics.mean(composite_cv),
            "distance_mean": statistics.mean(all_composite),
            "distance_min": min(all_composite),
            "distance_max": max(all_composite),
        },
        "per_stratum_relative_contrast_mean": {
            s: statistics.mean(v) for s, v in sorted(per_stratum_rc.items())
        },
    }

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    c = result["composite"]
    print(f"datasets {result['n_datasets']}  ordered pairs {result['n_ordered_pairs']}")
    print("\ncomposite distance D(q,h)")
    print(f"  range over all pairs      {c['distance_min']:.4f} - {c['distance_max']:.4f}"
          f"  (mean {c['distance_mean']:.4f})")
    print(f"  relative contrast (mean)  {c['relative_contrast_mean']:.3f}"
          f"   [min {c['relative_contrast_min']:.3f}, max {c['relative_contrast_max']:.3f}]")
    print(f"  coeff. of variation       {c['cv_mean']:.3f}")
    print("\nper-stratum relative contrast (mean over queries)")
    for s, v in result["per_stratum_relative_contrast_mean"].items():
        print(f"  {s:24s} {v:.3f}")
    print(f"\nwritten: {OUT}")


if __name__ == "__main__":
    main()
