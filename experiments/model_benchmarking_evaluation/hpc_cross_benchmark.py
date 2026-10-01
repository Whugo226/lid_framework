#!/usr/bin/env python3
"""
hpc_cross_benchmark.py

Cross-dataset benchmark runner for LID Experiments.

Tests every trained LID model (FastText, Logistic Regression, Naive Bayes)
against every evaluation dataset and writes results to model_benchmarking_evaluation/
with variant dirs named {variant}_{training_dataset}, matching the MKB naming
convention so that validate_recommendations.py can resolve cross-dataset Rec scores.

Checkpoint recovery: any combination whose benchmark_metadata.json already exists
is silently skipped.  Re-submit the HPC job to resume after a timeout.

Usage
-----
Full matrix (HPC):
    python hpc_cross_benchmark.py

Targeted dry-run (one combination):
    python hpc_cross_benchmark.py --family fasttext \\
        --training-dataset massive --eval-dataset mmarco

Environment variable overrides (for HPC scratch):
    LID_TRAINING_RESULTS_DIR  → paths.training_results_dir
    LID_EVAL_DATA_DIR         → paths.eval_data_dir
    LID_BENCHMARK_EVAL_DIR    → paths.benchmark_eval_dir
"""

# ─────────────────────────────────────────────────────────────────────────────
# Standard library
# ─────────────────────────────────────────────────────────────────────────────
import argparse
import json
import logging
import os
import pickle
import sys
import time
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Third-party
# ─────────────────────────────────────────────────────────────────────────────
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
# Constants
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR: Path = Path(__file__).resolve().parent
CONFIG_PATH: Path = SCRIPT_DIR / "config_cross_benchmark.yaml"

TEXT_COL: str = "text"
LANG_COL: str = "lang"

TARGET_LANGS: frozenset = frozenset({
    "ca", "da", "de", "el", "en", "es", "fi", "fr", "hr", "it",
    "ja", "ko", "lt", "mk", "nb", "nl", "pl", "pt", "ro", "ru",
    "sl", "sv", "uk", "zh",
})


# ─────────────────────────────────────────────────────────────────────────────
# Config loading
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: Path) -> dict:
    """Load config_cross_benchmark.yaml and apply env var overrides."""
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    for env_var, cfg_key in [
        ("LID_TRAINING_RESULTS_DIR", "training_results_dir"),
        ("LID_EVAL_DATA_DIR",        "eval_data_dir"),
        ("LID_BENCHMARK_EVAL_DIR",   "benchmark_eval_dir"),
    ]:
        if env_var in os.environ:
            cfg["paths"][cfg_key] = os.environ[env_var]

    repo_root = SCRIPT_DIR.parent
    for key in ("training_results_dir", "eval_data_dir", "benchmark_eval_dir"):
        p = Path(cfg["paths"][key])
        cfg["paths"][key] = p if p.is_absolute() else repo_root / p

    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# Logging setup
# ─────────────────────────────────────────────────────────────────────────────

def setup_logging(output_dir: Path, log_filename: str, level_str: str) -> logging.Logger:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / log_filename
    level = getattr(logging, level_str.upper(), logging.INFO)
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("cross_benchmark")
    logger.setLevel(level)
    logger.handlers.clear()
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.info("Log: %s", log_path)
    return logger


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark data loading  (verbatim from test_fasttext_benchmark.py)
# ─────────────────────────────────────────────────────────────────────────────

def load_benchmark_data(data_dir: Path, logger: logging.Logger) -> pd.DataFrame:
    """
    Load all parquet files from data_dir and return a validated DataFrame.

    Two-phase load: metadata scan then selective column read.  Filters to
    TARGET_LANGS only.  No per-language cap applied — all rows used.
    """
    parquet_files = sorted(data_dir.rglob("*.parquet"))
    logger.info("  Parquet files: %d under %s", len(parquet_files), data_dir.name)

    lang_file_index: dict[str, list[tuple[Path, int]]] = {}
    for fp in parquet_files:
        try:
            meta = pq.read_metadata(fp)
            lang = fp.stem.split("_")[0]
            if lang not in TARGET_LANGS:
                continue
            lang_file_index.setdefault(lang, []).append((fp, meta.num_rows))
        except Exception as exc:
            logger.warning("  Metadata read failed %s: %s", fp.name, exc)

    chunks: list[pd.DataFrame] = []
    for lang in sorted(lang_file_index):
        for fp, _ in lang_file_index[lang]:
            try:
                table = pq.read_table(fp, columns=[TEXT_COL, LANG_COL])
                df_chunk = table.to_pandas()
            except Exception as exc:
                logger.warning("  Read failed %s: %s", fp.name, exc)
                continue
            df_chunk = df_chunk[df_chunk[LANG_COL] == lang]
            chunks.append(df_chunk)

    if not chunks:
        raise RuntimeError(f"No data loaded from {data_dir}")

    df = pd.concat(chunks, ignore_index=True)
    initial_len = len(df)
    df = df.dropna(subset=[TEXT_COL, LANG_COL])
    df = df[df[TEXT_COL].str.strip().str.len() > 0]
    df = df[df[LANG_COL].isin(TARGET_LANGS)]
    dropped = initial_len - len(df)
    if dropped > 0:
        logger.warning("  Dropped %d invalid rows", dropped)
    logger.info("  Loaded %d samples (%d languages)", len(df), df[LANG_COL].nunique())
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Model loaders
# ─────────────────────────────────────────────────────────────────────────────

def load_fasttext_model(model_path: Path, logger: logging.Logger):
    import fasttext
    try:
        model = fasttext.load_model(str(model_path))
        logger.info("  Loaded FastText model: %s", model_path)
        return model
    except Exception as exc:
        raise RuntimeError(f"FastText load failed {model_path}: {exc}") from exc


def load_sklearn_model(model_path: Path, logger: logging.Logger):
    try:
        with open(model_path, "rb") as fh:
            pipeline = pickle.load(fh)
        logger.info("  Loaded sklearn pipeline: %s", model_path)
        return pipeline
    except Exception as exc:
        raise RuntimeError(f"Sklearn load failed {model_path}: {exc}") from exc


def load_model(family: str, model_path: Path, logger: logging.Logger):
    if family == "fasttext":
        return load_fasttext_model(model_path, logger)
    return load_sklearn_model(model_path, logger)


# ─────────────────────────────────────────────────────────────────────────────
# Inference
# ─────────────────────────────────────────────────────────────────────────────

def predict_fasttext(model, X: list[str]) -> list[str]:
    X_clean = [" ".join(t.split()) for t in X]
    labels, _ = model.predict(X_clean, k=1)
    return [lbl[0].replace("__label__", "") for lbl in labels]


def predict_sklearn(model, X: list[str]) -> list[str]:
    return list(model.predict(X))


def predict(family: str, model, X: list[str]) -> list[str]:
    if family == "fasttext":
        return predict_fasttext(model, X)
    return predict_sklearn(model, X)


# ─────────────────────────────────────────────────────────────────────────────
# Metrics  (verbatim from test_fasttext_benchmark.py)
# ─────────────────────────────────────────────────────────────────────────────

def run_benchmark(
    family: str,
    model,
    df: pd.DataFrame,
    logger: logging.Logger,
) -> tuple[dict[str, float], str]:
    """Run inference and compute the same 11 metrics as the per-family scripts."""
    X: list[str] = df[TEXT_COL].tolist()
    y_true: list[str] = df[LANG_COL].tolist()
    label_names: list[str] = sorted(TARGET_LANGS)
    n = len(X)

    t0 = time.perf_counter()
    y_pred = predict(family, model, X)
    inference_time_s = time.perf_counter() - t0

    metrics: dict[str, float] = {
        "accuracy":                     round(accuracy_score(y_true, y_pred), 6),
        "f1_macro":                     round(f1_score(y_true, y_pred, average="macro",    zero_division=0), 6),
        "f1_weighted":                  round(f1_score(y_true, y_pred, average="weighted", zero_division=0), 6),
        "precision_macro":              round(precision_score(y_true, y_pred, average="macro",    zero_division=0), 6),
        "precision_weighted":           round(precision_score(y_true, y_pred, average="weighted", zero_division=0), 6),
        "recall_macro":                 round(recall_score(y_true, y_pred, average="macro",    zero_division=0), 6),
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
    logger.info(
        "  acc=%.4f  f1_macro=%.4f  f1_weighted=%.4f  n=%d  %.2fs",
        metrics["accuracy"], metrics["f1_macro"], metrics["f1_weighted"],
        n, inference_time_s,
    )
    return metrics, report_str


# ─────────────────────────────────────────────────────────────────────────────
# Artifact saving
# ─────────────────────────────────────────────────────────────────────────────

def save_artifacts(
    out_dir: Path,
    eval_dataset: str,
    training_dataset: str,
    variant: str,
    metrics: dict[str, float],
    report_str: str,
    logger: logging.Logger,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    variant_key = f"{variant}_{training_dataset}"
    meta = {
        "dataset":          eval_dataset,
        "training_dataset": training_dataset,
        "variant":          variant_key,
        "metrics":          metrics,
    }
    meta_path = out_dir / "benchmark_metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    report_path = out_dir / "benchmark_report.txt"
    report_path.write_text(report_str, encoding="utf-8")

    logger.info("  Saved → %s", out_dir)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cross-dataset LID benchmark runner."
    )
    parser.add_argument("--config",           default=None, help="Path to config YAML (default: config_cross_benchmark.yaml next to this script)")
    parser.add_argument("--family",           default=None, help="Limit to one model family")
    parser.add_argument("--training-dataset", default=None, help="Limit to one training dataset")
    parser.add_argument("--eval-dataset",     default=None, help="Limit to one eval dataset")
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    config_path = Path(args.config) if args.config else CONFIG_PATH
    cfg = load_config(config_path)

    training_results_dir: Path = Path(cfg["paths"]["training_results_dir"])
    eval_data_dir:        Path = Path(cfg["paths"]["eval_data_dir"])
    benchmark_eval_dir:   Path = Path(cfg["paths"]["benchmark_eval_dir"])

    logger = setup_logging(
        output_dir=benchmark_eval_dir,
        log_filename=cfg["logging"]["log_filename"],
        level_str=cfg["logging"]["level"],
    )

    logger.info("Python               : %s", sys.version.split()[0])
    logger.info("Training results dir : %s", training_results_dir)
    logger.info("Eval data dir        : %s", eval_data_dir)
    logger.info("Benchmark eval dir   : %s", benchmark_eval_dir)

    eval_datasets: list[str] = cfg["eval_datasets"]
    if args.eval_dataset:
        eval_datasets = [d for d in eval_datasets if d == args.eval_dataset]

    families: dict = cfg["families"]
    if args.family:
        families = {k: v for k, v in families.items() if k == args.family}

    total_done = total_skipped = total_errors = 0

    for family, fcfg in families.items():
        training_root = training_results_dir / fcfg["results_subdir"]
        if not training_root.is_dir():
            logger.warning("Training root not found, skipping family %s: %s", family, training_root)
            continue

        training_dataset_dirs = sorted(
            d for d in training_root.iterdir()
            if d.is_dir() and not d.name.startswith("mlruns")
        )
        if args.training_dataset:
            training_dataset_dirs = [d for d in training_dataset_dirs if d.name == args.training_dataset]

        logger.info("=" * 70)
        logger.info("FAMILY: %s  (%d training datasets)", family, len(training_dataset_dirs))

        for training_dir in training_dataset_dirs:
            training_dataset = training_dir.name

            for variant in fcfg["variants"]:
                model_path = training_dir / variant / fcfg["model_file"]
                if not model_path.exists():
                    logger.warning("Missing model, skipping: %s", model_path)
                    continue

                sep = "─" * 70
                logger.info(sep)
                logger.info("Model: %s / %s / %s", family, training_dataset, variant)

                try:
                    model = load_model(family, model_path, logger)
                except RuntimeError as exc:
                    logger.error("Load failed: %s", exc)
                    total_errors += 1
                    continue

                for eval_dataset in eval_datasets:
                    variant_dir_name = f"{variant}_{training_dataset}"
                    out_dir = benchmark_eval_dir / family / eval_dataset / variant_dir_name
                    out_file = out_dir / "benchmark_metadata.json"

                    if out_file.exists():
                        logger.info("  SKIP (exists): %s / %s", eval_dataset, variant_dir_name)
                        total_skipped += 1
                        continue

                    eval_data_path = eval_data_dir / eval_dataset
                    if not eval_data_path.is_dir():
                        logger.warning("  Eval dataset dir missing: %s", eval_data_path)
                        continue

                    logger.info("  → eval: %s", eval_dataset)
                    try:
                        df = load_benchmark_data(eval_data_path, logger)
                        metrics, report_str = run_benchmark(family, model, df, logger)
                        save_artifacts(
                            out_dir, eval_dataset, training_dataset,
                            variant, metrics, report_str, logger,
                        )
                        total_done += 1
                    except Exception as exc:
                        logger.error("  FAILED %s / %s: %s", eval_dataset, variant_dir_name, exc)
                        total_errors += 1

    logger.info("=" * 70)
    logger.info(
        "Finished. Done: %d  |  Skipped: %d  |  Errors: %d",
        total_done, total_skipped, total_errors,
    )


if __name__ == "__main__":
    main()
