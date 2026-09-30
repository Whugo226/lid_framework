"""
paradigm_regret.py

Quantifies how much the TML-versus-DL paradigm choice actually costs on the 17
held-out evaluation datasets, and whether the framework discriminates between
the two paradigms at all.

DO NOT QUOTE THE "corpus_excluded" SCENARIO AS LEAVE-ONE-CORPUS-OUT
-------------------------------------------------------------------
The ``corpus_excluded`` scenario below drops the held-out corpus from the k-NN
candidate pool only.  It reuses the single FeatureStratifier fitted on all 17
corpora, so the PCA coordinate system still carries knowledge of the "excluded"
corpus.  It is therefore NOT a clean leave-one-corpus-out estimate and must not
be reported as one.  The clean estimate refits the stratifier per fold and lives
in ``analysis/corpus_exclusion_refit.py``; it is what ``reporting_measures.py``
reads for condition C, and it is the artifact of record for any LOO claim.

The LaTeX table this script emits (``paradigm_regret_table.tex``, embedded in
Chapter 5) is unaffected: the per-paradigm best scores are read straight off the
benchmark performance matrix and involve neither the recommender nor the PCA
projection.

WHY THIS EXISTS
---------------
Chapter 1 frames the research question as mapping operational context to the
"near-optimal model paradigm" between two architectural paradigms (TML and DL).
This script tests that framing empirically. It answers three questions:

  (1) How large is the paradigm decision?  For each evaluation dataset it
      computes the best TML score and the best DL score, and the gap between
      them.  The mean gap over datasets where TML wins is the cost a
      practitioner incurs by always choosing DL.

  (2) Does the framework discriminate paradigms?  It records the paradigm of
      each recommendation and compares the framework's paradigm accuracy
      against the MAJORITY-CLASS BASELINE (always guess the more common
      paradigm).  A framework that merely tracks the base rate carries no
      paradigm signal, however high its raw accuracy looks.

  (3) Is the answer robust to corpus re-identification?  The recorded
      evaluation queries the MKB with a fresh split of a corpus the MKB
      already contains.  The script therefore repeats (2) under a
      CORPUS-EXCLUSION condition, where the query corpus's own entry is
      removed from the MKB before the query, so the framework must generalise
      from the other 16 corpora.

  NOTE ON TERMINOLOGY: the corpus-exclusion condition is a supplementary
  diagnostic, NOT the thesis's validation protocol.  The validation protocol is
  held-out sample validation.  Do not describe either as "leave-one-out".

Paradigm assignment follows Chapter 3 (methodology_chapter.tex:119): the
character n-gram Multinomial Naive Bayes and Logistic Regression configurations
are TML; FastText (word and subword), CLD3, lid.176 and XLM-V Base are neural.

Reads only committed artifacts (validation_report.json, mkb.pkl, eval_profiles/);
writes a dated JSON snapshot and a LaTeX table.  Modifies nothing else.

Run (repo root, thesis_final):
    python analysis/paradigm_regret.py [--no-exclusion]
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics as st
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402
from lid_toolkit.recommender import Recommender  # noqa: E402
from corpus_names import display  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

# Architectures trained/benchmarked in the candidate pool, by paradigm.
# Source: chapters/methodology_chapter.tex:119 (three trained families in six
# configurations) plus the three off-the-shelf zero-shot detectors.
TML_ARCHITECTURES = {
    "bow_char_ngram_3_5",             # Multinomial Naive Bayes, bag-of-words
    "tfidf_char_ngram_3_5",           # Multinomial Naive Bayes, TF-IDF
    "bow_maxabs_lr_char_ngram_3_5",   # Logistic Regression, bag-of-words
    "tfidf_lr_char_ngram_3_5",        # Logistic Regression, TF-IDF
}
FAMILY_OF = {
    "bow_char_ngram_3_5": "naive_bayes",
    "tfidf_char_ngram_3_5": "naive_bayes",
    "bow_maxabs_lr_char_ngram_3_5": "logistic_regression",
    "tfidf_lr_char_ngram_3_5": "logistic_regression",
    "fasttext_word": "fasttext",
    "fasttext_subword": "fasttext",
    "lid.176": "fasttext_ots",
    "cld3": "cld3",
    "xlm_v_base_language_id": "xlm_v",
}


def make_arch_resolver(corpora: list[str]):
    """Strip the trailing '_<corpus>' suffix from a benchmark variant key."""
    ordered = sorted(corpora, key=len, reverse=True)

    def arch(key: str) -> str:
        for c in ordered:
            if key.endswith("_" + c):
                return key[: -(len(c) + 1)]
        return key

    return arch


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-exclusion", action="store_true",
                    help="skip the corpus-exclusion condition (faster)")
    args = ap.parse_args()

    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    corpora = [d["dataset"] for d in report["per_dataset"]]
    arch = make_arch_resolver(corpora)

    def paradigm(key: str) -> str:
        return "TML" if arch(key) in TML_ARCHITECTURES else "DL"

    def family(key: str) -> str:
        return FAMILY_OF.get(arch(key), arch(key))

    # ── (1) How large is the paradigm decision? ──────────────────────────────
    per_dataset = []
    for d in report["per_dataset"]:
        scores = d["all_benchmark_scores"]
        best_tml = max((v for k, v in scores.items() if paradigm(k) == "TML"), default=None)
        best_dl = max((v for k, v in scores.items() if paradigm(k) == "DL"), default=None)
        gt_par = paradigm(d["ground_truth_model"])
        per_dataset.append({
            "dataset": d["dataset"],
            "gt_paradigm": gt_par,
            "best_tml": round(best_tml, 6),
            "best_dl": round(best_dl, 6),
            "paradigm_gap": round(abs(best_tml - best_dl), 6),
            # cost of always choosing DL: zero when DL already wins
            "cost_of_always_dl": round(max(0.0, best_tml - best_dl), 6),
        })

    costs = [r["cost_of_always_dl"] for r in per_dataset]
    tml_wins = [r for r in per_dataset if r["gt_paradigm"] == "TML"]
    gt_par_dist = collections.Counter(r["gt_paradigm"] for r in per_dataset)
    n = len(per_dataset)

    # ── (2)/(3) Does the framework discriminate paradigms? ───────────────────
    recommender = Recommender.from_store(REPO / "mkb.pkl", k=3)
    store = recommender.store
    all_entries = dict(store._entries)
    all_names = list(store.datasets)

    fingerprints = []
    for d in report["per_dataset"]:
        profile = pd.read_pickle(REPO / "eval_profiles" / f"{d['dataset']}.pkl")
        fingerprints.append((d, store.builder.build(profile)))

    def evaluate(exclude_self: bool) -> dict:
        rows = []
        for d, fp in fingerprints:
            pool = [x for x in all_names if x != d["dataset"]] if exclude_self else all_names
            store._entries = {x: all_entries[x] for x in pool}
            rec = recommender.engine.query(fp, priority_metric=metric, user_iso_codes=None)
            gt = d["ground_truth_model"]
            scores = d["all_benchmark_scores"]
            best = max(scores.values())
            rows.append({
                "dataset": d["dataset"],
                "recommended": rec.recommended_model,
                "recommended_paradigm": paradigm(rec.recommended_model),
                "gt_paradigm": paradigm(gt),
                "paradigm_correct": paradigm(rec.recommended_model) == paradigm(gt),
                "family_correct": family(rec.recommended_model) == family(gt),
                "exact_correct": rec.recommended_model == gt,
                "regret": round(best - scores.get(rec.recommended_model, best), 6),
            })
        store._entries = dict(all_entries)
        rec_par = collections.Counter(r["recommended_paradigm"] for r in rows)
        return {
            "paradigm_correct": sum(r["paradigm_correct"] for r in rows),
            "family_correct": sum(r["family_correct"] for r in rows),
            "exact_correct": sum(r["exact_correct"] for r in rows),
            "mean_regret": round(st.mean(r["regret"] for r in rows), 6),
            "recommended_paradigm_distribution": dict(rec_par),
            "tml_wins_caught": sum(
                1 for r in rows if r["gt_paradigm"] == "TML" and r["recommended_paradigm"] == "TML"
            ),
            "per_dataset": rows,
        }

    scenarios = {"as_published": evaluate(exclude_self=False)}
    if not args.no_exclusion:
        scenarios["corpus_excluded"] = evaluate(exclude_self=True)

    majority_paradigm = gt_par_dist.most_common(1)[0]

    out = {
        "generated": str(date.today()),
        "priority_metric": metric,
        "n_datasets": n,
        "paradigm_assignment": {
            "TML": sorted(TML_ARCHITECTURES),
            "DL": sorted(set(FAMILY_OF) - TML_ARCHITECTURES),
        },
        "ground_truth_paradigm_distribution": dict(gt_par_dist),
        "majority_class_baseline": {
            "paradigm": majority_paradigm[0],
            "correct": majority_paradigm[1],
            "accuracy": round(majority_paradigm[1] / n, 4),
        },
        "cost_of_always_choosing_dl": {
            "mean": round(st.mean(costs), 6),
            "max": round(max(costs), 6),
            "n_datasets_where_tml_wins": len(tml_wins),
            "gaps_where_tml_wins": [r["paradigm_gap"] for r in tml_wins],
        },
        "scenarios": {
            k: {kk: vv for kk, vv in v.items() if kk != "per_dataset"}
            for k, v in scenarios.items()
        },
        "per_dataset": per_dataset,
        "per_dataset_recommendations": {k: v["per_dataset"] for k, v in scenarios.items()},
    }

    stamp = date.today().isoformat()
    dest = REPO / "analysis" / f"paradigm_regret_{stamp}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── LaTeX table (regenerate, never hand-edit) ────────────────────────────
    lines = [
        "% ── AUTO-GENERATED by analysis/paradigm_regret.py — do not edit by hand ──",
        f"% generated {stamp}",
        # [htbp], not [H]: a pinned 17-row table stranded most of a page empty in
        # the Supplementary Evaluation appendix (2026-09-26). [tp], not [htbp]:
        # as a bottom float it overflowed the page under the pinned sweep table
        # (2026-09-28).
        "\\begin{table}[!tp]",
        "\\mytable",
        "\\caption[Best achievable weighted $F_1$ per paradigm on each evaluation "
        "dataset]{Best achievable weighted $F_1$ per paradigm on each held-out "
        "evaluation dataset, and the performance loss of always choosing the "
        "neural paradigm.}",
        "\\label{tab:paradigm_regret}",
        # First column wraps (house L = ragged-right X) so the long dataset
        # names and summary labels stay within \textwidth.
        "\\begin{tabularx}{\\textwidth}{|L|c|c|c|c|}",
        "\\hline",
        "\\textbf{Evaluation dataset} & \\textbf{Best TML} & \\textbf{Best neural} & "
        "\\textbf{Gap} & \\textbf{Best paradigm} \\\\",
        "\\hline",
    ]
    # Display names from tab:benchmark_datasets, rows in alphabetical order.
    for r in sorted(per_dataset, key=lambda r: display(r["dataset"]).casefold()):
        name = display(r["dataset"])
        lines.append(
            f"{name} & {r['best_tml']:.4f} & {r['best_dl']:.4f} & "
            f"{r['paradigm_gap']:.5f} & "
            f"{'Neural' if r['gt_paradigm'] == 'DL' else r['gt_paradigm']} \\\\"
        )
        lines.append("\\hline")
    lines += [
        f"\\textbf{{Mean performance loss of always choosing neural}} & \\multicolumn{{4}}{{c|}}"
        f"{{{st.mean(costs):.5f}}} \\\\",
        "\\hline",
        f"\\textbf{{Maximum performance loss of always choosing neural}} & \\multicolumn{{4}}{{c|}}"
        f"{{{max(costs):.5f}}} \\\\",
        "\\hline",
        "\\end{tabularx}",
        "\\end{table}",
        "% ── END AUTO-GENERATED ──",
    ]
    tex_dest = REPO / "analysis" / "paradigm_regret_table.tex"
    tex_dest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ── Console summary ─────────────────────────────────────────────────────
    print(f"ground-truth paradigm distribution : {dict(gt_par_dist)}")
    print(f"majority-class baseline            : {majority_paradigm[1]}/{n} "
          f"= {majority_paradigm[1] / n:.1%} (always '{majority_paradigm[0]}')")
    print(f"cost of always choosing DL         : mean {st.mean(costs):.5f}  "
          f"max {max(costs):.5f}")
    print(f"datasets where TML wins            : {len(tml_wins)} "
          f"{[r['dataset'] for r in tml_wins]}")
    for name, sc in scenarios.items():
        print(f"\n[{name}]")
        print(f"  paradigm correct : {sc['paradigm_correct']}/{n} "
              f"= {sc['paradigm_correct'] / n:.1%}")
        print(f"  family correct   : {sc['family_correct']}/{n}")
        print(f"  exact correct    : {sc['exact_correct']}/{n}")
        print(f"  mean regret      : {sc['mean_regret']:.5f}")
        print(f"  recommends       : {sc['recommended_paradigm_distribution']}")
        print(f"  TML wins caught  : {sc['tml_wins_caught']}/{len(tml_wins)}")
    print(f"\nsnapshot -> {dest}")
    print(f"table    -> {tex_dest}")


if __name__ == "__main__":
    main()
