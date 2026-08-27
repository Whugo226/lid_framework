"""
stratification_ablation.py

PANEL FINDING C4 — the ablation of Theoretical Contribution 1.

Stratified fingerprinting is the thesis's first theoretical contribution and is
the only framework component never ablated. Every Chapter 5 condition varies
something around the representation (k, stratum weights, corpus set, baseline
strategy); nothing removes or replaces the stratification itself. This script
supplies the missing measurement.

ARMS
----
  stratified   the shipped framework, unmodified: five strata, per-stratum PCA
               to 95% variance (cap 20), 63 PCs, six-term composite distance
  a1           UNSTRATIFIED. One global PCA over the same 2,726-feature core,
               the framework's own 95%-variance rule, single Euclidean distance
  a2           UNSTRATIFIED, budget-maximal. As a1 but retaining every
               component the fit basis admits, so the baseline cannot be
               accused of having been starved
  b            TRIVIAL META-FEATURES. Retrieval on corpus size, document
               length, sentence length, word length and language count alone.
               Doubles as the naive meta-learner baseline that panel finding
               M5 says the novelty claim lacks

WHAT IS HELD FIXED
------------------
Everything downstream of the representation: the same 17 evaluation-split
queries, the same MKB entries and performance records, k=3, the IDW vote, the
coverage guard on the profile-derived language set, the priority metric taken
from validation_report.json, and score_row()/measures() imported from
reporting_measures.py rather than reimplemented. Only the fingerprint and the
distance function change between arms.

BASIS
-----
Evaluation splits only (Condition A). The reserved validation splits were used
once, for the confirmatory re-run after the coverage-guard correction, and are
not re-queried here. This matches every other secondary analysis in Chapter 5
(k ablation, weight search, paradigm regret, level ablation, LLM baseline).

PARITY NOTES
------------
1. The unstratified arms are fitted on the identical basis as the stratifier:
   the deduplicated pooled language matrix (see stratifier_fitbasis_refit.py
   and Appendix "Sensitivity of the Fingerprint Basis"). Fitting the baseline
   on a cleaner basis than the incumbent would measure the basis, not the
   stratification.
2. The unstratified arms use exactly the union of the stratifier's retained
   feature names, so both representations see the identical feature set and
   the only difference is stratified versus global compression.
3. The categorical S6 block is dropped from the unstratified arms, per the
   single-Euclidean specification. This cannot drive the outcome: the
   categorical term is a measured 0.18% mean share of the composite numerator
   (analysis/distance_scale_disparity_2026-08-15.json).
4. Composite D is a MEAN of six terms, so a single global Euclidean is
   numerically larger. This does not confound the comparison: IDW weights are
   ratios and at these magnitudes the 1e-9 floor is inert, so the vote is
   scale-invariant, and similarity_pct normalises within each arm.

READ-ONLY with respect to every existing artifact. Nothing under src/ is
modified. mkb.pkl is never rewritten. Writes one dated JSON snapshot.

Run (repo root, thesis_final):
    python analysis/stratification_ablation.py
"""
from __future__ import annotations

import copy
import itertools
import json
import math
import statistics as st
import sys
from collections import Counter, OrderedDict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "analysis"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from lid_toolkit.recommender import Recommender  # noqa: E402
from lid_toolkit.recommender.mkb_store import MKBStore  # noqa: E402
from lid_toolkit.recommender.mkb_similarity import SimilarityEngine  # noqa: E402

from reporting_measures import measures, score_row  # noqa: E402

K = 3
EXPERIMENTS = Path(r"c:\Users\User\OneDrive\Masters\LID_experiments")
BASELINE_OF_RECORD = {
    "mean_regret": 0.007287,
    "mean_range_capture_pct": 99.18,
    "top1_fraction": "2/17",
}

# Condition (b) meta-features drawn from the profile. "Median text length" is
# named in the C4 brief but the DeepProfiler schema emits no median at any
# aggregation level, so it is omitted rather than silently substituted.
PROFILE_META = [
    "Word count (Doc)",
    "Sentence length (Sent Avg)",
    "Word length (Sent Avg)",
]


# ───────────────────────────────────────────────────────────────────────────
# Engine: single-block distance. Everything else inherited unchanged.
# ───────────────────────────────────────────────────────────────────────────
class AblationEngine(SimilarityEngine):
    """
    Replaces the six-term composite with one Euclidean distance over the whole
    fingerprint vector.

    NOTE: this subclass deliberately violates its parent's contract --
    _stratum_distances no longer returns strata. It is only ever used with the
    unstratified fingerprints built below. The stratified arm must be run
    through the untouched Recommender path, never through this class.
    """

    def _stratum_distances(self, fp_a, fp_b, _trace=None):
        va = np.fromiter(fp_a.values(), dtype=float, count=len(fp_a))
        vb = np.fromiter(fp_b.values(), dtype=float, count=len(fp_b))
        n = min(va.size, vb.size)
        return {"global": float(np.linalg.norm(va[:n] - vb[:n]))}


# ───────────────────────────────────────────────────────────────────────────
# Shared helpers
# ───────────────────────────────────────────────────────────────────────────
def aggregate_over_languages(mat: np.ndarray, prefix: str) -> OrderedDict:
    """
    Summarise a (n_langs, n_components) matrix with the same five statistics
    FingerprintBuilder uses: mean, std, min, max, and within-dataset
    heterogeneity (ddof=1, zero when a single language).
    """
    if mat.ndim == 1:
        mat = mat.reshape(1, -1)
    n_langs = mat.shape[0]
    fp: OrderedDict[str, float] = OrderedDict()
    for i in range(mat.shape[1]):
        col = mat[:, i]
        key = f"{prefix}_PC{i:02d}"
        fp[f"{key}_mean"] = float(np.mean(col))
        fp[f"{key}_std"] = float(np.std(col, ddof=0))
        fp[f"{key}_min"] = float(np.min(col))
        fp[f"{key}_max"] = float(np.max(col))
        fp[f"{key}_het"] = float(np.std(col, ddof=1) if n_langs > 1 else 0.0)
    return fp


def paired_sign_flip(base_rows: list[dict], arm_rows: list[dict]) -> dict:
    """
    Exact paired sign-flip permutation test on per-dataset regret, two-sided.
    Positive difference = the arm has HIGHER regret than the stratified base.
    """
    by_base = {r["dataset"]: r["regret"] for r in base_rows}
    diffs = [r["regret"] - by_base[r["dataset"]] for r in arm_rows]
    nz = [x for x in diffs if abs(x) > 1e-9]
    k = len(nz)
    obs = abs(sum(nz))
    if k == 0:
        p = 1.0
    elif k > 22:
        p = None
    else:
        hits = sum(
            1
            for signs in itertools.product([1, -1], repeat=k)
            if abs(sum(v * s for v, s in zip(nz, signs))) >= obs - 1e-12
        )
        p = hits / 2 ** k
    return {
        "stratified_better": sum(1 for x in diffs if x > 1e-9),
        "arm_better": sum(1 for x in diffs if x < -1e-9),
        "identical_recommendation": sum(1 for x in diffs if abs(x) <= 1e-9),
        "informative_pairs": k,
        "mean_regret_difference": round(st.mean(diffs), 6) if diffs else None,
        "two_sided_p": round(p, 4) if p is not None else None,
    }


def run_arm(store, fp_mkb: dict, fp_query: dict, bench: dict, metric: str):
    """Query all 17 evaluation splits with an alternative representation."""
    alt = copy.deepcopy(store)
    for name in alt.datasets:
        alt._entries[name].fingerprint = fp_mkb[name]
    engine = AblationEngine(alt, k=K)

    rows, nn1 = [], Counter()
    self_top1 = self_top3 = 0
    for name in bench:
        profile = pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        rec = engine.query(
            fp_query[name],
            priority_metric=metric,
            user_iso_codes=frozenset(profile.columns),
        )
        rows.append(score_row(name, rec.recommended_model, bench[name]))
        top3 = [nb.dataset_name for nb in rec.neighbours[:3]]
        nn1[top3[0]] += 1
        self_top1 += top3[0] == name
        self_top3 += name in top3
    diag = {
        "nearest_neighbour_distribution": dict(nn1.most_common()),
        "self_retrieval_top1": f"{self_top1}/{len(rows)}",
        "self_retrieval_top3": f"{self_top3}/{len(rows)}",
    }
    return rows, diag


# ───────────────────────────────────────────────────────────────────────────
# Condition (a): one global PCA
# ───────────────────────────────────────────────────────────────────────────
def build_unstratified(store, bench, n_components=None):
    """
    Fit one global PCA on the same basis as the stratifier, over exactly the
    union of the strata's retained feature names. Returns
    (mkb_fingerprints, query_fingerprints, info).
    """
    # Same fit basis as MKBStore.finalise(): pooled then deduplicated by label.
    pooled = pd.concat(list(store._raw_profiles.values()), axis=1)
    fit_df = pooled.loc[:, ~pooled.columns.duplicated()]

    # Same feature set the stratified arm actually uses.
    feats = [f for s in store.stratifier.stratum_names
             for f in store.stratifier._fits[s].feature_names]

    X = fit_df.reindex(feats).T.values.astype(float)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    keep = X.std(axis=0) > 0
    feats = [f for f, v in zip(feats, keep) if v]
    X = X[:, keep]

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    ceiling = min(Xs.shape[0] - 1, Xs.shape[1])

    probe = PCA(n_components=ceiling, random_state=42).fit(Xs)
    cum = np.cumsum(probe.explained_variance_ratio_)
    n95 = int(np.searchsorted(cum, 0.95) + 1)

    n_keep = ceiling if n_components == "max" else (n_components or n95)
    n_keep = min(n_keep, ceiling)
    pca = PCA(n_components=n_keep, random_state=42).fit(Xs)

    def fingerprint(df: pd.DataFrame) -> OrderedDict:
        M = df.reindex(feats).T.values.astype(float)
        M = np.nan_to_num(M, nan=0.0, posinf=0.0, neginf=0.0)
        return aggregate_over_languages(pca.transform(scaler.transform(M)), "G")

    fp_mkb = {n: fingerprint(df) for n, df in store._raw_profiles.items()}
    fp_query = {n: fingerprint(pd.read_pickle(REPO / "eval_profiles" / f"{n}.pkl"))
                for n in bench}
    info = {
        "fit_rows": int(Xs.shape[0]),
        "features_used": len(feats),
        "component_ceiling": ceiling,
        "components_for_95pct": n95,
        "components_retained": n_keep,
        "variance_explained_pct": round(float(np.sum(pca.explained_variance_ratio_)) * 100, 1),
        "fingerprint_dims": len(next(iter(fp_mkb.values()))),
    }
    return fp_mkb, fp_query, info


# ───────────────────────────────────────────────────────────────────────────
# Condition (b): trivial meta-features
# ───────────────────────────────────────────────────────────────────────────
def split_sizes(root: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for p in (EXPERIMENTS / root).rglob("benchmark_metadata.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        n = d.get("metrics", {}).get("n_samples")
        if n is not None:
            out[d.get("dataset")] = n
    return out


def build_trivial(store, bench, keys=None):
    """
    Five scalars per corpus: language count, log10 corpus size, mean document
    length in words, mean sentence length, mean word length.

    Corpus size is log-transformed because raw sizes span 2,597 to 944,323 --
    nearly three orders of magnitude -- and raw z-scoring would let the two
    largest corpora dominate every distance. The transform makes the naive
    baseline stronger, which is the correct direction to err for a baseline
    the framework is being asked to beat.

    The scaler is fitted on the 17 MKB-side vectors only and applied to the
    query side, so both live in one space and the queries leak nothing.
    """
    size_mkb = split_sizes("model_benchmarking_knowledge")
    size_query = split_sizes("model_benchmarking_evaluation")
    missing = [n for n in store.datasets if n not in size_mkb or n not in size_query]
    if missing:
        raise RuntimeError(f"no n_samples recorded for: {missing}")

    all_keys = ["n_languages", "log10_corpus_size"] + [
        f.split(" (")[0].lower().replace(" ", "_") for f in PROFILE_META
    ]
    keys = list(keys) if keys else all_keys
    idx = [all_keys.index(k) for k in keys]

    def vec(df: pd.DataFrame, n_samples: int) -> list[float]:
        full = [float(df.shape[1]), math.log10(n_samples)] + [
            float(df.loc[f].mean()) for f in PROFILE_META
        ]
        return [full[i] for i in idx]

    names = list(store.datasets)
    V_mkb = np.array([vec(store._raw_profiles[n], size_mkb[n]) for n in names])
    scaler = StandardScaler().fit(V_mkb)
    Z_mkb = scaler.transform(V_mkb)

    fp_mkb = {n: OrderedDict(zip(keys, map(float, z))) for n, z in zip(names, Z_mkb)}

    fp_query = {}
    for n in bench:
        df = pd.read_pickle(REPO / "eval_profiles" / f"{n}.pkl")
        z = scaler.transform(np.array([vec(df, size_query[n])]))[0]
        fp_query[n] = OrderedDict(zip(keys, map(float, z)))

    info = {
        "features": keys,
        "n_features": len(keys),
        "median_text_length": "omitted -- no median emitted at any aggregation level",
        "size_transform": "log10, then z-scored on the 17 MKB-side vectors",
        "raw_mkb_vectors": {n: [round(x, 4) for x in v]
                            for n, v in zip(names, V_mkb.tolist())},
    }
    return fp_mkb, fp_query, info


def main() -> None:
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    bench = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}
    store = MKBStore.load(REPO / "mkb.pkl")
    print(f"priority metric: {metric}   datasets: {len(bench)}   k: {K}")
    print("basis: evaluation splits (Condition A) only\n")

    arms: dict[str, dict] = {}

    # ── stratified incumbent, through the untouched public path ──────────────
    rec = Recommender.from_store(REPO / "mkb.pkl", k=K)
    rows, nn1 = [], Counter()
    self1 = self3 = 0
    for name in bench:
        profile = pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        r = rec.recommend_from_profile(profile, priority_metric=metric)
        rows.append(score_row(name, r.recommended_model, bench[name]))
        top3 = [nb.dataset_name for nb in r.neighbours[:3]]
        nn1[top3[0]] += 1
        self1 += top3[0] == name
        self3 += name in top3
    base_rows = rows
    arms["stratified"] = {
        "description": "shipped framework: five strata, 63 PCs, six-term composite",
        "measures": measures(rows),
        "diagnostics": {
            "nearest_neighbour_distribution": dict(nn1.most_common()),
            "self_retrieval_top1": f"{self1}/17",
            "self_retrieval_top3": f"{self3}/17",
        },
        "rows": rows,
    }
    drift = {k: {"reproduced": arms["stratified"]["measures"][k], "of_record": v}
             for k, v in BASELINE_OF_RECORD.items()
             if arms["stratified"]["measures"][k] != v}
    print("stratified arm vs reporting_measures_2026-08-04.json:",
          "EXACT" if not drift else f"DRIFT -> {drift}")
    if drift:
        print("  !! comparison column does not reproduce; investigate before reading on")

    # ── (a) unstratified ─────────────────────────────────────────────────────
    for label, spec, desc in [
        ("a1_unstratified_95pct", None,
         "one global PCA, framework's own 95%-variance rule, single Euclidean"),
        ("a2_unstratified_max", "max",
         "one global PCA, every component the basis admits, single Euclidean"),
    ]:
        fp_m, fp_q, info = build_unstratified(store, bench, n_components=spec)
        r, d = run_arm(store, fp_m, fp_q, bench, metric)
        arms[label] = {"description": desc, "info": info, "measures": measures(r),
                       "diagnostics": d, "rows": r}
        print(f"{label}: {info['components_retained']} PCs "
              f"({info['variance_explained_pct']}% var, ceiling {info['component_ceiling']})")

    # ── (b) trivial meta-features ────────────────────────────────────────────
    fp_m, fp_q, info = build_trivial(store, bench)
    r, d = run_arm(store, fp_m, fp_q, bench, metric)
    arms["b_trivial_meta"] = {
        "description": "corpus size, document/sentence/word length, language count",
        "info": info, "measures": measures(r), "diagnostics": d, "rows": r,
    }
    print(f"b_trivial_meta: {info['n_features']} features -> {info['features']}\n")

    # ── (b) decomposition: which trivial feature carries the result? ─────────
    # Guards against the obvious objection that language count and corpus size
    # act as a parent-corpus identifier under Condition A, where the query's
    # sibling split is in the MKB.
    SUBSETS = {
        "b2_no_language_count": ["log10_corpus_size", "word_count",
                                 "sentence_length", "word_length"],
        "b3_lengths_only": ["word_count", "sentence_length", "word_length"],
        "b4_language_count_only": ["n_languages"],
        "b5_corpus_size_only": ["log10_corpus_size"],
    }
    sensitivity = {}
    for label, keys in SUBSETS.items():
        fp_m2, fp_q2, info2 = build_trivial(store, bench, keys=keys)
        r2, d2 = run_arm(store, fp_m2, fp_q2, bench, metric)
        sensitivity[label] = {
            "features": keys,
            "measures": measures(r2),
            "self_retrieval_top1": d2["self_retrieval_top1"],
            "paired_vs_stratified": paired_sign_flip(base_rows, r2),
        }
    print("trivial-feature decomposition:")
    print(f"  {'subset':26s} {'regret':>10s} {'rangecap':>9s} {'self1':>7s}")
    for label, v in sensitivity.items():
        print(f"  {label:26s} {v['measures']['mean_regret']:>10.6f} "
              f"{v['measures']['mean_range_capture_pct']:>9.2f} "
              f"{v['self_retrieval_top1']:>7s}")
    print()

    # ── comparison ───────────────────────────────────────────────────────────
    paired = {k: paired_sign_flip(base_rows, v["rows"])
              for k, v in arms.items() if k != "stratified"}

    order = ["stratified", "a1_unstratified_95pct", "a2_unstratified_max", "b_trivial_meta"]
    short = {"stratified": "stratified", "a1_unstratified_95pct": "a1 unstrat 95%",
             "a2_unstratified_max": "a2 unstrat max", "b_trivial_meta": "b trivial"}
    print("=" * 88)
    print(f"{'measure':28s}" + "".join(f"{short[a]:>15s}" for a in order))
    print("-" * 88)
    for key in ("top1_fraction", "mean_regret", "median_regret", "max_regret",
                "mean_rank", "top3_hit", "top10_hit",
                "mean_range_capture_pct", "min_range_capture_pct"):
        print(f"{key:28s}" + "".join(
            f"{str(arms[a]['measures'][key]):>15s}" for a in order))
    print(f"{'self-retrieval top-1':28s}" + "".join(
        f"{arms[a]['diagnostics']['self_retrieval_top1']:>15s}" for a in order))
    print("=" * 88)
    print("\npaired sign-flip permutation tests against the stratified arm:")
    print(json.dumps(paired, indent=2))

    out = {
        "generated": str(date.today()),
        "panel_finding": "C4 (ablation of Theoretical Contribution 1); also discharges M5",
        "priority_metric": metric,
        "k": K,
        "basis": (
            "Evaluation splits (Condition A) only. The reserved validation splits "
            "were used once, for the confirmatory re-run after the coverage-guard "
            "correction, and are not re-queried here. This matches every other "
            "secondary analysis in Chapter 5."
        ),
        "reproduction_check": {
            "of_record": BASELINE_OF_RECORD,
            "status": "EXACT" if not drift else "DRIFT",
            "drift": drift,
        },
        "arms": {k: {kk: vv for kk, vv in v.items() if kk != "rows"}
                 for k, v in arms.items()},
        "paired_vs_stratified": paired,
        "trivial_feature_decomposition": sensitivity,
        "per_dataset": {k: v["rows"] for k, v in arms.items()},
    }
    dest = REPO / "analysis" / f"stratification_ablation_{date.today().isoformat()}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
