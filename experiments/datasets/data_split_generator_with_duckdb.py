#!/usr/bin/env python3
"""
data_split_generator_with_duckdb.py

Multi-level hierarchical splitter for multilingual LID datasets.

Directory layout produced under BASE_PATH:
  01a_knowledge_train_50/<dataset>/     50 % of accepted rows  (model training)
  01b_knowledge_benchmark_20/<dataset>/ 20 % of accepted rows  (KB ground-truth)
  02_evaluation_15/<dataset>/           15 % of accepted rows  (metric tuning)
  03_validation_15/<dataset>/           15 % of accepted rows  (final unseen test)

Two-step routing (fixed seed = 42, using random.random()):
  Step 1 — r ~ U[0,1):
      r < 0.15  → validation   (15 %)
      r < 0.30  → evaluation   (15 %)
      else      → knowledge    (70 %)
  Step 2 — for knowledge rows only, r2 ~ U[0,1):
      r2 < 5/7  → train        (5/7 × 70 % = 50 % total)
      else      → benchmark    (2/7 × 70 % = 20 % total)

Data ingestion (per dataset):
  Primary  — DuckDB hf:// protocol querying the @~parquet export.
             SQL pre-filters on language IN list and length <= 120.
             Results are fetched in BATCH_SIZE chunks via fetch_df_chunk().
  Fallback — HF datasets streaming API (load_dataset streaming=True).
             Used automatically when DuckDB connection fails or the dataset
             has no Parquet export.

Filters applied per row (both paths):
  - safe_truncate() is the final quality gate:
      CJK   → hard cut at CJK_MAX (40) chars; discard if result < CJK_MIN (10)
      Alpha → word-boundary cut at ALPHA_MAX (120) chars; discard if result < ALPHA_MIN (30)
  - Language must map to one of the 24 canonical ISO 639-1 target codes.

Parquet files are written per language in BATCH_SIZE chunks.
Filename format: <lang>_<HHMMSS>.parquet  (e.g. en_171138.parquet)
"""

import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"   # must be set before datasets import

import re
import random
from datetime import datetime
from typing import Optional, Iterator

import pandas as pd
import pyarrow.parquet as pq
from datasets import load_dataset, concatenate_datasets

# ─────────────────────────────────────────────────────────────────────────────
# 1. Global Configuration
# ─────────────────────────────────────────────────────────────────────────────
BASE_PATH         = "D:/Masters/LID_experiments/datasets"
SNAPSHOT_CACHE    = "D:/Masters/LID_experiments/hf_snapshots"  # local parquet cache
SEED              = 42
BATCH_SIZE        = 50_000   # large batches reduce I/O overhead on D: drive
MAX_ROWS_PER_LANG = 200_000  # cap per language per dataset config
STREAM_SAMPLE_RATE = 1.0     # fraction of rows to consider; <1.0 thins massive streams
HEARTBEAT_INTERVAL = 100_000 # print saturation progress every N seen rows
# Script-aware truncation limits (used by safe_truncate)
CJK_MAX   = 40    # hard cut for CJK scripts
CJK_MIN   = 10    # discard CJK result shorter than this
ALPHA_MAX = 120   # word-boundary cut for alphabetic scripts
ALPHA_MIN = 30    # discard alphabetic result shorter than this

TARGET_LANGS: frozenset = frozenset({
    "en", "ca", "zh", "hr", "da", "nl", "fi", "fr", "de", "el",
    "it", "ja", "ko", "lt", "mk", "nb", "pl", "pt", "ro", "ru",
    "sl", "es", "sv", "uk",
})

# Split thresholds for route_row()
VAL_UPPER  = 0.15   # [0.00, 0.15) → validation  (15 %)
EVAL_UPPER = 0.30   # [0.15, 0.30) → evaluation  (15 %)
                    # [0.30, 1.00) → knowledge   (70 %)
KNOW_TRAIN = 5 / 7  #   └─ of knowledge: 5/7 → train (50 % total), 2/7 → benchmark (20 % total)

# Matches any single CJK character (Chinese ideographs, Japanese kana, Korean Hangul)
CJK_PATTERN = re.compile(
    r'[\u3040-\u30FF'   # Hiragana + Katakana
    r'\u3400-\u4DBF'    # CJK Extension A
    r'\u4E00-\u9FFF'    # CJK Unified Ideographs (core block)
    r'\uAC00-\uD7A3'    # Hangul Syllables
    r'\uF900-\uFAFF]'   # CJK Compatibility Ideographs
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Language Normalisation Map  (variant → canonical ISO 639-1)
# ─────────────────────────────────────────────────────────────────────────────
LANG_MAP: dict = {
    # English
    "eng": "en", "english": "en", "eng_Latn": "en", "en_xx": "en",
    # Catalan
    "cat": "ca", "catalan": "ca", "cat_Latn": "ca",
    # Chinese (simplified & traditional both collapse to zh)
    "zho": "zh", "chi": "zh", "chinese": "zh",
    "zh-cn": "zh", "zh-tw": "zh", "zh-hans": "zh", "zh-hant": "zh",
    "zho_Hans": "zh", "zho_hant": "zh", "cmn": "zh",
    # Croatian
    "hrv": "hr", "croatian": "hr", "hrv_Latn": "hr",
    # Danish
    "dan": "da", "danish": "da", "dan_Latn": "da",
    # Dutch
    "nld": "nl", "dutch": "nl", "nld_Latn": "nl",
    # Finnish
    "fin": "fi", "finnish": "fi", "fin_Latn": "fi",
    # French
    "fra": "fr", "fre": "fr", "french": "fr", "fra_Latn": "fr",
    # German
    "deu": "de", "ger": "de", "german": "de", "deu_Latn": "de",
    # Greek
    "ell": "el", "gre": "el", "greek": "el", "ell_Grek": "el",
    # Italian
    "ita": "it", "italian": "it", "ita_Latn": "it",
    # Japanese
    "jpn": "ja", "japanese": "ja", "jpn_Jpan": "ja",
    # Korean
    "kor": "ko", "korean": "ko", "kor_Hang": "ko",
    # Lithuanian
    "lit": "lt", "lithuanian": "lt", "lit_Latn": "lt",
    # Macedonian
    "mkd": "mk", "macedonian": "mk", "mkd_Cyrl": "mk",
    # Norwegian Bokmål  (nb / no both map to nb)
    "nob": "nb", "nor": "nb", "no": "nb",
    "norwegian": "nb", "nob_Latn": "nb",
    # Polish
    "pol": "pl", "polish": "pl", "pol_Latn": "pl",
    # Portuguese
    "por": "pt", "portuguese": "pt",
    "pt-br": "pt", "pt-pt": "pt", "por_Latn": "pt",
    # Romanian
    "ron": "ro", "rum": "ro", "romanian": "ro", "ron_Latn": "ro",
    # Russian
    "rus": "ru", "russian": "ru", "rus_Cyrl": "ru", "ru_Cyrl": "ru",
    # Slovenian
    "slv": "sl", "slovenian": "sl", "slv_Latn": "sl",
    # Spanish
    "spa": "es", "spanish": "es", "spa_Latn": "es",
    # Swedish
    "swe": "sv", "swedish": "sv", "swe_Latn": "sv",
    # Ukrainian
    "ukr": "uk", "ukrainian": "uk", "ukr_Cyrl": "uk",
}

# Full set of raw language codes accepted by the SQL IN clause.
# Includes all canonical codes plus every known variant alias so that datasets
# which store language as "eng", "fra_Latn", etc. are not silently dropped by
# the upstream pre-filter.  Python's normalise_lang() remains the final gate.
_SQL_LANG_CODES: frozenset = TARGET_LANGS | frozenset(LANG_MAP.keys())

# ─────────────────────────────────────────────────────────────────────────────
# 3. Dataset Registry
#
#  id           : Hugging Face dataset identifier
#  name         : (optional) folder name under each pool directory;
#                 defaults to the repo portion of the HF id (after "/")
#  text_field   : row key that holds the raw text
#  lang_field   : row key that holds the language label (None if from config)
#  splits       : list of HF split names to stream (concatenated in order)
#  config       : HF config name (None = default)
#  lang_configs : {iso_code: hf_config_name} — used when language is encoded
#                 in the HF config rather than as a row field; the iso_code
#                 is injected as fixed_lang so no lang_field lookup is needed.
# ─────────────────────────────────────────────────────────────────────────────
DATASETS: list = [
    # {
    #     # LID-specific dataset: short texts, ~200 languages, all splits combined.
    #     "id":          "laurievb/OpenLID-v2",
    #     "text_field":  "text",
    #     "lang_field":  "language",
    #     "splits":      ["train", "validation", "test"],
    #     "config":      None,
    #     "lang_configs": None,
    # },
    # {
    #     # Wikipedia: encyclopedic domain, parquet available, all 24 target languages.
    #     # Norwegian Bokmål (nb) is stored under the 'no' config in Wikipedia.
    #     "id":          "wikimedia/wikipedia",
    #     "text_field":  "text",
    #     "lang_field":  None,
    #     "splits":      ["train"],
    #     "config":      None,
    #     "lang_configs": {
    #         "en": "20231101.en", "ca": "20231101.ca", "zh": "20231101.zh",
    #         "hr": "20231101.hr", "da": "20231101.da", "nl": "20231101.nl",
    #         "fi": "20231101.fi", "fr": "20231101.fr", "de": "20231101.de",
    #         "el": "20231101.el", "it": "20231101.it", "ja": "20231101.ja",
    #         "ko": "20231101.ko", "lt": "20231101.lt", "mk": "20231101.mk",
    #         "nb": "20231101.no", "pl": "20231101.pl", "pt": "20231101.pt",
    #         "ro": "20231101.ro", "ru": "20231101.ru", "sl": "20231101.sl",
    #         "es": "20231101.es", "sv": "20231101.sv", "uk": "20231101.uk",
    #     },
    # },
    # {
    #     # CC-100: web text used to train XLM-R, monolingual per-language configs.
    #     # Not parquet (uses a dataset script) — stream_only + trust_remote_code.
    #     # Chinese is zh-Hans (simplified); Norwegian Bokmål maps to 'no' config.
    #     "id":          "statmt/cc100",
    #     "text_field":  "text",
    #     "lang_field":  None,
    #     "splits":      ["train"],
    #     "config":      None,
    #     "stream_only": True,
    #     "trust_remote_code": True,
    #     "lang_configs": {
    #         "en": "en",      "ca": "ca",      "zh": "zh-Hans", "hr": "hr",
    #         "da": "da",      "nl": "nl",      "fi": "fi",      "fr": "fr",
    #         "de": "de",      "el": "el",      "it": "it",      "ja": "ja",
    #         "ko": "ko",      "lt": "lt",      "mk": "mk",      "nb": "no",
    #         "pl": "pl",      "pt": "pt",      "ro": "ro",      "ru": "ru",
    #         "sl": "sl",      "es": "es",      "sv": "sv",      "uk": "uk",
    #     },
    # },
    # {
    #     # Exorde: social media posts, blogs and news articles across 122 languages.
    #     # MIT licence, parquet available, language detected by fasttext (ISO 639-1).
    #     "id":          "Exorde/exorde-social-media-december-2024-week1",
    #     "text_field":  "original_text",
    #     "lang_field":  "language",
    #     "splits":      ["train"],
    #     "config":      None,
    #     "lang_configs": None,
    # },
    # {
    #     # CulturaX: large web-text corpus, parquet available, all 24 target languages.
    #     # Norwegian Bokmål (nb) is stored under the 'no' config in CulturaX.
    #     # Requires HuggingFace gated access approval.
    #     "id":          "uonlp/CulturaX",
    #     "text_field":  "text",
    #     "lang_field":  None,
    #     "splits":      ["train"],
    #     "config":      None,
    #     "lang_configs": {
    #         "en": "en", "ca": "ca", "zh": "zh", "hr": "hr",
    #         "da": "da", "nl": "nl", "fi": "fi", "fr": "fr",
    #         "de": "de", "el": "el", "it": "it", "ja": "ja",
    #         "ko": "ko", "lt": "lt", "mk": "mk", "nb": "no",
    #         "pl": "pl", "pt": "pt", "ro": "ro", "ru": "ru",
    #         "sl": "sl", "es": "es", "sv": "sv", "uk": "uk",
    #     },
    # },
    # {
    #     "id":          "openlanguagedata/flores_plus",
    #     "text_field":  "text",
    #     "lang_field":  "language",
    #     "splits":      ["dev", "devtest"],
    #     "config":      None,
    #     "lang_configs": None,
    #     "lang_in_path": True,
    # },
    # {
    #     # C4/mC4: web text, 108 languages (missing hr/Croatian).
    #     # Files are json.gz not parquet — use stream_only.
    #     "id":          "allenai/c4",
    #     "text_field":  "text",
    #     "lang_field":  None,
    #     "splits":      ["train", "validation"],
    #     "config":      None,
    #     "stream_only": True,
    #     "lang_configs": {
    #         "ca": "ca", "da": "da", "de": "de", "el": "el",
    #         "en": "en", "es": "es", "fi": "fi", "fr": "fr",
    #         "it": "it", "ja": "ja", "ko": "ko", "lt": "lt",
    #         "mk": "mk", "nl": "nl", "nb": "no", "pl": "pl",
    #         "pt": "pt", "ro": "ro", "ru": "ru", "sl": "sl",
    #         "sv": "sv", "uk": "uk", "zh": "zh",
    #     },
    # },
    # {
    #     # CardiffNLP: tweet sentiment, 8 languages only.
    #     "id":          "cardiffnlp/tweet_sentiment_multilingual",
    #     "text_field":  "text",
    #     "lang_field":  None,
    #     "splits":      ["train", "validation", "test"],
    #     "config":      None,
    #     "lang_configs": {
    #         "de": "german",   "en": "english",  "es": "spanish",
    #         "fr": "french",   "it": "italian",  "nl": "dutch",
    #         "pt": "portuguese", "ro": "romanian",
    #     },
    # },
    # {
    #     # papluca: small (90K rows), CSV only, missing 12 target languages.
    #     "id":          "papluca/language-identification",
    #     "text_field":  "text",
    #     "lang_field":  "labels",
    #     "splits":      ["train", "validation", "test"],
    #     "config":      None,
    #     "lang_configs": None,
    # },

    # ── GROUP A: Formal / Legal ───────────────────────────────────────────────
    # DISABLED: coastalcph/multi_eurlex uses a legacy .py loader script.
    # datasets v3.x removed all script support; trust_remote_code no longer valid.
    # Re-enable if/when the dataset authors publish a parquet-format version.
    # {
    #     "id":         "coastalcph/multi_eurlex",
    #     "name":       "multi_eurlex",
    #     "text_field": "text",
    #     "lang_field": None,
    #     "splits":     ["train", "validation", "test"],
    #     "config":     None,
    #     "lang_configs": {
    #         "da": "da", "de": "de", "el": "el", "en": "en",
    #         "es": "es", "fi": "fi", "fr": "fr", "hr": "hr",
    #         "it": "it", "lt": "lt", "nl": "nl", "pl": "pl",
    #         "pt": "pt", "ro": "ro", "sl": "sl", "sv": "sv",
    #     },
    # },
    # DISABLED: unicamp-dl/mmarco uses a legacy .py loader script.
    # Same issue as multi_eurlex above.
    # {
    #     "id":         "unicamp-dl/mmarco",
    #     "name":       "mmarco",
    #     "text_field": "positive",
    #     "lang_field": None,
    #     "splits":     ["train"],
    #     "config":     None,
    #     "lang_configs": {
    #         "de": "german",   "en": "english",  "es": "spanish",
    #         "fr": "french",   "it": "italian",  "ja": "japanese",
    #         "nl": "dutch",    "pt": "portuguese", "ru": "russian",
    #         "zh": "chinese",
    #     },
    # },
    # {
    #     # TyDiQA: natively-written (non-translated) Wikipedia-based questions.
    #     # primary_task config; language in per-row "language" field (full
    #     # lowercase name: "english", "finnish", …). LANG_MAP already covers
    #     # all these values.  Target from our 24: en, fi, ja, ko, ru.
    #     "id":         "google-research-datasets/tydiqa",
    #     "name":       "tydiqa",
    #     "text_field": "question_text",
    #     "lang_field": "language",
    #     "splits":     ["train", "validation"],
    #     "config":     "primary_task",
    #     "lang_configs": None,
    # },

    # ── GROUP B: News & Broadcast ─────────────────────────────────────────────
    # DISABLED: csebuetnlp/xlsum uses a legacy .py loader script.
    # Same issue as multi_eurlex above.
    # {
    #     "id":         "csebuetnlp/xlsum",
    #     "name":       "xlsum",
    #     "text_field": "text",
    #     "lang_field": None,
    #     "splits":     ["train", "validation", "test"],
    #     "config":     None,
    #     "lang_configs": {
    #         "en": "english",            "es": "spanish",
    #         "fr": "french",             "ja": "japanese",
    #         "ko": "korean",             "pt": "portuguese",
    #         "ru": "russian",            "uk": "ukrainian",
    #         "zh": "chinese_simplified",
    #     },
    # },
    # {
    #     # CC-News Multilingual: CommonCrawl news articles, 168 language configs.
    #     # text_field="maintext" (article body).  Single "train" split only.
    #     # Norwegian Bokmål (nb) is stored under the "no" config here.
    #     "id":         "hotchpotch/multilingual_cc_news",
    #     "name":       "multilingual_cc_news",
    #     "text_field": "maintext",
    #     "lang_field": None,
    #     "splits":     ["train"],
    #     "config":     None,
    #     "lang_configs": {
    #         # es/fr/it configs are absent from this dataset — removed.
    #         "ca": "ca", "da": "da", "de": "de", "el": "el",
    #         "en": "en", "fi": "fi", "hr": "hr", "ja": "ja",
    #         "ko": "ko", "lt": "lt", "mk": "mk", "nb": "no",
    #         "nl": "nl", "pl": "pl", "pt": "pt", "ro": "ro",
    #         "ru": "ru", "sl": "sl", "sv": "sv", "uk": "uk", "zh": "zh",
    #     },
    # },

    # ── GROUP C: Conversational / Short ───────────────────────────────────────
    # DISABLED: AmazonScience/massive uses a legacy .py loader script.
    # Same issue as multi_eurlex above.
    # {
    #     "id":         "AmazonScience/massive",
    #     "name":       "massive",
    #     "text_field": "utt",
    #     "lang_field": None,
    #     "splits":     ["train", "validation", "test"],
    #     "config":     None,
    #     "lang_configs": {
    #         "da": "da-DK", "de": "de-DE", "el": "el-GR", "en": "en-US",
    #         "es": "es-ES", "fi": "fi-FI", "fr": "fr-FR", "hr": "hr-HR",
    #         "it": "it-IT", "ja": "ja-JP", "ko": "ko-KR", "lt": "lt-LT",
    #         "nl": "nl-NL", "pl": "pl-PL", "pt": "pt-PT", "ro": "ro-RO",
    #         "ru": "ru-RU", "sl": "sl-SI", "sv": "sv-SE", "zh": "zh-CN",
    #     },
    # },

    # ── GROUP D: User-Generated ───────────────────────────────────────────────
    # DISABLED: amazon_reviews_multi uses a legacy .py loader script AND has
    # been moved to defunct-datasets/amazon_reviews_multi. Same issue as above.
    # {
    #     "id":         "neonwatty/amazon_reviews_multi",
    #     "name":       "amazon_reviews_multi",
    #     "text_field": "review_body",
    #     "lang_field": None,
    #     "splits":     ["train", "validation", "test"],
    #     "config":     None,
    #     "lang_configs": {
    #         "de": "de", "en": "en", "es": "es",
    #         "fr": "fr", "ja": "ja", "zh": "zh",
    #     },
    # },
    {
        # Multilingual Toxicity: toxic/offensive social media text (short).
        # Language is encoded in the HF split name (e.g. "en", "de").
        # Requires stream_only=True so the Python stream loops over the exact splits,
        # otherwise DuckDB's glob would read all languages simultaneously.
        "id":         "textdetox/multilingual_toxicity_dataset",
        "name":       "multilingual_toxicity_dataset",
        "text_field": "text",
        "lang_field": None,
        "config":     "default",
        "stream_only": True,
        "lang_splits": {
            "de": "de", "en": "en", "es": "es", "fr": "fr",
            "it": "it", "ja": "ja", "ru": "ru", "uk": "uk", "zh": "zh",
        },
    },

    # ── GROUP E: QA & Inference ───────────────────────────────────────────────
    # {
    #     # XNLI: NLI premise+hypothesis pairs (10-40 words), 15 language configs.
    #     # Using "premise" field only to avoid creating duplicate rows with hypothesis.
    #     # Non-English configs typically lack a "train" split — pipeline warns
    #     # and skips missing splits gracefully.
    #     "id":         "facebook/xnli",
    #     "name":       "xnli",
    #     "text_field": "premise",
    #     "lang_field": None,
    #     "splits":     ["train", "validation", "test"],
    #     "config":     None,
    #     "lang_configs": {
    #         "de": "de", "el": "el", "en": "en",
    #         "es": "es", "fr": "fr", "ru": "ru", "zh": "zh",
    #     },
    # },
    # {
    #     # STS-B Multilingual: sentence-similarity pairs (10-40 words).
    #     # Using "sentence1" field only.  Split names are "train"/"dev"/"test"
    #     # (not "validation") — pipeline skips unknown split names with a warning.
    #     "id":         "PhilipMay/stsb_multi_mt",
    #     "name":       "stsb_multi_mt",
    #     "text_field": "sentence1",
    #     "lang_field": None,
    #     "splits":     ["train", "dev", "test"],
    #     "config":     None,
    #     "lang_configs": {
    #         "de": "de", "en": "en", "es": "es", "fr": "fr",
    #         "it": "it", "nl": "nl", "pl": "pl", "pt": "pt",
    #         "ru": "ru", "zh": "zh",
    #     },
    # },
]

# ─────────────────────────────────────────────────────────────────────────────
# 4. Helpers
# ─────────────────────────────────────────────────────────────────────────────

def safe_truncate(text: str) -> Optional[str]:
    """Return a script-fair truncation of text, or None if too short to keep.

    CJK scripts (Chinese, Japanese, Korean):
      - Hard cut at CJK_MAX (40) characters.
      - Discard if the result is shorter than CJK_MIN (10) characters.

    Alphabetic scripts (Latin, Cyrillic, Greek, etc.):
      - If text fits within ALPHA_MAX (120) characters, keep as-is.
      - Otherwise truncate at the last whitespace before index ALPHA_MAX+1
        so no word is split; fall back to a hard cut if no whitespace exists.
      - Discard if the result is shorter than ALPHA_MIN (30) characters.
    """
    if CJK_PATTERN.search(text):
        result = text[:CJK_MAX]
        return result if len(result) >= CJK_MIN else None

    # Alphabetic path
    if len(text) <= ALPHA_MAX:
        return text if len(text) >= ALPHA_MIN else None

    cut = text[:ALPHA_MAX + 1].rfind(' ')       # last space within first 121 chars
    result = text[:cut].rstrip() if cut > 0 else text[:ALPHA_MAX]
    return result if len(result) >= ALPHA_MIN else None


def normalise_lang(raw) -> Optional[str]:
    """Return canonical ISO 639-1 code, or None if not in target set."""
    if raw is None:
        return None
    s = str(raw).strip()
    if s in TARGET_LANGS:
        return s
    key = s.lower()
    # Try original case first (handles mixed-case codes like "cat_Latn"),
    # then lowercase, then with hyphens replaced by underscores
    return (LANG_MAP.get(s)
            or LANG_MAP.get(key)
            or LANG_MAP.get(key.replace("-", "_")))


def make_dirs(dataset_name: str) -> dict:
    """Create the four destination directories and return a {dest: path} dict."""
    paths = {
        "train":      os.path.join(BASE_PATH, "01a_knowledge_train_50",    dataset_name),
        "benchmark":  os.path.join(BASE_PATH, "01b_knowledge_benchmark_20", dataset_name),
        "evaluation": os.path.join(BASE_PATH, "02_evaluation_15",           dataset_name),
        "validation": os.path.join(BASE_PATH, "03_validation_15",           dataset_name),
    }
    for p in paths.values():
        os.makedirs(p, exist_ok=True)
    return paths


def flush_buffer(rows: list, dest_dir: str, lang: str) -> None:
    """Write a batch of row dicts to a per-language Parquet file."""
    ts = datetime.now().strftime("%H%M%S")
    filepath = os.path.join(dest_dir, f"{lang}_{ts}.parquet")
    # Guard against same-second collision (rare but possible for large batches)
    counter = 1
    while os.path.exists(filepath):
        filepath = os.path.join(dest_dir, f"{lang}_{ts}_{counter}.parquet")
        counter += 1
    pd.DataFrame(rows).to_parquet(filepath, index=False)
    print(f"    Wrote {len(rows):>6,} rows -> {filepath}")


def count_existing_rows(dataset_name: str, lang: str) -> int:
    """Return the total number of rows already written for (dataset_name, lang).

    Scans all four pool directories and reads only the Parquet file-level
    metadata (no column data is decoded), so this is fast even for large files.
    """
    pool_dirs = [
        os.path.join(BASE_PATH, "01a_knowledge_train_50",    dataset_name),
        os.path.join(BASE_PATH, "01b_knowledge_benchmark_20", dataset_name),
        os.path.join(BASE_PATH, "02_evaluation_15",           dataset_name),
        os.path.join(BASE_PATH, "03_validation_15",           dataset_name),
    ]
    total = 0
    for d in pool_dirs:
        if not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            if fname.startswith(f"{lang}_") and fname.endswith(".parquet"):
                try:
                    total += pq.read_metadata(os.path.join(d, fname)).num_rows
                except Exception:
                    pass
    return total


def is_lang_done(dataset_name: str, lang: str) -> bool:
    """Return True only when the language has reached MAX_ROWS_PER_LANG rows."""
    return count_existing_rows(dataset_name, lang) >= MAX_ROWS_PER_LANG


def route_row() -> str:
    """
    Two-step random routing using the global seeded RNG (random.random()).

    Step 1 — global split:
      [0.00, 0.15) -> validation   (15 %)
      [0.15, 0.30) -> evaluation   (15 %)
      [0.30, 1.00) -> knowledge    (70 %)

    Step 2 — knowledge internal split:
      [0.00, 5/7)  -> train        (5/7 × 70 % = 50 % total)
      [5/7,  1.00) -> benchmark    (2/7 × 70 % = 20 % total)
    """
    r = random.random()
    if r < VAL_UPPER:
        return "validation"
    if r < EVAL_UPPER:
        return "evaluation"
    return "train" if random.random() < KNOW_TRAIN else "benchmark"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Shared Row-Processing Core
# ─────────────────────────────────────────────────────────────────────────────

def _process_rows(
    row_iter: Iterator[dict],
    cfg: dict,
    paths: dict,
    fixed_lang: Optional[str],
    lang_counts: dict,
) -> tuple[int, int]:
    """
    Consume row_iter, apply quality filters, route each valid row, and flush
    full buffers.  Returns (seen, kept) counts.

    row_iter must yield dicts with at minimum the keys cfg["text_field"] and
    (when fixed_lang is None) cfg["lang_field"].

    lang_counts is mutated in-place so callers can share saturation state
    across multiple calls.
    """
    buffers: dict = {dest: {} for dest in paths}
    seen = kept = 0

    for row in row_iter:
        seen += 1

        # ── Stochastic stream sampling ───────────────────────────────────────
        if random.random() > STREAM_SAMPLE_RATE:
            continue

        # ── Heartbeat ────────────────────────────────────────────────────────
        if not fixed_lang and seen % HEARTBEAT_INTERVAL == 0:
            saturated = sum(
                1 for l in TARGET_LANGS
                if lang_counts.get(l, 0) >= MAX_ROWS_PER_LANG
            )
            print(f"  [Heartbeat] {seen:,} rows seen — "
                  f"{saturated}/{len(TARGET_LANGS)} languages saturated")

        # ── Filter 1: script-aware truncation (final quality gate) ───────────
        raw_text = row.get(cfg["text_field"], "") or ""
        if not isinstance(raw_text, str):
            continue
        text = safe_truncate(raw_text.strip())
        if text is None:
            continue

        # ── Filter 2: language ───────────────────────────────────────────────
        if fixed_lang:
            lang = fixed_lang
        else:
            lang = normalise_lang(row.get(cfg["lang_field"]))
        if lang not in TARGET_LANGS:
            continue

        # ── Per-language cap ─────────────────────────────────────────────────
        if lang_counts.get(lang, 0) >= MAX_ROWS_PER_LANG:
            continue

        kept += 1
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

        # ── Global saturation exit (mixed-lang streams only) ─────────────────
        if not fixed_lang and all(
            lang_counts.get(l, 0) >= MAX_ROWS_PER_LANG for l in TARGET_LANGS
        ):
            print(f"\n  [SATURATION REACHED] All {len(TARGET_LANGS)} languages "
                  f"have reached {MAX_ROWS_PER_LANG:,} rows after {seen:,} seen "
                  f"rows — exiting stream early.")
            # Flush before break
            _flush_all(buffers, paths)
            return seen, kept

        # ── Route ────────────────────────────────────────────────────────────
        dest = route_row()
        buf  = buffers[dest].setdefault(lang, [])
        buf.append({"text": text, "lang": lang})

        # ── Flush full batches ───────────────────────────────────────────────
        if len(buf) >= BATCH_SIZE:
            flush_buffer(buf, paths[dest], lang)
            buffers[dest][lang] = []

    _flush_all(buffers, paths)
    return seen, kept


def _flush_all(buffers: dict, paths: dict) -> None:
    """Flush every non-empty buffer to disk."""
    for dest, lang_bufs in buffers.items():
        for lang, rows in lang_bufs.items():
            if rows:
                flush_buffer(rows, paths[dest], lang)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Snapshot Download Helper
# ─────────────────────────────────────────────────────────────────────────────

def _try_snapshot_download(cfg: dict, lang_filter: Optional[str] = None) -> Optional[str]:
    """Download parquet files for cfg to SNAPSHOT_CACHE via snapshot_download.

    When lang_filter is provided (a HF config/folder name such as "ca" or "en"),
    only parquet files under that language subfolder are downloaded.  This is
    critical for large multi-language datasets like CulturaX where downloading
    all languages would require several TB.

    Returns the local directory path on success, None on failure.
    Skips the network call if parquet files are already present locally.
    """
    try:
        from huggingface_hub import snapshot_download as _hf_snapshot
    except ImportError:
        return None

    snap_dir = os.path.join(SNAPSHOT_CACHE, cfg["id"].replace("/", "__"))

    # Build allow_patterns: restrict to target language folder when specified
    if lang_filter:
        allow_patterns = [f"{lang_filter}/*.parquet", f"{lang_filter}/**/*.parquet"]
    else:
        allow_patterns = ["*.parquet", "**/*.parquet"]

    # Re-use existing cache without re-downloading
    check_dir = os.path.join(snap_dir, lang_filter) if lang_filter else snap_dir
    if os.path.isdir(check_dir) and any(
        fname.endswith(".parquet")
        for _, _, files in os.walk(check_dir)
        for fname in files
    ):
        print(f"  [Snapshot] Using cached files at {check_dir}")
        return check_dir

    label = f"{cfg['id']!r} [{lang_filter}]" if lang_filter else f"{cfg['id']!r}"
    print(f"  [Snapshot] Downloading parquet files for {label} …")
    try:
        _hf_snapshot(
            repo_id=cfg["id"],
            repo_type="dataset",
            local_dir=snap_dir,
            allow_patterns=allow_patterns,
        )
        print(f"  [Snapshot] Download complete → {check_dir}")
        return check_dir
    except Exception as exc:
        print(f"  [Snapshot] Failed ({exc}) — will use hf:// path")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 7. Primary Path — DuckDB SQL Filtering
# ─────────────────────────────────────────────────────────────────────────────

def _build_duckdb_query(cfg: dict, local_dir: Optional[str] = None) -> str:
    """Return the SQL query string for one (dataset, config) pair.

    When local_dir is provided (snapshot download path), the query reads from
    local parquet files directly — no hive partitioning assumed, no HF token
    required, and the full dataset is available (no 5 GB cap).

    When local_dir is None, falls back to the hf:// protocol against the
    @~parquet export (capped at ~5 GB for large datasets).

    The WHERE clause is a rough pre-filter only; safe_truncate() and
    normalise_lang() remain the authoritative quality gate in Python.
    """
    text_col = cfg["text_field"]
    lang_col = cfg.get("lang_field")
    config   = cfg.get("config")

    if local_dir:
        # Local snapshot: glob all parquet files; language is a real column.
        safe_path = local_dir.replace("\\", "/")
        parquet_glob = f"{safe_path}/**/*.parquet"
        partitioning = "false"
    elif config:
        parquet_glob = f"hf://datasets/{cfg['id']}@~parquet/{config}/**/*.parquet"
        partitioning = "true"
    else:
        parquet_glob = f"hf://datasets/{cfg['id']}@~parquet/**/*.parquet"
        partitioning = "true"

    lang_csv = ", ".join(f"'{c}'" for c in sorted(_SQL_LANG_CODES))

    if lang_col and cfg.get("lang_in_path") and not local_dir:
        # Language encoded as a path segment — only meaningful for hf:// paths.
        lang_pattern = r'@~parquet/([^/]+)/[^/]+/[^/]+\.parquet'
        return (
            f'SELECT "{text_col}", '
            f'  regexp_extract(filename, \'{lang_pattern}\', 1) AS "{lang_col}" '
            f"FROM read_parquet('{parquet_glob}', hive_partitioning=false, filename=true) "
            f'WHERE regexp_extract(filename, \'{lang_pattern}\', 1) IN ({lang_csv}) '
            f'  AND length("{text_col}") >= {CJK_MIN}'
        )
    elif lang_col:
        return (
            f'SELECT "{text_col}", "{lang_col}" '
            f"FROM read_parquet('{parquet_glob}', hive_partitioning={partitioning}) "
            f'WHERE "{lang_col}" IN ({lang_csv}) '
            f'  AND length("{text_col}") >= {CJK_MIN}'
        )
    else:
        # fixed_lang dataset: no language column to filter on
        return (
            f'SELECT "{text_col}" '
            f"FROM read_parquet('{parquet_glob}', hive_partitioning={partitioning}) "
            f'WHERE length("{text_col}") >= {CJK_MIN}'
        )


def duckdb_and_split(cfg: dict, dataset_name: str, fixed_lang: Optional[str] = None) -> bool:
    """
    Primary ingestion path: query the dataset via DuckDB hf:// protocol and
    route valid rows into the four destination directories.

    Returns True on success, False if DuckDB is unavailable or the dataset
    has no Parquet export (so the caller can fall back to streaming).
    """
    try:
        import duckdb  # type: ignore[import-untyped]
    except ImportError:
        print("  [DuckDB] duckdb not installed — falling back to streaming")
        return False

    paths = make_dirs(dataset_name)

    # ── Try snapshot download first (bypasses the 5 GB @~parquet cap) ────────
    local_dir = _try_snapshot_download(cfg, lang_filter=cfg.get("config"))

    # ── Initialise DuckDB connection ──────────────────────────────────────────
    try:
        con = duckdb.connect()
        # Allow DuckDB to spill to disk so large parquet files (e.g. en Wikipedia
        # at 11 GB) don't cause an out-of-memory allocation failure.
        duckdb_tmp = os.path.join(BASE_PATH, "_duckdb_tmp")
        os.makedirs(duckdb_tmp, exist_ok=True)
        con.execute(f"SET temp_directory='{duckdb_tmp.replace(chr(92), '/')}'")
        con.execute("SET memory_limit='4GB'")
        if local_dir is None:
            # httpfs only needed when querying hf:// remote paths
            con.install_extension("httpfs")
            con.load_extension("httpfs")
    except Exception as exc:
        print(f"  [DuckDB] Connection setup failed: {exc} — falling back to streaming")
        return False

    # ── HF token (only required for remote hf:// queries) ────────────────────
    if local_dir is None:
        hf_token = (
            os.environ.get("HUGGING_FACE_HUB_TOKEN")
            or os.environ.get("HF_TOKEN")
        )
        if not hf_token:
            try:
                from huggingface_hub import get_token as _hf_get_token
                hf_token = _hf_get_token()
            except Exception:
                pass
        if not hf_token:
            print("  [DuckDB] No HF token found — falling back to streaming "
                  "(run `huggingface-cli login` or set HF_TOKEN)")
            con.close()
            return False
        try:
            con.execute(
                f"CREATE OR REPLACE SECRET hf_secret ("
                f"  TYPE huggingface, TOKEN '{hf_token}'"
                f")"
            )
        except Exception as exc:
            print(f"  [DuckDB] Could not register HF secret ({exc}) — falling back to streaming")
            con.close()
            return False

    # ── Build and execute query ───────────────────────────────────────────────
    source = "local snapshot" if local_dir else "hf:// remote"
    try:
        sql = _build_duckdb_query(cfg, local_dir=local_dir)
        print(f"  [DuckDB] Executing SQL filter ({source}) …")
        result = con.execute(sql)
    except Exception as exc:
        print(f"  [DuckDB] Query failed: {exc} — falling back to streaming")
        con.close()
        return False

    # ── Seed per-language counters from existing files ────────────────────────
    if fixed_lang:
        existing  = count_existing_rows(dataset_name, fixed_lang)
        remaining = MAX_ROWS_PER_LANG - existing
        if remaining <= 0:
            print(f"  [RESUME] {fixed_lang!r} already complete "
                  f"({existing:,}/{MAX_ROWS_PER_LANG:,} rows) — skipping")
            con.close()
            return True
        if existing > 0:
            print(f"  [RESUME] {fixed_lang!r}: existing={existing:,}  "
                  f"remaining={remaining:,}")
        lang_counts: dict = {}
    else:
        lang_counts = {
            lang: count_existing_rows(dataset_name, lang)
            for lang in TARGET_LANGS
        }

    # ── Fetch in memory-efficient chunks and process ──────────────────────────
    text_col = cfg["text_field"]
    lang_col = cfg.get("lang_field")
    total_seen = total_kept = 0

    try:
        while True:
            chunk: pd.DataFrame = result.fetch_df_chunk(BATCH_SIZE)
            if chunk is None or len(chunk) == 0:
                break

            # Rename columns to the generic keys _process_rows expects
            col_map = {text_col: cfg["text_field"]}
            if lang_col and lang_col in chunk.columns:
                col_map[lang_col] = cfg["lang_field"]
            chunk = chunk.rename(columns=col_map)

            def _chunk_iter(df: pd.DataFrame):
                for row_tuple in df.itertuples(index=False):
                    yield row_tuple._asdict()

            s, k = _process_rows(
                _chunk_iter(chunk), cfg, paths, fixed_lang, lang_counts
            )
            total_seen += s
            total_kept += k

    except Exception as exc:
        print(f"  [DuckDB] Error while fetching chunks: {exc}")
        con.close()
        return False

    con.close()
    print(f"  [{dataset_name}] DuckDB path — seen={total_seen:,}  kept={total_kept:,}")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# 7. Fallback Path — HF Streaming
# ─────────────────────────────────────────────────────────────────────────────

def stream_and_split(cfg: dict, dataset_name: str, fixed_lang: Optional[str] = None) -> None:
    """
    Fallback ingestion path: stream the dataset via the HF datasets API and
    route every valid row into the four destination directories.

    Args:
        cfg:          Entry from DATASETS (shallow copy may override 'config').
        dataset_name: Folder name used under each pool directory.
        fixed_lang:   ISO 639-1 code to assign to every row when the language
                      is implicit in the HF config (no per-row lang_field).
    """
    paths = make_dirs(dataset_name)

    load_kwargs: dict = {"streaming": True}
    if cfg.get("config"):
        load_kwargs["name"] = cfg["config"]
    if cfg.get("trust_remote_code"):
        load_kwargs["trust_remote_code"] = True

    split_streams = []
    for split_name in cfg["splits"]:
        try:
            split_streams.append(load_dataset(cfg["id"], split=split_name, token=True, **load_kwargs))
            print(f"    Loaded split {split_name!r}")
        except Exception as exc:
            print(f"    [WARN] split {split_name!r} unavailable: {exc}")

    if not split_streams:
        print(f"  [SKIP] {cfg['id']} (config={cfg.get('config')!r}): no splits loaded")
        return

    ds = concatenate_datasets(split_streams) if len(split_streams) > 1 else split_streams[0]
    ds = ds.shuffle(buffer_size=10_000, seed=SEED)

    if fixed_lang:
        existing  = count_existing_rows(dataset_name, fixed_lang)
        remaining = MAX_ROWS_PER_LANG - existing
        if remaining <= 0:
            print(f"  [RESUME] {fixed_lang!r} already complete "
                  f"({existing:,}/{MAX_ROWS_PER_LANG:,} rows) — skipping")
            return
        if existing > 0:
            print(f"  [RESUME] {fixed_lang!r}: existing={existing:,}  "
                  f"remaining={remaining:,} — resuming stream")
        ds = ds.skip(existing).take(remaining)
        lang_counts: dict = {}
    else:
        lang_counts = {
            lang: count_existing_rows(dataset_name, lang)
            for lang in TARGET_LANGS
        }

    seen, kept = _process_rows(iter(ds), cfg, paths, fixed_lang, lang_counts)
    print(f"  [{dataset_name}] streaming fallback — seen={seen:,}  kept={kept:,}")


# ─────────────────────────────────────────────────────────────────────────────
# 8. Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def _ingest(cfg: dict, dataset_name: str, fixed_lang: Optional[str] = None) -> None:
    """Try DuckDB first; fall back to streaming on failure.

    Set "stream_only": True in a dataset entry to skip the DuckDB attempt
    entirely (e.g. for datasets whose lang column is a hive partition key
    rather than a real row field).
    """
    if cfg.get("stream_only"):
        stream_and_split(cfg, dataset_name, fixed_lang)
        return
    success = duckdb_and_split(cfg, dataset_name, fixed_lang)
    if not success:
        print(f"  [Fallback] Switching to HF streaming for {cfg['id']!r} …")
        stream_and_split(cfg, dataset_name, fixed_lang)


def main() -> None:
    random.seed(SEED)
    print(f"Seed={SEED}  BATCH_SIZE={BATCH_SIZE:,}  "
          f"CJK {CJK_MIN}-{CJK_MAX} chars  Alpha {ALPHA_MIN}-{ALPHA_MAX} chars")
    print(f"Split: train=50%  benchmark=20%  evaluation=15%  validation=15%")
    print(f"BASE_PATH: {BASE_PATH}\n")

    for cfg in DATASETS:
        # name is optional; fall back to the repo portion of the HF id
        dataset_name = cfg.get("name") or cfg["id"].split("/")[-1]
        sep = "=" * 66
        print(f"\n{sep}")
        print(f"  Dataset : {cfg['id']}")
        print(f"  Folder  : {dataset_name}")
        print(sep)

        if cfg.get("lang_configs"):
            for iso_lang, hf_config in cfg["lang_configs"].items():
                if is_lang_done(dataset_name, iso_lang):
                    print(f"  [CHECKPOINT] {iso_lang!r} already complete — skipping")
                    continue
                print(f"  -> config={hf_config!r}  fixed_lang={iso_lang!r}")
                sub_cfg = {**cfg, "config": hf_config}
                _ingest(sub_cfg, dataset_name, fixed_lang=iso_lang)
        elif cfg.get("lang_splits"):
            for iso_lang, hf_split in cfg["lang_splits"].items():
                if is_lang_done(dataset_name, iso_lang):
                    print(f"  [CHECKPOINT] {iso_lang!r} already complete — skipping")
                    continue
                print(f"  -> split={hf_split!r}  fixed_lang={iso_lang!r}")
                sub_cfg = {**cfg, "splits": [hf_split]}
                _ingest(sub_cfg, dataset_name, fixed_lang=iso_lang)
        else:
            _ingest(cfg, dataset_name)


if __name__ == "__main__":
    main()
