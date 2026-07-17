"""
Weighted Multi-Stratum Similarity Engine.

Computes the dissimilarity between a query dataset fingerprint and every
historical fingerprint stored in the MKBStore, then performs k-NN retrieval
and generates a ranked, explained model recommendation.

Key design choices (see architectural plan for full justification)
------------------------------------------------------------------
* **Per-stratum Euclidean distance** rather than global cosine similarity.
  In a PCA-reduced space, Euclidean distance is both valid and informative;
  cosine similarity suffers from concentration-of-measure in high dimensions.

* **Stratum weights** reflect each stratum's predictive relevance.  By
  default, all strata are weighted equally (weight = 1.0).  Call
  :meth:`SimilarityEngine.learn_weights` once historical ground-truth labels
  are available to derive data-driven weights via Pearson correlation.

* **Categorical Stratum S6** contributes a normalised Hamming distance on
  binary flags (``cat__*`` keys) and is kept separate from the continuous
  block so that it can be weighted independently.

* **Confidence score**: the fraction of the k neighbours whose own best
  model agrees with the recommendation (1 = unanimous, 0 = none agree).
  This is a *consensus measure* of neighbourhood consistency — not a
  calibrated probability that the recommendation is optimal.
"""

from __future__ import annotations

import logging
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from .fingerprint_builder import FingerprintBuilder
from .mkb_store import MKBStore, CORE_METRICS, LOWER_IS_BETTER_METRICS
from .model_language_coverage import zero_shot_inventory

logger = logging.getLogger(__name__)

# Default weight for each stratum (equal weighting)
_DEFAULT_STRATUM_WEIGHTS: dict[str, float] = {
    "S1_morphological":   1.0,
    "S2_lexical_diversity": 1.0,
    "S3_structural":      1.0,
    "S4_info_theoretic":  1.0,
    "S5_cross_level":     1.0,
    "cat":                1.0,   # categorical S6 block
}


@dataclass
class NeighbourResult:
    """One k-NN result entry."""
    dataset_name: str
    distance: float
    similarity_pct: float          # 100 * (1 - normalised_distance)
    best_model: str                # best covered model for this neighbour (by priority metric)
    best_score: float              # its score on the priority metric
    per_stratum_distances: dict[str, float]
    performances: dict[str, dict[str, float]]
    # Coverage fields — populated when user_iso_codes is provided to query()
    coverage_gap: frozenset[str] = field(default_factory=frozenset)
    # model_variant → set of languages it cannot handle from the user's set
    per_model_gaps: dict[str, frozenset[str]] = field(default_factory=dict)


@dataclass
class Recommendation:
    """Full recommendation output returned to the user."""
    recommended_model: str
    priority_metric: str
    confidence: float                          # 0–1 (fraction of neighbours agreeing)
    neighbours: list[NeighbourResult]
    all_model_scores: dict[str, float]         # inverse-distance-weighted score per model
    explanation: str                           # human-readable explanation
    # Languages in the user's dataset that no recommended model covers
    uncoverable_languages: frozenset[str] = field(default_factory=frozenset)


class SimilarityEngine:
    """
    Computes weighted multi-stratum similarity and k-NN retrieval.

    Parameters
    ----------
    store : MKBStore
        A finalised MKB store.
    stratum_weights : dict[str, float], optional
        Per-stratum distance weights.  Keys must match the stratum names
        returned by ``store.stratifier.stratum_names`` plus ``"cat"`` for
        the categorical block.  Missing keys default to 1.0.
    k : int
        Number of nearest neighbours to retrieve (default 3).
    """

    def __init__(
        self,
        store: MKBStore,
        stratum_weights: Optional[dict[str, float]] = None,
        k: int = 3,
    ):
        self.store = store
        self.k = k
        self.stratum_weights: dict[str, float] = {
            **_DEFAULT_STRATUM_WEIGHTS,
            **(stratum_weights or {}),
        }

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(
        self,
        query_fingerprint: OrderedDict[str, float],
        priority_metric: str = "f1_macro",
        k: Optional[int] = None,
        user_iso_codes: Optional[frozenset[str]] = None,
        strict_coverage: bool = False,
    ) -> Recommendation:
        """
        Find the k nearest historical datasets and produce a recommendation.

        Parameters
        ----------
        query_fingerprint :
            Output of ``FingerprintBuilder.build()``.
        priority_metric :
            Which benchmark metric to optimise: one of ``accuracy``,
            ``f1_macro``, ``precision_macro``, ``recall_macro``.
        k :
            Override the instance-level k (useful for ablation studies).
        user_iso_codes :
            The set of ISO 639-1 language codes present in the user's dataset
            (i.e. ``frozenset(lang_profile_df.columns)``, or an explicitly
            declared language set for deployment queries).  When provided, the
            engine applies a **language coverage guard**: each candidate model
            is checked against the languages it can identify — its published
            inventory for the zero-shot models (see
            ``model_language_coverage``), otherwise the language set of its
            training corpus.  Models that cannot cover all user languages are
            soft-penalised in the vote (Eq. idw_vote) and the recommendation
            explanation lists any coverage gaps and uncoverable languages
            explicitly.
        strict_coverage :
            Operational deployment mode.  When True, models with a coverage
            gap are hard-filtered from the vote (coverage factor 0.0) whenever
            at least one candidate covers every coverable user language, so a
            partially-covering model can never outvote a fully-covering one.
            Default False — the soft-penalty behaviour of Eq. (idw_vote).

        Returns
        -------
        Recommendation

        Notes
        -----
        The ``priority_metric`` can be any metric stored in the MKBStore
        (e.g., accuracy, f1_macro, f1_weighted, inference_time_total_s, etc.).
        """
        k_use = k if k is not None else self.k
        neighbours = self._compute_neighbours(
            query_fingerprint, priority_metric, user_iso_codes=user_iso_codes
        )

        if not neighbours:
            raise RuntimeError("No neighbours found — MKB store may be empty or unfinalised.")

        top_k = neighbours[:k_use]

        # Inverse-distance-weighted model voting — coverage-aware
        model_scores = self._idw_vote(
            top_k, priority_metric,
            user_iso_codes=user_iso_codes, strict_coverage=strict_coverage,
        )

        # Confidence: fraction of neighbours whose best_model agrees with the winner
        best_model = max(model_scores, key=model_scores.__getitem__)
        n_agreeing = sum(1 for nb in top_k if nb.best_model == best_model)
        confidence = n_agreeing / len(top_k)

        # Languages that no model in the top-k can cover
        uncoverable: frozenset[str] = frozenset()
        if user_iso_codes:
            all_covered: set[str] = set()
            for nb in top_k:
                entry = self.store.get_entry(nb.dataset_name)
                for variant, perfs in nb.performances.items():
                    all_covered |= self._model_known_languages(variant, perfs, entry)
            uncoverable = user_iso_codes - all_covered

        explanation = self._build_explanation(
            query_fingerprint, top_k, best_model, model_scores,
            priority_metric, confidence, user_iso_codes, uncoverable
        )

        return Recommendation(
            recommended_model=best_model,
            priority_metric=priority_metric,
            confidence=confidence,
            neighbours=top_k,
            all_model_scores=model_scores,
            explanation=explanation,
            uncoverable_languages=uncoverable,
        )

    def trace_query(
        self,
        query_fingerprint: OrderedDict[str, float],
        priority_metric: str = "f1_macro",
        k: Optional[int] = None,
        user_iso_codes: Optional[frozenset[str]] = None,
        strict_coverage: bool = False,
    ) -> tuple["Recommendation", dict]:
        """
        Run the full query pipeline and return (Recommendation, math_trace).

        The math_trace dict contains every intermediate variable for manual
        verification: PCA pipeline, per-stratum Euclidean distances, Hamming,
        weighted composite D, max_D, similarity%, top-k list, IDW
        inv_d/coverage_factor/numerators/denominators, and confidence.
        """
        trace: dict = {
            "priority_metric": priority_metric,
            "k": k if k is not None else self.k,
            "strict_coverage": strict_coverage,
        }

        # § 0: PCA pipeline summary
        strat = self.store.stratifier
        trace["pca_pipeline"] = {
            s: {
                "n_components": sfit.n_components,
                "explained_variance_pct": [
                    round(float(v) * 100, 2) for v in sfit.explained_variance_ratio
                ],
                "cumulative_pct": round(float(sum(sfit.explained_variance_ratio)) * 100, 2),
            }
            for s, sfit in strat._fits.items()
        }
        trace["stratum_weights"] = dict(self.stratum_weights)

        # §§ 1–5: distances, max_D, sorted candidates (collected inside _compute_neighbours)
        neighbours = self._compute_neighbours(
            query_fingerprint, priority_metric,
            user_iso_codes=user_iso_codes, _outer_trace=trace,
        )
        if not neighbours:
            raise RuntimeError("No neighbours found — MKB store may be empty or unfinalised.")

        k_use = k if k is not None else self.k
        top_k = neighbours[:k_use]
        trace["top_k"] = [
            {"dataset": r.dataset_name, "D": r.distance, "sim_pct": r.similarity_pct}
            for r in top_k
        ]

        # §§ 6–7: IDW vote (collected inside _idw_vote)
        idw_trace: dict = {}
        model_scores = self._idw_vote(
            top_k, priority_metric,
            user_iso_codes=user_iso_codes, strict_coverage=strict_coverage,
            _trace=idw_trace,
        )
        trace["idw"] = idw_trace

        # § 8: confidence
        best_model = max(model_scores, key=model_scores.__getitem__)
        n_agreeing = sum(1 for nb in top_k if nb.best_model == best_model)
        confidence = n_agreeing / len(top_k)
        trace["confidence"] = {
            "n_agreeing": n_agreeing,
            "k": len(top_k),
            "confidence": confidence,
        }
        trace["recommended_model"] = best_model

        # Build the full Recommendation via the existing query() path
        rec = self.query(
            query_fingerprint, priority_metric=priority_metric,
            k=k, user_iso_codes=user_iso_codes, strict_coverage=strict_coverage,
        )
        return rec, trace

    # ------------------------------------------------------------------
    # Weight learning (optional, data-driven)
    # ------------------------------------------------------------------

    def learn_weights(self, priority_metric: str = "f1_macro") -> dict[str, float]:
        """
        Derive stratum weights via leave-one-out Pearson correlation.

        For each stratum, computes the correlation between the within-stratum
        distance and the performance gap (best-model F1 delta) across all
        LOO pairs.  Higher correlation → stratum is more predictive → higher
        weight.

        Weights are normalised to sum to 1.0 × n_strata (so average weight
        stays 1.0).  Results are stored in ``self.stratum_weights``.

        Returns
        -------
        dict[str, float]
            Updated stratum weights.
        """
        store = self.store
        entry_names = [
            n for n in store.datasets
            if store.get_entry(n).fingerprint is not None
            and store.get_entry(n).performances
        ]
        if len(entry_names) < 3:
            logger.warning(
                "Only %d datasets — too few for reliable weight learning. "
                "Using equal weights.", len(entry_names)
            )
            return self.stratum_weights

        stratum_names = store.stratifier.stratum_names + ["cat"]
        per_stratum_dists: dict[str, list[float]] = {s: [] for s in stratum_names}
        perf_gaps: list[float] = []

        lower_is_better = priority_metric in LOWER_IS_BETTER_METRICS
        for i, name_i in enumerate(entry_names):
            fp_i  = store.get_entry(name_i).fingerprint
            if lower_is_better:
                best_i = min(
                    store.get_entry(name_i).performances.items(),
                    key=lambda kv: kv[1].get(priority_metric, float("inf"))
                )[1].get(priority_metric, 0.0)
            else:
                best_i = max(
                    store.get_entry(name_i).performances.items(),
                    key=lambda kv: kv[1].get(priority_metric, -1)
                )[1].get(priority_metric, 0.0)

            for j, name_j in enumerate(entry_names):
                if i == j:
                    continue
                fp_j   = store.get_entry(name_j).fingerprint
                dists  = self._stratum_distances(fp_i, fp_j)
                if lower_is_better:
                    best_j = min(
                        store.get_entry(name_j).performances.items(),
                        key=lambda kv: kv[1].get(priority_metric, float("inf"))
                    )[1].get(priority_metric, 0.0)
                else:
                    best_j = max(
                        store.get_entry(name_j).performances.items(),
                        key=lambda kv: kv[1].get(priority_metric, -1)
                    )[1].get(priority_metric, 0.0)

                for s in stratum_names:
                    per_stratum_dists[s].append(dists.get(s, 0.0))
                perf_gaps.append(abs(best_i - best_j))

        gaps = np.array(perf_gaps)
        new_weights: dict[str, float] = {}
        for s in stratum_names:
            dists = np.array(per_stratum_dists[s])
            if dists.std() < 1e-9 or gaps.std() < 1e-9:
                new_weights[s] = 1.0
                continue
            corr = float(np.corrcoef(dists, gaps)[0, 1])
            # Higher |corr| → more predictive → higher weight
            new_weights[s] = max(0.1, abs(corr))

        # Normalise so average weight = 1.0
        mean_w = np.mean(list(new_weights.values()))
        if mean_w > 0:
            new_weights = {s: w / mean_w for s, w in new_weights.items()}

        self.stratum_weights.update(new_weights)
        logger.info("Stratum weights learned: %s", new_weights)
        return self.stratum_weights

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _stratum_distances(
        self,
        fp_a: OrderedDict[str, float],
        fp_b: OrderedDict[str, float],
        _trace: Optional[dict] = None,
    ) -> dict[str, float]:
        """
        Compute per-stratum Euclidean distance between two fingerprints.

        Returns
        -------
        dict[str, float]
            Keys are stratum names (continuous) + ``"cat"`` (categorical).
        """
        store = self.store
        stratum_names = store.stratifier.stratum_names

        result: dict[str, float] = {}

        for s in stratum_names:
            va, _ = FingerprintBuilder.stratum_slice(fp_a, s)
            vb, _ = FingerprintBuilder.stratum_slice(fp_b, s)
            if va.size == 0 or vb.size == 0:
                result[s] = 0.0
                continue
            # Ensure same length (should always be equal after fitting)
            min_len = min(va.size, vb.size)
            diff = va[:min_len] - vb[:min_len]
            result[s] = float(np.linalg.norm(diff))
            if _trace is not None:
                _trace.setdefault("stratum_details", {})[s] = {
                    "query_vec": va[:min_len].tolist(),
                    "candidate_vec": vb[:min_len].tolist(),
                    "diff_vec": diff.tolist(),
                    "euclidean_d": result[s],
                }

        # Categorical S6: normalised Hamming distance on cat__ keys
        cat_keys_a = {k: v for k, v in fp_a.items() if k.startswith("cat__")}
        cat_keys_b = {k: v for k, v in fp_b.items() if k.startswith("cat__")}
        all_cat_keys = set(cat_keys_a) | set(cat_keys_b)
        if all_cat_keys:
            differing = [
                k for k in all_cat_keys
                if abs(cat_keys_a.get(k, 0.0) - cat_keys_b.get(k, 0.0)) > 0.5
            ]
            n_diff = len(differing)
            result["cat"] = n_diff / len(all_cat_keys)
        else:
            differing = []
            n_diff = 0
            result["cat"] = 0.0

        if _trace is not None:
            _trace["hamming"] = {
                "n_cat_flags": len(all_cat_keys),
                "n_differing": n_diff,
                "differing_keys": differing,
                "d_cat": result["cat"],
            }

        return result

    def _weighted_distance(
        self,
        per_stratum: dict[str, float],
        _trace: Optional[dict] = None,
    ) -> float:
        """Compute the scalar weighted composite distance from per-stratum distances."""
        total = 0.0
        weight_sum = 0.0
        terms: dict = {}
        for s, d in per_stratum.items():
            w = self.stratum_weights.get(s, 1.0)
            total += w * d
            weight_sum += w
            if _trace is not None:
                terms[s] = {"w": w, "d": d, "w_times_d": w * d}
        composite = total / weight_sum if weight_sum > 0 else 0.0
        if _trace is not None:
            _trace["weighted_composite"] = {
                "per_stratum_terms": terms,
                "weight_sum": weight_sum,
                "total_numerator": total,
                "composite_D": composite,
            }
        return composite

    def _model_known_languages(
        self,
        variant: str,
        perfs: dict[str, float],
        entry,
    ) -> frozenset[str]:
        """
        Languages that model `variant` can identify.

        Resolution order:
        1. An explicit ``_training_languages`` set stored in the performance
           record (authoritative when present).
        2. The published inventory for zero-shot models (lid.176, CLD3,
           XLM-V language-id) — these models' coverage is a property of the
           model, NOT of the benchmark corpus they were evaluated on.
        3. Fallback for trained configurations: the language set of the
           training corpus inferred from the variant-name suffix
           (longest dataset-name match wins).
        """
        train_langs = perfs.get("_training_languages")
        if isinstance(train_langs, (set, frozenset)):
            return frozenset(train_langs)
        zs = zero_shot_inventory(variant)
        if zs is not None:
            return zs
        known = frozenset(entry.iso_codes)
        for ds_name in sorted(self.store.datasets, key=len, reverse=True):
            if variant.endswith(f"_{ds_name}"):
                known = frozenset(self.store.get_entry(ds_name).iso_codes)
                break
        return known

    def _compute_neighbours(
        self,
        query_fp: OrderedDict[str, float],
        priority_metric: str,
        user_iso_codes: Optional[frozenset[str]] = None,
        _outer_trace: Optional[dict] = None,
    ) -> list[NeighbourResult]:
        """
        Compute distances to all historical datasets and sort ascending.

        When ``user_iso_codes`` is provided, each model variant is checked for
        language coverage.  The ``best_model`` field of each NeighbourResult is
        set to the best *fully-covering* model variant.  If no variant covers all
        user languages, the variant with the smallest coverage gap (fewest missing
        languages) is chosen and the gap is recorded in ``coverage_gap``.
        """
        store = self.store
        results: list[NeighbourResult] = []

        for name in store.datasets:
            entry = store.get_entry(name)
            if entry.fingerprint is None or not entry.performances:
                continue

            candidate_trace: Optional[dict] = {} if _outer_trace is not None else None
            per_stratum = self._stratum_distances(query_fp, entry.fingerprint, _trace=candidate_trace)
            dist = self._weighted_distance(per_stratum, _trace=candidate_trace)

            # ── Coverage-aware model selection ────────────────────────────────
            per_model_gaps: dict[str, frozenset[str]] = {}
            if user_iso_codes:
                for variant, perfs in entry.performances.items():
                    known = self._model_known_languages(variant, perfs, entry)
                    gap = user_iso_codes - known
                    per_model_gaps[variant] = gap

                # Prefer fully-covering variants; fall back to smallest gap.
                # Languages that NO variant covers are reported separately as
                # uncoverable — they must not disqualify otherwise fully-
                # covering models, so coverage is judged on the effective gap
                # (gap minus the entry-wide uncoverable set).
                entry_uncoverable: frozenset[str] = (
                    frozenset.intersection(*per_model_gaps.values())
                    if per_model_gaps else frozenset()
                )
                fully_covering = {v: p for v, p in entry.performances.items()
                                  if not (per_model_gaps[v] - entry_uncoverable)}
                candidates = fully_covering if fully_covering else entry.performances
            else:
                candidates = entry.performances

            if priority_metric in LOWER_IS_BETTER_METRICS:
                best_var, best_perf = min(
                    candidates.items(),
                    key=lambda kv: kv[1].get(priority_metric, float("inf")),
                )
            else:
                best_var, best_perf = max(
                    candidates.items(),
                    key=lambda kv: kv[1].get(priority_metric, -1),
                )
            best_score = best_perf.get(priority_metric, float("nan"))
            gap = per_model_gaps.get(best_var, frozenset())

            results.append(NeighbourResult(
                dataset_name=name,
                distance=dist,
                similarity_pct=0.0,          # filled below after normalisation
                best_model=best_var,
                best_score=best_score,
                per_stratum_distances=per_stratum,
                performances=entry.performances,
                coverage_gap=gap,
                per_model_gaps=per_model_gaps,
            ))

            if _outer_trace is not None and candidate_trace is not None:
                candidate_trace["dataset"] = name
                candidate_trace["composite_D"] = dist
                candidate_trace["best_model"] = best_var
                candidate_trace["best_score"] = best_score
                _outer_trace.setdefault("all_candidates", []).append(candidate_trace)

        if not results:
            return []

        # Normalise distances → similarity percentages
        max_dist = max(r.distance for r in results) or 1.0
        for r in results:
            r.similarity_pct = round((1.0 - r.distance / max_dist) * 100, 1)

        results.sort(key=lambda r: r.distance)

        if _outer_trace is not None:
            _outer_trace["max_D"] = max_dist
            _outer_trace["sorted_candidates"] = [
                {"dataset": r.dataset_name, "D": r.distance, "sim_pct": r.similarity_pct}
                for r in results
            ]

        return results

    def _idw_vote(
        self,
        neighbours: list[NeighbourResult],
        priority_metric: str,
        user_iso_codes: Optional[frozenset[str]] = None,
        strict_coverage: bool = False,
        _trace: Optional[dict] = None,
    ) -> dict[str, float]:
        """
        Inverse-distance-weighted voting across k neighbours.

        Each model's IDW score = sum(inv_distance × metric_score × coverage_factor).

        When ``user_iso_codes`` is provided, the coverage factor cov(m, q)
        depends on the mode:

        - **Default (soft penalty)** — the thesis Eq. (idw_vote) behaviour:
          cov = 1.0 for fully-covering models, else ``1 - |gap|/|L_q|``.
          Gapped models are penalised but can still win the vote.
        - **strict_coverage=True** — operational deployment mode: if at least
          one model in the top-k covers every *coverable* user language,
          gapped models are hard-filtered (cov = 0.0) so they cannot win.
          Languages that NO candidate covers are reported separately as
          ``uncoverable_languages`` and excluded from this test (effective
          gaps), so a few exotic languages cannot disable the filter.  Only
          when no fully-covering model exists does the soft penalty apply,
          ensuring a recommendation is always returned.
        """
        model_weighted_scores: dict[str, float] = {}

        n_user_langs = len(user_iso_codes) if user_iso_codes else 0

        # Strict mode: determine whether any model in the top-k covers every
        # coverable user language (effective gap = gap minus the languages no
        # candidate at all can cover).
        any_fully_covering = False
        global_uncoverable: frozenset[str] = frozenset()
        n_coverable = n_user_langs
        if strict_coverage and user_iso_codes and n_user_langs > 0:
            all_gaps = [
                nb.per_model_gaps.get(model, frozenset())
                for nb in neighbours
                for model in nb.performances
            ]
            if all_gaps:
                global_uncoverable = frozenset.intersection(*all_gaps)
            n_coverable = n_user_langs - len(global_uncoverable)
            any_fully_covering = any(not (g - global_uncoverable) for g in all_gaps)

        idw_per_nb: list[dict] = [] if _trace is not None else []  # always built for trace

        total_inv_d: float = 0.0
        lower_is_better = priority_metric in LOWER_IS_BETTER_METRICS
        for nb in neighbours:
            inv_d = 1.0 / (nb.distance + 1e-9)
            total_inv_d += inv_d
            nb_record: dict = {"dataset": nb.dataset_name, "inv_d": inv_d, "per_model": {}}
            for model, perfs in nb.performances.items():
                raw_score = perfs.get(priority_metric, 0.0)
                # Invert lower-is-better metrics so higher scores always win
                if lower_is_better:
                    score = 1.0 / (raw_score + 1e-9) if raw_score > 0 else 1e9
                else:
                    score = raw_score

                # Coverage factor cov(m, q) — see docstring for the two modes.
                if user_iso_codes and n_user_langs > 0:
                    gap = nb.per_model_gaps.get(model, frozenset())
                    if strict_coverage:
                        eff_gap = gap - global_uncoverable
                        if not eff_gap:
                            coverage_factor = 1.0
                        elif any_fully_covering:
                            coverage_factor = 0.0
                        else:
                            coverage_factor = (
                                1.0 - len(eff_gap) / n_coverable
                                if n_coverable > 0 else 1.0
                            )
                    else:
                        # Default: soft penalty exactly as Eq. (idw_vote) —
                        # full gap over the total user language count.
                        coverage_factor = 1.0 - len(gap) / n_user_langs
                else:
                    gap = frozenset()
                    coverage_factor = 1.0

                contribution = inv_d * score * coverage_factor
                model_weighted_scores[model] = (
                    model_weighted_scores.get(model, 0.0) + contribution
                )

                if _trace is not None:
                    nb_record["per_model"][model] = {
                        "score": score,
                        "gap_size": len(gap),
                        "coverage_factor": coverage_factor,
                        "contribution": contribution,
                    }
            if _trace is not None:
                idw_per_nb.append(nb_record)

        # Normalise by total inv-distance (global), not per-model inv-distance.
        # Per-model normalisation cancels the distance weight for models that appear
        # in only one neighbour, making proximity irrelevant.  Global normalisation
        # preserves the closest-neighbour advantage.
        denom = total_inv_d or 1.0
        normalized = {m: model_weighted_scores[m] / denom for m in model_weighted_scores}
        if _trace is not None:
            _trace["per_neighbour"] = idw_per_nb
            _trace["raw_numerators"] = dict(model_weighted_scores)
            _trace["denominator"] = denom
            _trace["normalized_idw_scores"] = normalized
        return normalized

    def _build_explanation(
        self,
        query_fp: OrderedDict[str, float],
        top_k: list[NeighbourResult],
        best_model: str,
        model_scores: dict[str, float],
        priority_metric: str,
        confidence: float,
        user_iso_codes: Optional[frozenset[str]] = None,
        uncoverable: frozenset[str] = frozenset(),
    ) -> str:
        """Generate a human-readable explanation string."""
        lines: list[str] = []

        lines.append(f"Recommended model: {best_model}")
        lines.append(
            f"Confidence: {confidence:.0%} ({sum(1 for nb in top_k if nb.best_model == best_model)}"
            f"/{len(top_k)} neighbours agree)"
        )

        # ── Coverage warning — placed prominently at the top ─────────────────
        if user_iso_codes:
            best_gap = top_k[0].per_model_gaps.get(best_model, frozenset()) if top_k else frozenset()
            if best_gap:
                lines.append(
                    f"\n⚠️  COVERAGE WARNING: '{best_model}' was not trained on "
                    f"{len(best_gap)} of your {len(user_iso_codes)} language(s): "
                    f"{sorted(best_gap)}.\n"
                    "   These languages will be silently misclassified. "
                    "Consider retraining on your full language set."
                )
            if uncoverable:
                lines.append(
                    f"⚠️  UNCOVERABLE LANGUAGES: {sorted(uncoverable)} appear in your dataset "
                    "but are absent from ALL historical benchmark datasets. "
                    "No reliable recommendation can be made for these languages."
                )

        lines.append("")
        lines.append("Top-k nearest historical datasets:")
        for i, nb in enumerate(top_k, 1):
            gap_note = ""
            if user_iso_codes:
                nb_gap = nb.per_model_gaps.get(nb.best_model, frozenset())
                gap_note = f",  coverage gap: {sorted(nb_gap)}" if nb_gap else ",  full coverage"
            lines.append(
                f"  {i}. {nb.dataset_name}  "
                f"(similarity: {nb.similarity_pct:.1f}%,  "
                f"best model: {nb.best_model},  "
                f"{priority_metric}: {nb.best_score:.4f}{gap_note})"
            )

        lines.append("")
        lines.append(f"Primary similarity driver (nearest neighbour = '{top_k[0].dataset_name}'):")
        if top_k:
            psd = top_k[0].per_stratum_distances
            sorted_strata = sorted(psd.items(), key=lambda kv: kv[1])
            for s, d in sorted_strata:
                label = {
                    "S1_morphological":   "Morphological richness",
                    "S2_lexical_diversity": "Lexical diversity",
                    "S3_structural":      "Structural/syntactic structure",
                    "S4_info_theoretic":  "Information-theoretic profile",
                    "S5_cross_level":     "Cross-level cohesion",
                    "cat":                "Typological flags (script, tonality, family)",
                }.get(s, s)
                lines.append(f"  {label}: distance = {d:.4f}")

        lines.append("")
        lines.append(f"All model scores (IDW-weighted {priority_metric}, coverage-penalised):")
        for model, score in sorted(model_scores.items(), key=lambda kv: -kv[1]):
            marker = " ← recommended" if model == best_model else ""
            # Show gap size across top-k neighbours for each model
            if user_iso_codes and top_k:
                gaps = [nb.per_model_gaps.get(model, frozenset()) for nb in top_k]
                avg_gap = sum(len(g) for g in gaps) / len(gaps)
                gap_info = f"  [avg gap: {avg_gap:.1f} langs]" if avg_gap > 0 else "  [full coverage]"
            else:
                gap_info = ""
            lines.append(f"  {model}: {score:.4f}{gap_info}{marker}")

        # ── Categorical notes ─────────────────────────────────────────────────
        n_tonal = int(query_fp.get("cat__n_tonal", 0))
        n_cjk   = int(query_fp.get("cat__has_cjk", 0))
        if n_tonal > 0:
            lines.append(
                f"\nNote: {n_tonal} tonal language(s) detected — "
                "character-aware models generally perform better on tonal languages."
            )
        if n_cjk:
            lines.append(
                "Note: CJK script detected — ensure your chosen model was trained on CJK data."
            )

        return "\n".join(lines)
