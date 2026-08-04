"""
Semantically-stratified PCA compression of DeepProfiler features.

The raw linguistic features (a fixed 2,726-feature core schema per language;
up to ~2,926 in the pooled union when conditional paragraph-level variants
fire for multi-paragraph corpora) are partitioned into five linguistically
coherent strata *before* any dimensionality reduction, then PCA is applied
independently within each stratum. The fitting step's validity filter keeps
exactly the 2,726-feature core, so every fingerprint is built from the same
fixed feature space.  This avoids the instability of a global
PCA at low n, and preserves linguistic semantics in the reduced space.

Strata (mutually exclusive, exhaustive over the features produced by
``DeepProfiler.get_multilingual_profile()``):

    S1 – Morphological Richness
         Inflectional morphology: person, number, definiteness, tense,
         voice, word-lemma Levenshtein distance, and word-types-per-lemma
         measures (inflected types per lemma ≈ paradigm size).
    S2 – Lexical Diversity
         Type-token ratios, hapax legomena, and Zipf frequency scores.
    S3 – Structural / Syntactic
         PoS incidence and count, PoS ratios, word/sentence/paragraph
         length and count statistics.
    S4 – Information-Theoretic
         Shannon entropy (word, letter), Zipf curve steepness and
         goodness-of-fit.
    S5 – Cross-Level Cohesion
         All cross-level overlap, cosine-distance, and Levenshtein
         measures (Par-Doc, Sent-Doc, Par-Par adj, Sent-Par, Sent-Sent adj).

Usage::

    stratifier = FeatureStratifier()
    stratifier.fit(lang_profile_df)           # pd.DataFrame: features × languages
    compressed = stratifier.transform(vec)    # dict: stratum_name → np.ndarray (n_PCs,)
    stratifier.save("stratifier.pkl")
    stratifier2 = FeatureStratifier.load("stratifier.pkl")
"""

from __future__ import annotations

import re
import pickle
import logging
from pathlib import Path
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stratum keyword definitions
# Each stratum is a list of (case-insensitive) substring patterns.
# Assignment is *first-match wins*, strata are checked in priority order.
# ---------------------------------------------------------------------------

# Priority order matters: more specific patterns first.
_STRATUM_PATTERNS: dict[str, list[str]] = {
    # ── S4: Information-Theoretic (most specific — checked first) ───────────
    "S4_info_theoretic": [
        "entropy",
        "zipf steepness",
        "zipf goodness",
    ],

    # ── S5: Cross-Level Cohesion ─────────────────────────────────────────────
    "S5_cross_level": [
        "overlap count",
        "overlap ratio",
        "cosine distance",
        "levenshtein char",
        "levenshtein word dist",
        "levenshtein lemma dist",
        "levenshtein pos dist",
        # pair-type suffixes that appear in cross-level feature names
        "par-doc",
        "sent-doc",
        "par-par",
        "sent-par",
        "sent-sent",
    ],

    # ── S1: Morphological Richness ────────────────────────────────────────────
    "S1_morphological": [
        "first person pronoun",
        "second person pronoun",
        "third person pronoun",
        "personal pronoun",
        "interrogative",
        "demonstrative",
        "singular word",
        "plural word",
        "indefinite word",
        "definite word",
        "finite verb",
        "infinitive verb",
        "verbal adjective",
        "past tense",
        "present tense",
        "passive voice",
        "word-lemma levenshtein",
        "word types per lemma",
        "types per lemma",
    ],

    # ── S2: Lexical Diversity ─────────────────────────────────────────────────
    "S2_lexical_diversity": [
        "type-token ratio",
        "moving average type",
        "hapax legomena",
        # NOTE: inert — Honoré's statistic is not emitted by DeepProfiler
        # (omitted from the schema as a transform of the retained hapax
        # legomena measures), so this pattern never matches. Kept for
        # forward-compatibility if the measure is reinstated.
        "honoré",
        "zipf frequency",
        "frequent word",
        "infrequent word",
        # NOTE: unreachable — S4's "entropy" pattern is checked first under
        # first-match-wins, so all entropy features route to S4
        # (information-theoretic), never here. Kept only to document that
        # entropy was considered for this stratum; do not read these as
        # live S2 members.
        "word entropy",
        "letter entropy",
        # per-PoS type counts contribute to lexical diversity
        "type count",
    ],

    # ── S3: Structural / Syntactic (catch-all) ────────────────────────────────
    "S3_structural": [
        # everything not already claimed above
        "",  # empty string matches every feature name — always last
    ],
}

_STRATUM_ORDER = list(_STRATUM_PATTERNS.keys())


def _assign_stratum(feature_name: str) -> str:
    """Return the stratum key for a single feature name (first-match wins)."""
    lower = feature_name.lower()
    for stratum, patterns in _STRATUM_PATTERNS.items():
        for pat in patterns:
            if pat in lower:
                return stratum
    return "S3_structural"  # fallback (should be covered by "" above)


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

@dataclass
class StratumFit:
    """Fitted PCA + scaler for one stratum."""
    feature_names: list[str]       # ordered subset of raw feature names
    scaler: StandardScaler
    pca: PCA
    n_components: int              # actual PCs retained (≥95 % explained)
    explained_variance_ratio: np.ndarray


class FeatureStratifier:
    """
    Fits per-stratum PCA transforms on historical language profiles and
    projects new language profiles into the reduced space.

    Parameters
    ----------
    variance_threshold : float
        Minimum cumulative explained variance to retain (default 0.95).
    max_components : int
        Hard upper limit on PCs per stratum (default 20).
    """

    def __init__(self, variance_threshold: float = 0.95, max_components: int = 20):
        self.variance_threshold = variance_threshold
        self.max_components = max_components
        self._fits: dict[str, StratumFit] = {}
        self._feature_to_stratum: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Fitting
    # ------------------------------------------------------------------

    def fit(self, lang_profile_df: pd.DataFrame) -> "FeatureStratifier":
        """
        Fit per-stratum PCAs on historical language profiles.

        Parameters
        ----------
        lang_profile_df : pd.DataFrame
            Output of ``DeepProfiler.get_multilingual_profile()``.
            Shape: (n_features, n_languages).  Each column is one language's
            mean feature vector over its profiled text samples.
        """
        # Transpose: rows = language samples, columns = features
        X = lang_profile_df.T  # shape (n_languages, n_features)
        all_feature_names = list(X.columns)

        # Assign every feature to exactly one stratum
        stratum_map: dict[str, list[str]] = {k: [] for k in _STRATUM_ORDER}
        for fname in all_feature_names:
            s = _assign_stratum(fname)
            stratum_map[s].append(fname)
            self._feature_to_stratum[fname] = s

        n_samples = X.shape[0]
        logger.info("Fitting FeatureStratifier on %d language samples, %d features.",
                    n_samples, len(all_feature_names))

        self._fits.clear()
        for stratum, feat_names in stratum_map.items():
            if not feat_names:
                logger.debug("Stratum %s: no features — skipped.", stratum)
                continue

            X_sub = X[feat_names].values.astype(float)

            # Drop columns that are constant across all samples (PCA can't use them)
            col_std = X_sub.std(axis=0)
            valid_mask = col_std > 0
            feat_names_valid = [f for f, v in zip(feat_names, valid_mask) if v]
            X_sub = X_sub[:, valid_mask]

            if X_sub.shape[1] == 0:
                logger.warning("Stratum %s: all features are constant — skipped.", stratum)
                continue

            # Standardise within the stratum
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_sub)

            # PCA — can use at most min(n_samples-1, n_valid_features) components
            max_pc = min(self.max_components, X_scaled.shape[0] - 1, X_scaled.shape[1])
            pca = PCA(n_components=max_pc, random_state=42)
            pca.fit(X_scaled)

            # Retain components up to the variance threshold
            cum_var = np.cumsum(pca.explained_variance_ratio_)
            n_keep = int(np.searchsorted(cum_var, self.variance_threshold) + 1)
            n_keep = min(n_keep, max_pc)

            # Refit with only the kept components for clean storage
            pca_final = PCA(n_components=n_keep, random_state=42)
            pca_final.fit(X_scaled)

            self._fits[stratum] = StratumFit(
                feature_names=feat_names_valid,
                scaler=scaler,
                pca=pca_final,
                n_components=n_keep,
                explained_variance_ratio=pca_final.explained_variance_ratio_,
            )
            logger.info(
                "  %-22s  %4d raw → %4d PCs  (%.1f%% var explained,  %d valid feats)",
                stratum, len(feat_names), n_keep,
                float(np.sum(pca_final.explained_variance_ratio_)) * 100,
                len(feat_names_valid),
            )

        return self

    # ------------------------------------------------------------------
    # Projection
    # ------------------------------------------------------------------

    def transform(self, lang_vector: dict | pd.Series) -> dict[str, np.ndarray]:
        """
        Project a single language's feature vector into the PCA spaces.

        Parameters
        ----------
        lang_vector : dict or pd.Series
            Mapping from feature name → scalar value.  Missing features
            are filled with 0 (mean-imputed relative to historical data
            because the scaler centres around the training mean).

        Returns
        -------
        dict
            Keys are stratum names; values are 1-D numpy arrays (n_PCs,).
        """
        if not self._fits:
            raise RuntimeError("FeatureStratifier has not been fitted yet. Call fit() first.")

        result: dict[str, np.ndarray] = {}
        for stratum, sfit in self._fits.items():
            # Build the raw feature vector for this stratum
            vals = np.array(
                [float(lang_vector.get(f, 0.0)) for f in sfit.feature_names],
                dtype=float,
            )
            # Replace NaN/Inf with 0 before scaling
            vals = np.nan_to_num(vals, nan=0.0, posinf=0.0, neginf=0.0)

            X_scaled = sfit.scaler.transform(vals.reshape(1, -1))
            pc_vec   = sfit.pca.transform(X_scaled)[0]
            result[stratum] = pc_vec

        return result

    # ------------------------------------------------------------------
    # Summary helpers
    # ------------------------------------------------------------------

    def stratum_summary(self) -> pd.DataFrame:
        """Return a DataFrame summarising each stratum's fit."""
        rows = []
        for name, sfit in self._fits.items():
            rows.append({
                "stratum": name,
                "n_raw_features": len(sfit.feature_names),
                "n_pcs": sfit.n_components,
                "var_explained_pct": round(float(np.sum(sfit.explained_variance_ratio)) * 100, 1),
            })
        return pd.DataFrame(rows).set_index("stratum")

    @property
    def stratum_names(self) -> list[str]:
        return list(self._fits.keys())

    @property
    def total_pcs(self) -> int:
        return sum(s.n_components for s in self._fits.values())

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        with open(path, "wb") as fh:
            pickle.dump(self, fh, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info("FeatureStratifier saved to %s.", path)

    @classmethod
    def load(cls, path: str | Path) -> "FeatureStratifier":
        with open(path, "rb") as fh:
            obj = pickle.load(fh)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected FeatureStratifier, got {type(obj)}")
        logger.info("FeatureStratifier loaded from %s.", path)
        return obj
