"""
paradigm_recommendation_sweep.py — does the framework ever recommend a TML model?

Re-queries the deployed engine (mkb.pkl, k = 3, default settings) with the 17
fixed evaluation-split profiles (eval_profiles/*.pkl) under every priority
metric the MKB stores, and records the paradigm of each recommendation, plus
where the best-ranked TML candidate sits in the IDW-ranked shortlist.

This measures the framework's OUTPUT only; it scores nothing against ground
truth.  Paradigm assignment follows analysis/paradigm_regret.py (Ch3
tab:paradigm_assignment): the four character n-gram MNB/LR configurations are
TML, everything else is neural.

Reads only committed artifacts (mkb.pkl, eval_profiles/, validation_report.json
for the corpus names); writes analysis/paradigm_recommendation_sweep_<date>.json.

Run (repo root, thesis_final):
    python analysis/paradigm_recommendation_sweep.py
"""
from __future__ import annotations

import collections
import json
import pickle
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "analysis"))

from lid_toolkit.recommender import Recommender  # noqa: E402
from paradigm_regret import TML_ARCHITECTURES, make_arch_resolver  # noqa: E402
from paradigm_metric_sensitivity import EVAL_BENCH_DIR, load_archive  # noqa: E402

METRICS = (
    "accuracy", "f1_macro", "f1_weighted",
    "precision_macro", "precision_weighted",
    "recall_macro", "recall_weighted",
    "inference_time_total_s", "inference_time_ms_per_sample",
    "throughput_samples_per_sec",
)


def main() -> None:
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    corpora = [d["dataset"] for d in report["per_dataset"]]
    arch = make_arch_resolver(corpora)

    def paradigm(key: str) -> str:
        return "TML" if arch(key) in TML_ARCHITECTURES else "neural"

    engine = Recommender.from_store(REPO / "mkb.pkl", k=3)
    profiles = {}
    for pf in sorted((REPO / "eval_profiles").glob("*.pkl")):
        if pf.stem in corpora:
            with open(pf, "rb") as fh:
                profiles[pf.stem] = pickle.load(fh)

    # Ground truth: the evaluation-split benchmark archive, every metric kept
    # (same source as analysis/paradigm_metric_sensitivity.py).
    archive = load_archive(EVAL_BENCH_DIR)
    lower = {"inference_time_total_s", "inference_time_ms_per_sample"}

    out = {"generated": str(date.today()), "k": 3, "n_queries": len(profiles),
           "ground_truth_source": str(EVAL_BENCH_DIR), "per_metric": {}}
    missing = set()
    for metric in METRICS:
        pick = min if metric in lower else max
        rows = []
        for name, df in profiles.items():
            r = engine.recommend_from_profile(df, priority_metric=metric, k=3)
            ranked = sorted(r.all_model_scores, key=r.all_model_scores.get, reverse=True)
            tml_ranks = [i + 1 for i, m in enumerate(ranked) if paradigm(m) == "TML"]
            cand = {v: m[metric] for v, m in archive.get(name, {}).items() if metric in m}
            gt = pick(cand, key=cand.get) if cand else None
            if r.recommended_model not in cand:
                missing.add((name, r.recommended_model))
            rows.append({
                "dataset": name,
                "recommended": r.recommended_model,
                "paradigm": paradigm(r.recommended_model),
                "gt_model": gt,
                "gt_paradigm": paradigm(gt) if gt else None,
                "best_tml_rank_in_shortlist": tml_ranks[0] if tml_ranks else None,
                "shortlist_size": len(ranked),
            })
        counts = collections.Counter(x["paradigm"] for x in rows)
        gt_counts = collections.Counter(x["gt_paradigm"] for x in rows if x["gt_paradigm"])
        majority = gt_counts.most_common(1)[0][0] if gt_counts else None
        agree = sum(x["paradigm"] == x["gt_paradigm"] for x in rows)
        tml_hits = sum(x["paradigm"] == "TML" and x["gt_paradigm"] == "TML" for x in rows)
        ranks = sorted(x["best_tml_rank_in_shortlist"] for x in rows
                       if x["best_tml_rank_in_shortlist"] is not None)
        out["per_metric"][metric] = {
            "n_TML_recommendations": counts.get("TML", 0),
            "n_neural_recommendations": counts.get("neural", 0),
            "gt_TML_corpora": gt_counts.get("TML", 0),
            "paradigm_agreement": agree,
            "majority_baseline_agreement": gt_counts.get(majority, 0),
            "TML_recommendations_correct": tml_hits,
            "median_best_tml_rank": ranks[len(ranks) // 2] if ranks else None,
            "min_best_tml_rank": ranks[0] if ranks else None,
            "rows": rows,
        }
        print(f"{metric:30s} rec TML {counts.get('TML', 0):2d}/17 | GT TML "
              f"{gt_counts.get('TML', 0):2d}/17 | paradigm agree {agree:2d}/17 vs "
              f"majority {gt_counts.get(majority, 0):2d}/17 | TML picks correct "
              f"{tml_hits}/{counts.get('TML', 0)}")
        for x in rows:
            if x["paradigm"] == "TML" or x["gt_paradigm"] == "TML":
                print(f"    {x['dataset'][:28]:28s} rec={x['paradigm']:6s} gt={x['gt_paradigm']}")
    if missing:
        print("\nWARNING recommended keys absent from the evaluation archive:")
        for m in sorted(missing):
            print("   ", m)

    dst = REPO / "analysis" / f"paradigm_recommendation_sweep_{date.today()}.json"
    dst.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {dst.relative_to(REPO)}")

    # ── LaTeX table for the thesis (appen:paradigm_supplement) ───────────────
    label = {
        "accuracy": "Accuracy", "f1_macro": "Macro $F_1$", "f1_weighted": "Weighted $F_1$",
        "precision_macro": "Macro precision", "precision_weighted": "Weighted precision",
        "recall_macro": "Macro recall", "recall_weighted": "Weighted recall",
        "inference_time_total_s": "Total inference time",
        "inference_time_ms_per_sample": "Inference time per sample",
        "throughput_samples_per_sec": "Throughput",
    }
    tex = [
        "% ── AUTO-GENERATED by analysis/paradigm_recommendation_sweep.py — do not edit by hand ──",
        f"% generated {date.today()}",
        # [!tp], not [H]: pinned below the paradigm-regret table it overflowed the
        # page (2026-09-28).
        "\\begin{table}[!tp]",
        "\\mytable",
        "\\caption[Paradigm outcome and framework recommendations under each priority metric]"
        "{Paradigm outcome and framework recommendations under each priority metric on the "
        "17 held-out evaluation splits ($k = 3$). \\emph{TML best} counts the corpora on which a "
        "TML pipeline is the best candidate; \\emph{TML recommended} counts the queries on which "
        "the framework recommends one; \\emph{Always neural} is the paradigm agreement of "
        "always answering ``neural'', the paradigm that is best on most corpora under every metric.}",
        "\\label{tab:paradigm_metric_sweep}",
        # Two-line headers keep the table inside the text width (2026-09-28).
        "\\begin{tabular}{|l|c|c|c|c|}",
        "\\hline",
        "\\textbf{Priority metric} & \\makecell{\\textbf{TML}\\\\\\textbf{best}} & "
        "\\makecell{\\textbf{TML}\\\\\\textbf{recommended}} & "
        "\\makecell{\\textbf{Paradigm}\\\\\\textbf{agreement}} & "
        "\\makecell{\\textbf{Always}\\\\\\textbf{neural}} \\\\",
        "\\hline",
    ]
    for metric in METRICS:
        s = out["per_metric"][metric]
        tex.append(
            f"{label[metric]} & {s['gt_TML_corpora']} & {s['n_TML_recommendations']} & "
            f"{s['paradigm_agreement']}/17 & {s['majority_baseline_agreement']}/17 \\\\"
        )
        tex.append("\\hline")
    tex += ["\\end{tabular}", "\\end{table}", "% ── END AUTO-GENERATED ──", ""]
    tdst = REPO / "analysis" / "paradigm_recommendation_sweep_table.tex"
    tdst.write_text("\n".join(tex), encoding="utf-8")
    print(f"wrote {tdst.relative_to(REPO)}")


if __name__ == "__main__":
    main()
