"""
validate_recommendations.py

Evaluates the LID toolkit's recommendation accuracy on 17 held-out evaluation
datasets by comparing Recommender.recommend_from_profile() suggestions against
ground-truth benchmark results from model_benchmarking_evaluation/.

Algorithm recap
---------------
Similarity mapping:
  1. Per-stratum Euclidean distance:  d_s(Q,H) = ||v_s(Q) - v_s(H)||_2
  2. Categorical Hamming (S6):        d_cat = |differing cat__ flags| / |all cat__ flags|
  3. Weighted composite:              D(Q,H) = sum(w_s * d_s) / sum(w_s)
  4. Similarity %:                    sim(Q,H) = (1 - D(Q,H) / max_D) * 100
  5. Top-k neighbours: sort by D ascending, take k=3

Multi-criteria recommendation:
  6. IDW vote:   IDW(m) = sum_i[inv_d_i * score_{i,m} * cf_{i,m}] / sum_i[inv_d_i]
                 where inv_d_i = 1/(D_i + 1e-9),
                       cf_{i,m} = 1 - |gap_{i,m}| / |user_langs|
  7. Recommended model:  argmax_m IDW(m)
  8. Confidence:  |{i : best_model_i == recommended}| / k

Usage
-----
    python validate_recommendations.py [options]

    --n-per-lang INT      Texts to sample per language file (default 500, 0 = all)
    --force-reprofile     Re-generate profiles even if cached versions exist
    --metric STR          Priority metric (default: f1_weighted)
    --k INT               Number of nearest neighbours (default: 3)
    --datasets STR [...]  Subset of dataset names to evaluate (default: all 17)
"""

from __future__ import annotations

import argparse
import json
import logging
import pickle
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Define paths early for logging setup
SCRIPT_DIR = Path(__file__).parent.resolve()

# Add src/ to path so lid_toolkit package can be imported from anywhere
SRC_DIR = SCRIPT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from lid_toolkit.recommender import Recommender

# Setup logging to both console and file
log_file = SCRIPT_DIR / "validation_run.log"
log_format = logging.Formatter(
    "%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)

# File handler
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info("Validation run starting — logging to %s", log_file)

# ---------------------------------------------------------------------------
# Paths (SCRIPT_DIR defined earlier for logging)
# ---------------------------------------------------------------------------
MASTERS_DIR = SCRIPT_DIR.parents[2]  # .../OneDrive/Masters/

EVAL_DATASETS_DIR = MASTERS_DIR / "LID_experiments" / "datasets" / "02_evaluation_15_cleaned"
BENCHMARK_DIR = MASTERS_DIR / "LID_experiments" / "model_benchmarking_evaluation"
MKB_PATH = SCRIPT_DIR / "mkb.pkl"
PROFILE_CACHE_DIR = SCRIPT_DIR / "eval_profiles"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
EVAL_DATASETS = [
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

DEFAULT_PRIORITY_METRIC = "f1_weighted"
DEFAULT_N_PER_LANG = 500
DEFAULT_K = 3


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_eval_texts(dataset_dir: Path, n_per_lang: int) -> pd.Series:
    """
    Load text from all parquet files in a dataset directory.

    Language labels are discarded to simulate the real user scenario where
    the corpus has no language annotations. Each file is capped at n_per_lang
    rows (or all rows when n_per_lang == 0) to balance language representation.
    """
    parquet_files = sorted(dataset_dir.glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"No parquet files found in {dataset_dir}")

    chunks: list[pd.Series] = []
    for pf in parquet_files:
        col = pd.read_parquet(pf, columns=["text"])["text"].dropna()
        if n_per_lang > 0 and len(col) > n_per_lang:
            col = col.sample(n_per_lang, random_state=42)
        chunks.append(col)

    combined = pd.concat(chunks, ignore_index=True)
    return combined.sample(frac=1, random_state=42).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Profile generation / caching
# ---------------------------------------------------------------------------

def get_or_generate_profile(
    dataset_name: str,
    eval_datasets_dir: Path,
    cache_dir: Path,
    n_per_lang: int,
    force_reprofile: bool,
) -> pd.DataFrame:
    """Return a cached language profile or generate one with DeepProfiler."""
    cache_path = cache_dir / f"{dataset_name}.pkl"

    if cache_path.exists() and not force_reprofile:
        logger.info("[%s] Loading cached profile from %s", dataset_name, cache_path.name)
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    logger.info("[%s] Generating profile (n_per_lang=%d) …", dataset_name, n_per_lang)
    text_series = load_eval_texts(eval_datasets_dir / dataset_name, n_per_lang)
    logger.info("[%s] Loaded %d text samples", dataset_name, len(text_series))

    # Import DeepProfiler (sys.path already includes parent dir)
    from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler
    profiler = DeepProfiler()
    lang_profile_df = profiler.run_profile("user", text_series=text_series)

    if lang_profile_df is None or lang_profile_df.empty:
        raise ValueError(
            f"DeepProfiler returned an empty profile for '{dataset_name}'. "
            "Check that the parquet files contain valid, non-trivial text."
        )

    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "wb") as f:
        pickle.dump(lang_profile_df, f, protocol=pickle.HIGHEST_PROTOCOL)
    logger.info("[%s] Profile cached → %s", dataset_name, cache_path.name)

    return lang_profile_df


# ---------------------------------------------------------------------------
# Ground-truth benchmark loading
# ---------------------------------------------------------------------------

def load_all_benchmarks(
    benchmark_dir: Path,
    dataset_name: str,
    metric: str,
) -> dict[str, float]:
    """
    Scan all model families / variants for a dataset and return {variant: score}.

    Directory structure expected:
        benchmark_dir/{family}/{dataset_name}/{variant}/benchmark_metadata.json

    Silently skips missing or malformed JSON files.
    """
    scores: dict[str, float] = {}
    for metadata_path in benchmark_dir.glob(f"*/{dataset_name}/*/benchmark_metadata.json"):
        variant_name = metadata_path.parent.name
        try:
            with open(metadata_path, encoding="utf-8") as f:
                data = json.load(f)
            score = data.get("metrics", {}).get(metric)
            if score is not None:
                scores[variant_name] = float(score)
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            logger.warning("Skipping %s: %s", metadata_path, exc)

    return scores


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate_results(results: list[dict]) -> dict:
    """Compute recommendation accuracy, delta distribution, and confidence calibration."""
    n = len(results)
    if n == 0:
        return {}

    correct_flags = [int(r["is_correct"]) for r in results]
    accuracy = sum(correct_flags) / n

    deltas = [r["performance_delta"] for r in results if r["performance_delta"] is not None]
    delta_stats: dict[str, float] = {}
    if deltas:
        arr = np.array(deltas, dtype=float)
        delta_stats = {
            "mean":   round(float(arr.mean()),         6),
            "std":    round(float(arr.std()),           6),
            "min":    round(float(arr.min()),           6),
            "max":    round(float(arr.max()),           6),
            "median": round(float(np.median(arr)),      6),
        }

    # Pearson r: confidence vs. correctness (calibration)
    calibration_r: Optional[float] = None
    calibration_p: Optional[float] = None
    confidences = [r["confidence"] for r in results]
    if len(set(correct_flags)) > 1 and len(set(confidences)) > 1:
        corr_matrix = np.corrcoef(confidences, correct_flags)
        calibration_r = round(float(corr_matrix[0, 1]), 4)
        # Approximate p-value via t-distribution: t = r * sqrt(n-2) / sqrt(1-r^2)
        r2 = corr_matrix[0, 1] ** 2
        if r2 < 1.0:
            from scipy.stats import t as t_dist
            t_stat = calibration_r * np.sqrt(n - 2) / np.sqrt(1.0 - r2)
            calibration_p = round(float(2 * t_dist.sf(abs(t_stat), df=n - 2)), 4)

    return {
        "recommendation_accuracy": round(accuracy, 4),
        "n_correct":               sum(correct_flags),
        "n_total":                 n,
        "performance_delta":       delta_stats,
        "confidence_calibration_r": calibration_r,
        "confidence_calibration_p": calibration_p,
    }


# ---------------------------------------------------------------------------
# Report output
# ---------------------------------------------------------------------------

def write_math_trace_report(traces: list[dict], output_path: Path) -> None:
    """Write a human-readable step-by-step math trace for all evaluated datasets."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Math Trace Report\n\n")
        f.write("Step-by-step verification of the recommendation math for each dataset.\n\n")

        for trace in traces:
            dataset = trace.get("dataset_name", "unknown")
            f.write(f"---\n\n## Dataset: `{dataset}`\n\n")
            f.write(f"**Query languages:** `{trace.get('query_iso_codes', [])}`  \n")
            f.write(f"**Priority metric:** `{trace.get('priority_metric')}` | k = {trace.get('k')}\n\n")

            # § 0: PCA pipeline
            f.write("### § 0 · PCA Pipeline\n\n")
            f.write("| Stratum | PCs retained | Per-PC variance % | Cumulative % |\n")
            f.write("|---|---|---|---|\n")
            for s, info in trace.get("pca_pipeline", {}).items():
                per_pc = ", ".join(f"{v:.1f}" for v in info["explained_variance_pct"])
                f.write(f"| {s} | {info['n_components']} | [{per_pc}] | {info['cumulative_pct']}% |\n")
            f.write(f"\n**Stratum weights (w_s):** `{trace.get('stratum_weights', {})}`\n\n")

            # §§ 1–3: Per-stratum distances for every candidate
            f.write("### §§ 1–3 · Per-Stratum Distances (all candidates)\n\n")
            for cand in trace.get("all_candidates", []):
                f.write(f"#### Candidate: `{cand['dataset']}`\n\n")
                details = cand.get("stratum_details", {})
                if details:
                    f.write("| Stratum | d_s (Euclidean) |\n|---|---|\n")
                    for s, d in details.items():
                        f.write(f"| {s} | `{d['euclidean_d']:.6f}` |\n")
                hamming = cand.get("hamming", {})
                if hamming:
                    f.write(f"| cat (Hamming) | `{hamming['d_cat']:.6f}` "
                            f"({hamming['n_differing']}/{hamming['n_cat_flags']} flags differ) |\n")
                    if hamming.get("differing_keys"):
                        f.write(f"\nDiffering categorical flags: `{hamming['differing_keys']}`\n")
                wc = cand.get("weighted_composite", {})
                if wc:
                    f.write("\n**Weighted composite D:**\n\n")
                    f.write("| Stratum | w_s | d_s | w_s × d_s |\n|---|---|---|---|\n")
                    for s, t in wc["per_stratum_terms"].items():
                        f.write(f"| {s} | {t['w']} | {t['d']:.6f} | {t['w_times_d']:.6f} |\n")
                    f.write(f"| **Total** | Σw = {wc['weight_sum']:.4f} | | "
                            f"**D = {wc['composite_D']:.6f}** |\n\n")

            # §§ 4–5: Similarity % and sorted candidate list
            max_d = trace.get("max_D", float("nan"))
            f.write(f"### §§ 4–5 · Similarity % (max_D = `{max_d:.6f}`)\n\n")
            f.write("sim% = (1 − D / max_D) × 100\n\n")
            f.write("| # | Dataset | D | sim% | In top-k? |\n|---|---|---|---|---|\n")
            k_val = trace.get("k", 3)
            for i, c in enumerate(trace.get("sorted_candidates", []), 1):
                in_topk = "← yes" if i <= k_val else ""
                f.write(f"| {i} | {c['dataset']} | `{c['D']:.6f}` | {c['sim_pct']}% | {in_topk} |\n")
            f.write("\n")

            # §§ 6–7: IDW vote
            f.write("### §§ 6–7 · IDW Vote\n\n")
            f.write("score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)\n\n")
            idw = trace.get("idw", {})
            for nb in idw.get("per_neighbour", []):
                f.write(f"**Neighbour: `{nb['dataset']}`** — inv_d = `{nb['inv_d']:.6f}`\n\n")
                f.write("| Model | metric score | gap_size | coverage_factor | contribution |\n")
                f.write("|---|---|---|---|---|\n")
                for model, m in nb["per_model"].items():
                    f.write(f"| {model} | {m['score']:.6f} | {m['gap_size']} "
                            f"| {m['coverage_factor']:.4f} | {m['contribution']:.6f} |\n")
                f.write("\n")

            f.write("**IDW aggregated scores (numerator / denominator → normalized):**\n\n")
            f.write("| Model | Σ numerator | Σ denominator | IDW score |\n|---|---|---|---|\n")
            for model in sorted(idw.get("normalized_idw_scores", {})):
                num = idw["raw_numerators"].get(model, 0)
                den = idw["denominators"].get(model, 0)
                score = idw["normalized_idw_scores"][model]
                f.write(f"| {model} | {num:.6f} | {den:.6f} | **{score:.6f}** |\n")
            f.write("\n")

            # § 8: Confidence
            conf = trace.get("confidence", {})
            f.write("### § 8 · Confidence\n\n")
            f.write(f"confidence = n_agreeing / k = "
                    f"{conf.get('n_agreeing')} / {conf.get('k')} = "
                    f"**{conf.get('confidence', 0):.2%}**\n\n")
            f.write(f"**→ Recommended model:** `{trace.get('recommended_model')}`\n\n")


def write_json_report(
    results: list[dict],
    agg: dict,
    metric: str,
    output_path: Path,
) -> None:
    report = {
        "timestamp":       datetime.now().isoformat(),
        "priority_metric": metric,
        **agg,
        "per_dataset": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    logger.info("JSON report → %s", output_path)


def write_markdown_report(
    results: list[dict],
    agg: dict,
    metric: str,
    output_path: Path,
) -> None:
    lines: list[str] = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    n_total = agg.get("n_total", 0)
    n_correct = agg.get("n_correct", 0)
    accuracy = agg.get("recommendation_accuracy", 0.0)

    lines += [
        "# LID Toolkit — Recommendation Validation Report",
        "",
        f"**Generated:** {ts}  ",
        f"**Priority metric:** `{metric}`  ",
        f"**Datasets evaluated:** {n_total}",
        "",
        "---",
        "",
        "## Aggregate Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Recommendation accuracy | **{accuracy:.1%}** ({n_correct}/{n_total} correct) |",
    ]

    ds = agg.get("performance_delta", {})
    if ds:
        lines += [
            f"| Δ `{metric}` mean   | {ds['mean']:+.4f} |",
            f"| Δ `{metric}` std    | {ds['std']:.4f} |",
            f"| Δ `{metric}` median | {ds['median']:+.4f} |",
            f"| Δ `{metric}` min    | {ds['min']:+.4f} |",
            f"| Δ `{metric}` max    | {ds['max']:+.4f} |",
        ]

    cr = agg.get("confidence_calibration_r")
    cp = agg.get("confidence_calibration_p")
    if cr is not None:
        lines.append(f"| Confidence–accuracy Pearson r | {cr:.3f} (p = {cp}) |")

    lines += [
        "",
        "---",
        "",
        "## Per-Dataset Results",
        "",
        f"| Dataset | Recommended | Ground Truth | ✓ | GT score | Rec score | Δ `{metric}` | Confidence |",
        "|---------|-------------|-------------|---|----------|-----------|------------|------------|",
    ]

    for r in results:
        tick = "✓" if r["is_correct"] else "✗"
        delta_s = f"{r['performance_delta']:+.4f}" if r["performance_delta"] is not None else "—"
        gt_s    = f"{r['ground_truth_score']:.4f}"  if r["ground_truth_score"]  is not None else "—"
        rec_s   = f"{r['recommended_score']:.4f}"   if r.get("recommended_score") is not None else "—"
        lines.append(
            f"| {r['dataset']} "
            f"| `{r['recommended_model']}` "
            f"| `{r['ground_truth_model']}` "
            f"| {tick} "
            f"| {gt_s} "
            f"| {rec_s} "
            f"| {delta_s} "
            f"| {r['confidence']:.2f} |"
        )

    # Failure mode analysis
    failures = [r for r in results if not r["is_correct"]]
    failures.sort(key=lambda r: (r["performance_delta"] or 0.0), reverse=True)

    if failures:
        lines += [
            "",
            "---",
            "",
            "## Failure Mode Analysis",
            "",
            f"Datasets where the top-1 recommendation did not match ground truth "
            f"({len(failures)}/{n_total}), sorted by performance loss:",
            "",
        ]
        for r in failures:
            delta_s = f"{r['performance_delta']:+.4f}" if r["performance_delta"] is not None else "N/A"
            rec_s   = f"{r.get('recommended_score', 'N/A'):.4f}" if r.get("recommended_score") is not None else "N/A"
            lines.append(
                f"- **{r['dataset']}**: toolkit recommended `{r['recommended_model']}` "
                f"(score {rec_s}), but ground truth was `{r['ground_truth_model']}` "
                f"(score {r['ground_truth_score']:.4f}); "
                f"performance gap = {delta_s}"
            )
            nb_strs = [
                f"{nb['dataset']} ({nb['similarity_pct']:.1f}%, best=`{nb['best_model']}`)"
                for nb in r.get("top3_neighbours", [])
            ]
            if nb_strs:
                lines.append(f"  - Neighbours: {' | '.join(nb_strs)}")

    # Confidence calibration note
    if cr is not None:
        direction = "positive" if cr > 0 else "negative"
        strength = (
            "strong"    if abs(cr) >= 0.5 else
            "moderate"  if abs(cr) >= 0.3 else
            "weak"
        )
        lines += [
            "",
            "---",
            "",
            "## Confidence Calibration",
            "",
            f"Pearson *r* between the toolkit's confidence score and prediction correctness: "
            f"**{cr:.3f}** (p = {cp}).",
            "",
            f"There is a {strength} {direction} correlation — "
            f"{'high' if cr > 0 else 'low'}-confidence recommendations are "
            f"{'more' if cr > 0 else 'less'} likely to be correct.",
        ]

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Markdown report → %s", output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate LID toolkit recommendation accuracy on held-out datasets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--n-per-lang", type=int, default=DEFAULT_N_PER_LANG,
        help="Texts to sample per language file (0 = use all rows)",
    )
    parser.add_argument(
        "--force-reprofile", action="store_true",
        help="Re-generate profiles even if cached versions exist in eval_profiles/",
    )
    parser.add_argument(
        "--metric", default=DEFAULT_PRIORITY_METRIC,
        help="Priority metric used for both recommendation and ground-truth ranking",
    )
    parser.add_argument(
        "--k", type=int, default=DEFAULT_K,
        help="Number of nearest neighbours for the Recommender",
    )
    parser.add_argument(
        "--datasets", nargs="+", default=None, metavar="DATASET",
        help="Subset of dataset names to evaluate (default: all 17)",
    )
    parser.add_argument(
        "--math-trace", action="store_true",
        help="Dump step-by-step math to debug_math_trace.md for manual verification",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    datasets_to_run = args.datasets if args.datasets else EVAL_DATASETS
    unknown = [d for d in datasets_to_run if d not in EVAL_DATASETS]
    if unknown:
        raise ValueError(
            f"Unknown dataset name(s): {unknown}\n"
            f"Valid names: {EVAL_DATASETS}"
        )

    logger.info("Loading MKBStore from %s …", MKB_PATH)
    recommender = Recommender.from_store(MKB_PATH, k=args.k)
    logger.info(
        "MKBStore loaded. %d training datasets in MKB.",
        len(recommender.store.datasets),
    )

    PROFILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    all_traces: list[dict] = []

    for idx, dataset_name in enumerate(datasets_to_run, 1):
        logger.info("─" * 60)
        logger.info("[%d/%d]  %s", idx, len(datasets_to_run), dataset_name)

        # ── Step 1: linguistic profile ────────────────────────────────────
        try:
            lang_profile_df = get_or_generate_profile(
                dataset_name=dataset_name,
                eval_datasets_dir=EVAL_DATASETS_DIR,
                cache_dir=PROFILE_CACHE_DIR,
                n_per_lang=args.n_per_lang,
                force_reprofile=args.force_reprofile,
            )
        except Exception as exc:
            logger.error("[%s] Profile generation failed: %s — skipping.", dataset_name, exc)
            continue

        logger.info(
            "[%s] Profile: %d features × %d languages  (detected: %s)",
            dataset_name, lang_profile_df.shape[0], lang_profile_df.shape[1],
            sorted(lang_profile_df.columns.tolist()),
        )

        # ── Step 2: recommendation ────────────────────────────────────────
        try:
            if args.math_trace:
                rec_result, math_trace = recommender.recommend_from_profile_traced(
                    lang_profile_df, priority_metric=args.metric
                )
                math_trace["dataset_name"] = dataset_name
                all_traces.append(math_trace)
            else:
                rec_result = recommender.recommend_from_profile(
                    lang_profile_df, priority_metric=args.metric
                )
        except Exception as exc:
            logger.error("[%s] Recommendation failed: %s — skipping.", dataset_name, exc)
            continue

        logger.info(
            "[%s] Recommendation: %-40s  confidence: %.0f%%",
            dataset_name, rec_result.recommended_model, rec_result.confidence * 100,
        )

        # ── Step 3: ground-truth benchmarks ──────────────────────────────
        benchmarks = load_all_benchmarks(BENCHMARK_DIR, dataset_name, args.metric)
        if not benchmarks:
            logger.warning("[%s] No benchmark data found — skipping.", dataset_name)
            continue

        gt_model = max(benchmarks, key=benchmarks.__getitem__)
        gt_score = benchmarks[gt_model]

        is_correct  = rec_result.recommended_model == gt_model
        rec_score   = benchmarks.get(rec_result.recommended_model)
        delta       = (gt_score - rec_score) if rec_score is not None else None

        status = "CORRECT ✓" if is_correct else f"WRONG  ✗  (GT = {gt_model})"
        delta_s = f"{delta:+.4f}" if delta is not None else "N/A"
        logger.info("[%s] %s  |  Δ = %s", dataset_name, status, delta_s)

        top3 = [
            {
                "dataset":        nb.dataset_name,
                "similarity_pct": nb.similarity_pct,
                "best_model":     nb.best_model,
                "best_score":     round(nb.best_score, 6),
            }
            for nb in rec_result.neighbours[:3]
        ]

        results.append({
            "dataset":             dataset_name,
            "recommended_model":   rec_result.recommended_model,
            "confidence":          round(rec_result.confidence, 4),
            "idw_scores":          {k: round(v, 6) for k, v in rec_result.all_model_scores.items()},
            "is_correct":          is_correct,
            "ground_truth_model":  gt_model,
            "ground_truth_score":  round(gt_score, 6),
            "recommended_score":   round(rec_score, 6) if rec_score is not None else None,
            "performance_delta":   round(delta, 6)     if delta     is not None else None,
            "all_benchmark_scores":{k: round(v, 6) for k, v in sorted(benchmarks.items())},
            "top3_neighbours":     top3,
        })

    if not results:
        logger.error("No results collected — check dataset paths and benchmark data.")
        return

    # ── Aggregate ─────────────────────────────────────────────────────────
    agg = aggregate_results(results)
    logger.info("─" * 60)
    logger.info(
        "SUMMARY: %d/%d correct  (accuracy = %.1f%%)",
        agg["n_correct"], agg["n_total"], agg["recommendation_accuracy"] * 100,
    )
    if agg.get("performance_delta"):
        ds = agg["performance_delta"]
        logger.info(
            "Δ %s:  mean=%+.4f  std=%.4f  median=%+.4f  min=%+.4f  max=%+.4f",
            args.metric, ds["mean"], ds["std"], ds["median"], ds["min"], ds["max"],
        )
    if agg.get("confidence_calibration_r") is not None:
        logger.info(
            "Confidence calibration r = %.3f (p = %s)",
            agg["confidence_calibration_r"], agg.get("confidence_calibration_p"),
        )

    # ── Reports ───────────────────────────────────────────────────────────
    write_json_report(results, agg, args.metric, SCRIPT_DIR / "validation_report.json")
    write_markdown_report(results, agg, args.metric, SCRIPT_DIR / "validation_report.md")
    if args.math_trace and all_traces:
        trace_path = SCRIPT_DIR / "debug_math_trace.md"
        write_math_trace_report(all_traces, trace_path)
        logger.info("Math trace written to %s", trace_path)
    logger.info("Done.")


if __name__ == "__main__":
    main()
