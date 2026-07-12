"""
validation_statistics.py — offline statistics for the Chapter 5 evaluation,
computed entirely from validation_report.json (no new experiments).

Reports:
  1. Chance level and random-policy expected performance gap.
  2. Constant-policy baselines (every model variant available on all datasets).
  3. Top-k accuracy and MRR of the ground-truth model in the IDW ranking.
  4. Exact (hypergeometric) test for the confidence-stratified accuracy split,
     plus Wilson 95% confidence intervals for the headline proportions.
  5. Corpus re-identification rate (query's source corpus as top-1/top-3 neighbour).

Usage:  conda run -n thesis_final python analysis/validation_statistics.py
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "validation_report.json"


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return centre - half, centre + half


def main() -> None:
    rep = json.load(open(REPORT))
    per = rep["per_dataset"]
    n = len(per)
    fw_mean = rep["performance_delta"]["mean"]
    print(f"n = {n}, priority = {rep['priority_metric']}, "
          f"reported accuracy = {rep['recommendation_accuracy']}, mean gap = {fw_mean}")

    # 1. random policy
    n_models = [len(d["all_benchmark_scores"]) for d in per]
    rand_gap = sum(
        sum(d["ground_truth_score"] - s for s in d["all_benchmark_scores"].values())
        / len(d["all_benchmark_scores"])
        for d in per
    ) / n
    print(f"\n[1] chance exact-match = {100/ (sum(n_models)/n):.2f}%   "
          f"random-policy mean gap = {rand_gap:.4f}")

    # 2. constant policies
    common = set(per[0]["all_benchmark_scores"])
    for d in per[1:]:
        common &= set(d["all_benchmark_scores"])
    rows = []
    for v in common:
        gaps = [d["ground_truth_score"] - d["all_benchmark_scores"][v] for d in per]
        rows.append((sum(gaps) / n, max(gaps), v))
    rows.sort()
    print(f"\n[2] constant policies evaluated: {len(rows)}; best five:")
    for mg, mx, v in rows[:5]:
        print(f"    mean {mg:.4f}  max {mx:.4f}  {v}")
    print(f"    policies beating framework mean gap ({fw_mean}): "
          f"{sum(1 for mg, _, _ in rows if mg <= fw_mean)}")

    # 3. ranking quality
    top = {1: 0, 3: 0, 5: 0}
    rr = []
    for d in per:
        ranked = sorted(d["idw_scores"], key=d["idw_scores"].get, reverse=True)
        gtm = d["ground_truth_model"]
        r = ranked.index(gtm) + 1 if gtm in ranked else None
        rr.append(1 / r if r else 0.0)
        for kk in top:
            top[kk] += bool(r and r <= kk)
    print(f"\n[3] top-1 {top[1]}/{n}, top-3 {top[3]}/{n}, top-5 {top[5]}/{n}, "
          f"MRR {sum(rr)/n:.3f}")

    # 4. confidence stratification
    conf_nz = [(d["confidence"] > 0, d["is_correct"]) for d in per]
    nz = [c for nzf, c in conf_nz if nzf]
    z0 = [c for nzf, c in conf_nz if not nzf]
    K = sum(c for _, c in conf_nz)          # total correct
    m = len(nz)                              # non-zero-confidence draws
    x = sum(nz)                              # correct among them
    pval = sum(
        math.comb(K, i) * math.comb(n - K, m - i) / math.comb(n, m)
        for i in range(x, min(K, m) + 1)
    )
    print(f"\n[4] non-zero conf: {sum(nz)}/{len(nz)} correct;  zero conf: {sum(z0)}/{len(z0)}")
    print(f"    hypergeometric one-sided p = {pval:.4f}")
    a = sum(d['is_correct'] for d in per)
    print(f"    Wilson 95% CI accuracy {a}/{n}: "
          f"[{wilson(a, n)[0]*100:.1f}%, {wilson(a, n)[1]*100:.1f}%]")
    if len(nz):
        print(f"    Wilson 95% CI non-zero-conf {sum(nz)}/{len(nz)}: "
              f"[{wilson(sum(nz), len(nz))[0]*100:.1f}%, {wilson(sum(nz), len(nz))[1]*100:.1f}%]")

    # 5. re-identification
    s1 = sum(1 for d in per
             if d["top3_neighbours"] and d["top3_neighbours"][0]["dataset"] == d["dataset"])
    s3 = sum(1 for d in per
             if any(t["dataset"] == d["dataset"] for t in d["top3_neighbours"]))
    print(f"\n[5] corpus re-identification: top-1 {s1}/{n}, top-3 {s3}/{n}")


if __name__ == "__main__":
    main()
