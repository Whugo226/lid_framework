#!/usr/bin/env python3
"""
test_xlm_v_base_benchmark.py

Benchmark evaluation for juliensimon/xlm-v-base-language-id —
a fine-tuned facebook/xlm-v-base trained on google/fleurs (102 languages).

Key difference from test_xlm_roberta_benchmark.py: the model outputs full
English language names ("English", "French") rather than ISO codes ("en", "fr").
FLEURS_TO_ISO maps predictions back to BCP-47 codes before metric computation.

Output layout (compatible with mkb_store.build_from_filesystem):
    output_dir/<eval_dataset>/<variant_name>/
        benchmark_metadata.json
        benchmark_report.txt

Checkpoint recovery: any dataset whose benchmark_metadata.json already exists
is silently skipped.

Usage:
    python test_xlm_v_base_benchmark.py [--config config_test.yaml]

HPC path overrides via environment variables:
    LID_BENCH_DIR   → paths.benchmark_data_dir
    LID_OUTPUT_DIR  → paths.output_dir
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import torch
import yaml
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# ─────────────────────────────────────────────────────────────────────────────
# Constants
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

# Maps FLEURS full English language names → ISO-639-1 codes for TARGET_LANGS.
# The model outputs labels as defined in its config.id2label (derived from FLEURS).
# Alternates are included for labels that vary across FLEURS versions/model cards.
# If the job log shows "Unmapped FLEURS labels" warnings, add the exact strings here.
FLEURS_TO_ISO: dict[str, str] = {
    "Catalan":           "ca",
    "Danish":            "da",
    "German":            "de",
    "Greek":             "el",
    "English":           "en",
    "Spanish":           "es",
    "Finnish":           "fi",
    "French":            "fr",
    "Croatian":          "hr",
    "Italian":           "it",
    "Japanese":          "ja",
    "Korean":            "ko",
    "Lithuanian":        "lt",
    "Macedonian":        "mk",
    "Norwegian":         "nb",
    "Norwegian Bokmål":  "nb",   # alternate label in some FLEURS versions
    "Dutch":             "nl",
    "Polish":            "pl",
    "Portuguese":        "pt",
    "Romanian":          "ro",
    "Russian":           "ru",
    "Slovenian":         "sl",
    "Swedish":           "sv",
    "Ukrainian":         "uk",
    "Chinese Mandarin":  "zh",
    "Chinese":           "zh",   # alternate label in some FLEURS versions
    "Mandarin Chinese":  "zh",
}


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark xlm-v-base-language-id.")
    parser.add_argument("--config", default=None, help="Path to config YAML (default: config_test.yaml)")
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    if "LID_BENCH_DIR" in os.environ:
        cfg["paths"]["benchmark_data_dir"] = os.environ["LID_BENCH_DIR"]
    if "LID_OUTPUT_DIR" in os.environ:
        cfg["paths"]["output_dir"] = os.environ["LID_OUTPUT_DIR"]

    # model_id is a HuggingFace Hub ID — do not resolve as a filesystem path
    repo_root = SCRIPT_DIR.parent.parent
    for key in ("benchmark_data_dir", "output_dir"):
        p = Path(cfg["paths"][key])
        cfg["paths"][key] = p if p.is_absolute() else repo_root / p

    cfg["datasets"] = cfg.get("datasets", [])
    return cfg


# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

def setup_logging(output_dir: Path, log_filename: str, level_str: str) -> logging.Logger:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / log_filename
    level = getattr(logging, level_str.upper(), logging.INFO)
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("xlm_v_base_benchmark")
    logger.setLevel(level)
    logger.handlers.clear()
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


# ─────────────────────────────────────────────────────────────────────────────
# Data loading  (same two-phase strategy as test_xlm_roberta_benchmark.py)
# ─────────────────────────────────────────────────────────────────────────────

def load_benchmark_data(data_dir: Path, logger: logging.Logger) -> pd.DataFrame:
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
# Device
# ─────────────────────────────────────────────────────────────────────────────

def resolve_device(device_cfg: str, logger: logging.Logger) -> torch.device:
    if device_cfg == "auto":
        device_str = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device_str = device_cfg
    device = torch.device(device_str)
    if device.type == "cuda":
        logger.info("Device: %s  (%s)", device, torch.cuda.get_device_name(device))
    else:
        logger.info("Device: %s  (CUDA not available)", device)
    return device


# ─────────────────────────────────────────────────────────────────────────────
# Model loading
# ─────────────────────────────────────────────────────────────────────────────

def load_model(model_id: str, device: torch.device, logger: logging.Logger) -> tuple:
    logger.info("Loading tokenizer: %s", model_id)
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
    except Exception as exc:
        raise RuntimeError(f"Tokenizer load failed: {exc}") from exc

    logger.info("Loading model: %s", model_id)
    try:
        model = AutoModelForSequenceClassification.from_pretrained(model_id)
    except Exception as exc:
        raise RuntimeError(f"Model load failed: {exc}") from exc

    model.to(device)
    model.eval()

    id2label: dict[int, str] = {int(k): v for k, v in model.config.id2label.items()}
    logger.info("Model loaded. Labels: %d  (e.g. %s)", len(id2label), ", ".join(list(id2label.values())[:6]))

    unmapped = set(id2label.values()) - set(FLEURS_TO_ISO.keys())
    if unmapped:
        logger.warning(
            "%d model label(s) not in FLEURS_TO_ISO (predictions will be '<UNK>'): %s",
            len(unmapped), sorted(unmapped),
        )

    return tokenizer, model, id2label


# ─────────────────────────────────────────────────────────────────────────────
# PyTorch Dataset
# ─────────────────────────────────────────────────────────────────────────────

class TextDataset(Dataset):
    def __init__(self, texts: list, tokenizer, max_length: int) -> None:
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict:
        encoding = self.tokenizer(
            self.texts[idx],
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        return {key: val.squeeze(0) for key, val in encoding.items()}


# ─────────────────────────────────────────────────────────────────────────────
# Label mapping
# ─────────────────────────────────────────────────────────────────────────────

def map_fleurs_to_iso(raw_labels: list[str], logger: logging.Logger) -> list[str]:
    unmapped: set[str] = set()
    result = []
    for lbl in raw_labels:
        iso = FLEURS_TO_ISO.get(lbl)
        if iso is None:
            unmapped.add(lbl)
            result.append("<UNK>")
        else:
            result.append(iso)
    if unmapped:
        logger.warning(
            "Unmapped FLEURS labels (add to FLEURS_TO_ISO if legitimate): %s",
            sorted(unmapped),
        )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Inference & metrics
# ─────────────────────────────────────────────────────────────────────────────

def run_benchmark(
    tokenizer,
    model,
    id2label: dict,
    X: list,
    y_true: list,
    label_names: list,
    batch_size: int,
    max_length: int,
    device: torch.device,
    logger: logging.Logger,
) -> tuple[dict, str]:
    n = len(X)
    dataset = TextDataset(X, tokenizer, max_length)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    raw_preds: list[str] = []
    t0 = time.perf_counter()
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="  Inferring", unit="batch", file=sys.stdout):
            batch = {k: v.to(device) for k, v in batch.items()}
            logits = model(**batch).logits
            pred_ids = logits.argmax(dim=-1).cpu().tolist()
            raw_preds.extend(id2label[pid] for pid in pred_ids)
    inference_time_s = time.perf_counter() - t0

    y_pred = map_fleurs_to_iso(raw_preds, logger)

    metrics: dict = {
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
    output_dir: Path,
    dataset_name: str,
    variant_name: str,
    model_id: str,
    metrics: dict,
    report_str: str,
    logger: logging.Logger,
) -> None:
    run_dir = output_dir / dataset_name / variant_name
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "dataset":    dataset_name,
        "variant":    variant_name,
        "model_path": model_id,
        "metrics":    metrics,
    }
    (run_dir / "benchmark_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (run_dir / "benchmark_report.txt").write_text(report_str, encoding="utf-8")
    logger.info("  Saved → %s", run_dir)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    import transformers

    args = parse_args()
    config_path = Path(args.config) if args.config else CONFIG_PATH
    cfg = load_config(config_path)

    benchmark_data_dir: Path = Path(cfg["paths"]["benchmark_data_dir"])
    output_dir: Path         = Path(cfg["paths"]["output_dir"])
    model_id: str            = cfg["paths"]["model_id"]
    variant_name: str        = cfg["model"]["variant_name"]
    batch_size: int          = cfg["inference"]["batch_size"]
    max_length: int          = cfg["inference"]["max_length"]
    device_cfg: str          = cfg["inference"]["device"]

    logger = setup_logging(output_dir, cfg["logging"]["log_filename"], cfg["logging"]["level"])

    logger.info("Python       : %s", sys.version.split()[0])
    logger.info("torch        : %s", torch.__version__)
    logger.info("transformers : %s", transformers.__version__)
    logger.info("Model ID     : %s", model_id)
    logger.info("Variant name : %s", variant_name)
    logger.info("Bench dir    : %s", benchmark_data_dir)
    logger.info("Output dir   : %s", output_dir)
    logger.info("Batch size   : %d", batch_size)
    logger.info("Max length   : %d", max_length)

    device = resolve_device(device_cfg, logger)

    try:
        tokenizer, model, id2label = load_model(model_id, device, logger)
    except RuntimeError as exc:
        logger.error("Cannot load model: %s", exc)
        sys.exit(1)

    all_dirs = sorted(d for d in benchmark_data_dir.iterdir() if d.is_dir())
    target_datasets = set(cfg["datasets"])
    dataset_dirs = [d for d in all_dirs if d.name in target_datasets]
    logger.info("Target datasets: %d", len(dataset_dirs))

    label_names = sorted(TARGET_LANGS)
    results_summary = []

    for dataset_dir in dataset_dirs:
        dataset_name = dataset_dir.name
        checkpoint = output_dir / dataset_name / variant_name / "benchmark_metadata.json"

        if checkpoint.exists():
            logger.info("SKIP (exists): %s / %s", dataset_name, variant_name)
            continue

        sep = "█" * 70
        logger.info("\n%s\n  DATASET : %s\n%s", sep, dataset_name, sep)

        try:
            df = load_benchmark_data(dataset_dir, logger)
        except RuntimeError as exc:
            logger.warning("Skipping %s — %s", dataset_name, exc)
            continue

        X = df[TEXT_COL].tolist()
        y = df[LANG_COL].tolist()

        metrics, report_str = run_benchmark(
            tokenizer=tokenizer,
            model=model,
            id2label=id2label,
            X=X,
            y_true=y,
            label_names=label_names,
            batch_size=batch_size,
            max_length=max_length,
            device=device,
            logger=logger,
        )

        save_artifacts(output_dir, dataset_name, variant_name, model_id, metrics, report_str, logger)
        results_summary.append({"dataset": dataset_name, **metrics})

    sep = "█" * 70
    logger.info("\n%s\n  SUMMARY\n%s", sep, sep)
    header = f"  {'Dataset':<45}  {'Acc':>8}  {'F1':>8}  {'ms/sample':>12}  {'samples/s':>12}"
    logger.info(header)
    logger.info("  %s", "-" * (len(header) - 2))
    for row in results_summary:
        logger.info(
            "  %-45s  %8.4f  %8.4f  %12.4f  %12.2f",
            row["dataset"], row["accuracy"], row["f1_macro"],
            row["inference_time_ms_per_sample"], row["throughput_samples_per_sec"],
        )
    logger.info("Done. %d dataset(s) evaluated.", len(results_summary))


if __name__ == "__main__":
    main()
