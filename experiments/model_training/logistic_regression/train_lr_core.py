#!/usr/bin/env python3
"""
train_lr_core.py

Production training suite for Multinomial Logistic Regression Language Identification.

Trains two sklearn pipelines:
  - CountVectorizer (BoW) + MaxAbsScaler + LogisticRegression  (char n-grams 3–5)
  - TfidfVectorizer (TFIDF)              + LogisticRegression  (char n-grams 3–5)

MaxAbsScaler is inserted after CountVectorizer because raw counts vary widely across
documents; MaxAbsScaler preserves sparsity while bringing features onto a common scale,
which is critical for L1/L2-penalised logistic regression convergence.
TF-IDF already produces per-document normalized vectors so a scaler is redundant there.

Each pipeline is tuned with RandomizedSearchCV (3-fold StratifiedKFold, per config.yaml) and evaluated
on a held-out 20% test set. Results and artefacts are logged to MLflow if available,
otherwise written as local JSON/CSV fallbacks.

Usage (local):
    python train_lr_core.py

Usage (HPC — override paths via environment variables):
    LID_DATA_DIR=/scratch/data LID_OUTPUT_DIR=/scratch/out python train_lr_core.py
"""

# ─────────────────────────────────────────────────────────────────────────────
# Standard library
# ─────────────────────────────────────────────────────────────────────────────
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
from scipy.stats import loguniform
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MaxAbsScaler

# ─────────────────────────────────────────────────────────────────────────────
# Optional MLflow
# ─────────────────────────────────────────────────────────────────────────────
try:
    import mlflow
    import mlflow.sklearn
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


def build_param_distributions(cfg: dict) -> tuple[dict, dict]:
    """
    Convert config.yaml param_space entries into sklearn-compatible
    distributions for RandomizedSearchCV.

    Parameter names use sklearn Pipeline step-prefix convention:
      "vectorizer__max_features", "clf__C", "clf__penalty", etc.

    The BoW pipeline has a "scaler" step between "vectorizer" and "clf",
    but MaxAbsScaler has no tunable hyperparameters so it does not appear
    in the search distributions.

    Returns:
        (bow_param_dist, tfidf_param_dist)
    """
    def _resolve(spec: dict):
        if spec["type"] == "loguniform":
            return loguniform(spec["low"], spec["high"])
        elif spec["type"] == "list":
            return spec["values"]
        elif spec["type"] == "bool_list":
            return [True, False]
        else:
            raise ValueError(f"Unknown param spec type: {spec['type']!r}")

    ps = cfg["param_space"]

    # Classifier hyperparameters shared by both pipelines
    clf_dist = {
        "clf__C":       _resolve(ps["lr"]["C"]),
        "clf__penalty": _resolve(ps["lr"]["penalty"]),
    }

    bow_dist = {
        **clf_dist,
        "vectorizer__max_features": _resolve(ps["count_vectorizer"]["max_features"]),
        "vectorizer__min_df":       _resolve(ps["count_vectorizer"]["min_df"]),
    }
    tfidf_dist = {
        **clf_dist,
        "vectorizer__max_features": _resolve(ps["tfidf_vectorizer"]["max_features"]),
        "vectorizer__min_df":       _resolve(ps["tfidf_vectorizer"]["min_df"]),
        "vectorizer__sublinear_tf": _resolve(ps["tfidf_vectorizer"]["sublinear_tf"]),
    }
    return bow_dist, tfidf_dist


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

    StreamHandler writes to sys.stdout so PBS/SLURM captures it in the .out
    file rather than .err. output_dir is created here — the only mkdir call
    in the entire script.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / log_filename

    level = getattr(logging, level_str.upper(), logging.INFO)
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger("lr_lid")
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
      without deserialising any text columns.

    Phase 2 (selective loading):
      Files are read per language with pq.read_table(columns=[...]), which
      performs column-level I/O — only the two needed columns are loaded.
      Loading stops once the per-language quota is met. When the last file
      overshoots the quota, .sample() (not .head()) is used to avoid
      head-of-file bias.

    Down-sampling is controlled via max_samples_per_lang in config.yaml:
      - Set to an integer (e.g. 5000) for rapid dev/test runs.
      - Set to null to load the full dataset.

    Args:
        data_dir: Root of the cleaned training data directory.
        max_samples_per_lang: Per-language row cap. None disables capping.
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
# 5. Pipeline Definitions
# ─────────────────────────────────────────────────────────────────────────────

def build_pipelines(cfg: dict) -> list[dict]:
    """
    Build both sklearn Pipelines and return a list of pipeline descriptors.

    Each descriptor contains:
      name       — used as MLflow run name, output directory, and log header
      pipeline   — sklearn Pipeline with vectorizer → [scaler] → clf steps
      param_dist — parameter distribution dict for RandomizedSearchCV
      tags       — dict of MLflow run tags

    Pipeline step naming convention:
      BoW   : ("vectorizer", CountVectorizer), ("scaler", MaxAbsScaler), ("clf", LR)
      TF-IDF: ("vectorizer", TfidfVectorizer),                           ("clf", LR)

    Fixed LR hyperparameters (not in search space):
      solver      = "saga"       — only solver supporting L1+L2+multinomial on large data
      multi_class = "multinomial"— softmax cross-entropy loss for 24 classes
      max_iter    = 1000         — generous upper bound; saga with warm_start converges early
      tol         = lr_fixed.tol — stop when gradient norm falls below this threshold

    Tuned LR hyperparameters (in search space):
      C           — inverse regularisation strength (loguniform 1e-4 … 1e4)
      penalty     — 'l2' (weight decay) or 'l1' (sparse weight vector)
    """
    feat_cfg    = cfg["features"]
    analyzer    = feat_cfg["analyzer"]
    ngram_range = tuple(feat_cfg["ngram_range"])
    lr_cfg      = cfg["lr_fixed"]

    bow_dist, tfidf_dist = build_param_distributions(cfg)

    dataset_version = cfg["mlflow"]["dataset_version"]
    ngram_str       = f"({ngram_range[0]},{ngram_range[1]})"

    def _make_lr() -> LogisticRegression:
        """Return a LogisticRegression with fixed architectural hyperparameters."""
        return LogisticRegression(
            solver=lr_cfg["solver"],
            max_iter=lr_cfg["max_iter"],
            tol=lr_cfg["tol"],
            n_jobs=1,
            random_state=cfg["split"]["random_seed"],
        )

    return [
        {
            "name": "bow_maxabs_lr_char_ngram_3_5",
            "pipeline": Pipeline([
                ("vectorizer", CountVectorizer(analyzer=analyzer, ngram_range=ngram_range)),
                ("scaler",     MaxAbsScaler()),
                ("clf",        _make_lr()),
            ]),
            "param_dist": bow_dist,
            "tags": {
                "feature_type":     "bow",
                "scaler":           "MaxAbsScaler",
                "n_gram_range":     ngram_str,
                "dataset_version":  dataset_version,
                "vectorizer_class": "CountVectorizer",
            },
        },
        {
            "name": "tfidf_lr_char_ngram_3_5",
            "pipeline": Pipeline([
                ("vectorizer", TfidfVectorizer(
                    analyzer=analyzer,
                    ngram_range=ngram_range,
                    sublinear_tf=True,   # default; overridden by search space if included
                )),
                ("clf", _make_lr()),
            ]),
            "param_dist": tfidf_dist,
            "tags": {
                "feature_type":     "tfidf",
                "scaler":           "none",
                "n_gram_range":     ngram_str,
                "dataset_version":  dataset_version,
                "vectorizer_class": "TfidfVectorizer",
            },
        },
    ]


# ─────────────────────────────────────────────────────────────────────────────
# 6. Hyperparameter Search
# ─────────────────────────────────────────────────────────────────────────────

def run_search(
    pipeline: Pipeline,
    param_dist: dict,
    X_train: list[str],
    y_train: list[str],
    cfg: dict,
    logger: logging.Logger,
) -> RandomizedSearchCV:
    """
    Run RandomizedSearchCV for one pipeline on the training set.

    Design notes:
      refit=True       — best_estimator_ is refit on the full X_train after
                         CV, ready for direct evaluation on the test set.
      verbose=2        — prints per-fold timing to stdout; visible in PBS .out
                         file so you can monitor progress with `tail -f`.
      error_score=raise— fail loudly in unattended batch jobs rather than
                         silently returning NaN scores.
      StratifiedKFold  — ensures proportional language coverage in every fold,
                         important given class imbalance (e.g. ca << en).
      return_train_score=False — saves memory; train scores not needed.
    """
    cv = StratifiedKFold(
        n_splits=cfg["cv"]["n_folds"],
        shuffle=True,
        random_state=cfg["split"]["random_seed"],
    )
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_dist,
        n_iter=cfg["search"]["n_iter"],
        scoring=cfg["cv"]["scoring"],
        cv=cv,
        n_jobs=cfg["cv"]["n_jobs"],
        verbose=2,
        refit=True,
        error_score="raise",
        random_state=cfg["sampling"]["random_seed"],
        return_train_score=False,
    )

    logger.info(
        "Starting RandomizedSearchCV  (n_iter=%d, cv=%d, scoring=%s, n_jobs=%s)",
        cfg["search"]["n_iter"], cfg["cv"]["n_folds"],
        cfg["cv"]["scoring"], cfg["cv"]["n_jobs"],
    )
    t0 = time.perf_counter()
    search.fit(X_train, y_train)
    elapsed = time.perf_counter() - t0

    logger.info("Search complete in %.1f s  (%.1f min)", elapsed, elapsed / 60)
    logger.info("Best CV %s : %.4f", cfg["cv"]["scoring"], search.best_score_)
    logger.info("Best params: %s", search.best_params_)
    return search


# ─────────────────────────────────────────────────────────────────────────────
# 7. Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_pipeline(
    best_pipeline: Pipeline,
    X_test: list[str],
    y_test: list[str],
    label_names: list[str],
    logger: logging.Logger,
) -> tuple[dict[str, float], str]:
    """
    Evaluate the best (refitted) pipeline on the held-out test set.

    Metrics returned:
      accuracy                     — fraction of correctly classified samples
      f1_macro                     — macro-averaged F1 across 24 languages
      precision_macro              — macro-averaged precision
      recall_macro                 — macro-averaged recall
      inference_time_total_s       — wall-clock seconds for the full test set
      inference_time_ms_per_sample — average milliseconds per text sample
      throughput_samples_per_sec   — samples processed per second

    The inference timing wraps the full pipeline.predict() call, covering
    both vectorisation and classification — this is the production-relevant
    latency figure.

    Returns:
        (metrics_dict, classification_report_str)
    """
    t0 = time.perf_counter()
    y_pred = best_pipeline.predict(X_test)
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
# 8. Artifact Saving
# ─────────────────────────────────────────────────────────────────────────────

def save_artifacts(
    run_name: str,
    best_pipeline: Pipeline,
    search: RandomizedSearchCV,
    metrics: dict[str, float],
    report_str: str,
    best_params: dict,
    tags: dict,
    output_dir: Path,
    logger: logging.Logger,
) -> dict[str, Path]:
    """
    Persist all artefacts for one pipeline run to disk.

    Directory layout:
        output_dir/<run_name>/
            best_pipeline.pkl          sklearn Pipeline (vectorizer + [scaler] + LR)
            cv_results.csv             all RandomizedSearchCV iterations
            classification_report.txt  per-language precision/recall/f1 on test set
            run_metadata.json          params + metrics + tags (MLflow fallback)

    Returns a dict of artefact_name -> Path for use by log_to_mlflow().
    """
    run_dir = output_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, Path] = {}

    # best_pipeline.pkl
    pkl_path = run_dir / "best_pipeline.pkl"
    with pkl_path.open("wb") as fh:
        pickle.dump(best_pipeline, fh, protocol=4)
    logger.info("Saved pipeline  : %s", pkl_path)
    artifacts["best_pipeline"] = pkl_path

    # cv_results.csv
    cv_path = run_dir / "cv_results.csv"
    pd.DataFrame(search.cv_results_).to_csv(cv_path, index=False)
    logger.info("Saved CV results: %s", cv_path)
    artifacts["cv_results"] = cv_path

    # classification_report.txt
    report_path = run_dir / "classification_report.txt"
    report_path.write_text(report_str, encoding="utf-8")
    logger.info("Saved report    : %s", report_path)
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
    logger.info("Saved metadata  : %s", meta_path)
    artifacts["run_metadata"] = meta_path

    return artifacts


# ─────────────────────────────────────────────────────────────────────────────
# 9. MLflow Logging
# ─────────────────────────────────────────────────────────────────────────────

def log_to_mlflow(
    cfg: dict,
    run_name: str,
    tags: dict,
    best_params: dict,
    metrics: dict[str, float],
    artifacts: dict[str, Path],
    search: RandomizedSearchCV,
    logger: logging.Logger,
) -> None:
    """
    Log a complete training run to MLflow (only called when MLFLOW_AVAILABLE).

    Structure:
        Experiment: cfg["mlflow"]["experiment_name"]
          Parent run: run_name
            Tags:    feature_type, scaler, n_gram_range, dataset_version, ...
            Params:  best hyperparameters
            Metrics: accuracy, f1_macro, precision_macro, recall_macro,
                     inference_time_total_s, inference_time_ms_per_sample,
                     throughput_samples_per_sec
            Artifacts: best_pipeline.pkl, cv_results.csv, classification_report.txt
            Child runs (nested=True): one per RandomizedSearchCV iteration
              Params:  param combination for that iteration
              Metrics: mean_test_score, std_test_score, rank
    """
    mlflow.set_tracking_uri(str(cfg["paths"]["mlflow_tracking_uri"]))
    mlflow.set_experiment(cfg["mlflow"]["experiment_name"])

    with mlflow.start_run(run_name=run_name) as parent_run:
        mlflow.set_tags(tags)
        mlflow.log_params({str(k): str(v) for k, v in best_params.items()})
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(artifacts["best_pipeline"]))
        mlflow.log_artifact(str(artifacts["cv_results"]))
        mlflow.log_artifact(str(artifacts["classification_report"]))

        cv_res  = search.cv_results_
        n_iters = len(cv_res["params"])
        for i in range(n_iters):
            with mlflow.start_run(run_name=f"iter_{i:03d}", nested=True):
                mlflow.log_params(
                    {str(k): str(v) for k, v in cv_res["params"][i].items()}
                )
                mlflow.log_metric("mean_test_score", float(cv_res["mean_test_score"][i]))
                mlflow.log_metric("std_test_score",  float(cv_res["std_test_score"][i]))
                mlflow.log_metric("rank",             float(cv_res["rank_test_score"][i]))

        logger.info(
            "MLflow logged: experiment=%s  run=%s  run_id=%s",
            cfg["mlflow"]["experiment_name"], run_name, parent_run.info.run_id,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 10. Main Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    End-to-end training pipeline — iterates over all dataset subdirectories.

    Execution order:
      1.  Load config (with env var overrides)
      2.  Setup logging → output_dir/training.log  (single shared log)
      3.  Log environment info and down-sampling mode
      4.  Discover dataset subdirectories under paths.data_dir
      5.  For each dataset subdirectory:
            a. Load and validate data (memory-efficient two-phase load)
            b. 80/20 stratified train/test split
            c. Set cfg["mlflow"]["dataset_version"] to the subdirectory name
            d. Build pipeline descriptors (BoW+MaxAbsScaler+LR  and  TF-IDF+LR)
            e. For each pipeline:
                 i.  RandomizedSearchCV on training set
                 ii. Evaluate best estimator on test set
                 iii.Save artefacts to output_dir/<dataset_name>/<run_name>/
                 iv. Log to MLflow (if available) or rely on local JSON fallback
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
    import sklearn
    logger.info("Python      : %s", sys.version.split()[0])
    logger.info("scikit-learn: %s", sklearn.__version__)
    logger.info("MLflow      : %s", mlflow.__version__ if MLFLOW_AVAILABLE else "not installed")
    logger.info("Config      : %s", CONFIG_PATH)
    logger.info("Data dir    : %s", cfg["paths"]["data_dir"])
    logger.info("Output dir  : %s", cfg["paths"]["output_dir"])

    max_spl = cfg["sampling"]["max_samples_per_lang"]
    if max_spl is None:
        logger.info("Down-sampling : DISABLED — loading full dataset")
    else:
        logger.info("Down-sampling : ENABLED  — max %d rows per language", max_spl)

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

        # 5a. Load data — skip directory if it contains no valid parquet files
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

        X: list[str]      = df[TEXT_COL].tolist()
        y: list[str]      = df[LANG_COL].tolist()

        # 5b. Train / test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=cfg["split"]["test_size"],
            random_state=cfg["split"]["random_seed"],
            stratify=y,
        )
        logger.info("Train size: %d  |  Test size: %d", len(X_train), len(X_test))

        # 5c. Tag this dataset (consumed by build_pipelines → descriptor tags)
        cfg["mlflow"]["dataset_version"] = dataset_name

        # 5d. Build pipeline descriptors
        pipeline_descriptors = build_pipelines(cfg)

        # 5e. Per-pipeline loop
        for descriptor in pipeline_descriptors:
            run_name:   str      = descriptor["name"]
            pipeline:   Pipeline = descriptor["pipeline"]
            param_dist: dict     = descriptor["param_dist"]
            tags:       dict     = descriptor["tags"]

            sep = "═" * 70
            logger.info("\n%s\n  Pipeline : %s\n%s", sep, run_name, sep)

            # i. RandomizedSearchCV
            search = run_search(
                pipeline=pipeline,
                param_dist=param_dist,
                X_train=X_train,
                y_train=y_train,
                cfg=cfg,
                logger=logger,
            )
            best_pipeline = search.best_estimator_
            best_params   = search.best_params_

            # ii. Evaluate on held-out test set
            metrics, report_str = evaluate_pipeline(
                best_pipeline=best_pipeline,
                X_test=X_test,
                y_test=y_test,
                label_names=label_names,
                logger=logger,
            )

            # iii. Save artefacts — namespaced under dataset_output_dir
            artifacts = save_artifacts(
                run_name=run_name,
                best_pipeline=best_pipeline,
                search=search,
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
                        search=search,
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
                "dataset":       dataset_name,
                "run_name":      run_name,
                "best_cv_score": search.best_score_,
                **metrics,
            })

    # ── 6. Cross-dataset summary ──────────────────────────────────────────────
    sep = "█" * 70
    logger.info("\n%s\n  CROSS-DATASET RESULTS SUMMARY\n%s", sep, sep)
    header = (
        f"  {'Dataset':<35}  {'Pipeline':<35}  {'CV f1':>8}"
        f"  {'Acc':>8}  {'F1':>8}  {'ms/sample':>12}  {'samples/s':>12}"
    )
    logger.info(header)
    logger.info("  %s", "-" * (len(header) - 2))
    for row in results_summary:
        logger.info(
            "  %-35s  %-35s  %8.4f  %8.4f  %8.4f  %12.4f  %12.2f",
            row["dataset"],
            row["run_name"],
            row["best_cv_score"],
            row["accuracy"],
            row["f1_macro"],
            row["inference_time_ms_per_sample"],
            row["throughput_samples_per_sec"],
        )
    logger.info(
        "Training complete. %d pipeline runs across %d datasets.",
        len(results_summary), len(dataset_dirs),
    )


if __name__ == "__main__":
    main()
