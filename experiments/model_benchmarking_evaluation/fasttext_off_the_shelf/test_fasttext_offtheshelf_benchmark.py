#!/usr/bin/env python3
"""
test_fasttext_offtheshelf_benchmark.py

Production-grade benchmark evaluation suite for the FastText pre-trained
Language Identification model (lid.176.bin).

Loads the off-the-shelf FastText LID model from off_the_shelf_models/fasttext/
and evaluates it on the held-out benchmark data in
datasets/02_evaluation_15_cleaned/.

Unlike the MNB benchmark, there is a single model (no training variants).
The outer loop iterates over all dataset subdirectories in benchmark_data_dir.

Metrics reported per dataset:
  Classification quality  — accuracy, macro F1, macro precision, macro recall
  Inference performance   — total wall-clock time, ms/sample, samples/sec

Usage (local):
    python test_fasttext_offtheshelf_benchmark.py

Usage (HPC — override paths via environment variables):
    LID_MODEL_PATH=/scratch/models/lid.176.bin LID_BENCH_DIR=/scratch/data \\
    LID_OUTPUT_DIR=/scratch/out python test_fasttext_offtheshelf_benchmark.py

Results are logged to MLflow if available, otherwise written as local
JSON/txt fallbacks (benchmark_metadata.json, benchmark_report.txt).
"""

# ─────────────────────────────────────────────────────────────────────────────
# Standard library
# ─────────────────────────────────────────────────────────────────────────────
import json
import logging
import os
import sys
import time
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Third-party
# ─────────────────────────────────────────────────────────────────────────────
import fasttext
import pandas as pd
import pyarrow.parquet as pq
import yaml
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)

# ─────────────────────────────────────────────────────────────────────────────
# Optional MLflow (not installed in thesis_final env by default)
# ─────────────────────────────────────────────────────────────────────────────
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# 1. Constants
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR: Path = Path(__file__).resolve().parent
CONFIG_PATH: Path = SCRIPT_DIR / "config_test.yaml"

TEXT_COL: str = "text"
LANG_COL: str = "lang"

TARGET_LANGS: frozenset = frozenset({
    "ca", "da", "de", "el", "en", "es", "fi", "fr", "hr", "it",
    "ja", "ko", "lt", "mk", "nb", "nl", "pl", "pt", "ro", "ru",
    "sl", "sv", "uk", "zh",
})


# ─────────────────────────────────────────────────────────────────────────────
# 2. Config Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: Path) -> dict:
    """
    Load config_test.yaml and apply environment variable overrides.

    Override hierarchy (highest to lowest priority):
      1. Environment variables: LID_MODEL_PATH, LID_BENCH_DIR, LID_OUTPUT_DIR,
         MLFLOW_TRACKING_URI
      2. config_test.yaml values

    All path strings are resolved to absolute Path objects relative to the
    repository root (SCRIPT_DIR.parent.parent), so the script can be invoked
    from any working directory — essential for PBS batch jobs.
    """
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    # Environment variable overrides
    if "LID_MODEL_PATH" in os.environ:
        cfg["paths"]["model_path"] = os.environ["LID_MODEL_PATH"]
    if "LID_BENCH_DIR" in os.environ:
        cfg["paths"]["benchmark_data_dir"] = os.environ["LID_BENCH_DIR"]
    if "LID_OUTPUT_DIR" in os.environ:
        cfg["paths"]["output_dir"] = os.environ["LID_OUTPUT_DIR"]
    if "MLFLOW_TRACKING_URI" in os.environ:
        cfg["paths"]["mlflow_tracking_uri"] = os.environ["MLFLOW_TRACKING_URI"]

    # Resolve relative paths against the repo root
    repo_root = SCRIPT_DIR.parent.parent
    for key in ("model_path", "benchmark_data_dir", "output_dir", "mlflow_tracking_uri"):
        p = Path(cfg["paths"][key])
        cfg["paths"][key] = p if p.is_absolute() else repo_root / p

    # Load dataset list from config (or empty list if not present)
    cfg["datasets"] = cfg.get("datasets", [])

    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# 3. Logging Setup
# ─────────────────────────────────────────────────────────────────────────────

def setup_logging(
    output_dir: Path,
    log_filename: str,
    level_str: str,
) -> logging.Logger:
    """
    Configure a logger with both FileHandler and StreamHandler.

    StreamHandler writes to sys.stdout so PBS captures it in the .out
    file rather than .err. output_dir is created here — the only mkdir
    call in the entire script.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / log_filename

    level = getattr(logging, level_str.upper(), logging.INFO)
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger("fasttext_ots_benchmark")
    logger.setLevel(level)
    logger.handlers.clear()  # prevent duplicate handlers on notebook re-runs

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    logger.info("Logging initialised. Log file: %s", log_path)
    return logger


# ─────────────────────────────────────────────────────────────────────────────
# 4. Benchmark Data Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_benchmark_data(
    data_dir: Path,
    logger: logging.Logger,
) -> pd.DataFrame:
    """
    Load all parquet files from data_dir and return a validated DataFrame.

    No per-language sampling cap is applied — all benchmark rows are used
    to maximise statistical validity of the results.

    Memory strategy — two-phase load:

    Phase 1 (metadata scan):
      pq.read_metadata() reads only the parquet footer (no row data).
      This builds a per-language index of (filepath, row_count) pairs
      without touching the actual text.

    Phase 2 (selective loading):
      Files are read per language with pq.read_table(columns=[...]) which
      performs column-level I/O — only the two needed columns are
      deserialised.

    Args:
        data_dir: Root of the cleaned benchmark data directory for one dataset.
        logger:   Logger instance.

    Returns:
        DataFrame with columns [TEXT_COL, LANG_COL], validated.
    """
    parquet_files = sorted(data_dir.rglob("*.parquet"))
    logger.info("Discovered %d parquet files under %s", len(parquet_files), data_dir)

    # ── Phase 1: metadata scan ────────────────────────────────────────────────
    lang_file_index: dict[str, list[tuple[Path, int]]] = {}
    for fp in parquet_files:
        try:
            meta = pq.read_metadata(fp)
            lang = fp.stem.split("_")[0]
            if lang not in TARGET_LANGS:
                continue
            lang_file_index.setdefault(lang, []).append((fp, meta.num_rows))
        except Exception as exc:
            logger.warning("Could not read metadata for %s: %s", fp, exc)

    pre_counts = {lang: sum(n for _, n in files) for lang, files in lang_file_index.items()}
    logger.info("─" * 70)
    logger.info("Benchmark row counts per language:")
    for lang in sorted(pre_counts):
        logger.info("  %-4s : %10d", lang, pre_counts[lang])
    logger.info("  TOTAL: %10d", sum(pre_counts.values()))
    logger.info("─" * 70)

    # ── Phase 2: full load ────────────────────────────────────────────────────
    chunks: list[pd.DataFrame] = []
    for lang in sorted(lang_file_index):
        for fp, _ in lang_file_index[lang]:
            try:
                table = pq.read_table(fp, columns=[TEXT_COL, LANG_COL])
                df_chunk = table.to_pandas()
            except Exception as exc:
                logger.warning("Failed to read %s: %s", fp, exc)
                continue
            # Guard against cross-language contamination within a file
            df_chunk = df_chunk[df_chunk[LANG_COL] == lang]
            chunks.append(df_chunk)

    if not chunks:
        raise RuntimeError(
            f"No data loaded from {data_dir}. "
            "Verify the directory contains valid .parquet files."
        )

    df = pd.concat(chunks, ignore_index=True)

    # ── Validation ────────────────────────────────────────────────────────────
    initial_len = len(df)
    df = df.dropna(subset=[TEXT_COL, LANG_COL])
    df = df[df[TEXT_COL].str.strip().str.len() > 0]
    df = df[df[LANG_COL].isin(TARGET_LANGS)]
    dropped = initial_len - len(df)
    if dropped > 0:
        logger.warning("Validation dropped %d invalid rows", dropped)

    logger.info("Loaded %d benchmark samples from %s", len(df), data_dir.name)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 5. Model Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_fasttext_model(
    model_path: Path,
    logger: logging.Logger,
) -> fasttext.FastText._FastText:
    """
    Load the pre-trained FastText LID model from disk.

    Args:
        model_path: Absolute path to lid.176.bin.
        logger:     Logger instance.

    Returns:
        Loaded FastText model ready for inference.

    Raises:
        RuntimeError if the file cannot be loaded.
    """
    try:
        model = fasttext.load_model(str(model_path))
        logger.info("Loaded FastText model from %s", model_path)
        return model
    except Exception as exc:
        raise RuntimeError(f"Failed to load FastText model from {model_path}: {exc}") from exc


# ─────────────────────────────────────────────────────────────────────────────
# 6. Benchmark Inference & Metrics
# ─────────────────────────────────────────────────────────────────────────────

def run_benchmark(
    model: fasttext.FastText._FastText,
    X: list[str],
    y_true: list[str],
    label_names: list[str],
    logger: logging.Logger,
) -> tuple[dict[str, float], str]:
    """
    Run inference on the benchmark set and compute quality + performance metrics.

    Cleaning: " ".join(t.split()) is applied to every sample before inference
    to collapse newlines and multi-spaces, which would otherwise cause
    FastText's predict() to raise a ValueError (it processes one line at a time
    internally when given a list).

    Batched inference uses FastText's native list-based model.predict(texts, k=1)
    for maximum throughput — a single C++ call over the full corpus.

    Timing covers the full model.predict() call, reflecting real-world
    end-to-end latency as seen by a caller.

    Metrics:
      accuracy                     — overall fraction correct
      f1_macro                     — unweighted mean F1 across all classes
      precision_macro              — unweighted mean precision across all classes
      recall_macro                 — unweighted mean recall across all classes
      inference_time_total_s       — wall-clock seconds for the full benchmark set
      inference_time_ms_per_sample — average milliseconds per text sample
      throughput_samples_per_sec   — total samples divided by total time

    Args:
        model:       Loaded FastText model.
        X:           List of text strings to classify.
        y_true:      Ground-truth language labels.
        label_names: Sorted list of expected label names for the report.
        logger:      Logger instance.

    Returns:
        (metrics_dict, classification_report_str)
    """
    n = len(X)

    # Clean: collapse whitespace / newlines to prevent FastText ValueError
    X_clean = [" ".join(t.split()) for t in X]

    t0 = time.perf_counter()
    labels, _ = model.predict(X_clean, k=1)
    inference_time_s = time.perf_counter() - t0

    # Strip "__label__" prefix from FastText output
    y_pred = [lbl[0].replace("__label__", "") for lbl in labels]

    metrics: dict[str, float] = {
        "accuracy":                     round(accuracy_score(y_true, y_pred), 6),
        "f1_macro":                     round(f1_score(y_true, y_pred, average="macro", zero_division=0), 6),
        "f1_weighted":                  round(f1_score(y_true, y_pred, average="weighted", zero_division=0), 6),
        "precision_macro":              round(precision_score(y_true, y_pred, average="macro", zero_division=0), 6),
        "precision_weighted":           round(precision_score(y_true, y_pred, average="weighted", zero_division=0), 6),
        "recall_macro":                 round(recall_score(y_true, y_pred, average="macro", zero_division=0), 6),
        "recall_weighted":              round(recall_score(y_true, y_pred, average="weighted", zero_division=0), 6),
        "inference_time_total_s":       round(inference_time_s, 4),
        "inference_time_ms_per_sample": round(inference_time_s / n * 1000, 6),
        "throughput_samples_per_sec":   round(n / inference_time_s, 2),
        "n_samples":                    n,
    }

    report_str = classification_report(
        y_true, y_pred,
        labels=label_names,
        target_names=label_names,
        zero_division=0,
    )

    logger.info("─" * 70)
    logger.info("Benchmark results  (n=%d samples):", n)
    for name, val in metrics.items():
        logger.info("  %-35s : %s", name, val)
    logger.info("\n%s", report_str)

    return metrics, report_str


# ─────────────────────────────────────────────────────────────────────────────
# 7. Artifact Saving
# ─────────────────────────────────────────────────────────────────────────────

def save_benchmark_artifacts(
    dataset_name: str,
    model_name: str,
    metrics: dict[str, float],
    report_str: str,
    output_dir: Path,
    logger: logging.Logger,
) -> dict[str, Path]:
    """
    Persist benchmark results for one dataset / model combination.

    Directory layout:
        output_dir/<dataset_name>/<model_name>/
            benchmark_metadata.json   metrics dict + provenance info
            benchmark_report.txt      per-language classification report

    Args:
        dataset_name: Name of the source dataset (e.g. "wikipedia").
        model_name:   Model identifier (e.g. "lid.176").
        metrics:      Dict of metric name → value from run_benchmark().
        report_str:   Classification report string from run_benchmark().
        output_dir:   Root output directory (model_benchmarking_evaluation/fasttext_off_the_shelf/).
        logger:       Logger instance.

    Returns:
        Dict of artifact_name → Path for use by log_to_mlflow().
    """
    run_dir = output_dir / dataset_name / model_name
    run_dir.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, Path] = {}

    # benchmark_metadata.json
    meta = {
        "dataset": dataset_name,
        "model":   model_name,
        "metrics": metrics,
    }
    meta_path = run_dir / "benchmark_metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Saved metadata : %s", meta_path)
    artifacts["benchmark_metadata"] = meta_path

    # benchmark_report.txt
    report_path = run_dir / "benchmark_report.txt"
    report_path.write_text(report_str, encoding="utf-8")
    logger.info("Saved report   : %s", report_path)
    artifacts["benchmark_report"] = report_path

    return artifacts


# ─────────────────────────────────────────────────────────────────────────────
# 8. MLflow Logging
# ─────────────────────────────────────────────────────────────────────────────

def log_to_mlflow(
    cfg: dict,
    dataset_name: str,
    model_name: str,
    metrics: dict[str, float],
    artifacts: dict[str, Path],
    logger: logging.Logger,
) -> None:
    """
    Log a complete benchmark run to MLflow (only called when MLFLOW_AVAILABLE).

    Structure:
        Experiment: cfg["mlflow"]["experiment_name"]
          Run: "{dataset_name}__{model_name}"
            Tags:    dataset, model, benchmark_data_version
            Metrics: accuracy, f1_macro, precision_macro, recall_macro,
                     inference_time_total_s, inference_time_ms_per_sample,
                     throughput_samples_per_sec, n_samples
            Artifacts: benchmark_metadata.json, benchmark_report.txt

    mlflow.set_experiment() auto-creates the experiment if it does not exist.
    """
    mlflow.set_tracking_uri(str(cfg["paths"]["mlflow_tracking_uri"]))
    mlflow.set_experiment(cfg["mlflow"]["experiment_name"])

    run_name = f"{dataset_name}__{model_name}"

    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags({
            "dataset":                dataset_name,
            "model":                  model_name,
            "benchmark_data_version": cfg["mlflow"]["benchmark_data_version"],
        })
        # n_samples is int — log separately to keep metrics dict float-only
        mlflow.log_metrics({k: v for k, v in metrics.items() if k != "n_samples"})
        mlflow.log_metric("n_samples", metrics["n_samples"])
        mlflow.log_artifact(str(artifacts["benchmark_metadata"]))
        mlflow.log_artifact(str(artifacts["benchmark_report"]))

        logger.info(
            "MLflow logged: experiment=%s  run=%s",
            cfg["mlflow"]["experiment_name"], run_name,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 9. Main Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    End-to-end benchmark pipeline — iterates over all dataset subdirectories.

    Execution order:
      1.  Load config (with env var overrides)
      2.  Setup logging → output_dir/benchmark.log
      3.  Log environment info
      4.  Load FastText model once (single model, used across all datasets)
      5.  Discover dataset directories: iterate all subdirs of benchmark_data_dir
      6.  For each dataset:
            a. Load all benchmark data (no sampling cap)
            b. Run inference + compute metrics
            c. Save artifacts to output_dir/<dataset>/<model_name>/
            d. Log to MLflow (if available) or rely on local JSON fallback
            e. Append row to results_summary
      7.  Print cross-dataset summary table
    """
    # ── 1. Config ─────────────────────────────────────────────────────────────
    cfg = load_config(CONFIG_PATH)
    model_path: Path = Path(cfg["paths"]["model_path"])
    benchmark_data_dir: Path = Path(cfg["paths"]["benchmark_data_dir"])
    output_dir: Path = Path(cfg["paths"]["output_dir"])
    model_name: str = model_path.stem  # e.g. "lid.176"

    # ── 2. Logging ────────────────────────────────────────────────────────────
    logger = setup_logging(
        output_dir=output_dir,
        log_filename=cfg["logging"]["log_filename"],
        level_str=cfg["logging"]["level"],
    )

    # ── 3. Environment info ───────────────────────────────────────────────────
    logger.info("Python         : %s", sys.version.split()[0])
    try:
    # fasttext doesn't always have __version__, this is safer
        import pkg_resources
        ft_version = pkg_resources.get_distribution("fasttext-wheel").version
    except:
        ft_version = "unknown"
    logger.info("fasttext    : %s", ft_version)
    logger.info("MLflow         : %s", mlflow.__version__ if MLFLOW_AVAILABLE else "not installed")
    logger.info("Config         : %s", CONFIG_PATH)
    logger.info("Model path     : %s", model_path)
    logger.info("Model name     : %s", model_name)
    logger.info("Benchmark dir  : %s", benchmark_data_dir)
    logger.info("Output dir     : %s", output_dir)

    # ── 4. Load FastText model once ───────────────────────────────────────────
    model = load_fasttext_model(model_path, logger)

    # ── 5. Discover dataset directories ──────────────────────────────────────
    all_dirs = sorted([d for d in benchmark_data_dir.iterdir() if d.is_dir()])
    target_datasets = set(cfg["datasets"])
    for d in all_dirs:
        if d.name not in target_datasets:
            logger.info("Skipping %s: Not in target dataset list", d.name)
    dataset_dirs: list[Path] = [d for d in all_dirs if d.name in target_datasets]

    logger.info("Found %d target dataset directories:", len(dataset_dirs))
    for d in dataset_dirs:
        logger.info("  %s", d.name)

    label_names: list[str] = sorted(TARGET_LANGS)
    results_summary: list[dict] = []

    # ── 6. Dataset loop ───────────────────────────────────────────────────────
    for bench_dir in dataset_dirs:
        dataset_name = bench_dir.name

        sep = "█" * 70
        logger.info("\n%s\n  DATASET : %s\n%s", sep, dataset_name, sep)

        # 6a. Load benchmark data — skip if no valid parquet files found
        try:
            df = load_benchmark_data(data_dir=bench_dir, logger=logger)
        except RuntimeError as exc:
            logger.warning("Skipping dataset %s — %s", dataset_name, exc)
            continue

        X: list[str] = df[TEXT_COL].tolist()
        y: list[str] = df[LANG_COL].tolist()

        # 6b. Run inference and compute metrics
        metrics, report_str = run_benchmark(
            model=model,
            X=X,
            y_true=y,
            label_names=label_names,
            logger=logger,
        )

        # 6c. Save artifacts
        artifacts = save_benchmark_artifacts(
            dataset_name=dataset_name,
            model_name=model_name,
            metrics=metrics,
            report_str=report_str,
            output_dir=output_dir,
            logger=logger,
        )

        # 6d. MLflow (or local JSON fallback already written by save_benchmark_artifacts)
        if MLFLOW_AVAILABLE:
            try:
                log_to_mlflow(
                    cfg=cfg,
                    dataset_name=dataset_name,
                    model_name=model_name,
                    metrics=metrics,
                    artifacts=artifacts,
                    logger=logger,
                )
            except Exception as exc:
                logger.warning(
                    "MLflow logging failed for %s (run continues): %s",
                    dataset_name, exc,
                )
        else:
            logger.info(
                "MLflow not available — metadata written to: %s",
                artifacts["benchmark_metadata"],
            )

        results_summary.append({
            "dataset": dataset_name,
            "model":   model_name,
            **metrics,
        })

    # ── 7. Cross-dataset summary ──────────────────────────────────────────────
    sep = "█" * 70
    logger.info("\n%s\n  CROSS-DATASET BENCHMARK SUMMARY\n%s", sep, sep)
    header = (
        f"  {'Dataset':<38}  {'Model':<12}  {'Acc':>8}"
        f"  {'F1':>8}  {'ms/sample':>12}  {'samples/s':>12}"
    )
    logger.info(header)
    logger.info("  %s", "-" * (len(header) - 2))
    for row in results_summary:
        logger.info(
            "  %-38s  %-12s  %8.4f  %8.4f  %12.4f  %12.2f",
            row["dataset"],
            row["model"],
            row["accuracy"],
            row["f1_macro"],
            row["inference_time_ms_per_sample"],
            row["throughput_samples_per_sec"],
        )
    logger.info(
        "Benchmark complete. %d dataset runs.",
        len(results_summary),
    )


if __name__ == "__main__":
    main()
