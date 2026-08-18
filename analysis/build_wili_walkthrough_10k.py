"""Build the 10,000-document WiLI-2018 walkthrough sample.

Supersedes the 600-document draw (``wili2018_walkthrough_600.csv``) used by the
first recorded session. Rationale, measured 2026-08-17:

  The DeepProfiler builds each language column of the fingerprint by AVERAGING
  meta-features over at most ``MAX_SAMPLES = 100`` documents of that language
  (profiler_knowledge_base.py, ``_profile_user_mode``). The 17 MKB corpora were
  profiled by ``_profile_building_mode`` from pooled sources large enough that
  every column saturated that cap. At 600 documents the WiLI query fingerprint
  had a MEDIAN of 6 documents per column (min 1, max 47) and NO column reached
  the cap, so the query side of every distance computation was dominated by
  sampling noise.

  Measured group sizes at this 10,000-document draw: 10 of 24 columns reach the
  100 cap, min 40, median 80.

WiLI-2018 spans 235 languages and the profiler characterises 24, so ~38% of any
draw lands in a profilable group; the rest is discarded as out of scope. That is
the honest deployment picture and is preserved deliberately — no label-based
filtering is applied, and no WiLI labels are read (only ``x_test`` is on disk).

10,000 is the ceiling that matters: ``_profile_user_mode`` snapshots at most
``SNAPSHOT_SIZE = 10_000`` rows for the census, so a larger CSV would not enlarge
the profiling groups.

Usage (thesis_final env, from the repo root):
    python analysis/build_wili_walkthrough_10k.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

TK = Path(__file__).resolve().parents[1]
SRC = TK / "test_examples" / "wili2018_test.txt"
OUT = TK / "test_examples" / "wili2018_walkthrough_10k.csv"

N = 10_000
SEED = 42
MIN_LEN = 30  # same length gate as the original 600-document draw


def main() -> int:
    lines = [l.strip() for l in SRC.read_text(encoding="utf-8").splitlines()
             if len(l.strip()) > MIN_LEN]
    print(f"{SRC.name}: {len(lines):,} usable lines (> {MIN_LEN} chars)")

    if len(lines) < N:
        sys.exit(f"only {len(lines)} usable lines; need {N}")

    sample = pd.Series(lines).sample(n=N, random_state=SEED).reset_index(drop=True)
    pd.DataFrame({"text": sample}).to_csv(OUT, index=False, encoding="utf-8")

    print(f"wrote {len(sample):,} rows (seed={SEED}) -> {OUT}")
    print(f"  unique texts: {sample.nunique():,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
