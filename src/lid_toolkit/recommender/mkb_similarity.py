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

* **Confidence score**: the standard deviation of the k neighbours'
  best-model choices (1 = unanimous, 0 = all disagree) gives a calibrated
  signal of recommendation certainty.
"""

from __future__ import annotations

import logging
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from .fingerprint_builder import FingerprintBuilder
from .mkb_store import MKBStore, METRICS

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
    best_model: str                # best model for this neighbour (by priority metric)
    best_score: float              # its score on the priority metric
    per_stratum_distances: dict[str, float]
    performances: dict[str, dict[str, float]]


@dataclass
class Recommendation:
    """Full recommendation output returned to the user."""
    recommended_model: str
    priority_metric: str
    confidence: float                          # 0–1 (fraction of neighbours agreeing)
    neighbours: list[NeighbourResult]
    all_model_scores: dict[str, float]         # inverse-distance-weighted score per model
    explanation: str                           # human-readable explanation


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

        Returns
        -------
        Recommendation
        """
        if priority_metric not in METRICS:
            raise ValueError(f"priority_metric must be one of {METRICS}.")

        k_use = k if k is not None else self.k
        neighbours = self._compute_neighbours(query_fingerprint, priority_metric)

        if not neighbours:
            raise RuntimeError("No neighbours found — MKB store may be empty or unfinalised.")

        top_k = neighbours[:k_use]

        # Inverse-distance-weighted model voting
        model_scores = self._idw_vote(top_k, priority_metric)

        # Confidence: fraction of neighbours whose best_model agrees with the winner
        best_model = max(model_scores, key=model_scores.__getitem__)
        n_agreeing = sum(1 for nb in top_k if nb.best_model == best_model)
        confidence = n_agreeing / len(top_k)

        explanation = self._build_explanation(
            query_fingerprint, top_k, best_model, model_scores, priority_metric, confidence
        )

        return Recommendation(
            recommended_model=best_model,
            priority_metric=priority_metric,
            confidence=confidence,
            neighbours=top_k,
            all_model_scores=model_scores,
            explanation=explanation,
        )

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

        for i, name_i in enumerate(entry_names):
            fp_i  = store.get_entry(name_i).fingerprint
            best_i = max(
                store.get_entry(name_i).performances.items(),
                key=lambda kv: kv[1].get(priority_metric, -1)
            )[1].get(priority_metric, 0.0)

            for j, name_j in enumerate(entry_names):
                if i == j:
                    continue
                fp_j   = store.get_entry(name_j).fingerprint
                dists  = self._stratum_distances(fp_i, fp_j)
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
            result[s] = float(np.linalg.norm(va[:min_len] - vb[:min_len]))

        # Categorical S6: normalised Hamming distance on cat__ keys
        cat_keys_a = {k: v for k, v in fp_a.items() if k.startswith("cat__")}
        cat_keys_b = {k: v for k, v in fp_b.items() if k.startswith("cat__")}
        all_cat_keys = set(cat_keys_a) | set(cat_keys_b)
        if all_cat_keys:
            n_diff = sum(
                1 for k in all_cat_keys
                if abs(cat_keys_a.get(k, 0.0) - cat_keys_b.get(k, 0.0)) > 0.5
            )
            result["cat"] = n_diff / len(all_cat_keys)
        else:
            result["cat"] = 0.0

        return result

    def _weighted_distance(self, per_stratum: dict[str, float]) -> float:
        """Compute the scalar weighted composite distance from per-stratum distances."""
        total = 0.0
        weight_sum = 0.0
        for s, d in per_stratum.items():
            w = self.stratum_weights.get(s, 1.0)
            total += w * d
            weight_sum += w
        return total / weight_sum if weight_sum > 0 else 0.0

    def _compute_neighbours(
        self,
        query_fp: OrderedDict[str, float],
        priority_metric: str,
    ) -> list[NeighbourResult]:
        """Compute distances to all historical datasets and sort ascending."""
        store = self.store
        results: list[NeighbourResult] = []

        for name in store.datasets:
            entry = store.get_entry(name)
            if entry.fingerprint is None or not entry.performances:
                continue

            per_stratum = self._stratum_distances(query_fp, entry.fingerprint)
            dist = self._weighted_distance(per_stratum)

            # Best model for this historical dataset
            best_var, best_perf = max(
                entry.performances.items(),
                key=lambda kv: kv[1].get(priority_metric, -1),
            )
            best_score = best_perf.get(priority_metric, float("nan"))

            results.append(NeighbourResult(
                dataset_name=name,
                distance=dist,
                similarity_pct=0.0,          # filled below after normalisation
                best_model=best_var,
                best_score=best_score,
                per_stratum_distances=per_stratum,
                performances=entry.performances,
            ))

        if not results:
            return []

        # Normalise distances → similarity percentages
        max_dist = max(r.distance for r in results) or 1.0
        for r in results:
            r.similarity_pct = round((1.0 - r.distance / max_dist) * 100, 1)

        results.sort(key=lambda r: r.distance)
        return results

    def _idw_vote(
        self,
        neighbours: list[NeighbourResult],
        priority_metric: str,
    ) -> dict[str, float]:
        """
        Inverse-distance-weighted voting across k neighbours.

        Each model's score is the sum of its (priority_metric performance ×
        inverse distance) across all neighbours that recommend it, normalised
        by the total inverse weight.
        """
        model_weighted_scores: dict[str, float] = {}
        model_weights: dict[str, float] = {}

        for nb in neighbours:
            inv_d = 1.0 / (nb.distance + 1e-9)
            for model, perfs in nb.performances.items():
                score = perfs.get(priority_metric, 0.0)
                model_weighted_scores[model] = (
                    model_weighted_scores.get(model, 0.0) + inv_d * score
                )
                model_weights[model] = model_weights.get(model, 0.0) + inv_d

        return {
            m: model_weighted_scores[m] / model_weights[m]
            for m in model_weighted_scores
        }

    def _build_explanation(
        self,
        query_fp: OrderedDict[str, float],
        top_k: list[NeighbourResult],
        best_model: str,
        model_scores: dict[str, float],
        priority_metric: str,
        confidence: float,
    ) -> str:
        """Generate a human-readable explanation string."""
        lines: list[str] = []

        lines.append(f"Recommended model: {best_model}")
        lines.append(
            f"Confidence: {confidence:.0%} ({sum(1 for nb in top_k if nb.best_model == best_model)}"
            f"/{len(top_k)} neighbours agree)"
        )
        lines.append("")

        lines.append("Top-k nearest historical datasets:")
        for i, nb in enumerate(top_k, 1):
            lines.append(
                f"  {i}. {nb.dataset_name}  "
                f"(similarity: {nb.similarity_pct:.1f}%,  "
                f"best model: {nb.best_model},  "
                f"{priority_metric}: {nb.best_score:.4f})"
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
        lines.append(f"All model scores (IDW-weighted {priority_metric}):")
        for model, score in sorted(model_scores.items(), key=lambda kv: -kv[1]):
            marker = " ← recommended" if model == best_model else ""
            lines.append(f"  {model}: {score:.4f}{marker}")

        # Categorical notes
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
