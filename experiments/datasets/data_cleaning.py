"""
data_cleaning.py — Strategy 1: Sanitized Raw
=============================================
Mirrors the raw corpus folder structure into corresponding _cleaned directories,
applying a Regex-based sanitization pipeline to the 'text' column of every
Parquet file.

Pipeline (no lowercasing — preserves casing signals for DL models):
  1. Remove URLs       : http/https/www links
  2. Remove HTML tags  : <tag> / </tag>
  3. Remove @mentions  : social-media handles
  4. Normalize whitespace: collapse tabs/multi-spaces, strip edges
"""

import gc
import re
from pathlib import Path

import pandas as pd
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ROOT = Path(r"C:\Users\User\OneDrive\Masters\LID_experiments\datasets")
SUFFIX = "_cleaned"
TEXT_COL = "text"

# Only process these newly added datasets; skip all others (already cleaned).
NEW_DATASETS: frozenset = frozenset({
    "tydiqa", "multilingual_cc_news", "librispeech_asr", "xnli",
    "stsb_multi_mt", "amazon_reviews_multi", "europarl", "massive",
    "mmarco", "multi_eurlex", "xlsum", "multilingual_toxicity_dataset",
})

# ---------------------------------------------------------------------------
# Pre-compiled regex patterns (compiled once for performance)
# ---------------------------------------------------------------------------
RE_URL = re.compile(
    r"https?://\S+|www\.\S+",
    flags=re.IGNORECASE,
)
RE_HTML = re.compile(r"<[^>]+>")
RE_MENTION = re.compile(r"@\w+")
RE_WHITESPACE = re.compile(r"[ \t]+")


# ---------------------------------------------------------------------------
# Core sanitization (vectorized via pandas str.replace)
# ---------------------------------------------------------------------------
def sanitize_series(series: pd.Series) -> pd.Series:
    """Apply the full sanitization pipeline to a string Series."""
    s = series.astype(str)
    s = s.str.replace(RE_URL, " ", regex=True)
    s = s.str.replace(RE_HTML, " ", regex=True)
    s = s.str.replace(RE_MENTION, " ", regex=True)
    s = s.str.replace(RE_WHITESPACE, " ", regex=True)
    s = s.str.strip()
    return s


# ---------------------------------------------------------------------------
# File-level processing
# ---------------------------------------------------------------------------
def process_file(src: Path, dst: Path) -> tuple[int, int]:
    """
    Read *src*, sanitize, drop empty rows, write to *dst*.

    Returns (rows_before, rows_after).
    """
    df = pd.read_parquet(src)

    rows_before = len(df)

    if TEXT_COL not in df.columns:
        # Nothing to clean — copy as-is and report no change
        dst.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(dst, index=False)
        return rows_before, rows_before

    df[TEXT_COL] = sanitize_series(df[TEXT_COL])

    # Drop rows that became empty after cleaning
    mask_empty = df[TEXT_COL].str.len() == 0
    df = df[~mask_empty]

    rows_after = len(df)

    # Atomic-safe write: ensure destination directory exists
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dst, index=False)

    return rows_before, rows_after


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    # Discover source splits: directories that do NOT end with _cleaned
    source_splits = sorted(
        p for p in ROOT.iterdir()
        if p.is_dir() and not p.name.endswith(SUFFIX)
    )

    if not source_splits:
        print("No source split directories found. Exiting.")
        return

    print(f"Found {len(source_splits)} split(s) to process:\n")
    for sp in source_splits:
        print(f"  {sp.name}  →  {sp.name}{SUFFIX}")
    print()

    # Summary accumulators
    total_before = 0
    total_after = 0
    summary_rows: list[dict] = []

    # Collect all (src_file, dst_file) pairs first so tqdm can show grand total.
    # Only include files whose top-level dataset folder is in NEW_DATASETS.
    all_pairs: list[tuple[Path, Path]] = []
    skipped_datasets: set[str] = set()
    for split_dir in source_splits:
        dst_split = ROOT / (split_dir.name + SUFFIX)
        for src_file in split_dir.rglob("*.parquet"):
            relative = src_file.relative_to(split_dir)
            dataset_name = relative.parts[0]  # first component = dataset folder
            if dataset_name not in NEW_DATASETS:
                skipped_datasets.add(dataset_name)
                continue
            dst_file = dst_split / relative
            all_pairs.append((src_file, dst_file))

    if skipped_datasets:
        print(f"Skipping {len(skipped_datasets)} already-processed dataset(s):")
        for name in sorted(skipped_datasets):
            print(f"  Skipping {name}: Already processed")
        print()

    print(f"Total Parquet files to process: {len(all_pairs)}\n")

    with tqdm(total=len(all_pairs), unit="file", desc="Sanitizing") as pbar:
        current_split = None

        for src_file, dst_file in all_pairs:
            # Detect split transitions for sub-progress logging
            split_name = src_file.parts[len(ROOT.parts)]
            if split_name != current_split:
                current_split = split_name
                tqdm.write(f"\n--- Processing split: {split_name} ---")

            before, after = process_file(src_file, dst_file)
            dropped = before - after

            total_before += before
            total_after += after
            summary_rows.append(
                {
                    "split": split_name,
                    "file": src_file.relative_to(ROOT / split_name).as_posix(),
                    "rows_before": before,
                    "rows_after": after,
                    "rows_dropped": dropped,
                }
            )

            pbar.set_postfix(
                file=src_file.name[:30],
                before=before,
                after=after,
                dropped=dropped,
            )
            pbar.update(1)

            # Free memory between files
            gc.collect()

    # ---------------------------------------------------------------------------
    # Summary report
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SANITIZATION SUMMARY")
    print("=" * 70)

    summary_df = pd.DataFrame(summary_rows)
    split_summary = (
        summary_df.groupby("split")[["rows_before", "rows_after", "rows_dropped"]]
        .sum()
        .reset_index()
    )
    split_summary["drop_%"] = (
        split_summary["rows_dropped"] / split_summary["rows_before"].replace(0, 1) * 100
    ).round(4)

    # Print per-split table
    col_w = max(len(s) for s in split_summary["split"]) + 2
    header = (
        f"{'Split':<{col_w}} {'Before':>12} {'After':>12} {'Dropped':>10} {'Drop%':>8}"
    )
    print(header)
    print("-" * len(header))
    for _, row in split_summary.iterrows():
        print(
            f"{row['split']:<{col_w}} {row['rows_before']:>12,} "
            f"{row['rows_after']:>12,} {row['rows_dropped']:>10,} "
            f"{row['drop_%']:>7.4f}%"
        )

    print("-" * len(header))
    total_dropped = total_before - total_after
    drop_pct = total_dropped / total_before * 100 if total_before else 0.0
    print(
        f"{'TOTAL':<{col_w}} {total_before:>12,} {total_after:>12,} "
        f"{total_dropped:>10,} {drop_pct:>7.4f}%"
    )
    print("=" * 70)
    print(f"\nDone. Cleaned files written to: {ROOT}  (*{SUFFIX} folders)")


if __name__ == "__main__":
    main()
