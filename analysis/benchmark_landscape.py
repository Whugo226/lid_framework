"""
benchmark_landscape.py — Chapter 4 "performance landscape" statistics (EQ1).

Walks every benchmark_metadata.json under LID_experiments/model_benchmarking_knowledge
(the knowledge-side cross-benchmark that populates the MKB) and computes:

  1. Per model configuration: in-domain (train == eval) vs cross-domain f1_weighted.
  2. Zero-shot off-the-shelf models: per-model f1_weighted across evaluation datasets.
  3. Best variant per evaluation dataset and paradigm winner counts.
  4. Inference latency / throughput per configuration.
  5. A 17x17 train-by-eval transfer heatmap for fasttext_subword (saved as PDF).

librispeech_asr is excluded (outside the 17-dataset portfolio).

Usage:  conda run -n thesis_final python analysis/benchmark_landscape.py
"""
import json
import statistics
from collections import defaultdict
from pathlib import Path

BENCH = Path(r"c:/Users/User/OneDrive/Masters/LID_experiments/model_benchmarking_knowledge")
FIG_OUT = Path(r"C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/figures/benchmark_transfer_heatmap.pdf")
EXCLUDE = {"librispeech_asr"}
SKIP_DIRS = {"mlruns", "__pycache__"}

CONFIG_LABELS = {
    "bow_char_ngram_3_5":           "MNB BoW (char 3-5)",
    "tfidf_char_ngram_3_5":         "MNB TF-IDF (char 3-5)",
    "bow_maxabs_lr_char_ngram_3_5": "LR BoW+MaxAbs (char 3-5)",
    "tfidf_lr_char_ngram_3_5":      "LR TF-IDF (char 3-5)",
    "fasttext_word":                "FastText word",
    "fasttext_subword":             "FastText subword",
}
TML = {"bow_char_ngram_3_5", "tfidf_char_ngram_3_5",
       "bow_maxabs_lr_char_ngram_3_5", "tfidf_lr_char_ngram_3_5"}

SHORT = {
    "OpenLID-v2": "openlid", "amazon_reviews_multi": "amazon", "europarl": "europarl",
    "exorde-social-media-december-2024-week1": "exorde", "flores_plus": "flores",
    "language-identification": "lang-id", "massive": "massive", "mmarco": "mmarco",
    "multi_eurlex": "eurlex", "multilingual_cc_news": "cc-news",
    "multilingual_toxicity_dataset": "toxicity", "stsb_multi_mt": "stsb",
    "tweet_sentiment_multilingual": "tweet", "tydiqa": "tydiqa",
    "wikipedia": "wikipedia", "xlsum": "xlsum", "xnli": "xnli",
}


def load_records():
    records = []
    for mf in BENCH.rglob("benchmark_metadata.json"):
        if any(s in mf.parts for s in SKIP_DIRS):
            continue
        meta = json.loads(mf.read_text())
        eval_ds = meta.get("dataset")
        train_ds = meta.get("training_dataset")
        variant = meta.get("variant") or mf.parent.name
        if eval_ds in EXCLUDE or train_ds in EXCLUDE:
            continue
        m = meta.get("metrics", {})
        if train_ds:
            config = variant[: -(len(train_ds) + 1)] if variant.endswith("_" + train_ds) else variant
        elif variant.startswith("cld3"):
            config, train_ds = "cld3", None
        elif variant.startswith("lid.176"):
            config, train_ds = "lid.176", None
        elif variant.startswith("xlm_v_base"):
            config, train_ds = "xlm_v_base", None
        else:
            config = variant
        records.append({
            "eval": eval_ds, "train": train_ds, "config": config, "variant": variant,
            "f1w": m.get("f1_weighted"), "ms": m.get("inference_time_ms_per_sample"),
            "tput": m.get("throughput_samples_per_sec"),
        })
    return [r for r in records if r["f1w"] is not None]


def main():
    recs = load_records()
    evals = sorted({r["eval"] for r in recs})
    print(f"records = {len(recs)}, eval datasets = {len(evals)}")

    # ── 1. trained configs: in-domain vs cross-domain ────────────────────────
    print("\n[1] Trained configurations — f1_weighted")
    print(f"{'config':30s} {'in-dom mean':>11s} {'in-dom min':>10s} "
          f"{'x-dom mean':>10s} {'x-dom sd':>9s} {'x-dom min':>9s}")
    for cfg, label in CONFIG_LABELS.items():
        ind = [r["f1w"] for r in recs if r["config"] == cfg and r["train"] == r["eval"]]
        xd = [r["f1w"] for r in recs if r["config"] == cfg
              and r["train"] and r["train"] != r["eval"]]
        print(f"{label:30s} {statistics.mean(ind):11.4f} {min(ind):10.4f} "
              f"{statistics.mean(xd):10.4f} {statistics.stdev(xd):9.4f} {min(xd):9.4f}"
              f"   (n_in={len(ind)}, n_x={len(xd)})")

    # ── 2. off-the-shelf zero-shot ────────────────────────────────────────────
    print("\n[2] Off-the-shelf zero-shot — f1_weighted across evaluation datasets")
    for cfg in ("cld3", "lid.176", "xlm_v_base"):
        vals = [r["f1w"] for r in recs if r["config"] == cfg]
        print(f"{cfg:12s} mean {statistics.mean(vals):.4f}  "
              f"min {min(vals):.4f}  max {max(vals):.4f}  (n={len(vals)})")

    # ── 3. best variant per evaluation dataset ───────────────────────────────
    print("\n[3] Best variant per evaluation dataset (f1_weighted)")
    winners = defaultdict(int)
    for ev in evals:
        rows = [r for r in recs if r["eval"] == ev]
        best = max(rows, key=lambda r: r["f1w"])
        paradigm = ("TML" if best["config"] in TML
                    else "FastText" if best["config"].startswith("fasttext_")
                    else "OTS")
        winners[paradigm] += 1
        indom = "in-domain" if best["train"] == ev else (
            "zero-shot" if best["train"] is None else f"trained on {SHORT.get(best['train'], best['train'])}")
        print(f"  {SHORT.get(ev, ev):10s} {best['f1w']:.4f}  {best['variant']}  [{paradigm}, {indom}]")
    print(f"  paradigm winner counts: {dict(winners)}")
    n_indom = sum(1 for ev in evals
                  if max((r for r in recs if r['eval'] == ev), key=lambda r: r['f1w'])['train'] == ev)
    print(f"  best model is the in-domain-trained variant in {n_indom}/{len(evals)} datasets")

    # ── 4. latency / throughput ───────────────────────────────────────────────
    print("\n[4] Inference latency (median across all evaluations)")
    for cfg in list(CONFIG_LABELS) + ["cld3", "lid.176", "xlm_v_base"]:
        ms = [r["ms"] for r in recs if r["config"] == cfg and r["ms"] is not None]
        tp = [r["tput"] for r in recs if r["config"] == cfg and r["tput"] is not None]
        if ms:
            print(f"  {cfg:30s} {statistics.median(ms):10.4f} ms/sample   "
                  f"{statistics.median(tp):12.0f} samples/s")

    # ── 5. fasttext_subword transfer heatmap ─────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        mat = np.full((len(evals), len(evals)), np.nan)
        for r in recs:
            if r["config"] == "fasttext_subword" and r["train"] in evals:
                mat[evals.index(r["train"]), evals.index(r["eval"])] = r["f1w"]
        labels = [SHORT.get(e, e) for e in evals]
        fig, ax = plt.subplots(figsize=(9.5, 8))
        im = ax.imshow(mat, cmap="viridis", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(labels)), labels, rotation=90, fontsize=8)
        ax.set_yticks(range(len(labels)), labels, fontsize=8)
        ax.set_xlabel("Evaluation dataset")
        ax.set_ylabel("Training dataset")
        for i in range(len(labels)):
            for j in range(len(labels)):
                if not np.isnan(mat[i, j]):
                    ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center",
                            fontsize=5.5,
                            color="white" if mat[i, j] < 0.6 else "black")
        fig.colorbar(im, ax=ax, label="Weighted F1")
        fig.tight_layout()
        FIG_OUT.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIG_OUT)
        print(f"\n[5] heatmap saved -> {FIG_OUT}")
        diag = np.nanmean(np.diag(mat))
        off = np.nanmean(mat[~np.eye(len(evals), dtype=bool)])
        print(f"    fasttext_subword: diagonal mean {diag:.4f}, off-diagonal mean {off:.4f}")
    except ImportError:
        print("\n[5] matplotlib unavailable — heatmap skipped")


if __name__ == "__main__":
    main()
