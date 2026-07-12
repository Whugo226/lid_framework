"""
validate_recommendations_validation.py — ONE-SHOT confirmatory run on the
reserved validation splits (03_validation_15_cleaned).

FROZEN PROTOCOL — mirrors the recorded evaluation run exactly:
  - priority metric : f1_weighted
  - neighbourhood   : k = 3, inverse-distance-weighted voting
  - recommender call: recommend_from_profile(profile) with NO user_iso_codes
                      (coverage guard inactive, as in the recorded run)
  - sampling        : 500 texts per language file, seed 42
  - MKB             : mkb.pkl (17-dataset portfolio, librispeech excluded)

This script is intentionally a standalone copy of the evaluation runner
(validate_recommendations.py): importing that module would truncate its
recorded log file (mode="w" handler at import time), and the confirmatory
protocol must not drift with future edits to the evaluation runner.

Prerequisites (run on the HPC first, then sync back):
  1. model_benchmarking_validation/submit_cross_benchmark_validation.sh
  2. model_benchmarking_validation/submit_xlm_v_validation.sh

Then run this locally:
    python validate_recommendations_validation.py

Outputs (distinct from the evaluation artifacts, which are never overwritten):
    validation_confirmatory_report.json / .md
    validation_profiles/<dataset>.pkl   (profile cache)
    validation_confirmatory_run.log
"""

from __future__ import annotations

import argparse
import json
import logging
import pickle
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR / "src"))

from lid_toolkit.recommender import Recommender

log_file = SCRIPT_DIR / "validation_confirmatory_run.log"
log_format = logging.Formatter(
    "%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("confirmatory")
logger.setLevel(logging.INFO)
for handler in (logging.StreamHandler(), logging.FileHandler(log_file, mode="w", encoding="utf-8")):
    handler.setLevel(logging.INFO)
    handler.setFormatter(log_format)
    logger.addHandler(handler)

# ---------------------------------------------------------------------------
# Frozen paths and protocol constants — do not expose as CLI flags
# ---------------------------------------------------------------------------
MASTERS_DIR = SCRIPT_DIR.parents[2]
VAL_DATASETS_DIR = MASTERS_DIR / "LID_experiments" / "datasets" / "03_validation_15_cleaned"
BENCHMARK_DIR = MASTERS_DIR / "LID_experiments" / "model_benchmarking_validation"
MKB_PATH = SCRIPT_DIR / "mkb.pkl"
PROFILE_CACHE_DIR = SCRIPT_DIR / "validation_profiles"

VAL_DATASETS = [
    "OpenLID-v2",
    "amazon_reviews_multi",
    "europarl",
    "exorde-social-media-december-2024-week1",
    "flores_plus",
    "language-identification",
    "massive",
    "mmarco",
    "multi_eurlex",
    "multilingual_cc_news",
    "multilingual_toxicity_dataset",
    "stsb_multi_mt",
    "tweet_sentiment_multilingual",
    "tydiqa",
    "wikipedia",
    "xlsum",
    "xnli",
]

PRIORITY_METRIC = "f1_weighted"
K = 3
N_PER_LANG = 500
SEED = 42


def load_val_texts(dataset_dir: Path) -> pd.Series:
    parquet_files = sorted(dataset_dir.glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"No parquet files found in {dataset_dir}")
    chunks: list[pd.Series] = []
    for pf in parquet_files:
        col = pd.read_parquet(pf, columns=["text"])["text"].dropna()
        if len(col) > N_PER_LANG:
            col = col.sample(N_PER_LANG, random_state=SEED)
        chunks.append(col)
    combined = pd.concat(chunks, ignore_index=True)
    return combined.sample(frac=1, random_state=SEED).reset_index(drop=True)


def get_or_generate_profile(dataset_name: str, force: bool) -> pd.DataFrame:
    cache_path = PROFILE_CACHE_DIR / f"{dataset_name}.pkl"
    if cache_path.exists() and not force:
        logger.info("[%s] Loading cached profile", dataset_name)
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    logger.info("[%s] Generating profile (n_per_lang=%d) …", dataset_name, N_PER_LANG)
    text_series = load_val_texts(VAL_DATASETS_DIR / dataset_name)
    from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler
    profiler = DeepProfiler()
    profile = profiler.run_profile("user", text_series=text_series)
    if profile is None or profile.empty:
        raise ValueError(f"Empty profile for '{dataset_name}'")

    PROFILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "wb") as f:
        pickle.dump(profile, f, protocol=pickle.HIGHEST_PROTOCOL)
    return profile


def load_all_benchmarks(dataset_name: str) -> dict[str, float]:
    scores: dict[str, float] = {}
    for metadata_path in BENCHMARK_DIR.glob(f"*/{dataset_name}/*/benchmark_metadata.json"):
        variant = metadata_path.parent.name
        try:
            data = json.loads(metadata_path.read_text(encoding="utf-8"))
            score = data.get("metrics", {}).get(PRIORITY_METRIC)
            if score is not None:
                scores[variant] = float(score)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Skipping %s: %s", metadata_path, exc)
    return scores


def preflight() -> bool:
    """Fail early if the validation-side cross-benchmark is not in place."""
    ok = True
    if not VAL_DATASETS_DIR.exists():
        logger.error("Validation data dir missing: %s", VAL_DATASETS_DIR)
        ok = False
    missing = [d for d in VAL_DATASETS
               if not any(BENCHMARK_DIR.glob(f"*/{d}/*/benchmark_metadata.json"))]
    if missing:
        logger.error(
            "No benchmark metadata under %s for: %s — run the HPC jobs in "
            "model_benchmarking_validation/ first and sync the results back.",
            BENCHMARK_DIR, missing,
        )
        ok = False
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force-reprofile", action="store_true")
    args = ap.parse_args()

    if not preflight():
        sys.exit(1)

    out_json = SCRIPT_DIR / "validation_confirmatory_report.json"
    if out_json.exists():
        logger.error(
            "%s already exists. This is a ONE-SHOT confirmatory run — delete "
            "the file manually only if the previous run was invalid.", out_json.name,
        )
        sys.exit(1)

    logger.info("Loading MKBStore from %s …", MKB_PATH)
    recommender = Recommender.from_store(MKB_PATH, k=K)
    logger.info("MKB loaded: %d datasets.", len(recommender.store.datasets))

    results: list[dict] = []
    for idx, dataset_name in enumerate(VAL_DATASETS, 1):
        logger.info("─" * 60)
        logger.info("[%d/%d]  %s", idx, len(VAL_DATASETS), dataset_name)

        profile = get_or_generate_profile(dataset_name, args.force_reprofile)
        rec = recommender.recommend_from_profile(profile, priority_metric=PRIORITY_METRIC)

        benchmarks = load_all_benchmarks(dataset_name)
        gt_model = max(benchmarks, key=benchmarks.__getitem__)
        gt_score = benchmarks[gt_model]

        # OTS variants carry per-dataset suffixes in the benchmark dirs
        rec_key = rec.recommended_model
        if rec_key not in benchmarks:
            base = rec_key.rsplit("_", 1)[0]
            fallback = f"{base}_{dataset_name}"
            if fallback in benchmarks:
                rec_key = fallback

        rec_score = benchmarks.get(rec_key)
        delta = (gt_score - rec_score) if rec_score is not None else None
        is_correct = rec_key == gt_model

        logger.info("[%s] rec=%s  conf=%.2f  %s  Δ=%s",
                    dataset_name, rec.recommended_model, rec.confidence,
                    "CORRECT" if is_correct else f"wrong (GT={gt_model})",
                    f"{delta:+.4f}" if delta is not None else "n/a")

        results.append({
            "dataset": dataset_name,
            "recommended_model": rec.recommended_model,
            "confidence": round(rec.confidence, 4),
            "idw_scores": {k: round(v, 6) for k, v in rec.all_model_scores.items()},
            "is_correct": is_correct,
            "ground_truth_model": gt_model,
            "ground_truth_score": round(gt_score, 6),
            "recommended_score": round(rec_score, 6) if rec_score is not None else None,
            "performance_delta": round(delta, 6) if delta is not None else None,
            "all_benchmark_scores": {k: round(v, 6) for k, v in sorted(benchmarks.items())},
            "top3_neighbours": [
                {"dataset": nb.dataset_name, "similarity_pct": nb.similarity_pct,
                 "best_model": nb.best_model, "best_score": round(nb.best_score, 6)}
                for nb in rec.neighbours[:3]
            ],
        })

    n = len(results)
    correct = sum(r["is_correct"] for r in results)
    deltas = np.array([r["performance_delta"] for r in results
                       if r["performance_delta"] is not None])
    nonzero = [r for r in results if r["confidence"] > 0]
    zero = [r for r in results if r["confidence"] == 0]

    report = {
        "timestamp": datetime.now().isoformat(),
        "protocol": {
            "priority_metric": PRIORITY_METRIC, "k": K,
            "n_per_lang": N_PER_LANG, "seed": SEED,
            "coverage_guard": "inactive (no user_iso_codes; mirrors recorded evaluation run)",
            "mkb": str(MKB_PATH), "splits": "03_validation_15_cleaned",
            "frozen": "protocol fixed before ground-truth inspection; single run",
        },
        "recommendation_accuracy": round(correct / n, 4) if n else None,
        "n_correct": correct,
        "n_total": n,
        "performance_delta": {
            "mean": round(float(deltas.mean()), 6),
            "std": round(float(deltas.std()), 6),
            "median": round(float(np.median(deltas)), 6),
            "min": round(float(deltas.min()), 6),
            "max": round(float(deltas.max()), 6),
        } if len(deltas) else {},
        "confidence_stratified": {
            "nonzero_conf_correct": sum(r["is_correct"] for r in nonzero),
            "nonzero_conf_total": len(nonzero),
            "zero_conf_correct": sum(r["is_correct"] for r in zero),
            "zero_conf_total": len(zero),
        },
        "per_dataset": results,
    }
    out_json.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    logger.info("─" * 60)
    logger.info("CONFIRMATORY SUMMARY: %d/%d correct; mean Δ=%.4f; max Δ=%.4f",
                correct, n, deltas.mean(), deltas.max())
    logger.info("JSON report → %s", out_json)


if __name__ == "__main__":
    main()
