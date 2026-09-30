"""
split_resampling_variation.py

Measures how much the benchmark scores of the candidate pool move when the same,
already-trained candidates are re-scored on a second disjoint held-out split of
each corpus.  It exists to back (or correct) Chapter 5 wording that compares the
margins between leading candidates with "run-to-run" or "resampling" variation.

WHAT IS COMPARED
----------------
  evaluation split  — validation_report.json            (all_benchmark_scores)
  validation split  — validation_confirmatory_report.json (all_benchmark_scores)

Every candidate is a fixed artefact (trained variants are not retrained, zero-shot
detectors are used as published), so the difference between the two archives for
one candidate is sampling variation of the held-out text alone.

KEY NORMALISATION: the evaluation archive keys the zero-shot CLD3 and lid.176
records per corpus (``cld3_<corpus>``); the validation archive keys them bare
(``cld3``).  Validation keys are renamed to the evaluation convention.

Reads only committed artifacts; writes a dated JSON snapshot. Modifies nothing.

Run (repo root, thesis_final):
    python analysis/split_resampling_variation.py
"""
from __future__ import annotations

import json
import statistics as st
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paradigm_regret import TML_ARCHITECTURES, make_arch_resolver  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
TOP_N = 5
BARE_ZERO_SHOT = {"cld3", "lid.176"}


def load(path: Path) -> dict[str, dict[str, float]]:
    report = json.loads(path.read_text(encoding="utf-8"))
    return {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}


def normalise(scores: dict[str, float], corpus: str) -> dict[str, float]:
    return {(f"{k}_{corpus}" if k in BARE_ZERO_SHOT else k): v for k, v in scores.items()}


def main() -> None:
    ev = load(REPO / "validation_report.json")
    va = load(REPO / "validation_confirmatory_report.json")
    arch = make_arch_resolver(list(ev))

    def paradigm(key: str) -> str:
        return "TML" if arch(key) in TML_ARCHITECTURES else "neural"

    def paradigm_split(scores: dict[str, float]) -> dict:
        best = {p: max(v for k, v in scores.items() if paradigm(k) == p) for p in ("TML", "neural")}
        winner = "TML" if best["TML"] > best["neural"] else "neural"
        return {"best_tml": best["TML"], "best_neural": best["neural"], "winner": winner,
                "margin": round(abs(best["TML"] - best["neural"]), 6)}

    rows = []
    for corpus, e_scores in ev.items():
        v_scores = normalise(va[corpus], corpus)
        common = sorted(set(e_scores) & set(v_scores))
        e = {k: e_scores[k] for k in common}
        v = {k: v_scores[k] for k in common}

        e_ranked = sorted(common, key=lambda k: -e[k])
        gt_eval, gt_val = e_ranked[0], max(common, key=v.__getitem__)
        top_shift = [abs(e[k] - v[k]) for k in e_ranked[:TOP_N]]
        best_second_gap = e[e_ranked[0]] - e[e_ranked[1]]
        p_eval, p_val = paradigm_split(e), paradigm_split(v)

        rows.append({
            "dataset": corpus,
            "n_common_candidates": len(common),
            "gt_eval": gt_eval,
            "gt_val": gt_val,
            "gt_same": gt_eval == gt_val,
            "best_second_gap_eval": round(best_second_gap, 6),
            f"top{TOP_N}_median_abs_shift": round(st.median(top_shift), 6),
            f"top{TOP_N}_max_abs_shift": round(max(top_shift), 6),
            "gap_below_median_shift": best_second_gap < st.median(top_shift),
            "all_candidates_median_abs_shift": round(st.median(abs(e[k] - v[k]) for k in common), 6),
            "paradigm_eval": p_eval,
            "paradigm_val": p_val,
            "paradigm_winner_same": p_eval["winner"] == p_val["winner"],
        })

    tml_wins = [r for r in rows if r["paradigm_eval"]["winner"] == "TML"]
    summary = {
        "n_corpora": len(rows),
        "gt_changes_between_splits": sum(not r["gt_same"] for r in rows),
        "gt_changes_datasets": [r["dataset"] for r in rows if not r["gt_same"]],
        "median_best_second_gap_eval": round(st.median(r["best_second_gap_eval"] for r in rows), 6),
        f"pooled_median_top{TOP_N}_abs_shift": round(
            st.median(r[f"top{TOP_N}_median_abs_shift"] for r in rows), 6),
        "corpora_gap_below_median_shift": sum(r["gap_below_median_shift"] for r in rows),
        "corpora_gap_below_median_shift_datasets": [r["dataset"] for r in rows if r["gap_below_median_shift"]],
        "tml_win_corpora_eval": [
            {"dataset": r["dataset"], "margin_eval": r["paradigm_eval"]["margin"],
             "winner_val": r["paradigm_val"]["winner"], "margin_val": r["paradigm_val"]["margin"],
             f"top{TOP_N}_max_abs_shift": r[f"top{TOP_N}_max_abs_shift"]}
            for r in tml_wins
        ],
        "paradigm_winner_flips": sum(not r["paradigm_winner_same"] for r in rows),
        "paradigm_winner_flips_datasets": [r["dataset"] for r in rows if not r["paradigm_winner_same"]],
    }

    stamp = date.today().isoformat()
    dest = REPO / "analysis" / f"split_resampling_variation_{stamp}.json"
    dest.write_text(json.dumps({"generated": stamp, "top_n": TOP_N, "summary": summary,
                                "per_dataset": rows}, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
