#!/usr/bin/env python3
"""
train_fasttext_core.py

Production training suite for FastText Language Identification.

Trains two fastText model variants:
  - fasttext_word    : word unigrams only  (wordNgrams=1, minn=0, maxn=0)
  - fasttext_subword : character subwords + word bigrams (wordNgrams=2, minn=2, maxn=4)

Hyperparameter search: manual grid over epoch × lr, evaluated on a held-out
10% validation split from the training set.  Best params are then retrained
on the full 80% training set before final evaluation on the 20% test set.

Usage (local):
    python train_fasttext_core.py

Usage (HPC — override paths via environment variables):
    LID_DATA_DIR=/scratch/data LID_OUTPUT_DIR=/scratch/out python train_fasttext_core.py
"""

# ─────────────────────────────────────────────────────────────────────────────
# Standard library
# ─────────────────────────────────────────────────────────────────────────────
import json
import logging
import os
import sys
import tempfile
import time
from itertools import product
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Third-party
# ─────────────────────────────────────────────────────────────────────────────
import fasttext
import pandas as pd
import pyarrow.parquet as pq
import logging
import yaml
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

# ─────────────────────────────────────────────────────────────────────────────
# Optional MLflow
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
CONFIG_PATH: Path = SCRIPT_DIR / "config.yaml"

TEXT_COL: str = "text"
LANG_COL: str = "lang"

TARGET_LANGS: frozenset = frozenset({
    "ca", "da", "de", "el", "en", "es", "fi", "fr", "hr", "it",
    "ja", "ko", "lt", "mk", "nb", "nl", "pl", "pt", "ro", "ru",
    "sl", "sv", "uk", "zh",
})

# Only train on these newly added datasets; skip all others (already trained).
NEW_DATASETS: frozenset = frozenset({
    "tydiqa", "multilingual_cc_news", "xnli",
    "stsb_multi_mt", "amazon_reviews_multi", "europarl", "massive",
    "mmarco", "multi_eurlex", "xlsum", "multilingual_toxicity_dataset",
})

# ─────────────────────────────────────────────────────────────────────────────
# 2. Config Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: Path) -> dict:
    """
    Load config.yaml and apply environment variable overrides.

    Override hierarchy (highest to lowest priority):
      1. Environment variables: LID_DATA_DIR, LID_OUTPUT_DIR, MLFLOW_TRACKING_URI
      2. config.yaml values

    All path strings are resolved to absolute Path objects relative to the
    repository root (SCRIPT_DIR.parent.parent), so the script can be invoked
    from any working directory — essential for SLURM/PBS batch jobs.
    """
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    if "LID_DATA_DIR" in os.environ:
        cfg["paths"]["data_dir"] = os.environ["LID_DATA_DIR"]
    if "LID_OUTPUT_DIR" in os.environ:
        cfg["paths"]["output_dir"] = os.environ["LID_OUTPUT_DIR"]
    if "MLFLOW_TRACKING_URI" in os.environ:
        cfg["paths"]["mlflow_tracking_uri"] = os.environ["MLFLOW_TRACKING_URI"]

    repo_root = SCRIPT_DIR.parent.parent
    for key in ("data_dir", "output_dir", "mlflow_tracking_uri"):
        p = Path(cfg["paths"][key])
        cfg["paths"][key] = p if p.is_absolute() else repo_root / p

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

    StreamHandler writes to sys.stdout so PBS captures it in the .out file
    rather than .err.  output_dir is created here — the only mkdir call.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / log_filename

    level = getattr(logging, level_str.upper(), logging.INFO)
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger("fasttext_lid")
    logger.setLevel(level)
    logger.handlers.clear()

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    logger.info("Logging initialised. Log file: %s", log_path)
    return logger


# ─────────────────────────────────────────────────────────────────────────────
# 4. Data Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def load_data(
    data_dir: Path,
    max_samples_per_lang: int | None,
    random_seed: int,
    logger: logging.Logger,
) -> pd.DataFrame:
    """
    Load parquet files from data_dir and return a validated DataFrame.

    Memory strategy — two-phase load:

    Phase 1 (metadata scan):
      pq.read_metadata() reads only the parquet footer (no row data).
      This builds a per-language index of (filepath, row_count) pairs
      without touching the actual text.

    Phase 2 (selective loading):
      Files are read per language with pq.read_table(columns=[...]) which
      performs column-level I/O — only the two needed columns are
      deserialised.  Loading stops once the per-language quota is met.
      When the last file overshoots the quota, .sample() (not .head())
      is used to avoid head-of-file bias.

    Args:
        data_dir: Root of the cleaned training data directory.
        max_samples_per_lang: Per-language row cap.  None disables capping.
        random_seed: Seed for .sample() calls.
        logger: Logger instance.

    Returns:
        DataFrame with columns [TEXT_COL, LANG_COL], validated and sampled.
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
    logger.info("Pre-sampling row counts per language:")
    for lang in sorted(pre_counts):
        logger.info("  %-4s : %10d", lang, pre_counts[lang])
    logger.info("  TOTAL: %10d", sum(pre_counts.values()))
    logger.info("─" * 70)

    # ── Phase 2: selective loading ────────────────────────────────────────────
    chunks: list[pd.DataFrame] = []
    for lang in sorted(lang_file_index):
        lang_rows_loaded = 0
        for fp, _ in lang_file_index[lang]:
            if max_samples_per_lang is not None and lang_rows_loaded >= max_samples_per_lang:
                break
            try:
                table = pq.read_table(fp, columns=[TEXT_COL, LANG_COL])
                df_chunk = table.to_pandas()
            except Exception as exc:
                logger.warning("Failed to read %s: %s", fp, exc)
                continue

            df_chunk = df_chunk[df_chunk[LANG_COL] == lang]

            if max_samples_per_lang is not None:
                remaining = max_samples_per_lang - lang_rows_loaded
                if len(df_chunk) > remaining:
                    df_chunk = df_chunk.sample(n=remaining, random_state=random_seed)

            chunks.append(df_chunk)
            lang_rows_loaded += len(df_chunk)

    if not chunks:
        raise RuntimeError(
            f"No data loaded from {data_dir}. "
            "Verify the directory contains valid .parquet files."
        )

    df = pd.concat(chunks, ignore_index=True)

    # ── Phase 3: validation ───────────────────────────────────────────────────
    initial_len = len(df)
    df = df.dropna(subset=[TEXT_COL, LANG_COL])
    df = df[df[TEXT_COL].str.strip().str.len() > 0]
    df = df[df[LANG_COL].isin(TARGET_LANGS)]
    dropped = initial_len - len(df)
    if dropped > 0:
        logger.warning("Validation dropped %d invalid rows", dropped)

    post_counts = df[LANG_COL].value_counts().sort_index()
    logger.info("Post-sampling row counts per language:")
    for lang, count in post_counts.items():
        logger.info("  %-4s : %10d", lang, count)
    logger.info("  TOTAL: %10d", len(df))
    logger.info("─" * 70)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 5. FastText File Writer
# ─────────────────────────────────────────────────────────────────────────────

def write_fasttext_file(
    texts: list[str],
    labels: list[str],
    file_path: Path,
) -> None:
    """
    Write data in the fastText supervised format:
        __label__<lang> <text>

    Each text is whitespace-normalised (collapsed to single spaces) and
    written on a single line.  fasttext.train_supervised() requires this
    one-sample-per-line format.
    """
    with file_path.open("w", encoding="utf-8") as fh:
        for text, label in zip(texts, labels):
            clean = " ".join(text.split())
            fh.write(f"__label__{label} {clean}\n")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Model Configuration Descriptors
# ─────────────────────────────────────────────────────────────────────────────

def build_model_configs(cfg: dict) -> list[dict]:
    """
    Return two fastText model configuration descriptors.

    Analogous to build_pipelines() in train_mnb_core.py — each descriptor
    carries everything needed to train, log, and save one model variant:
      name            — used as output directory name, MLflow run name, log header
      fasttext_params — kwargs passed directly to fasttext.train_supervised()
      tags            — MLflow run tags

    The two variants mirror the BoW / TF-IDF split in the NB and LR scripts:
      fasttext_word     — word-level unigrams; the fastest, simplest baseline
      fasttext_subword  — character subwords (minn=2,maxn=4) + word bigrams;
                          the standard configuration for multilingual LID
    """
    dataset_version = cfg["mlflow"]["dataset_version"]
    thread: int = cfg["fasttext"]["thread"]
    verbose: int = cfg["fasttext"]["verbose"]

    return [
        {
            "name": "fasttext_word",
            "fasttext_params": {
                "wordNgrams": 1,
                "minn":       0,
                "maxn":       0,
                "loss":       "softmax",
                "thread":     thread,
                "verbose":    verbose,
            },
            "tags": {
                "feature_type":  "word_ngram",
                "wordNgrams":    "1",
                "minn":          "0",
                "maxn":          "0",
                "loss":          "softmax",
                "dataset_version": dataset_version,
            },
        },
        {
            "name": "fasttext_subword",
            "fasttext_params": {
                "wordNgrams": 2,
                "minn":       2,
                "maxn":       4,
                "loss":       "softmax",
                "thread":     thread,
                "verbose":    verbose,
            },
            "tags": {
                "feature_type":  "subword",
                "wordNgrams":    "2",
                "minn":          "2",
                "maxn":          "4",
                "loss":          "softmax",
                "dataset_version": dataset_version,
            },
        },
    ]


# ─────────────────────────────────────────────────────────────────────────────
# 7. Hyperparameter Search + Training
# ─────────────────────────────────────────────────────────────────────────────

def run_training(
    X_train: list[str],
    y_train: list[str],
    model_config: dict,
    cfg: dict,
    logger: logging.Logger,
) -> tuple[object, dict, list[dict]]:
    """
    Run a manual epoch × lr grid search on a held-out validation split,
    then retrain the winner on the full training set.

    Procedure:
      1. Split X_train 90/10 (stratified) → X_tr / X_val.
      2. Write X_tr to a temp file; write X_val to a temp file.
      3. For every (epoch, lr) combination:
           - train on X_tr
           - predict on X_val with model.predict()
           - compute macro-F1 on the val labels
           - record result
      4. Identify best (epoch, lr) by highest val macro-F1.
      5. Retrain with best params on full X_train (not just X_tr).
      6. Return (best_model, best_params_dict, search_results_list).

    tempfile.TemporaryDirectory ensures all .txt files are cleaned up even
    if training raises an exception.

    Args:
        X_train: Training texts (80% of the full dataset).
        y_train: Corresponding language labels.
        model_config: Descriptor dict from build_model_configs().
        cfg: Full config dict.
        logger: Logger instance.

    Returns:
        (best_model, best_params, search_results)
        where best_model is a fasttext model object ready for inference,
        best_params is {"epoch": int, "lr": float},
        and search_results is a list of per-combination metric dicts.
    """
    val_size: float = cfg["split"]["val_size"]
    random_seed: int = cfg["split"]["random_seed"]
    epoch_grid: list[int] = cfg["param_space"]["epoch"]
    lr_grid: list[float] = cfg["param_space"]["lr"]
    fixed_params: dict = model_config["fasttext_params"]

    # 1. Val split from X_train
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train,
        test_size=val_size,
        random_state=random_seed,
        stratify=y_train,
    )
    
    # FastText C++ crashes on newlines during batch predict; sanitize validation input
    X_val_clean = [" ".join(x.split()) for x in X_val]

    logger.info(
        "Param search split: train=%d  val=%d  (val_fraction=%.2f)",
        len(X_tr), len(X_val), val_size,
    )

    search_results: list[dict] = []
    best_val_f1: float = -1.0
    best_params: dict = {}

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        tr_file = tmp / "train.txt"
        val_file = tmp / "val.txt"
        full_train_file = tmp / "full_train.txt"

        write_fasttext_file(X_tr, y_tr, tr_file)
        write_fasttext_file(X_val, y_val, val_file)

        # 3. Grid search
        combinations = list(product(epoch_grid, lr_grid))
        logger.info(
            "Grid search: %d combinations  (epoch in %s, lr in %s)",
            len(combinations), epoch_grid, lr_grid,
        )

        for epoch, lr in combinations:
            t0 = time.perf_counter()
            model = fasttext.train_supervised(
                input=str(tr_file),
                epoch=epoch,
                lr=lr,
                **fixed_params,
            )
            train_elapsed = time.perf_counter() - t0

            # Predict on val set
            labels, probabilities = model.predict(X_val_clean)
            val_preds = [l[0].replace("__label__", "") for l in labels]
            val_f1 = f1_score(y_val, val_preds, average="macro", zero_division=0)

            logger.info(
                "  epoch=%3d  lr=%.3f  val_f1_macro=%.4f  train_time=%.1f s",
                epoch, lr, val_f1, train_elapsed,
            )
            search_results.append({
                "epoch":        epoch,
                "lr":           lr,
                "val_f1_macro": round(val_f1, 6),
                "train_time_s": round(train_elapsed, 2),
            })

            if val_f1 > best_val_f1:
                best_val_f1 = val_f1
                best_params = {"epoch": epoch, "lr": lr}

        logger.info(
            "Best params: epoch=%d  lr=%.3f  (val_f1=%.4f)",
            best_params["epoch"], best_params["lr"], best_val_f1,
        )

        # 5. Retrain on full X_train with best params
        write_fasttext_file(X_train, y_train, full_train_file)
        logger.info(
            "Retraining on full training set (%d samples) with best params...",
            len(X_train),
        )
        t0 = time.perf_counter()
        best_model = fasttext.train_supervised(
            input=str(full_train_file),
            epoch=best_params["epoch"],
            lr=best_params["lr"],
            **fixed_params,
        )
        logger.info("Retrain complete in %.1f s", time.perf_counter() - t0)

    return best_model, best_params, search_results


# ─────────────────────────────────────────────────────────────────────────────
# 8. Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_model(
    model: object,
    X_test: list[str],
    y_test: list[str],
    label_names: list[str],
    logger: logging.Logger,
) -> tuple[dict[str, float], str]:
    """
    Evaluate the trained fastText model on the held-out test set.

    Metrics returned:
      accuracy, f1_macro, precision_macro, recall_macro
      inference_time_total_s, inference_time_ms_per_sample,
      throughput_samples_per_sec

    Returns:
        (metrics_dict, classification_report_str)
    """
    # Data Sanitization (The Newline Fix)
    # Done outside the profiling block so string ops don't artificially lower throughput
    X_test_clean = [" ".join(x.split()) for x in X_test]

    t0 = time.perf_counter()
    labels, probabilities = model.predict(X_test_clean)
    y_pred = [l[0].replace("__label__", "") for l in labels]
    inference_time_s = time.perf_counter() - t0

    n = len(X_test)
    metrics: dict[str, float] = {
        "accuracy":                     accuracy_score(y_test, y_pred),
        "f1_macro":                     f1_score(y_test, y_pred, average="macro", zero_division=0),
        "precision_macro":              precision_score(y_test, y_pred, average="macro", zero_division=0),
        "recall_macro":                 recall_score(y_test, y_pred, average="macro", zero_division=0),
        "inference_time_total_s":       round(inference_time_s, 4),
        "inference_time_ms_per_sample": round(inference_time_s / n * 1000, 6),
        "throughput_samples_per_sec":   round(n / inference_time_s, 2),
    }

    report_str = classification_report(
        y_test, y_pred,
        labels=label_names,
        target_names=label_names,
        zero_division=0,
    )

    logger.info("─" * 70)
    logger.info("Test set evaluation  (n=%d samples):", n)
    for name, val in metrics.items():
        logger.info("  %-35s : %s", name, val)
    logger.info("\n%s", report_str)

    return metrics, report_str


# ─────────────────────────────────────────────────────────────────────────────
# 9. Artifact Saving
# ─────────────────────────────────────────────────────────────────────────────

def save_artifacts(
    run_name: str,
    model: object,
    search_results: list[dict],
    metrics: dict[str, float],
    report_str: str,
    best_params: dict,
    tags: dict,
    output_dir: Path,
    logger: logging.Logger,
) -> dict[str, Path]:
    """
    Persist all artefacts for one model variant to disk.

    Directory layout:
        output_dir/<run_name>/
            model.bin                  fastText binary (model.save_model())
            param_search_results.csv   epoch × lr grid results with val_f1
            classification_report.txt  per-language breakdown on test set
            run_metadata.json          params + metrics + tags (MLflow fallback)

    Returns a dict of artefact_name -> Path for use by log_to_mlflow().
    """
    run_dir = output_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, Path] = {}

    # model.bin
    model_path = run_dir / "model.bin"
    model.save_model(str(model_path))
    logger.info("Saved model    : %s", model_path)
    artifacts["model"] = model_path

    # param_search_results.csv
    search_path = run_dir / "param_search_results.csv"
    pd.DataFrame(search_results).to_csv(search_path, index=False)
    logger.info("Saved search   : %s", search_path)
    artifacts["param_search_results"] = search_path

    # classification_report.txt
    report_path = run_dir / "classification_report.txt"
    report_path.write_text(report_str, encoding="utf-8")
    logger.info("Saved report   : %s", report_path)
    artifacts["classification_report"] = report_path

    # run_metadata.json (MLflow fallback)
    meta = {
        "run_name": run_name,
        "tags":     tags,
        "params":   {str(k): str(v) for k, v in best_params.items()},
        "metrics":  metrics,
    }
    meta_path = run_dir / "run_metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Saved metadata : %s", meta_path)
    artifacts["run_metadata"] = meta_path

    return artifacts


# ─────────────────────────────────────────────────────────────────────────────
# 10. MLflow Logging
# ─────────────────────────────────────────────────────────────────────────────

def log_to_mlflow(
    cfg: dict,
    run_name: str,
    tags: dict,
    best_params: dict,
    metrics: dict[str, float],
    artifacts: dict[str, Path],
    search_results: list[dict],
    logger: logging.Logger,
) -> None:
    """
    Log a complete training run to MLflow (only called when MLFLOW_AVAILABLE).

    Structure:
        Experiment: cfg["mlflow"]["experiment_name"]
          Parent run: run_name
            Tags:    feature_type, wordNgrams, minn, maxn, dataset_version
            Params:  best epoch, lr
            Metrics: accuracy, f1_macro, precision_macro, recall_macro,
                     inference_time_total_s, inference_time_ms_per_sample,
                     throughput_samples_per_sec
            Artifacts: model.bin, param_search_results.csv,
                       classification_report.txt
            Child runs (nested=True): one per grid search combination
              Params:  epoch, lr
              Metrics: val_f1_macro, train_time_s
    """
    mlflow.set_tracking_uri(str(cfg["paths"]["mlflow_tracking_uri"]))
    mlflow.set_experiment(cfg["mlflow"]["experiment_name"])

    with mlflow.start_run(run_name=run_name) as parent_run:
        mlflow.set_tags(tags)
        mlflow.log_params({str(k): str(v) for k, v in best_params.items()})
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(artifacts["model"]))
        mlflow.log_artifact(str(artifacts["param_search_results"]))
        mlflow.log_artifact(str(artifacts["classification_report"]))

        for i, result in enumerate(search_results):
            with mlflow.start_run(run_name=f"grid_{i:03d}", nested=True):
                mlflow.log_params({
                    "epoch": str(result["epoch"]),
                    "lr":    str(result["lr"]),
                })
                mlflow.log_metric("val_f1_macro", float(result["val_f1_macro"]))
                mlflow.log_metric("train_time_s", float(result["train_time_s"]))

        logger.info(
            "MLflow logged: experiment=%s  run=%s  run_id=%s",
            cfg["mlflow"]["experiment_name"], run_name, parent_run.info.run_id,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 11. Main Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    End-to-end training pipeline — iterates over all dataset subdirectories.

    Execution order:
      1.  Load config (with env var overrides)
      2.  Setup logging → output_dir/training.log  (single shared log)
      3.  Log environment info
      4.  Discover dataset subdirectories under paths.data_dir
      5.  For each dataset subdirectory:
            a. Load and validate data (memory-efficient two-phase load)
            b. 80/20 stratified train/test split
            c. Set cfg["mlflow"]["dataset_version"] to the subdirectory name
            d. Build model configuration descriptors (word + subword)
            e. For each descriptor:
                 i.   epoch × lr grid search → best model
                 ii.  Evaluate best model on held-out test set
                 iii. Save artefacts to output_dir/<dataset_name>/<run_name>/
                 iv.  Log to MLflow (if available) or rely on local JSON fallback
      6.  Print cross-dataset summary table
    """
    # ── 1. Config ─────────────────────────────────────────────────────────────
    cfg = load_config(CONFIG_PATH)
    output_dir: Path = Path(cfg["paths"]["output_dir"])

    # ── 2. Logging ────────────────────────────────────────────────────────────
    logger = setup_logging(
        output_dir=output_dir,
        log_filename=cfg["logging"]["log_filename"],
        level_str=cfg["logging"]["level"],
    )

    # ── 3. Environment info ───────────────────────────────────────────────────
    logger.info("Python      : %s", sys.version.split()[0])
    try:
    # fasttext doesn't always have __version__, this is safer
        import pkg_resources
        ft_version = pkg_resources.get_distribution("fasttext-wheel").version
    except:
        ft_version = "unknown"
    logger.info("fasttext    : %s", ft_version)
    logger.info("MLflow      : %s", mlflow.__version__ if MLFLOW_AVAILABLE else "not installed")
    logger.info("Config      : %s", CONFIG_PATH)
    logger.info("Data dir    : %s", cfg["paths"]["data_dir"])
    logger.info("Output dir  : %s", cfg["paths"]["output_dir"])
    logger.info("max_samples_per_lang: %s", cfg["sampling"]["max_samples_per_lang"])

    # ── 4. Discover dataset subdirectories ────────────────────────────────────
    data_root: Path = Path(cfg["paths"]["data_dir"])
    all_dirs = sorted([d for d in data_root.iterdir() if d.is_dir()])
    for d in all_dirs:
        if d.name not in NEW_DATASETS:
            logger.info("Skipping %s: Already processed", d.name)
    dataset_dirs = [d for d in all_dirs if d.name in NEW_DATASETS]
    logger.info("Found %d new dataset subdirectories under %s:", len(dataset_dirs), data_root)
    for d in dataset_dirs:
        logger.info("  %s", d.name)

    label_names: list[str] = sorted(TARGET_LANGS)
    results_summary: list[dict] = []

    # ── 5. Outer dataset loop ─────────────────────────────────────────────────
    for dataset_dir in dataset_dirs:
        dataset_name = dataset_dir.name
        dataset_output_dir = output_dir / dataset_name

        sep = "█" * 70
        logger.info("\n%s\n  DATASET : %s\n%s", sep, dataset_name, sep)

        # 5a. Load data
        try:
            df = load_data(
                data_dir=dataset_dir,
                max_samples_per_lang=cfg["sampling"]["max_samples_per_lang"],
                random_seed=cfg["sampling"]["random_seed"],
                logger=logger,
            )
        except RuntimeError as exc:
            logger.warning("Skipping dataset %s — %s", dataset_name, exc)
            continue

        X: list[str] = df[TEXT_COL].tolist()
        y: list[str] = df[LANG_COL].tolist()

        # 5b. Train / test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=cfg["split"]["test_size"],
            random_state=cfg["split"]["random_seed"],
            stratify=y,
        )
        logger.info("Train size: %d  |  Test size: %d", len(X_train), len(X_test))

        # 5c. Tag this dataset
        cfg["mlflow"]["dataset_version"] = dataset_name

        # 5d. Build model config descriptors
        model_configs = build_model_configs(cfg)

        # 5e. Per-variant loop
        for model_config in model_configs:
            run_name: str = model_config["name"]
            tags: dict    = model_config["tags"]

            sep = "═" * 70
            logger.info("\n%s\n  Variant : %s\n%s", sep, run_name, sep)

            # i. Hyperparameter search + training
            best_model, best_params, search_results = run_training(
                X_train=X_train,
                y_train=y_train,
                model_config=model_config,
                cfg=cfg,
                logger=logger,
            )

            # ii. Evaluate on held-out test set
            metrics, report_str = evaluate_model(
                model=best_model,
                X_test=X_test,
                y_test=y_test,
                label_names=label_names,
                logger=logger,
            )

            # iii. Save artefacts — namespaced under dataset_output_dir
            artifacts = save_artifacts(
                run_name=run_name,
                model=best_model,
                search_results=search_results,
                metrics=metrics,
                report_str=report_str,
                best_params=best_params,
                tags=tags,
                output_dir=dataset_output_dir,
                logger=logger,
            )

            # iv. MLflow (or local JSON fallback already written by save_artifacts)
            if MLFLOW_AVAILABLE:
                try:
                    log_to_mlflow(
                        cfg=cfg,
                        run_name=run_name,
                        tags=tags,
                        best_params=best_params,
                        metrics=metrics,
                        artifacts=artifacts,
                        search_results=search_results,
                        logger=logger,
                    )
                except Exception as exc:
                    logger.warning(
                        "MLflow logging failed for %s / %s (run continues): %s",
                        dataset_name, run_name, exc,
                    )
            else:
                logger.info(
                    "MLflow not available — metadata written to: %s",
                    artifacts["run_metadata"],
                )

            results_summary.append({
                "dataset":      dataset_name,
                "run_name":     run_name,
                "best_epoch":   best_params["epoch"],
                "best_lr":      best_params["lr"],
                **metrics,
            })

    # ── 6. Cross-dataset summary ──────────────────────────────────────────────
    sep = "█" * 70
    logger.info("\n%s\n  CROSS-DATASET RESULTS SUMMARY\n%s", sep, sep)
    header = (
        f"  {'Dataset':<35}  {'Variant':<20}  {'Epoch':>5}  {'LR':>6}"
        f"  {'Acc':>8}  {'F1':>8}  {'ms/sample':>12}  {'samples/s':>12}"
    )
    logger.info(header)
    logger.info("  %s", "-" * (len(header) - 2))
    for row in results_summary:
        logger.info(
            "  %-35s  %-20s  %5d  %6.3f  %8.4f  %8.4f  %12.4f  %12.2f",
            row["dataset"],
            row["run_name"],
            row["best_epoch"],
            row["best_lr"],
            row["accuracy"],
            row["f1_macro"],
            row["inference_time_ms_per_sample"],
            row["throughput_samples_per_sec"],
        )
    logger.info(
        "Training complete. %d model runs across %d datasets.",
        len(results_summary), len(dataset_dirs),
    )


if __name__ == "__main__":
    main()
