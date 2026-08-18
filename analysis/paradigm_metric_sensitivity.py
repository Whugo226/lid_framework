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
The sweep is computed on the EVALUATION split, the same partition as every
other result in Chapter 5. Three sources appear below and they are NOT
interchangeable:

  * model_benchmarking_evaluation/ — the EVALUATION split, read directly from
                                     the raw benchmark_metadata.json files
                                     (17 corpora x 105 variants = 1,785 files,
                                     each carrying all 11 metrics including
                                     latency and throughput). This is the
                                     PRIMARY basis: metric sweep and
                                     inference cost both come from here.
  * MKB records (mkb.pkl)          — the knowledge-BENCHMARKING split, also
                                     carrying all 11 metrics. Retained only so
                                     the two bases can be compared; the
                                     knowledge split is NOT the reporting basis.
  * validation_report.json         — the EVALUATION split reduced to
                                     f1_weighted alone. It is the basis for the
                                     thesis's "13 of 17" paradigm figure, and
                                     is kept for reconciliation against the
                                     f1_weighted column of the primary sweep.

CORRECTED 2026-08-17: an earlier version of this script, and the Chapter 5
paragraph that quoted it, stated that the knowledge split was "the only
source/partition carrying every metric". That is false. All three benchmark
archives record the same 11 metrics in every file; only the DERIVED artifact
validation_report.json discards the other 10 at write time. The sweep is
therefore now computed on the evaluation split directly.

HARDWARE ASYMMETRY (re-verified on the evaluation tree 2026-08-17)
------------------------------------------------------------------
XLM-V Base was benchmarked on GPU:
  model_benchmarking_evaluation/xlm_v_base/benchmark_run.log
  "Device: cuda  (Quadro RTX 4000)"
FastText, Naive Bayes, Logistic Regression and CLD3 have no CUDA references
anywhere in model_benchmarking_evaluation/ and are CPU-native libraries. The
same asymmetry holds in the knowledge tree. The latency comparison therefore gives the transformer a
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

MASTERS = REPO.parents[2]  # .../OneDrive/Masters/
EVAL_BENCH_DIR = MASTERS / "LID_experiments" / "model_benchmarking_evaluation"


def load_archive(bench_dir: Path) -> dict[str, dict[str, dict[str, float]]]:
    """
    perf[dataset][variant] = {metric: value}, read straight from the raw
    benchmark_metadata.json files so that every recorded metric survives.
    Layout: {family}/{dataset}/{variant}/benchmark_metadata.json
    """
    perf: dict[str, dict[str, dict[str, float]]] = {}
    for path in bench_dir.glob("*/*/*/benchmark_metadata.json"):
        dataset = path.parent.parent.name
        variant = path.parent.name
        blob = json.loads(path.read_text(encoding="utf-8"))
        metrics = blob.get("metrics", blob)
        perf.setdefault(dataset, {})[variant] = {
            k: v for k, v in metrics.items() if isinstance(v, (int, float))
        }
    return perf


def sweep_metrics(perf: dict[str, dict[str, dict[str, float]]], family, paradigm) -> dict:
    """Per-metric winner counts over the corpora of one benchmark archive."""
    all_metrics = set()
    for by_variant in perf.values():
        for m in by_variant.values():
            all_metrics |= set(m)
    result = {}
    for metric in sorted(all_metrics - SKIP_METRICS):
        by_family = collections.Counter()
        by_paradigm = collections.Counter()
        for by_variant in perf.values():
            cand = {v: m[metric] for v, m in by_variant.items() if metric in m}
            if not cand:
                continue
            pick = min if metric in LOWER_IS_BETTER else max
            best = pick(cand, key=cand.get)
            by_family[family(best)] += 1
            by_paradigm[paradigm(best)] += 1
        result[metric] = {
            "lower_is_better": metric in LOWER_IS_BETTER,
            "wins_by_family": dict(by_family),
            "wins_by_paradigm": dict(by_paradigm),
        }
    return result


def inference_cost(perf, arch) -> dict:
    """Median ms/sample per architecture, and its multiple of the fastest."""
    lat = collections.defaultdict(list)
    for by_variant in perf.values():
        for v, m in by_variant.items():
            if "inference_time_ms_per_sample" in m:
                lat[arch(v)].append(m["inference_time_ms_per_sample"])
    med = {a: st.median(x) for a, x in lat.items()}
    fastest = min(med.values())
    return {
        a: {
            "median_ms_per_sample": round(v, 4),
            "relative_to_fastest": round(v / fastest, 1),
            "paradigm": "TML" if a in TML_ARCHITECTURES else "DL",
            "family": FAMILY.get(a, a),
        }
        for a, v in sorted(med.items(), key=lambda kv: kv[1])
    }


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

    # ── (1) PRIMARY: sweep + inference cost on the EVALUATION split ─────────
    eval_perf = load_archive(EVAL_BENCH_DIR)
    eval_sweep = sweep_metrics(eval_perf, family, paradigm)
    eval_latency = inference_cost(eval_perf, arch)

    # ── (2) Knowledge split, retained only so the bases can be compared ─────
    mkb_perf = {d: dict(store.get_entry(d).performances) for d in corpora}
    mkb_sweep = sweep_metrics(mkb_perf, family, paradigm)
    mkb_latency = inference_cost(mkb_perf, arch)

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
            "PRIMARY basis is the evaluation split, read directly from "
            "model_benchmarking_evaluation/ (1,785 benchmark_metadata.json "
            "files, all 11 metrics present in every one). The knowledge-split "
            "blocks are retained for comparison only. All three archives carry "
            "every metric; only the derived artifact validation_report.json is "
            "reduced to f1_weighted, and it is used solely to reconcile the "
            "thesis's 13-of-17 paradigm figure."
        ),
        "hardware_note": (
            "XLM-V Base benchmarked on GPU (Quadro RTX 4000, per "
            "model_benchmarking_evaluation/xlm_v_base/benchmark_run.log). "
            "FastText, MNB, LR and CLD3 are CPU-native with no GPU references "
            "in the evaluation tree. Latency margins against the transformer "
            "are therefore lower bounds."
        ),
        "n_corpora": len(corpora),
        "n_corpora_evaluation_archive": len(eval_perf),
        "n_variants_per_corpus_evaluation_archive": sorted(
            {len(v) for v in eval_perf.values()}
        ),
        "metric_sweep_evaluation_basis": eval_sweep,
        "inference_cost_by_architecture_evaluation_basis": eval_latency,
        "metric_sweep_mkb_basis": mkb_sweep,
        "inference_cost_by_architecture_mkb_basis": mkb_latency,
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
