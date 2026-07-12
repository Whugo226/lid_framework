"""R13: end-to-end wall-clock of the production DeepProfiler (user mode).

Same corpus as the annotation benchmark: 100 europarl evaluation segments per
language, five languages (en/nl/de/es/fi), shuffled into one unlabelled series.
Times run_profile(mode="user"), i.e. fastText census + routing + spaCy
annotation + full measure extraction/aggregation, exactly as an interactive
user would experience it. Run from the toolkit root so fasttext_cache resolves.
"""
import json
import pathlib
import sys
import time

import pandas as pd

TK = pathlib.Path(r"c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit")
EURO = pathlib.Path(r"c:/Users/User/OneDrive/Masters/LID_experiments/datasets/02_evaluation_15_cleaned/europarl")
SC = pathlib.Path(__file__).parent
sys.path.insert(0, str(TK / "src"))

LANGS = ["en", "nl", "de", "es", "fi"]
N = 100
SEED = 42

texts = []
for lang in LANGS:
    f = sorted(EURO.glob(f"{lang}_*.parquet"))[0]
    df = pd.read_parquet(f)
    texts.extend(df["text"].dropna().astype(str).sample(N, random_state=SEED).tolist())
series = pd.Series(texts).sample(frac=1.0, random_state=SEED).reset_index(drop=True)
print(f"corpus: {len(series)} segments, {len(LANGS)} languages", flush=True)

from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler

t_init0 = time.perf_counter()
prof = DeepProfiler()
t_init = time.perf_counter() - t_init0
print(f"DeepProfiler init (lid.176 load): {t_init:.1f}s", flush=True)

t0 = time.perf_counter()
result = prof.run_profile(mode="user", text_series=series)
t_total = time.perf_counter() - t0

out = {"init_seconds": t_init, "profile_seconds": t_total,
       "languages": sorted(result.columns.tolist()),
       "n_features": int(result.shape[0]), "n_segments": int(len(series))}
(SC / "r13_timing.json").write_text(json.dumps(out, indent=2))
print(f"\nEND-TO-END profile time: {t_total:.1f}s "
      f"({result.shape[1]} languages x <=100 segments; {result.shape[0]} features)", flush=True)
