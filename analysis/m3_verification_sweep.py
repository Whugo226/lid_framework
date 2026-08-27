"""
m3_verification_sweep.py

PANEL FINDING M3 — a dozen table figures could not be traced to a saved
artifact.

The project's own rule (session-facts ledger, convention #4) is that no
numeric claim enters prose without a saved artifact behind it. The 2026-08-13
panel found roughly twelve figures in Chapter 5 that did not meet it: some
were produced by scripts that print to console and save nothing, some predate
the last verification sweep, and some had no artifact at all.

This script closes that gap. For each figure it names the source, re-derives
the value, and reports MATCH / MISMATCH / NO-ARTIFACT against what the thesis
currently prints. It writes one dated JSON recording the provenance of every
claim, so the chain from prose to artifact is inspectable without re-running
anything.

Claims are stated as they appear in the CURRENT thesis text, not as the panel
recorded them; several were edited between 2026-08-13 and this sweep.

READ-ONLY. Nothing under src/ is touched, mkb.pkl is never rewritten, and no
existing artifact is overwritten.

Run (repo root, thesis_final):
    python analysis/m3_verification_sweep.py
"""
from __future__ import annotations

import json
import statistics as st
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "analysis"))

import pandas as pd  # noqa: E402

from lid_toolkit.recommender import Recommender  # noqa: E402

TOL = 5e-5          # rounding tolerance for 4-decimal prose figures
results: list[dict] = []


def check(claim_id, site, claimed, derived, artifact, note=""):
    """Record one verification. `derived` None means no artifact could supply it."""
    if derived is None:
        verdict = "NO-ARTIFACT"
    elif isinstance(claimed, str) or isinstance(derived, str):
        verdict = "MATCH" if str(claimed) == str(derived) else "MISMATCH"
    else:
        verdict = "MATCH" if abs(claimed - derived) <= TOL else "MISMATCH"
    results.append({
        "id": claim_id, "site": site, "claimed": claimed, "derived": derived,
        "artifact": artifact, "verdict": verdict, "note": note,
    })
    mark = {"MATCH": "ok  ", "MISMATCH": "FAIL", "NO-ARTIFACT": "????"}[verdict]
    print(f"  [{mark}] {claim_id:<26} claimed={claimed!s:<16} derived={derived!s:<16} {artifact}")


def main() -> None:
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    bench = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}
    gt = {d["dataset"]: d for d in report["per_dataset"]}
    rm_path = REPO / "analysis" / "reporting_measures_2026-08-04.json"
    rm = json.loads(rm_path.read_text(encoding="utf-8"))

    # ── 1. k-ablation table ─────────────────────────────────────────────────
    # analysis/ablation_k.py prints these and saves nothing: the figures in
    # tab:k_ablation came from console output. Re-derived live here.
    print("\n[1] Neighbourhood-size ablation (tab:k_ablation)")
    rec1 = Recommender.from_store(REPO / "mkb.pkl", k=1)
    gaps1, correct1 = [], 0
    for name in bench:
        prof = pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        r = rec1.recommend_from_profile(prof, priority_metric=metric)
        scores = bench[name]
        gaps1.append(max(scores.values()) - scores[r.recommended_model])
        correct1 += r.recommended_model == max(scores, key=scores.__getitem__)
    n = len(gaps1)
    src1 = "re-derived live from mkb.pkl + eval_profiles (ablation_k.py saves no artifact)"
    check("k1_exact_match", "demo:tab:k_ablation", "4/17", f"{correct1}/{n}", src1)
    check("k1_mean_gap", "demo:tab:k_ablation", 0.0080, round(st.mean(gaps1), 4), src1)
    check("k1_max_gap", "demo:tab:k_ablation", 0.0297, round(max(gaps1), 4), src1)

    a = rm["conditions"]["A_evaluation_splits_full_mkb"]
    src_rm = "analysis/reporting_measures_2026-08-04.json -> conditions/A"
    check("k3_exact_match", "demo:tab:k_ablation", "2/17", a["top1_fraction"], src_rm)
    check("k3_mean_gap", "demo:tab:k_ablation", 0.0073, round(a["mean_regret"], 4), src_rm)
    check("k3_max_gap", "demo:tab:k_ablation", 0.0259, round(a["max_regret"], 4), src_rm)

    # ── 2. Coverage-guard iteration table, "before" column ──────────────────
    # The pre-fix state is exactly what validation_report.json (2026-05-14)
    # records. It is SUPERSEDED as a source of reported figures, but it is the
    # correct and only artifact for the "before" column.
    print("\n[2] Coverage-guard iteration, before column (tab:coverage_guard)")
    src_vr = "validation_report.json (2026-05-14; superseded for headline use)"
    check("before_top1", "demo:tab:coverage_guard",
          "3/17", f"{report['n_correct']}/{report['n_total']}", src_vr)
    check("before_mean_gap", "demo:tab:coverage_guard",
          0.0078, round(report["performance_delta"]["mean"], 4), src_vr)
    check("before_max_gap", "demo:tab:coverage_guard",
          0.0489, round(report["performance_delta"]["max"], 4), src_vr)

    # ── 3. Confidence split, after the correction ───────────────────────────
    print("\n[3] Confidence split, after correction (demo:1099, tab:coverage_guard)")
    rec3 = Recommender.from_store(REPO / "mkb.pkl", k=3)
    nonzero, zero, nz_correct, z_correct = 0, 0, 0, 0
    for name in bench:
        prof = pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        r = rec3.recommend_from_profile(prof, priority_metric=metric)
        ok = r.recommended_model == max(bench[name], key=bench[name].__getitem__)
        if r.confidence > 0:
            nonzero += 1
            nz_correct += ok
        else:
            zero += 1
            z_correct += ok
    src3 = "re-derived live from mkb.pkl + eval_profiles"
    check("conf_nonzero_count", "demo:1099", "13 non-zero", f"{nonzero} non-zero", src3)
    check("conf_zero_count", "demo:1099", "4 zero", f"{zero} zero", src3)
    check("conf_split_after", "demo:tab:coverage_guard",
          "1/13 vs 1/4", f"{nz_correct}/{nonzero} vs {z_correct}/{zero}", src3)

    # ── 4. Stratum collinearity ─────────────────────────────────────────────
    print("\n[4] Stratum distance collinearity (appendix)")
    wi = json.loads((REPO / "analysis" /
                     "weight_insensitivity_diagnosis_2026-08-05.json").read_text(encoding="utf-8"))
    coll = wi.get("a_collinearity", {})
    src4 = "analysis/weight_insensitivity_diagnosis_2026-08-05.json -> a_collinearity"
    mean_off = coll.get("mean_offdiagonal_correlation")
    max_off = coll.get("max_offdiagonal_correlation")
    check("stratum_corr_mean", "appendix weight_insensitivity",
          0.44, round(mean_off, 2) if mean_off is not None else None, src4)
    check("stratum_corr_max", "appendix weight_insensitivity",
          0.91, round(max_off, 2) if max_off is not None else None, src4)

    # ── 5. learn_weights() range, and the in-sample gain ────────────────────
    print("\n[5] Weight search figures")
    ws = json.loads((REPO / "analysis" /
                     "stratum_weight_search_2026-08-05.json").read_text(encoding="utf-8"))
    src5 = "analysis/stratum_weight_search_2026-08-05.json"
    lw = ws.get("learned_weights") or {}
    lw_vals = [v for v in lw.values() if isinstance(v, (int, float))]
    check("learn_weights_min", "demo:1006", 0.92,
          round(min(lw_vals), 2) if lw_vals else None, src5 + " -> learned_weights")
    check("learn_weights_max", "demo:1006", 1.17,
          round(max(lw_vals), 2) if lw_vals else None, src5 + " -> learned_weights")

    pol = ws.get("policies", {})
    eq = pol.get("equal_weights_published", {}).get("mean_regret")
    best = pol.get("best_in_sample_draw", {}).get("mean_regret")
    gain = round(100 * (eq - best) / eq, 1) if (eq and best) else None
    check("in_sample_gain_pct", "demo:987", 8.7, gain,
          src5 + " -> policies (full precision, not the rounded 0.0073/0.0067)",
          "Panel M3 asked specifically whether 8.7% was computed at full "
          "precision or from rounded values; rounded would give 8.2%.")

    loo = pol.get("leave_one_corpus_out_selection", {}).get("mean_regret")
    check("loo_selection_regret", "demo:987", 0.0094,
          round(loo, 4) if loo else None, src5 + " -> policies")
    check("loo_worse_than_equal_pct", "demo:987", 29,
          round(100 * (loo - eq) / eq) if (loo and eq) else None,
          src5 + " -> policies")

    # ── 6. Tie-structure figures ────────────────────────────────────────────
    print("\n[6] Candidate tie structure (demo:189-209)")
    src6 = "validation_report.json -> per_dataset/all_benchmark_scores"
    second_gaps, spans, within = [], [], {}
    for name, scores in bench.items():
        vals = sorted(scores.values(), reverse=True)
        second_gaps.append(vals[0] - vals[1])
        spans.append(vals[0] - vals[-1])
        within[name] = sum(1 for v in vals if v >= vals[0] - 0.01)
    check("median_best_vs_second", "demo:189", 0.00070,
          round(st.median(second_gaps), 5), src6)
    check("europarl_within_0.01", "demo:191", 35, within.get("europarl"), src6)
    check("median_span", "demo:209", 0.877, round(st.median(spans), 3), src6)
    check("median_within_0.01", "demo:189", 6, int(st.median(within.values())), src6)

    # ── 7. LLM baseline range capture ───────────────────────────────────────
    print("\n[7] LLM baseline range capture (demo:388-397)")
    llm = json.loads((REPO / "llm_baseline_results.json").read_text(encoding="utf-8"))
    src7 = "llm_baseline_results.json + validation_report.json benchmark archive"
    caps = []
    for row in llm["per_dataset"]:
        d, g = row["dataset"], row.get("gap")
        if g is None or d not in bench:
            continue
        vals = list(bench[d].values())
        b, w = max(vals), min(vals)
        caps.append(100 * ((b - g) - w) / (b - w) if b > w else 100.0)
    check("llm_mean_range_capture", "demo:388", 90.2,
          round(st.mean(caps), 1) if caps else None, src7)
    check("llm_min_range_capture", "demo:389", 51.5,
          round(min(caps), 1) if caps else None, src7)

    # ── 8. Validation-split constant baseline ───────────────────────────────
    print("\n[8] Validation-split best constant policy (demo:1324)")
    conf_path = REPO / "validation_confirmatory_report.json"
    derived_b = None
    src8 = "validation_confirmatory_report.json -> per_dataset/all_benchmark_scores"
    if conf_path.exists():
        conf = json.loads(conf_path.read_text(encoding="utf-8"))
        vb = {r["dataset"]: r["all_benchmark_scores"] for r in conf["per_dataset"]}
        common = set.intersection(*(set(s) for s in vb.values()))
        best_mean = min(
            st.mean(max(s.values()) - s[v] for s in vb.values()) for v in common
        )
        derived_b = round(best_mean, 4)
    check("validation_best_constant", "demo:1324", 0.0132, derived_b, src8)

    # ── 9. Inference cost table and the 8.8-11.2x claim ─────────────────────
    # tab:inference_cost reports median ms/sample per architecture. Re-derived
    # from the per-record inference timings in the evaluation benchmark run.
    print("\n[9] Inference cost (tab:inference_cost, demo:642)")
    EXP = Path(r"c:\Users\User\OneDrive\Masters\LID_experiments")
    FAMILIES = {
        "fasttext_word": "FastText word",
        "lid.176": "lid.176 zero-shot",
        "fasttext_subword": "FastText subword",
        "cld3": "CLD3",
        "bow_maxabs_lr_char_ngram_3_5": "LR bag-of-words",
        "tfidf_lr_char_ngram_3_5": "LR TF-IDF",
        "tfidf_char_ngram_3_5": "NB TF-IDF",
        "bow_char_ngram_3_5": "NB bag-of-words",
        "xlm_v_base_language_id": "XLM-V Base",
    }
    timings: dict[str, list[float]] = {k: [] for k in FAMILIES}
    for p in (EXP / "model_benchmarking_evaluation").rglob("benchmark_metadata.json"):
        try:
            md = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        ms = md.get("metrics", {}).get("inference_time_ms_per_sample")
        variant = p.parent.name
        if ms is None:
            continue
        # longest matching prefix wins, so tfidf_lr_* is not caught by tfidf_*
        best_key = max((k for k in FAMILIES if variant.startswith(k)),
                       key=len, default=None)
        if best_key:
            timings[best_key].append(ms)

    src9 = ("LID_experiments/model_benchmarking_evaluation/**/benchmark_metadata.json "
            "-> metrics/inference_time_ms_per_sample (median per architecture)")
    # Ratios are taken at FULL precision, then rounded once. Dividing already
    # rounded medians shifts LR TF-IDF to 9.2 and XLM-V to 425.8, which would
    # be an artifact of this script rather than an error in the table.
    medians = {k: st.median(v) for k, v in timings.items() if v}
    if medians:
        fastest = min(medians.values())
        check("inference_fastext_word_ms", "demo:tab:inference_cost",
              0.0218, round(medians.get("fasttext_word"), 4), src9)
        tml = ["bow_maxabs_lr_char_ngram_3_5", "tfidf_lr_char_ngram_3_5",
               "tfidf_char_ngram_3_5", "bow_char_ngram_3_5"]
        mults = [round(medians[k] / fastest, 1) for k in tml if k in medians]
        if mults:
            check("inference_tml_min_multiple", "demo:642", 8.8, min(mults), src9)
            check("inference_tml_max_multiple", "demo:642", 11.2, max(mults), src9)
        check("inference_lr_tfidf_multiple", "demo:tab:inference_cost", 9.1,
              round(medians["tfidf_lr_char_ngram_3_5"] / fastest, 1), src9)
        check("inference_xlmv_multiple", "demo:tab:inference_cost", 425.7,
              round(medians["xlm_v_base_language_id"] / fastest, 1), src9)
        for k, lbl in FAMILIES.items():
            if k in medians:
                print(f"         {lbl:<22} median {medians[k]:.4f} ms/sample "
                      f"({medians[k]/fastest:.1f}x)  n={len(timings[k])}")
    else:
        check("inference_multiples", "demo:642", "8.8-11.2x", None,
              "no inference timings found under model_benchmarking_evaluation")

    # ── summary ─────────────────────────────────────────────────────────────
    tally = {v: sum(1 for r in results if r["verdict"] == v)
             for v in ("MATCH", "MISMATCH", "NO-ARTIFACT")}
    print("\n" + "=" * 78)
    print(f"MATCH {tally['MATCH']}   MISMATCH {tally['MISMATCH']}   "
          f"NO-ARTIFACT {tally['NO-ARTIFACT']}   (total {len(results)})")
    print("=" * 78)
    for r in results:
        if r["verdict"] != "MATCH":
            print(f"  {r['verdict']:<12} {r['id']:<26} {r['site']}")
            print(f"               claimed {r['claimed']}  derived {r['derived']}")
            if r["note"]:
                print(f"               {r['note']}")

    out = {
        "generated": str(date.today()),
        "panel_finding": "M3 (table figures untraced to a saved artifact)",
        "rule": "no numeric claim enters prose without a saved artifact behind it",
        "tolerance": TOL,
        "summary": tally,
        "claims": results,
    }
    dest = REPO / "analysis" / f"m3_verification_sweep_{date.today().isoformat()}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
