"""corpus_eda.py — Chapter 4 corpus portfolio characterisation (fig:corpus_eda
+ tab:corpus_summary).

Walks the 17 knowledge-benchmark splits (01b — the splits profiled into the
MKB) and computes, per corpus: row count, in-scope language count, and the
distribution of whitespace tokens per document. Emits:

  1. figures/corpus_eda.pdf — median + IQR of tokens/document per corpus,
     sorted by median (log-scale x axis).
  2. LaTeX rows for tab:corpus_summary printed to stdout.

Usage:  python analysis/corpus_eda.py
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(r"c:/Users/User/OneDrive/Masters/LID_experiments/datasets/01b_knowledge_benchmark_20_cleaned")
FIG_OUT = Path(r"C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/figures/corpus_eda.pdf")
SAMPLE_PER_LANG = 20_000
SEED = 42

DISPLAY = {
    "OpenLID-v2": "OpenLID-v2",
    "amazon_reviews_multi": "Amazon Reviews",
    "europarl": "Europarl",
    "exorde-social-media-december-2024-week1": "Exorde Social Media",
    "flores_plus": "FLORES+",
    "language-identification": "Language Identification",
    "massive": "MASSIVE",
    "mmarco": "MMARCO",
    "multi_eurlex": "Multi EurLex",
    "multilingual_cc_news": "Multilingual CC News",
    "multilingual_toxicity_dataset": "Multilingual Toxicity",
    "stsb_multi_mt": "STS-B Multi MT",
    "tweet_sentiment_multilingual": "Tweet Sentiment",
    "tydiqa": "TyDiQA",
    "wikipedia": "Wikipedia",
    "xlsum": "XLSum",
    "xnli": "XNLI",
}


def main() -> None:
    import pyarrow.parquet as pq

    rows = []
    for ds, label in DISPLAY.items():
        ds_dir = DATA / ds
        files = sorted(ds_dir.glob("*.parquet"))
        langs = sorted({m.group(1) for f in files
                        if (m := re.match(r"^([a-z]{2,3})_", f.stem))})
        n_rows = sum(pq.read_metadata(f).num_rows for f in files)

        # Characters are tracked alongside whitespace tokens because
        # str.split() does not segment unsegmented scripts: a 40-character
        # Chinese or Japanese document counts as one or two tokens, which
        # depresses the token statistics of every corpus carrying zh/ja.
        # Characters are script-neutral and are the quantity the ingestion
        # pipeline actually caps (120 alphabetic / 40 CJK).
        tokens, chars = [], []
        for f in files:
            col = pd.read_parquet(f, columns=["text"])["text"].dropna().astype(str)
            if len(col) > SAMPLE_PER_LANG:
                col = col.sample(SAMPLE_PER_LANG, random_state=SEED)
            tokens.extend(col.str.split().str.len().tolist())
            chars.extend(col.str.len().tolist())
        arr = np.array(tokens)
        carr = np.array(chars)
        rows.append({
            "label": label, "langs": len(langs), "rows": n_rows,
            "q1": float(np.percentile(arr, 25)),
            "med": float(np.median(arr)),
            "q3": float(np.percentile(arr, 75)),
            "cmed": float(np.median(carr)),
        })
        print(f"done {label:26s} rows={n_rows:>8,d} langs={len(langs):2d} "
              f"chars median={np.median(carr):.0f}  "
              f"tokens median={np.median(arr):.0f} IQR=[{rows[-1]['q1']:.0f},{rows[-1]['q3']:.0f}]")

    rows.sort(key=lambda r: r["med"])

    # ── Figure: median + IQR per corpus ──────────────────────────────────────
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.5, 6))
    y = np.arange(len(rows))
    for i, r in enumerate(rows):
        ax.plot([r["q1"], r["q3"]], [i, i], color="gray", lw=5, alpha=0.45,
                solid_capstyle="butt", zorder=1)
        ax.plot(r["med"], i, "o", color="black", ms=5, zorder=2)
    ax.set_yticks(y, [r["label"] for r in rows], fontsize=9)
    ax.set_xscale("log")
    ax.set_xlabel("Whitespace tokens per document (log scale; dot = median, bar = IQR)")
    ax.grid(axis="x", linestyle="--", color="gray", alpha=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()
    FIG_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_OUT)
    print(f"\nfigure -> {FIG_OUT}")

    # ── LaTeX table rows ──────────────────────────────────────────────────────
    print("\n% tab:corpus_summary rows (sorted by median tokens/document):")
    for r in rows:
        print(f"{r['label']} & {r['langs']} & {r['rows']:,} & {r['cmed']:.0f} & "
              f"{r['med']:.0f} & [{r['q1']:.0f}, {r['q3']:.0f}] \\\\ \\hline")


if __name__ == "__main__":
    main()
