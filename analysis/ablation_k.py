"""
ablation_k.py — genuine engine re-run of the held-out validation at k=1 and k=3.

Loads the current mkb.pkl (17 datasets) and the fixed evaluation-split profiles
(eval_profiles/*.pkl), queries the Recommender at k=1 and k=3, and scores each
recommendation against the ground truth recorded in validation_report.json
(ground_truth_model / ground_truth_score / all_benchmark_scores per dataset).

Outputs, per k: exact-match accuracy, mean/max performance gap (delta f1_weighted),
corpus re-identification rate (query's source corpus retrieved as top-1 / top-3
neighbour), and min-gap over the top-3 IDW-ranked models (shortlist utility).

Usage:  conda run -n thesis_final python analysis/ablation_k.py
"""
import json
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from lid_toolkit.recommender.recommender import Recommender  # noqa: E402

REPORT = ROOT / "validation_report.json"
EVAL_PROFILES = ROOT / "eval_profiles"
MKB = ROOT / "mkb.pkl"


def main() -> None:
    rep = json.load(open(REPORT))
    gt = {d["dataset"]: d for d in rep["per_dataset"]}

    results = {1: [], 3: []}
    for k in (1, 3):
        rec_engine = Recommender.from_store(MKB, k=k)
        for pf in sorted(EVAL_PROFILES.glob("*.pkl")):
            name = pf.stem
            if name not in gt:
                continue
            with open(pf, "rb") as fh:
                df = pickle.load(fh)
            r = rec_engine.recommend_from_profile(df, priority_metric="f1_weighted", k=k)
            g = gt[name]
            scores = g["all_benchmark_scores"]
            rec_score = scores.get(r.recommended_model, float("nan"))
            gap = g["ground_truth_score"] - rec_score
            nb_names = [nb.dataset_name for nb in r.neighbours]
            top3_models = sorted(r.all_model_scores, key=r.all_model_scores.get, reverse=True)[:3]
            min_gap_top3 = min(
                g["ground_truth_score"] - scores.get(m, 0.0) for m in top3_models
            )
            results[k].append({
                "dataset": name,
                "recommended": r.recommended_model,
                "gt": g["ground_truth_model"],
                "correct": r.recommended_model == g["ground_truth_model"],
                "gap": gap,
                "confidence": r.confidence,
                "nb1": nb_names[0] if nb_names else None,
                "self_top1": bool(nb_names) and nb_names[0] == name,
                "self_top3": name in nb_names,
                "min_gap_top3": min_gap_top3,
            })

    for k in (1, 3):
        rows = results[k]
        n = len(rows)
        acc = sum(r["correct"] for r in rows)
        gaps = [r["gap"] for r in rows]
        print(f"\n===== k = {k}  (n = {n}) =====")
        print(f"exact-match accuracy : {acc}/{n}")
        print(f"mean gap             : {sum(gaps)/n:.4f}")
        print(f"max  gap             : {max(gaps):.4f}")
        print(f"re-identification    : top-1 {sum(r['self_top1'] for r in rows)}/{n}, "
              f"top-3 {sum(r['self_top3'] for r in rows)}/{n}")
        mg3 = [r["min_gap_top3"] for r in rows]
        print(f"min-gap over top-3 recommended models: mean {sum(mg3)/n:.4f}, max {max(mg3):.4f}")
        if k == 3:
            print("\nper-dataset (k=3): dataset | recommended==report? | correct | gap | conf")
            for r in rows:
                match_report = r["recommended"] == gt[r["dataset"]]["recommended_model"]
                print(f"  {r['dataset'][:40]:40s}  report_match={match_report}  "
                      f"correct={r['correct']}  gap={r['gap']:.4f}  conf={r['confidence']:.2f}")


if __name__ == "__main__":
    main()
