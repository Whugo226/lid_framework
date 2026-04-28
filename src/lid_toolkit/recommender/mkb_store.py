"""
Meta-Knowledge Base (MKB) Store.

Persists historical dataset fingerprints and benchmark performance results so
that the recommender can find the nearest historical dataset at query time.

Workflow
--------
1.  Add raw language profiles (``pd.DataFrame`` from
    ``DeepProfiler.get_multilingual_profile()``) for each historical dataset
    via :meth:`add_raw_profile`.
2.  Optionally add model performance records via :meth:`add_performance`.
3.  Call :meth:`finalise` to fit the PCA stratifier on all pooled language
    samples and compute fingerprints.  This can only happen once enough
    datasets have been added.
4.  Save with :meth:`save` and reload later with :meth:`load`.

Alternatively, use :meth:`build_from_filesystem` to do all of the above
automatically from the standard directory layout used in LID_experiments.

Performance record format
-------------------------
A *performance record* is a nested dict::

    {
        "fasttext_word":            {"accuracy": 0.95, "f1_macro": 0.94, ...},
        "tfidf_lr_char_ngram_3_5":  {"accuracy": 0.98, "f1_macro": 0.99, ...},
        ...
    }

Any metric key from the benchmark metadata (e.g., ``accuracy``, ``f1_macro``,
``f1_weighted``, ``precision_weighted``, ``recall_weighted``,
``inference_time_total_s``) is stored without filtering.

Directory layout expected by ``build_from_filesystem``
-------------------------------------------------------
::

    benchmark_dir/
        <model_family>/           e.g. fasttext, logistic_regression
            <dataset_name>/
                <variant>/        e.g. fasttext_word
                    benchmark_metadata.json

    profiles_dir/
        <dataset_name>.pkl        — pickled pd.DataFrame (features × languages)
"""

from __future__ import annotations

import json
import logging
import pickle
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from .feature_stratifier import FeatureStratifier
from .fingerprint_builder import FingerprintBuilder

logger = logging.getLogger(__name__)

# Core metrics (used as defaults). All metrics from benchmark_metadata.json are stored.
CORE_METRICS = ("accuracy", "f1_macro", "precision_macro", "recall_macro")

# mlruns subdirectories are MLflow internals — never load from there
_SKIP_DIRS = {"mlruns", "__pycache__"}


@dataclass
class DatasetEntry:
    """One historical dataset in the MKB."""
    name: str
    iso_codes: list[str]
    # Filled after finalise()
    fingerprint: Optional[OrderedDict[str, float]] = None
    # performances[model_variant][metric] = float
    performances: dict[str, dict[str, float]] = field(default_factory=dict)


class MKBStore:
    """
    Container for the Meta-Knowledge Base.

    Holds raw language profiles (pre-finalise) and fitted fingerprints
    (post-finalise) for all historical benchmark datasets.
    """

    def __init__(self,
                 variance_threshold: float = 0.95,
                 max_pca_components: int = 20):
        self._raw_profiles: dict[str, pd.DataFrame] = {}
        self._entries: dict[str, DatasetEntry] = {}
        self._stratifier: Optional[FeatureStratifier] = None
        self._builder: Optional[FingerprintBuilder] = None
        self._finalised: bool = False
        self._variance_threshold = variance_threshold
        self._max_pca_components = max_pca_components

    # ------------------------------------------------------------------
    # Building the MKB
    # ------------------------------------------------------------------

    def add_raw_profile(
        self,
        dataset_name: str,
        lang_profile_df: pd.DataFrame,
    ) -> None:
        """
        Register a historical dataset's linguistic profile.

        Parameters
        ----------
        dataset_name :
            Unique identifier (e.g. ``"flores_plus"``).
        lang_profile_df :
            Output of ``DeepProfiler.get_multilingual_profile()``.
            Shape: (n_features, n_languages).
        """
        self._raw_profiles[dataset_name] = lang_profile_df
        iso_codes = list(lang_profile_df.columns)
        if dataset_name not in self._entries:
            self._entries[dataset_name] = DatasetEntry(
                name=dataset_name,
                iso_codes=iso_codes,
            )
        else:
            self._entries[dataset_name].iso_codes = iso_codes

    def add_performance(
        self,
        dataset_name: str,
        model_variant: str,
        metrics: dict[str, float],
    ) -> None:
        """
        Register benchmark results for one model variant on one dataset.

        Parameters
        ----------
        dataset_name :
            Must match a dataset already added via :meth:`add_raw_profile`
            (or will be created on the fly — fingerprint will be None until
            ``add_raw_profile`` is called).
        model_variant :
            Free-form label, e.g. ``"fasttext_word"`` or
            ``"tfidf_lr_char_ngram_3_5"``.
        metrics :
            Dict of any metrics (e.g., accuracy, f1_macro, f1_weighted,
            precision_weighted, recall_weighted, inference_time_total_s, etc.).
            All metrics in the dict are stored; none are filtered out.
        """
        if dataset_name not in self._entries:
            self._entries[dataset_name] = DatasetEntry(
                name=dataset_name, iso_codes=[],
            )
        entry = self._entries[dataset_name]
        # Store all metrics from the JSON, not just a hardcoded subset
        kept = {k: float(v) for k, v in metrics.items()}
        entry.performances[model_variant] = kept

    def finalise(self) -> None:
        """
        Fit the FeatureStratifier on all pooled language samples and compute
        fingerprints for every registered dataset.

        Must be called after all :meth:`add_raw_profile` calls and before
        :meth:`save` / querying.
        """
        if not self._raw_profiles:
            raise RuntimeError("No raw profiles loaded. Call add_raw_profile() first.")

        # Pool all language columns across all datasets for PCA fitting.
        # Concatenate horizontally (columns = language samples).
        all_profiles = pd.concat(list(self._raw_profiles.values()), axis=1)
        # Drop duplicate column names (same language code appearing in multiple datasets)
        all_profiles = all_profiles.loc[:, ~all_profiles.columns.duplicated()]

        logger.info(
            "Fitting stratifier on %d pooled language samples from %d datasets.",
            all_profiles.shape[1],
            len(self._raw_profiles),
        )

        self._stratifier = FeatureStratifier(
            variance_threshold=self._variance_threshold,
            max_components=self._max_pca_components,
        )
        self._stratifier.fit(all_profiles)
        self._builder = FingerprintBuilder(self._stratifier)

        for name, df in self._raw_profiles.items():
            fp = self._builder.build(df)
            self._entries[name].fingerprint = fp
            logger.info("  Fingerprint computed for '%s' (%d dims).", name, len(fp))

        self._finalised = True
        logger.info("MKBStore finalised. %d datasets in the knowledge base.", len(self._entries))

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    @property
    def datasets(self) -> list[str]:
        return list(self._entries.keys())

    @property
    def stratifier(self) -> FeatureStratifier:
        self._assert_finalised()
        return self._stratifier  # type: ignore[return-value]

    @property
    def builder(self) -> FingerprintBuilder:
        self._assert_finalised()
        return self._builder  # type: ignore[return-value]

    def get_entry(self, dataset_name: str) -> DatasetEntry:
        return self._entries[dataset_name]

    def best_model_per_dataset(self, metric: str = "f1_macro") -> dict[str, str]:
        """Return {dataset_name: best_model_variant} by ``metric``.

        The metric can be any metric stored in the performances (e.g., accuracy,
        f1_macro, f1_weighted, inference_time_total_s, etc.).
        """
        result = {}
        for name, entry in self._entries.items():
            if not entry.performances:
                continue
            best = max(
                entry.performances.items(),
                key=lambda kv: kv[1].get(metric, -1),
            )
            result[name] = best[0]
        return result

    def fingerprints_matrix(
        self, exclude_cat: bool = False
    ) -> tuple[np.ndarray, list[str], list[str]]:
        """
        Return all fingerprints as a matrix.

        Returns
        -------
        (matrix, dataset_names, feature_keys)
            matrix shape: (n_datasets, n_fingerprint_dims)
        """
        self._assert_finalised()
        entries_with_fp = [(n, e) for n, e in self._entries.items()
                           if e.fingerprint is not None]
        dataset_names = [n for n, _ in entries_with_fp]
        rows = []
        for _, entry in entries_with_fp:
            arr, keys = FingerprintBuilder.to_array(
                entry.fingerprint,  # type: ignore[arg-type]
                continuous_only=exclude_cat,
            )
            rows.append(arr)
        if not rows:
            return np.empty((0, 0)), [], []
        matrix = np.vstack(rows)
        return matrix, dataset_names, keys

    # ------------------------------------------------------------------
    # Filesystem construction helper
    # ------------------------------------------------------------------

    @classmethod
    def build_from_filesystem(
        cls,
        benchmark_dir: str | Path,
        profiles_dir: str | Path,
        variance_threshold: float = 0.95,
        max_pca_components: int = 20,
    ) -> "MKBStore":
        """
        Construct an MKBStore by scanning the standard LID_experiments layout.

        Parameters
        ----------
        benchmark_dir :
            Root of model_benchmarking/ (contains sub-dirs per model family).
        profiles_dir :
            Directory containing per-dataset language profiles as ``<name>.pkl``
            files (``pd.DataFrame`` serialised with ``pickle``).
        """
        store = cls(
            variance_threshold=variance_threshold,
            max_pca_components=max_pca_components,
        )

        # ── Load language profiles ─────────────────────────────────────────
        profiles_path = Path(profiles_dir)
        profile_files = list(profiles_path.glob("*.pkl"))
        if not profile_files:
            logger.warning("No .pkl profile files found in %s.", profiles_dir)
        for pf in profile_files:
            dataset_name = pf.stem
            try:
                with open(pf, "rb") as fh:
                    df: pd.DataFrame = pickle.load(fh)
                store.add_raw_profile(dataset_name, df)
                logger.info("Loaded profile for '%s' (%d features, %d languages).",
                            dataset_name, df.shape[0], df.shape[1])
            except Exception as exc:
                logger.warning("Skipping profile '%s': %s", pf.name, exc)

        # ── Scan benchmark metadata ────────────────────────────────────────
        bench_path = Path(benchmark_dir)
        metadata_files = [
            p for p in bench_path.rglob("benchmark_metadata.json")
            if not any(skip in p.parts for skip in _SKIP_DIRS)
        ]
        logger.info("Found %d benchmark_metadata.json files.", len(metadata_files))

        for mf in metadata_files:
            try:
                with open(mf) as fh:
                    meta = json.load(fh)
                dataset_name = meta.get("dataset") or meta.get("name") or mf.parent.parent.name
                variant      = meta.get("variant") or meta.get("pipeline") or mf.parent.name
                variant      = f"{variant}_{dataset_name}"
                metrics_raw  = meta.get("metrics", {})
                store.add_performance(dataset_name, variant, metrics_raw)
            except Exception as exc:
                logger.warning("Skipping metadata '%s': %s", mf, exc)

        store.finalise()
        return store

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Pickle the entire store (stratifier + fingerprints + performances)."""
        self._assert_finalised()
        with open(path, "wb") as fh:
            pickle.dump(self, fh, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info("MKBStore saved to %s.", path)

    @classmethod
    def load(cls, path: str | Path) -> "MKBStore":
        with open(path, "rb") as fh:
            obj = pickle.load(fh)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected MKBStore, got {type(obj)}")
        logger.info("MKBStore loaded from %s  (%d datasets).", path, len(obj.datasets))
        return obj

    def _assert_finalised(self) -> None:
        if not self._finalised:
            raise RuntimeError(
                "MKBStore has not been finalised. Call finalise() after adding all profiles."
            )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def summary(self) -> pd.DataFrame:
        """Return a DataFrame with one row per dataset."""
        # Collect all unique metrics across all entries
        all_metrics: set[str] = set()
        for entry in self._entries.values():
            for perf in entry.performances.values():
                all_metrics.update(perf.keys())
        all_metrics = sorted(all_metrics)  # Sort for consistent column order

        rows = []
        for name, entry in self._entries.items():
            row = {
                "dataset": name,
                "n_languages": len(entry.iso_codes),
                "n_model_variants": len(entry.performances),
                "has_fingerprint": entry.fingerprint is not None,
            }
            for metric in all_metrics:
                best_score = max(
                    (perf.get(metric, float("nan")) for perf in entry.performances.values()),
                    default=float("nan"),
                )
                row[f"best_{metric}"] = round(best_score, 4) if not np.isnan(best_score) else float("nan")
            rows.append(row)
        return pd.DataFrame(rows).set_index("dataset")
