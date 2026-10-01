#!/usr/bin/env python3
"""
test_cld3_benchmark.py

Production-grade benchmark evaluation suite for Google's CLD3
(Compact Language Detector v3) Language Identification model.

Uses the gcld3 Python bindings (NNetLanguageIdentifier) — a pre-trained
neural network bundled in the package; no external model files are loaded.
Evaluates the model on the held-out benchmark data in
datasets/02_evaluation_15_cleaned/.

Unlike MNB/FastText, there is a single model with no training variants.
The outer loop iterates over all dataset subdirectories in benchmark_data_dir.

CLD3 outputs BCP-47 language codes. A mapping dictionary (CLD3_LABEL_MAP)
aligns any non-matching codes (e.g. 'zh-Hans' → 'zh', 'no' → 'nb') to our
dataset's ISO 639-1 labels. Predictions that cannot be mapped are recorded
as "unsupported" rather than causing the script to crash.

Metrics reported per dataset:
  Classification quality  — accuracy, macro F1, macro precision, macro recall
  Inference performance   — total wall-clock time, ms/sample, samples/sec

Usage (local):
    python test_cld3_benchmark.py

Usage (HPC — override paths via environment variables):
    LID_BENCH_DIR=/scratch/data LID_OUTPUT_DIR=/scratch/out \\
    python test_cld3_benchmark.py

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
import gcld3
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

# Hard-coded model identifier — CLD3 is bundled in the gcld3 package,
# no external file is loaded.
MODEL_NAME: str = "cld3"

TARGET_LANGS: frozenset = frozenset({
    "ca", "da", "de", "el", "en", "es", "fi", "fr", "hr", "it",
    "ja", "ko", "lt", "mk", "nb", "nl", "pl", "pt", "ro", "ru",
    "sl", "sv", "uk", "zh",
})


# BCP-47 → dataset ISO 639-1 label mapping.
# CLD3 can emit BCP-47 script or region subtags that differ from the plain
# two-letter codes used in our parquet files. Map known cases here; anything
# not in this dict is used verbatim and checked against TARGET_LANGS.
CLD3_LABEL_MAP: dict[str, str] = {
    "zh-Hans": "zh",   # Simplified Chinese
    "zh-Hant": "zh",   # Traditional Chinese
    "no":      "nb",   # Norwegian (generic) → Norwegian Bokmål
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Config Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: Path) -> dict:
    """
    Load config_test.yaml and apply environment variable overrides.

    Override hierarchy (highest to lowest priority):
      1. Environment variables: LID_BENCH_DIR, LID_OUTPUT_DIR,
         MLFLOW_TRACKING_URI
      2. config_test.yaml values

    Note: LID_MODEL_DIR is not used here — CLD3 has no external model files.

    All path strings are resolved to absolute Path objects relative to the
    repository root (SCRIPT_DIR.parent.parent), so the script can be invoked
    from any working directory — essential for PBS batch jobs.
    """
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    # Environment variable overrides
    if "LID_BENCH_DIR" in os.environ:
        cfg["paths"]["benchmark_data_dir"] = os.environ["LID_BENCH_DIR"]
    if "LID_OUTPUT_DIR" in os.environ:
        cfg["paths"]["output_dir"] = os.environ["LID_OUTPUT_DIR"]
    if "MLFLOW_TRACKING_URI" in os.environ:
        cfg["paths"]["mlflow_tracking_uri"] = os.environ["MLFLOW_TRACKING_URI"]

    # Resolve relative paths against the repo root
    repo_root = SCRIPT_DIR.parent.parent
    for key in ("benchmark_data_dir", "output_dir", "mlflow_tracking_uri"):
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

    logger = logging.getLogger("cld3_benchmark")
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
# 5. Model Initialisation
# ─────────────────────────────────────────────────────────────────────────────

def init_cld3_model(logger: logging.Logger) -> gcld3.NNetLanguageIdentifier:
    """
    Initialise the CLD3 NNetLanguageIdentifier.

    min_num_bytes=0  — classify even very short strings (no minimum length gate).
    max_num_bytes=1000 — truncate inputs to 1000 bytes for consistent latency;
                         CLD3's accuracy plateaus well below this threshold.

    The model weights are bundled inside the gcld3 package — no external file
    path is required.

    Args:
        logger: Logger instance.

    Returns:
        Initialised gcld3.NNetLanguageIdentifier ready for inference.
    """
    identifier = gcld3.NNetLanguageIdentifier(min_num_bytes=0, max_num_bytes=1000)
    logger.info(
        "Initialised CLD3 NNetLanguageIdentifier (min_bytes=0, max_bytes=1000)"
    )
    return identifier


# ─────────────────────────────────────────────────────────────────────────────
# 6. Benchmark Inference & Metrics
# ─────────────────────────────────────────────────────────────────────────────

def run_benchmark(
    identifier: gcld3.NNetLanguageIdentifier,
    X: list[str],
    y_true: list[str],
    label_names: list[str],
    logger: logging.Logger,
) -> tuple[dict[str, float], str]:
    """
    Run inference on the benchmark set and compute quality + performance metrics.

    CLD3 has no native batch API; inference is performed sample-by-sample using
    identifier.FindLanguage(text), which returns a Result object with a
    .language attribute (BCP-47 string).

    Label normalisation:
      1. The raw BCP-47 code is looked up in CLD3_LABEL_MAP; if found, the
         mapped value is used.
      2. If the (possibly mapped) code is not in TARGET_LANGS, the prediction
         is recorded as "unsupported". A warning counts and logs these.
      3. "unsupported" predictions reduce F1 by appearing as false positives
         on no target class — the correct, honest treatment.

    Timing covers the full per-sample loop, reflecting real-world end-to-end
    latency including Python-level overhead for each call.

    Metrics:
      accuracy                     — overall fraction correct
      f1_macro                     — unweighted mean F1 across all classes
      precision_macro              — unweighted mean precision across all classes
      recall_macro                 — unweighted mean recall across all classes
      inference_time_total_s       — wall-clock seconds for the full benchmark set
      inference_time_ms_per_sample — average milliseconds per text sample
      throughput_samples_per_sec   — total samples divided by total time

    Args:
        identifier:  Initialised gcld3.NNetLanguageIdentifier.
        X:           List of text strings to classify.
        y_true:      Ground-truth language labels.
        label_names: Sorted list of expected label names for the report.
        logger:      Logger instance.

    Returns:
        (metrics_dict, classification_report_str)
    """
    n = len(X)
    unsupported_count = 0
    y_pred: list[str] = []

    t0 = time.perf_counter()
    for text in X:
        try:
            result = identifier.FindLanguage(text)
            raw_lang = result.language                          # BCP-47 string
            mapped = CLD3_LABEL_MAP.get(raw_lang, raw_lang)    # normalise
            if mapped not in TARGET_LANGS:
                unsupported_count += 1
                mapped = "unsupported"
        except Exception as exc:
            logger.debug("CLD3 exception on sample: %s", exc)
            unsupported_count += 1
            mapped = "unsupported"
        y_pred.append(mapped)
    inference_time_s = time.perf_counter() - t0

    if unsupported_count > 0:
        logger.warning(
            "CLD3 returned unsupported/unmapped labels for %d / %d samples "
            "(%.2f%% of set)",
            unsupported_count, n, 100.0 * unsupported_count / n,
        )

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
        model_name:   Model identifier (always "cld3" for this script).
        metrics:      Dict of metric name → value from run_benchmark().
        report_str:   Classification report string from run_benchmark().
        output_dir:   Root output directory (model_benchmarking_evaluation/cld3/).
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
            Metrics: accuracy, f1_macro, f1_weighted, precision_macro,
                     precision_weighted, recall_macro, recall_weighted,
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
      4.  Initialise CLD3 model once (single model, reused across all datasets)
      5.  Discover dataset directories: iterate all subdirs of benchmark_data_dir
      6.  For each dataset:
            a. Load all benchmark data (no sampling cap)
            b. Run inference + compute metrics (per-sample CLD3 loop)
            c. Save artifacts to output_dir/<dataset>/cld3/
            d. Log to MLflow (if available) or rely on local JSON fallback
            e. Append row to results_summary
      7.  Print cross-dataset summary table
    """
    # ── 1. Config ─────────────────────────────────────────────────────────────
    cfg = load_config(CONFIG_PATH)
    benchmark_data_dir: Path = Path(cfg["paths"]["benchmark_data_dir"])
    output_dir: Path = Path(cfg["paths"]["output_dir"])

    # ── 2. Logging ────────────────────────────────────────────────────────────
    logger = setup_logging(
        output_dir=output_dir,
        log_filename=cfg["logging"]["log_filename"],
        level_str=cfg["logging"]["level"],
    )

    # ── 3. Environment info ───────────────────────────────────────────────────
    logger.info("Python         : %s", sys.version.split()[0])
    try:
        import pkg_resources
        cld3_version = pkg_resources.get_distribution("gcld3").version
    except Exception:
        cld3_version = "unknown"
    logger.info("gcld3          : %s", cld3_version)
    logger.info("MLflow         : %s", mlflow.__version__ if MLFLOW_AVAILABLE else "not installed")
    logger.info("Config         : %s", CONFIG_PATH)
    logger.info("Benchmark dir  : %s", benchmark_data_dir)
    logger.info("Output dir     : %s", output_dir)
    logger.info("Model name     : %s", MODEL_NAME)
    logger.info("Label map      : %s", CLD3_LABEL_MAP)

    # ── 4. Initialise CLD3 model once ────────────────────────────────────────
    identifier = init_cld3_model(logger)

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
            identifier=identifier,
            X=X,
            y_true=y,
            label_names=label_names,
            logger=logger,
        )

        # 6c. Save artifacts
        artifacts = save_benchmark_artifacts(
            dataset_name=dataset_name,
            model_name=MODEL_NAME,
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
                    model_name=MODEL_NAME,
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
            "model":   MODEL_NAME,
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
