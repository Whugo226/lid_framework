
"""
ingest_europarl.py

Standalone ingestion script for Helsinki-NLP/europarl.

Why standalone: each row's text lives in a nested translation dict
    {"da": "...", "de": "..."}
rather than a plain string field.  The main pipeline's isinstance(str) guard
would silently drop every row, so we handle the dict unpacking here.

Strategy:
  - Process one language-pair config at a time (e.g. "de-en").
  - For each row, iterate both sides of the translation dict.
  - Route each side independently so both languages get data from every config.
  - Reuse safe_truncate / normalise_lang / route_row / flush_buffer / make_dirs
    from the main script.

Target configs chosen to cover all 13 EuroParl languages in our 24-lang set:
  da, de, el, en, es, fi, fr, it, nl, pl, pt, ro, sv.
Each language is paired with 'en' where possible (config names are
alphabetically ordered, e.g. "da-en" not "en-da").

Run:
    python datasets/ingest_europarl.py
"""

import os
import sys
import random

# ── Import shared helpers from main pipeline ──────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from data_split_generator_with_duckdb import (   # noqa: E402
    BASE_PATH, SEED, MAX_ROWS_PER_LANG, BATCH_SIZE,
    TARGET_LANGS,
    safe_truncate, normalise_lang, route_row,
    flush_buffer, make_dirs, count_existing_rows,
)

from datasets import load_dataset, concatenate_datasets  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DATASET_ID   = "Helsinki-NLP/europarl"
DATASET_NAME = "europarl"     # subfolder under each pool directory

# One config per target language, paired with English where possible.
# Config names in this dataset are alphabetically ordered (e.g. "da-en" not "en-da").
# English-English would be meaningless, so "en" is covered as the second side
# of every other config rather than needing its own dedicated config.
LANG_PAIR_CONFIGS: list[dict] = [
    # iso_codes = the two languages whose text we want from this config
    {"config": "da-en", "iso_codes": ["da", "en"]},
    {"config": "de-en", "iso_codes": ["de", "en"]},
    {"config": "el-en", "iso_codes": ["el", "en"]},
    {"config": "en-es", "iso_codes": ["en", "es"]},
    {"config": "en-fi", "iso_codes": ["en", "fi"]},
    {"config": "en-fr", "iso_codes": ["en", "fr"]},
    {"config": "en-it", "iso_codes": ["en", "it"]},
    {"config": "en-nl", "iso_codes": ["en", "nl"]},
    {"config": "en-pl", "iso_codes": ["en", "pl"]},
    {"config": "en-pt", "iso_codes": ["en", "pt"]},
    {"config": "en-ro", "iso_codes": ["en", "ro"]},
    {"config": "en-sv", "iso_codes": ["en", "sv"]},
]

SPLITS = ["train"]   # EuroParl only has a train split


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _is_lang_done(lang: str) -> bool:
    return count_existing_rows(DATASET_NAME, lang) >= MAX_ROWS_PER_LANG


def _process_pair_config(config_name: str, iso_codes: list[str], paths: dict,
                          lang_counts: dict) -> tuple[int, int]:
    """Stream one language-pair config and extract text for both sides."""
    print(f"  -> config={config_name!r}  sides={iso_codes}")

    split_streams = []
    for split in SPLITS:
        try:
            split_streams.append(
                load_dataset(DATASET_ID, config_name, split=split,
                             streaming=True, token=True)
            )
            print(f"     Loaded split {split!r}")
        except Exception as exc:
            print(f"     [WARN] split {split!r} unavailable: {exc}")

    if not split_streams:
        print(f"  [SKIP] {config_name!r}: no splits loaded")
        return 0, 0

    ds = concatenate_datasets(split_streams) if len(split_streams) > 1 else split_streams[0]
    ds = ds.shuffle(buffer_size=10_000, seed=SEED)

    buffers: dict = {dest: {} for dest in paths}
    seen = kept = 0

    for row in ds:
        seen += 1
        translation = row.get("translation")
        if not isinstance(translation, dict):
            continue

        for lang_code, text in translation.items():
            lang = normalise_lang(lang_code)
            if lang not in TARGET_LANGS:
                continue
            if not isinstance(text, str):
                continue
            text = safe_truncate(text.strip())
            if text is None:
                continue
            if lang_counts.get(lang, 0) >= MAX_ROWS_PER_LANG:
                continue

            kept += 1
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

            dest = route_row()
            buf  = buffers[dest].setdefault(lang, [])
            buf.append({"text": text, "lang": lang})

            if len(buf) >= BATCH_SIZE:
                flush_buffer(buf, paths[dest], lang)
                buffers[dest][lang] = []

        # Early exit if all target langs from this config are saturated
        if all(lang_counts.get(l, 0) >= MAX_ROWS_PER_LANG
               for l in iso_codes if l in TARGET_LANGS):
            print(f"  [SATURATED] All target langs for {config_name!r} done "
                  f"after {seen:,} rows — stopping early")
            break

    # Flush remaining buffers
    for dest, lang_bufs in buffers.items():
        for lang, rows in lang_bufs.items():
            if rows:
                flush_buffer(rows, paths[dest], lang)

    print(f"  [{config_name}] seen={seen:,}  kept={kept:,}")
    return seen, kept


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    random.seed(SEED)
    paths = make_dirs(DATASET_NAME)

    # Seed per-language counters from any existing files (resume support)
    lang_counts: dict = {
        lang: count_existing_rows(DATASET_NAME, lang)
        for lang in TARGET_LANGS
    }

    sep = "=" * 66
    print(f"\n{sep}")
    print(f"  Dataset : {DATASET_ID}")
    print(f"  Folder  : {DATASET_NAME}")
    print(sep)

    total_seen = total_kept = 0

    for pair_cfg in LANG_PAIR_CONFIGS:
        config_name = pair_cfg["config"]
        iso_codes   = pair_cfg["iso_codes"]

        # Skip config if all its languages are already complete
        if all(_is_lang_done(l) for l in iso_codes if l in TARGET_LANGS):
            print(f"  [CHECKPOINT] {config_name!r}: all target langs complete — skipping")
            continue

        s, k = _process_pair_config(config_name, iso_codes, paths, lang_counts)
        total_seen += s
        total_kept += k

    print(f"\n[DONE] europarl — total seen={total_seen:,}  kept={total_kept:,}")


if __name__ == "__main__":
    main()
