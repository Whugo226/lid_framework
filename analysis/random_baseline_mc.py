"""random_baseline_mc.py — Monte-Carlo random model selection baseline (EQ3).

Replaces the purely analytic random-selection expectation with a genuine
simulated experiment. A single "trial" is one complete random selection
policy: for each evaluation dataset, one model variant is drawn uniformly
at random from that dataset's benchmarked candidate pool, and the policy's
mean/max performance gap (ground-truth best minus drawn model, priority
metric f1_weighted) is recorded. Repeating this for T seeded trials yields
the full sampling distribution of the random policy, not just its mean.

Reported:
  - analytic expectation of the per-draw gap (should match the mean of the MC)
  - distribution of the per-trial MEAN gap (mean, sd, 2.5/50/97.5 percentiles)
  - distribution of the per-trial MAX gap
  - expected number of exact matches per trial and P(>= 3 exact matches),
    for comparison against the framework's 3/17
  - P(random trial mean gap <= framework mean gap)

Usage:
    python analysis/random_baseline_mc.py [--report PATH] [--trials 100000]
                                          [--framework-gap 0.0078] [--seed 42]

Works with any validation report that has per_dataset[].all_benchmark_scores,
.ground_truth_score and .ground_truth_model (i.e., the evaluation-split report
today, and the confirmatory validation-split report once it exists).
"""
import argparse
import json
from pathlib import Path

import numpy as np

DEFAULT_REPORT = Path(__file__).resolve().parents[1] / "validation_report.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    ap.add_argument("--trials", type=int, default=100_000)
    ap.add_argument("--framework-gap", type=float, default=0.0078,
                    help="framework mean gap to compare against")
    ap.add_argument("--framework-exact", type=int, default=3,
                    help="framework exact-match count to compare against")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    report = json.loads(args.report.read_text())
    per = report["per_dataset"] if isinstance(report, dict) else report
    if isinstance(per, dict):
        per = list(per.values())

    rng = np.random.default_rng(args.seed)

    # per-dataset candidate gap vectors and exact-match indicators
    gap_vectors, exact_vectors, names = [], [], []
    for d in per:
        scores = d["all_benchmark_scores"]
        gt_score = d["ground_truth_score"]
        gt_model = d["ground_truth_model"]
        variants = sorted(scores)
        gaps = np.array([gt_score - scores[v] for v in variants])
        exact = np.array([1.0 if v == gt_model else 0.0 for v in variants])
        gap_vectors.append(gaps)
        exact_vectors.append(exact)
        names.append(d.get("dataset", d.get("name", "?")))

    n_data = len(gap_vectors)
    pool_sizes = [len(g) for g in gap_vectors]
    analytic_mean = float(np.mean([g.mean() for g in gap_vectors]))
    analytic_exact = float(np.sum([e.mean() for e in exact_vectors]))

    # Monte Carlo: draws[t, i] = index drawn for dataset i in trial t
    trial_gaps = np.empty((args.trials, n_data))
    trial_exact = np.empty((args.trials, n_data))
    for i, (gaps, exact) in enumerate(zip(gap_vectors, exact_vectors)):
        idx = rng.integers(0, len(gaps), size=args.trials)
        trial_gaps[:, i] = gaps[idx]
        trial_exact[:, i] = exact[idx]

    mean_gap = trial_gaps.mean(axis=1)          # per-trial policy mean gap
    max_gap = trial_gaps.max(axis=1)            # per-trial policy worst case
    exact_count = trial_exact.sum(axis=1)       # per-trial exact matches

    pct = lambda a, q: float(np.percentile(a, q))
    out = {
        "report": str(args.report),
        "n_datasets": n_data,
        "candidate_pool_sizes": sorted(set(pool_sizes)),
        "trials": args.trials,
        "seed": args.seed,
        "analytic_expected_gap": analytic_mean,
        "mc_mean_gap": {
            "mean": float(mean_gap.mean()), "sd": float(mean_gap.std(ddof=1)),
            "p2.5": pct(mean_gap, 2.5), "median": pct(mean_gap, 50),
            "p97.5": pct(mean_gap, 97.5), "min": float(mean_gap.min()),
        },
        "mc_max_gap": {
            "mean": float(max_gap.mean()),
            "p2.5": pct(max_gap, 2.5), "median": pct(max_gap, 50),
            "p97.5": pct(max_gap, 97.5),
        },
        "exact_matches": {
            "analytic_expected": analytic_exact,
            "mc_mean": float(exact_count.mean()),
            "p_at_least_framework": float((exact_count >= args.framework_exact).mean()),
            "framework_exact": args.framework_exact,
        },
        "p_trial_mean_leq_framework": float((mean_gap <= args.framework_gap).mean()),
        "framework_mean_gap": args.framework_gap,
    }

    out_path = args.report.parent / "random_baseline_mc_results.json"
    out_path.write_text(json.dumps(out, indent=2))

    print(f"datasets = {n_data}, pool sizes = {sorted(set(pool_sizes))}, "
          f"trials = {args.trials}, seed = {args.seed}")
    print(f"\nanalytic expected per-draw gap : {analytic_mean:.4f}")
    print(f"MC per-trial MEAN gap          : {mean_gap.mean():.4f} "
          f"(sd {mean_gap.std(ddof=1):.4f}; 95% [{pct(mean_gap,2.5):.4f}, "
          f"{pct(mean_gap,97.5):.4f}]; min over {args.trials} trials "
          f"{mean_gap.min():.4f})")
    print(f"MC per-trial MAX gap           : median {pct(max_gap,50):.4f} "
          f"(95% [{pct(max_gap,2.5):.4f}, {pct(max_gap,97.5):.4f}])")
    print(f"exact matches per trial        : mean {exact_count.mean():.3f} "
          f"(analytic {analytic_exact:.3f}); "
          f"P(>= {args.framework_exact}) = "
          f"{(exact_count >= args.framework_exact).mean():.2e}")
    print(f"P(trial mean <= framework {args.framework_gap}) = "
          f"{(mean_gap <= args.framework_gap).mean():.2e}")
    print(f"\nsaved -> {out_path}")


if __name__ == "__main__":
    main()
