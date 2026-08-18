"""
distance_scale_disparity.py

HOW MUCH DOES THE CATEGORICAL STRATUM ACTUALLY CONTRIBUTE TO THE COMPOSITE
DISTANCE?

The composite distance of Equation 4.1 averages six terms under equal weights:
five per-stratum Euclidean norms over the continuous fingerprint slices, and
one normalised Hamming distance over the 17 categorical S6 flags. The five
Euclidean terms are unbounded and, on the deployed fingerprints, run to tens;
the Hamming term is a fraction of differing flags and is bounded in [0, 1] by
construction.

Equal weights therefore do not deliver equal influence. This script measures
the size of that disparity over every pair of datasets in the deployed MKB,
so the chapter can state it as a measured quantity rather than an impression.

WHAT IT REPORTS
---------------
  - the distribution of each per-stratum Euclidean term
  - the distribution of the S6 Hamming term
  - the share of the composite numerator contributed by S6, per pair

WHAT IT DOES NOT DO
-------------------
Nothing is rebuilt or refitted. mkb.pkl is read-only input and no file in the
estate is modified apart from this script's own dated JSON output.

Run (repo root, thesis_final):
    python analysis/distance_scale_disparity.py
"""
from __future__ import annotations

import itertools
import json
import pickle
import statistics as st
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from lid_toolkit.recommender.mkb_similarity import SimilarityEngine  # noqa: E402


def describe(values: list[float]) -> dict:
    return {
        "min": round(min(values), 6),
        "median": round(st.median(values), 6),
        "mean": round(st.mean(values), 6),
        "max": round(max(values), 6),
    }


def main() -> None:
    with open(REPO / "mkb.pkl", "rb") as fh:
        mkb = pickle.load(fh)
    engine = SimilarityEngine(mkb, k=3)

    per_stratum: dict[str, list[float]] = {}
    shares: list[float] = []
    pairs: list[dict] = []

    for a, b in itertools.combinations(list(mkb.datasets), 2):
        d = engine._stratum_distances(
            mkb.get_entry(a).fingerprint, mkb.get_entry(b).fingerprint
        )
        numerator = sum(d.values())
        share = d["cat"] / numerator if numerator else 0.0
        shares.append(share)
        for s, v in d.items():
            per_stratum.setdefault(s, []).append(v)
        pairs.append({
            "a": a, "b": b,
            "terms": {s: round(v, 6) for s, v in d.items()},
            "numerator": round(numerator, 6),
            "composite_D": round(engine._weighted_distance(d), 6),
            "cat_share_pct": round(100 * share, 6),
        })

    continuous = [v for s, vals in per_stratum.items() if s != "cat" for v in vals]

    out = {
        "generated": str(date.today()),
        "source_artifact": "mkb.pkl",
        "n_datasets": len(mkb.datasets),
        "n_pairs": len(pairs),
        "weights": "equal (w_s = 1.0 for all six terms)",
        "note": (
            "The five continuous terms are unbounded Euclidean norms over "
            "fingerprint slices of 25-80 dimensions; the S6 term is a bounded "
            "fraction of differing categorical flags. Under equal weights the "
            "categorical term is therefore a negligible share of the composite."
        ),
        "per_stratum_distance": {s: describe(v) for s, v in per_stratum.items()},
        "continuous_terms_pooled": describe(continuous),
        "cat_share_of_numerator_pct": describe([100 * s for s in shares]),
        "pairs": pairs,
    }

    dest = REPO / "analysis" / f"distance_scale_disparity_{date.today().isoformat()}.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"pairs: {out['n_pairs']}")
    print("per-stratum distance (median):")
    for s, v in sorted(out["per_stratum_distance"].items(),
                       key=lambda kv: -kv[1]["median"]):
        print(f"   {s:22s} {v['median']:8.4f}   [{v['min']:.4f}, {v['max']:.4f}]")
    c = out["cat_share_of_numerator_pct"]
    print(f"S6 share of numerator (%): median {c['median']:.3f}  "
          f"mean {c['mean']:.3f}  max {c['max']:.3f}")
    print(f"snapshot -> {dest}")


if __name__ == "__main__":
    main()
