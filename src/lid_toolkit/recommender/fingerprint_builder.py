"""
Dataset Fingerprint Builder.

Converts a ``DeepProfiler.get_multilingual_profile()`` output (a DataFrame
with linguistic feature vectors per language) into a fixed-length, fully
interpretable "dataset fingerprint" that can be compared across corpora.

Fingerprint structure
---------------------
1. **Continuous block** (one section per stratum S1–S5):
   For each stratum, each PC is summarised across all languages with four
   statistics: mean, std, min, max.  Additionally, the *within-dataset
   standard deviation* of each PC is kept as a "heterogeneity" signal.

   Example: stratum S1 with 8 PCs → 8 × 5 = 40 values
             (mean_PC0 … mean_PC7, std_PC0 … std_PC7, min_*, max_*, het_*)

2. **Categorical block** (Stratum S6 — never PCA'd):
   Binary/ratio flags from ``typology_lookup.dataset_typology_flags()``.
   Keys prefixed with ``cat__``.

The full fingerprint is returned as an ``OrderedDict[str, float]`` so it can
be trivially converted to a ``pd.Series`` or ``np.ndarray``.
"""

from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Optional

import numpy as np
import pandas as pd

from .feature_stratifier import FeatureStratifier
from .typology_lookup import dataset_typology_flags

logger = logging.getLogger(__name__)


class FingerprintBuilder:
    """
    Constructs fixed-length dataset fingerprints from per-language profiles.

    Parameters
    ----------
    stratifier : FeatureStratifier
        A *fitted* FeatureStratifier instance.
    """

    def __init__(self, stratifier: FeatureStratifier):
        if not stratifier._fits:
            raise ValueError("FeatureStratifier must be fitted before building fingerprints.")
        self.stratifier = stratifier

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self, lang_profile_df: pd.DataFrame) -> OrderedDict[str, float]:
        """
        Build a fingerprint for one dataset.

        Parameters
        ----------
        lang_profile_df : pd.DataFrame
            Output of ``DeepProfiler.get_multilingual_profile()``.
            Shape: (n_features, n_languages).

        Returns
        -------
        OrderedDict[str, float]
            All fingerprint values, keyed with descriptive names.
        """
        iso_codes = list(lang_profile_df.columns)
        n_langs   = len(iso_codes)

        if n_langs == 0:
            raise ValueError("lang_profile_df has no language columns.")

        # ── Step 1: per-language compressed vectors ─────────────────────────
        # Shape: n_langs × {stratum: np.ndarray}
        per_lang_strata: list[dict[str, np.ndarray]] = []
        for iso in iso_codes:
            lang_vec = lang_profile_df[iso]  # pd.Series: feature → value
            projected = self.stratifier.transform(lang_vec)
            per_lang_strata.append(projected)

        # ── Step 2: aggregate across languages per stratum ──────────────────
        fingerprint: OrderedDict[str, float] = OrderedDict()

        for stratum in self.stratifier.stratum_names:
            # Stack PC vectors for all languages: shape (n_langs, n_PCs)
            mat = np.vstack([pls[stratum] for pls in per_lang_strata
                             if stratum in pls])

            if mat.ndim == 1:
                mat = mat.reshape(1, -1)

            n_pcs = mat.shape[1]

            for pc_idx in range(n_pcs):
                col = mat[:, pc_idx]
                key_prefix = f"{stratum}_PC{pc_idx:02d}"
                fingerprint[f"{key_prefix}_mean"] = float(np.mean(col))
                fingerprint[f"{key_prefix}_std"]  = float(np.std(col, ddof=0))
                fingerprint[f"{key_prefix}_min"]  = float(np.min(col))
                fingerprint[f"{key_prefix}_max"]  = float(np.max(col))
                # Within-dataset heterogeneity (meaningful only when n_langs > 1)
                fingerprint[f"{key_prefix}_het"]  = float(
                    np.std(col, ddof=1) if n_langs > 1 else 0.0
                )

        # ── Step 3: categorical Stratum S6 typology flags ────────────────────
        cat_flags = dataset_typology_flags(iso_codes)
        for k, v in cat_flags.items():
            fingerprint[k] = float(v)

        logger.debug(
            "Fingerprint built: %d languages → %d dimensions  "
            "(%d continuous + %d categorical).",
            n_langs,
            len(fingerprint),
            len(fingerprint) - len(cat_flags),
            len(cat_flags),
        )
        return fingerprint

    # ------------------------------------------------------------------
    # Convenience: convert to numpy (continuous only or full)
    # ------------------------------------------------------------------

    @staticmethod
    def to_array(
        fingerprint: OrderedDict[str, float],
        continuous_only: bool = False,
    ) -> tuple[np.ndarray, list[str]]:
        """
        Convert a fingerprint dict to a (values, keys) tuple.

        Parameters
        ----------
        fingerprint :
            Output of ``build()``.
        continuous_only :
            If True, exclude ``cat__`` keys (useful when computing
            per-stratum Euclidean distances on the continuous block only).

        Returns
        -------
        (np.ndarray, list[str])
        """
        items = [
            (k, v) for k, v in fingerprint.items()
            if not (continuous_only and k.startswith("cat__"))
        ]
        keys = [k for k, _ in items]
        vals = np.array([v for _, v in items], dtype=float)
        return np.nan_to_num(vals, nan=0.0), keys

    @staticmethod
    def stratum_slice(
        fingerprint: OrderedDict[str, float],
        stratum_name: str,
    ) -> tuple[np.ndarray, list[str]]:
        """
        Extract just the keys belonging to one stratum (e.g. ``"S1_morphological"``).

        Returns (values_array, key_list).
        """
        items = [
            (k, v) for k, v in fingerprint.items()
            if k.startswith(stratum_name)
        ]
        if not items:
            return np.array([]), []
        keys = [k for k, _ in items]
        vals = np.array([v for _, v in items], dtype=float)
        return np.nan_to_num(vals, nan=0.0), keys
