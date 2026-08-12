"""
level_ablation.py

Answers the examiner-anticipated question: "the thesis scopes itself to
short-form text, so why does the feature schema measure at paragraph and
document level at all — and is the fingerprint really 2,726-dimensional when
the levels collapse on a 120-character document?"

WHY THIS EXISTS
---------------
Ingestion truncates every document to at most 120 characters (40 for CJK)
(design_and_implementation.tex, Dataset Curation Pipeline). At that length the
three segment levels of the Lingualyzer-derived schema largely coincide: a row
is typically one sentence and always one paragraph. Chapter 4 currently asserts
the three-level hierarchy without addressing the collapse, which leaves two
open questions this script settles empirically rather than rhetorically:

  1.  HOW degenerate are the levels, per corpus and pooled?  (Part 1)
  2.  Does restricting the schema to the levels that "really exist" in
      short text change retrieval quality?                     (Part 2)

Question 2 is the decision-relevant one. If a sentence-only or
sentence+document schema matched or beat the full schema, the honest response
would be to rebuild the MKB on the reduced schema. If they are equivalent, the
full schema stands and the ablation becomes the answer to the question.

THE FOUR CONDITIONS
-------------------
Feature names carry an explicit level suffix — "(Doc)", "(Sent Avg)",
"(Par SD)", "(Sent-Doc Max)" — so a schema restriction is exactly a filter on
the set of levels a feature is allowed to involve.

  full               all 2,726 core features                    (deployed schema)
  sentence_only      features involving only Sent               (Sent *, Sent-Sent *)
  document_only      features involving only Doc                (Doc)
  sentence_document  features involving only Sent and/or Doc    (drops the paragraph block)

EVALUATION
----------
Each condition is scored under the two protocols that matter:

  A    evaluation splits, full MKB — the recorded headline protocol. Mirrors
       reporting_measures.py: coverage guard active on the profile-derived
       language set, scored against validation_report.json.
  LOO  leave-one-corpus-out WITH refit — the generalisation bound. Mirrors
       corpus_exclusion_refit.py exactly: for each corpus the scaler + PCA are
       refitted on the other 16 under that condition's schema, then the
       held-out corpus is projected into the refit space.

LOO is the more informative comparison: under condition A the query corpus is
in the MKB, which masks schema differences.

WHAT THIS DOES NOT DO
---------------------
Nothing is rebuilt on disk. mkb.pkl is read-only input; every restricted store
is constructed in memory from the SAME raw profiles and the SAME performance
records the deployed MKB holds, so the only variable across conditions is the
feature schema. No re-profiling and no model retraining is involved: the
profiles already contain all 2,726 extracted features and the 1,785
performance records are independent of the feature schema.

Run (repo root, thesis_final):
    python analysis/level_ablation.py
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics as st
import sys
import warnings
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from lid_toolkit.recommender.mkb_similarity import SimilarityEngine  # noqa: E402
from lid_toolkit.recommender.mkb_store import MKBStore  # noqa: E402

warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parents[1]
K = 3

# ---------------------------------------------------------------------------
# Level parsing
# ---------------------------------------------------------------------------

_SUFFIX = re.compile(r"\(([^)]*)\)\s*$")
_LEVEL_TOKENS = {"Sent": "sentence", "Par": "paragraph", "Doc": "document"}


def levels_of(feature_name: str) -> frozenset[str]:
    """
    Return the set of segment levels a feature involves.

    "Word count (Doc)"                  -> {document}
    "Type-token ratio (Sent Avg)"       -> {sentence}
    "Lemma overlap ratio (Par-Doc Max)" -> {paragraph, document}
    """
    m = _SUFFIX.search(feature_name)
    if not m:
        return frozenset()
    head = m.group(1).split()[0]           # "Par-Doc Max" -> "Par-Doc"; "Doc" -> "Doc"
    return frozenset(
        _LEVEL_TOKENS[tok] for tok in head.split("-") if tok in _LEVEL_TOKENS
    )


CONDITIONS: dict[str, frozenset[str] | None] = {
    # None = no restriction (deployed schema)
    "full": None,
    "sentence_only": frozenset({"sentence"}),
    "document_only": frozenset({"document"}),
    "sentence_document": frozenset({"sentence", "document"}),
}


def select_features(all_names: list[str], allowed: frozenset[str] | None) -> list[str]:
    """Features whose involved levels are a subset of `allowed`."""
    if allowed is None:
        return list(all_names)
    return [n for n in all_names if levels_of(n) and levels_of(n) <= allowed]


# ---------------------------------------------------------------------------
# Part 1 — degeneracy statistics
# ---------------------------------------------------------------------------

def degeneracy_statistics(raw_profiles: dict[str, pd.DataFrame]) -> dict:
    """
    Quantify how far the three segment levels collapse under the 120-character
    truncation, per corpus and pooled across the fit matrix.
    """
    per_corpus = []
    for name, df in sorted(raw_profiles.items()):
        names = list(df.index)

        def mean_of(feat: str) -> float | None:
            return round(float(df.loc[feat].mean()), 4) if feat in names else None

        par_sd = [n for n in names if n.endswith("(Par SD)")]
        sent_sd = [n for n in names if n.endswith("(Sent SD)")]

        # Par Avg identical to its Doc counterpart => paragraph level adds nothing
        par_eq_doc, sent_doc_corr = [], []
        for n in names:
            if n.endswith("(Par Avg)"):
                d = n[: -len(" (Par Avg)")] + " (Doc)"
                if d in names:
                    par_eq_doc.append(
                        bool(np.allclose(df.loc[n].values.astype(float),
                                         df.loc[d].values.astype(float),
                                         rtol=1e-6, atol=1e-9))
                    )
            if n.endswith("(Sent Avg)"):
                d = n[: -len(" (Sent Avg)")] + " (Doc)"
                if d in names:
                    a = df.loc[n].values.astype(float)
                    b = df.loc[d].values.astype(float)
                    if np.std(a) > 1e-9 and np.std(b) > 1e-9:
                        sent_doc_corr.append(abs(float(np.corrcoef(a, b)[0, 1])))

        per_corpus.append({
            "corpus": name,
            "n_languages": int(df.shape[1]),
            "mean_sentences_per_document": mean_of("Sentence count (Doc)"),
            "mean_paragraphs_per_document": mean_of("Paragraph count (Doc)"),
            "frac_par_sd_identically_zero": round(
                float((df.loc[par_sd].abs() < 1e-12).values.mean()), 4) if par_sd else None,
            "frac_sent_sd_identically_zero": round(
                float((df.loc[sent_sd].abs() < 1e-12).values.mean()), 4) if sent_sd else None,
            "frac_par_avg_identical_to_doc": round(float(np.mean(par_eq_doc)), 4) if par_eq_doc else None,
            "median_abs_corr_sent_avg_vs_doc": round(float(np.median(sent_doc_corr)), 4) if sent_doc_corr else None,
        })

    # Pooled fit matrix — the space the stratifier is actually fitted on.
    core = sorted(set.intersection(*[set(df.index) for df in raw_profiles.values()]))
    X = np.concatenate(
        [raw_profiles[n].loc[core].values.astype(float) for n in sorted(raw_profiles)],
        axis=1,
    ).T  # (language samples, features)

    sd = X.std(axis=0)
    groups: dict[str, list[str]] = {}
    for i, n in enumerate(core):
        key = hashlib.md5(np.round(X[:, i], 10).tobytes()).hexdigest()
        groups.setdefault(key, []).append(n)
    dup_groups = [v for v in groups.values() if len(v) > 1]

    return {
        "note": (
            "Within a single short-text corpus the paragraph level is degenerate. "
            "Pooled across the 17-corpus fit matrix it is not: whether a corpus "
            "has internal paragraph structure is itself a discriminating property."
        ),
        "per_corpus": per_corpus,
        "pooled_fit_matrix": {
            "shape_samples_x_features": list(X.shape),
            "n_constant_columns": int((sd < 1e-12).sum()),
            "n_exact_duplicate_groups": len(dup_groups),
            "n_redundant_columns": sum(len(v) - 1 for v in dup_groups),
            "example_duplicate_groups": [g[:3] for g in dup_groups[:8]],
        },
    }


# ---------------------------------------------------------------------------
# Part 2 — schema-restricted stores
# ---------------------------------------------------------------------------

def build_store(
    raw_profiles: dict[str, pd.DataFrame],
    performances: dict[str, dict[str, dict[str, float]]],
    keep: list[str],
    variance_threshold: float,
    max_pca_components: int,
    exclude: str | None = None,
) -> MKBStore:
    """
    Build and finalise an in-memory MKB restricted to `keep` features.

    `exclude` drops one corpus entirely (profile AND performance records) so
    the refit sees no trace of it — the leave-one-corpus-out protocol of
    corpus_exclusion_refit.py.
    """
    store = MKBStore(
        variance_threshold=variance_threshold,
        max_pca_components=max_pca_components,
    )
    for name, df in raw_profiles.items():
        if name == exclude:
            continue
        store.add_raw_profile(name, df.loc[keep])
    for name, perfs in performances.items():
        if name == exclude:
            continue
        for variant, metrics in perfs.items():
            store.add_performance(name, variant, metrics)
    store.finalise()
    return store


def score_row(dataset: str, recommended: str, scores: dict[str, float]) -> dict:
    """Identical scoring to reporting_measures.py / corpus_exclusion_refit.py."""
    ranked = sorted(scores.values(), reverse=True)
    best, worst = ranked[0], ranked[-1]
    rec_score = scores[recommended]
    gt = max(scores, key=scores.__getitem__)
    return {
        "dataset": dataset,
        "recommended_model": recommended,
        "ground_truth_model": gt,
        "is_correct": recommended == gt,
        "regret": round(best - rec_score, 6),
        "rank": sum(1 for v in ranked if v > rec_score + 1e-12) + 1,
        "range_capture_pct": round(
            100 * ((rec_score - worst) / (best - worst) if best > worst else 1.0), 4
        ),
    }


def measures(rows: list[dict]) -> dict:
    n = len(rows)
    regrets = [r["regret"] for r in rows]
    ranks = [r["rank"] for r in rows]
    caps = [r["range_capture_pct"] for r in rows]
    correct = sum(r["is_correct"] for r in rows)
    return {
        "n": n,
        "top1_fraction": f"{correct}/{n}",
        "mean_regret": round(st.mean(regrets), 6),
        "median_regret": round(st.median(regrets), 6),
        "max_regret": round(max(regrets), 6),
        "mean_rank": round(st.mean(ranks), 2),
        "median_rank": st.median(ranks),
        "max_rank": max(ranks),
        "top3_hit": f"{sum(1 for r in ranks if r <= 3)}/{n}",
        "top10_hit": f"{sum(1 for r in ranks if r <= 10)}/{n}",
        "mean_range_capture_pct": round(st.mean(caps), 2),
        "min_range_capture_pct": round(min(caps), 2),
    }


def paired_vs_full(rows: list[dict], full_rows: list[dict]) -> dict:
    """
    Exact paired sign-flip permutation test of a restricted schema's regret
    against the full schema's, over the same corpora. Two-sided, because the
    question is whether the schemas DIFFER, not whether one is better.
    """
    import itertools

    by_ds = {r["dataset"]: r["regret"] for r in full_rows}
    diffs = [by_ds[r["dataset"]] - r["regret"] for r in rows]  # +ve = restricted better
    nz = [x for x in diffs if abs(x) > 1e-9]
    obs = abs(sum(nz))
    if not nz:
        p = 1.0
    elif len(nz) > 20:
        p = None
    else:
        hits = sum(
            1
            for signs in itertools.product([1, -1], repeat=len(nz))
            if abs(sum(v * s for v, s in zip(nz, signs))) >= obs - 1e-12
        )
        p = hits / 2 ** len(nz)
    return {
        "restricted_better": sum(1 for x in diffs if x > 1e-9),
        "full_better": sum(1 for x in diffs if x < -1e-9),
        "ties": sum(1 for x in diffs if abs(x) <= 1e-9),
        "informative_pairs": len(nz),
        "mean_regret_delta_vs_full": round(st.mean(diffs), 6),
        "two_sided_p": round(p, 4) if p is not None else None,
    }


# ---------------------------------------------------------------------------

def main() -> None:
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))
    metric = report["priority_metric"]
    bench = {d["dataset"]: d["all_benchmark_scores"] for d in report["per_dataset"]}

    full_store = MKBStore.load(REPO / "mkb.pkl")
    raw_profiles = dict(full_store._raw_profiles)
    performances = {
        name: dict(full_store.get_entry(name).performances)
        for name in full_store.datasets
    }
    vt = full_store._variance_threshold
    mpc = full_store._max_pca_components

    # The schema base is the 2,726-feature COMMON CORE, not any single profile:
    # Exorde and Wikipedia carry 200 extra conditional paragraph-level variants
    # (design_and_implementation.tex, Hierarchical Aggregation and Dimensionality).
    # finalise() already discards those — pd.concat unions the indexes, the
    # missing entries become NaN, and fit()'s constant-column filter drops them.
    # Selecting from the intersection reproduces that exclusion explicitly, and
    # keeps "full" identical to the deployed schema.
    core = set.intersection(*[set(df.index) for df in raw_profiles.values()])
    all_names = [n for n in next(iter(raw_profiles.values())).index if n in core]

    eval_profiles = {
        name: pd.read_pickle(REPO / "eval_profiles" / f"{name}.pkl")
        for name in full_store.datasets
    }

    print("Part 1 — degeneracy statistics …", file=sys.stderr)
    degeneracy = degeneracy_statistics(raw_profiles)

    results: dict[str, dict] = {}
    per_dataset: dict[str, dict] = {}

    for cond, allowed in CONDITIONS.items():
        keep = select_features(all_names, allowed)
        print(f"\nPart 2 — condition '{cond}' ({len(keep)} features) …", file=sys.stderr)

        # ── Condition A: evaluation splits, full (restricted-schema) MKB ─────
        store = build_store(raw_profiles, performances, keep, vt, mpc)
        engine = SimilarityEngine(store, k=K)
        rows_a = []
        for name in full_store.datasets:
            profile = eval_profiles[name]
            fp = store.builder.build(profile)
            rec = engine.query(
                fp, priority_metric=metric,
                user_iso_codes=frozenset(profile.columns),
            )
            rows_a.append(score_row(name, rec.recommended_model, bench[name]))

        strat = store.stratifier.stratum_summary()

        # ── LOO: leave-one-corpus-out WITH refit under this schema ───────────
        rows_loo = []
        for i, name in enumerate(full_store.datasets, 1):
            print(f"   LOO [{i}/{len(full_store.datasets)}] {name}", file=sys.stderr)
            loo_store = build_store(raw_profiles, performances, keep, vt, mpc, exclude=name)
            loo_engine = SimilarityEngine(loo_store, k=K)
            profile = eval_profiles[name]
            fp = loo_store.builder.build(profile)
            rec = loo_engine.query(
                fp, priority_metric=metric,
                user_iso_codes=frozenset(profile.columns),
            )
            rows_loo.append(score_row(name, rec.recommended_model, bench[name]))

        results[cond] = {
            "n_features": len(keep),
            "pct_of_full_schema": round(100 * len(keep) / len(all_names), 1),
            "levels_allowed": sorted(allowed) if allowed else "all",
            "stratum_fit": {
                s: {"n_raw_features": int(r.n_raw_features), "n_pcs": int(r.n_pcs),
                    "var_explained_pct": float(r.var_explained_pct)}
                for s, r in strat.iterrows()
            },
            "total_pcs": int(strat["n_pcs"].sum()),
            "A_evaluation_splits": measures(rows_a),
            "LOO_leave_one_corpus_out_refit": measures(rows_loo),
        }
        per_dataset[cond] = {"A": rows_a, "LOO": rows_loo}

    # ── Paired tests: each restricted schema against the full schema ────────
    paired = {}
    for cond in CONDITIONS:
        if cond == "full":
            continue
        paired[cond] = {
            "A_evaluation_splits": paired_vs_full(
                per_dataset[cond]["A"], per_dataset["full"]["A"]),
            "LOO_leave_one_corpus_out_refit": paired_vs_full(
                per_dataset[cond]["LOO"], per_dataset["full"]["LOO"]),
        }

    out = {
        "generated": str(date.today()),
        "priority_metric": metric,
        "k": K,
        "protocol": (
            "Level-restricted schema ablation. Every condition is built in "
            "memory from the SAME raw profiles and the SAME performance records "
            "as the deployed mkb.pkl; the only variable is which segment levels "
            "a feature may involve. Condition A mirrors reporting_measures.py "
            "(coverage guard active on the profile-derived language set); LOO "
            "mirrors corpus_exclusion_refit.py (scaler + PCA refitted on the "
            "other 16 corpora before the held-out corpus is projected in). "
            "Both score against validation_report.json."
        ),
        "degeneracy_statistics": degeneracy,
        "conditions": results,
        "paired_vs_full_schema": paired,
        "per_dataset": per_dataset,
    }

    dest = REPO / "analysis" / f"level_ablation_{date.today().isoformat()}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("per_dataset", "degeneracy_statistics")}, indent=2))
    print(f"\nsnapshot -> {dest}")


if __name__ == "__main__":
    main()
