"""
paradigm_metric_sensitivity.py

Tests whether the TML-versus-neural result is an artefact of having chosen
weighted F1 as the priority metric, and resolves what the "neural" winners
actually are.

WHY THIS EXISTS
---------------
Two open questions about the paradigm framing:

  (1) METRIC SENSITIVITY. Chapter 1 motivates the framework by a trade-off
      between the computational efficiency of traditional methods and the
      robustness of deep architectures. The evaluation optimises f1_weighted,
      which measures only the robustness side. If the paradigm winner flips
      under an efficiency metric, the TML-vs-DL framing is vindicated and the
      published result is simply metric-specific. This script sweeps every
      metric stored in the MKB, including inference latency and throughput.

  (2) WHAT COUNTS AS "DL". analysis/paradigm_regret.py assigns FastText to the
      deep-learning paradigm. FastText is a linear classifier over averaged
      word- and subword-embeddings — Joulin et al. (2017) position it as a fast
      *linear* baseline that rivals deep learning, not as deep learning, and
      methodology_chapter.tex:119 calls it "a strong neural baseline" rather
      than a deep one. This script therefore reports a four-way architecture
      breakdown alongside the binary split, so the composition of the "DL" wins
      is visible rather than assumed.

DATA BASIS — read before quoting any number
--------------------------------------------
Two different sources are used and they are NOT interchangeable:

  * MKB records (mkb.pkl)          — the knowledge-BENCHMARKING split. This is
                                     the only source carrying all metrics,
                                     including latency, so the metric sweep and
                                     the inference-cost table come from here.
  * validation_report.json         — the EVALUATION split, f1_weighted only.
                                     This is the basis for the thesis's
                                     "13 of 17" paradigm figure, so the
                                     eval-split breakdown is reported from here
                                     for reconciliation.

HARDWARE ASYMMETRY (verified 2026-07-20, favours the transformer)
------------------------------------------------------------------
XLM-V Base was benchmarked on GPU:
  model_benchmarking_knowledge/xlm_v_base/benchmark_run.log
  "Device: cuda  (Quadro RTX 4000)"
FastText, Naive Bayes, Logistic Regression and CLD3 have no CUDA or SBATCH
--gres=gpu references anywhere in model_benchmarking_knowledge/ and are
CPU-native libraries. The latency comparison therefore gives the transformer a
hardware advantage the others did not have; any margin against it is a lower
bound.

Reads only committed artifacts; writes a dated JSON snapshot. Modifies nothing.

Run (repo root, thesis_final):
    python analysis/paradigm_metric_sensitivity.py
"""
from __future__ import annotations

import collections
import json
import statistics as st
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lid_toolkit.recommender.mkb_store import MKBStore  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

# Paradigm assignment as used by analysis/paradigm_regret.py (methodology_chapter.tex:119)
TML_ARCHITECTURES = {
    "bow_char_ngram_3_5",
    "tfidf_char_ngram_3_5",
    "bow_maxabs_lr_char_ngram_3_5",
    "tfidf_lr_char_ngram_3_5",
}

# Finer breakdown: separates shallow-neural from genuinely deep architectures.
FAMILY = {
    "bow_char_ngram_3_5": "TML (char n-gram, MNB)",
    "tfidf_char_ngram_3_5": "TML (char n-gram, MNB)",
    "bow_maxabs_lr_char_ngram_3_5": "TML (char n-gram, LR)",
    "tfidf_lr_char_ngram_3_5": "TML (char n-gram, LR)",
    "fasttext_word": "FastText (shallow neural, trained)",
    "fasttext_subword": "FastText (shallow neural, trained)",
    "lid.176": "FastText lid.176 (shallow neural, zero-shot)",
    "cld3": "CLD3 (neural n-gram, zero-shot)",
    "xlm_v_base_language_id": "XLM-V Base (transformer, zero-shot)",
}

LOWER_IS_BETTER = {"inference_time_total_s", "inference_time_ms_per_sample"}
SKIP_METRICS = {"n_samples"}


def make_arch(corpora: list[str]):
    ordered = sorted(corpora, key=len, reverse=True)

    def arch(key: str) -> str:
        for c in ordered:
            if key.endswith("_" + c):
                return key[: -(len(c) + 1)]
        return key

    return arch


def main() -> None:
    store = MKBStore.load(REPO / "mkb.pkl")
    corpora = list(store.datasets)
    arch = make_arch(corpora)
    family = lambda k: FAMILY.get(arch(k), arch(k))  # noqa: E731
    paradigm = lambda k: "TML" if arch(k) in TML_ARCHITECTURES else "DL"  # noqa: E731

    # ── (1) Metric sweep over the MKB (knowledge-benchmarking split) ─────────
    all_metrics = set()
    for d in corpora:
        for perfs in store.get_entry(d).performances.values():
            all_metrics |= set(perfs)
    metrics = sorted(all_metrics - SKIP_METRICS)

    sweep = {}
    for m in metrics:
        by_family = collections.Counter()
        by_paradigm = collections.Counter()
        for d in corpora:
            cand = {
                v: p[m] for v, p in store.get_entry(d).performances.items() if m in p
            }
            if not cand:
                continue
            best = min(cand, key=cand.get) if m in LOWER_IS_BETTER else max(cand, key=cand.get)
            by_family[family(best)] += 1
            by_paradigm[paradigm(best)] += 1
        sweep[m] = {
            "lower_is_better": m in LOWER_IS_BETTER,
            "wins_by_family": dict(by_family),
            "wins_by_paradigm": dict(by_paradigm),
        }

    # ── (2) Inference cost by architecture (MKB basis) ──────────────────────
    lat = collections.defaultdict(list)
    for d in corpora:
        for v, p in store.get_entry(d).performances.items():
            if "inference_time_ms_per_sample" in p:
                lat[arch(v)].append(p["inference_time_ms_per_sample"])
    med = {a: st.median(x) for a, x in lat.items()}
    fastest = min(med.values())
    latency = {
        a: {
            "median_ms_per_sample": round(v, 4),
            "relative_to_fastest": round(v / fastest, 1),
            "paradigm": "TML" if a in TML_ARCHITECTURES else "DL",
            "family": FAMILY.get(a, a),
        }
        for a, v in sorted(med.items(), key=lambda kv: kv[1])
    }

    # ── (3) Eval-split reconciliation (f1_weighted only) ────────────────────
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    eval_bench = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}
    eval_family = collections.Counter()
    eval_paradigm = collections.Counter()
    xlm_ranks = []
    for d, scores in eval_bench.items():
        best = max(scores, key=scores.__getitem__)
        eval_family[family(best)] += 1
        eval_paradigm[paradigm(best)] += 1
        x = scores["xlm_v_base_language_id"]
        xlm_ranks.append(sum(1 for v in scores.values() if v > x + 1e-12) + 1)

    out = {
        "generated": str(date.today()),
        "basis_note": (
            "Metric sweep and latency come from mkb.pkl (knowledge-benchmarking "
            "split, the only source carrying all metrics). The eval-split block "
            "comes from validation_report.json (f1_weighted only) and is the "
            "basis for the thesis's 13-of-17 paradigm figure."
        ),
        "hardware_note": (
            "XLM-V Base benchmarked on GPU (Quadro RTX 4000, per "
            "model_benchmarking_knowledge/xlm_v_base/benchmark_run.log). FastText, "
            "MNB, LR and CLD3 are CPU-native with no GPU references in the "
            "benchmarking tree. Latency margins against the transformer are "
            "therefore lower bounds."
        ),
        "n_corpora": len(corpora),
        "metric_sweep_mkb_basis": sweep,
        "inference_cost_by_architecture_mkb_basis": latency,
        "evaluation_split_f1_weighted": {
            "wins_by_family": dict(eval_family),
            "wins_by_paradigm": dict(eval_paradigm),
            "xlm_v_rank_per_corpus": xlm_ranks,
            "xlm_v_best_rank": min(xlm_ranks),
            "xlm_v_median_rank": st.median(xlm_ranks),
            "n_candidates": len(next(iter(eval_bench.values()))),
        },
    }

    stamp = date.today().isoformat()
    dest = REPO / "analysis" / f"paradigm_metric_sensitivity_{stamp}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
