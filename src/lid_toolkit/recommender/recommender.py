"""
Top-level Recommender API.

Usage
-----
**One-time setup** (run once after collecting benchmark data and language profiles)::

    from lid_toolkit.recommender import Recommender

    # Build and save the knowledge base
    Recommender.build_mkb(
        benchmark_dir="path/to/LID_experiments/model_benchmarking",
        profiles_dir="path/to/profiles",        # .pkl files from profile_historical_datasets()
        output_path="mkb.pkl",
    )

**Query time** (load pre-built MKB, get recommendation for new data)::

    rec = Recommender.from_store("mkb.pkl")
    result = rec.recommend(user_text_series, priority_metric="f1_macro")
    print(result.explanation)

**Helper: profile and save historical datasets**::

    Recommender.profile_and_save_historical(
        datasets_root="path/to/LID_experiments/datasets/01a_knowledge_train_50",
        output_dir="path/to/profiles",
    )
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Optional

import pandas as pd

from .mkb_store import MKBStore
from .mkb_similarity import SimilarityEngine, Recommendation

logger = logging.getLogger(__name__)


class Recommender:
    """
    High-level interface for LID model recommendation.

    Parameters
    ----------
    store : MKBStore
        A finalised Meta-Knowledge Base store.
    stratum_weights : dict[str, float], optional
        Override default equal stratum weights.  Call
        :meth:`learn_weights` to derive data-driven weights automatically.
    k : int
        Number of nearest neighbours to use (default 3).
    """

    def __init__(
        self,
        store: MKBStore,
        stratum_weights: Optional[dict[str, float]] = None,
        k: int = 3,
    ):
        self.store  = store
        self.engine = SimilarityEngine(store, stratum_weights=stratum_weights, k=k)

    # ------------------------------------------------------------------
    # Primary recommendation API
    # ------------------------------------------------------------------

    def recommend(
        self,
        text_series: pd.Series,
        priority_metric: str = "f1_macro",
        k: Optional[int] = None,
    ) -> Recommendation:
        """
        Recommend the best LID model for a user-provided dataset.

        Parameters
        ----------
        text_series : pd.Series
            Raw text samples from the user's dataset (no language labels needed).
        priority_metric : str
            Metric to optimise: ``"accuracy"``, ``"f1_macro"``,
            ``"precision_macro"``, or ``"recall_macro"``.
        k : int, optional
            Number of nearest neighbours (overrides instance-level ``k``).

        Returns
        -------
        Recommendation
            Contains: ``recommended_model``, ``confidence``, ``neighbours``,
            ``all_model_scores``, and a human-readable ``explanation``.
        """
        from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler

        logger.info("Profiling user dataset (%d samples)...", len(text_series))
        profiler = DeepProfiler()
        lang_profile_df = profiler.get_multilingual_profile(text_series)

        if lang_profile_df.empty:
            raise ValueError(
                "DeepProfiler returned an empty profile. "
                "Check that the text_series contains valid, non-trivial text."
            )

        return self.recommend_from_profile(
            lang_profile_df, priority_metric=priority_metric, k=k
        )

    def recommend_from_profile(
        self,
        lang_profile_df: pd.DataFrame,
        priority_metric: str = "f1_macro",
        k: Optional[int] = None,
    ) -> Recommendation:
        """
        Recommend using a pre-computed language profile (skip profiling step).

        Useful when you have already run ``DeepProfiler.get_multilingual_profile()``
        and want to avoid re-running the profiler.
        """
        user_iso_codes = frozenset(lang_profile_df.columns)
        builder = self.store.builder
        fp      = builder.build(lang_profile_df)
        return self.engine.query(
            fp,
            priority_metric=priority_metric,
            k=k,
            user_iso_codes=user_iso_codes,
        )

    # ------------------------------------------------------------------
    # Weight learning
    # ------------------------------------------------------------------

    def learn_weights(self, priority_metric: str = "f1_macro") -> dict[str, float]:
        """
        Learn data-driven stratum weights via LOO Pearson correlation.

        Updates the internal engine weights.  Call this before :meth:`recommend`
        for better accuracy.

        Returns
        -------
        dict[str, float]
            Updated stratum weights.
        """
        return self.engine.learn_weights(priority_metric=priority_metric)

    # ------------------------------------------------------------------
    # LOO evaluation (for thesis validation)
    # ------------------------------------------------------------------

    def evaluate_loo(self, priority_metric: str = "f1_macro") -> pd.DataFrame:
        """
        Leave-one-out retrieval accuracy evaluation.

        For each historical dataset in the MKB, removes it temporarily,
        finds its nearest neighbour among the remainder, and checks whether
        the recommended model matches the ground-truth best model.

        Returns
        -------
        pd.DataFrame
            One row per dataset with columns: ``query``, ``predicted_model``,
            ``true_model``, ``correct``, ``top1_similarity``, ``confidence``.
        """
        store    = self.store
        datasets = [
            n for n in store.datasets
            if store.get_entry(n).fingerprint is not None
            and store.get_entry(n).performances
        ]

        rows = []
        for query_name in datasets:
            query_entry = store.get_entry(query_name)
            query_fp    = query_entry.fingerprint

            # Ground-truth best model for this dataset
            true_model = max(
                query_entry.performances.items(),
                key=lambda kv: kv[1].get(priority_metric, -1),
            )[0]

            # Temporarily mask this dataset
            orig_fp = query_entry.fingerprint
            query_entry.fingerprint = None

            try:
                rec = self.engine.query(
                    query_fp,  # type: ignore[arg-type]
                    priority_metric=priority_metric,
                    k=min(self.engine.k, len(datasets) - 1),
                )
            except RuntimeError:
                rows.append({
                    "query": query_name,
                    "predicted_model": "N/A",
                    "true_model": true_model,
                    "correct": False,
                    "top1_similarity": 0.0,
                    "confidence": 0.0,
                })
                query_entry.fingerprint = orig_fp
                continue

            query_entry.fingerprint = orig_fp

            top1_sim = rec.neighbours[0].similarity_pct if rec.neighbours else 0.0
            rows.append({
                "query": query_name,
                "predicted_model": rec.recommended_model,
                "true_model": true_model,
                "correct": rec.recommended_model == true_model,
                "top1_similarity": top1_sim,
                "confidence": rec.confidence,
            })

        df = pd.DataFrame(rows).set_index("query")
        accuracy = df["correct"].mean()
        logger.info(
            "LOO evaluation (%s): %d/%d correct  (accuracy = %.1f%%)",
            priority_metric, df["correct"].sum(), len(df), accuracy * 100
        )
        return df

    # ------------------------------------------------------------------
    # Factory / persistence
    # ------------------------------------------------------------------

    @classmethod
    def from_store(
        cls,
        store_path: str | Path,
        stratum_weights: Optional[dict[str, float]] = None,
        k: int = 3,
    ) -> "Recommender":
        """Load a pre-built MKBStore from disk and wrap it in a Recommender."""
        store = MKBStore.load(store_path)
        return cls(store, stratum_weights=stratum_weights, k=k)

    @classmethod
    def build_mkb(
        cls,
        benchmark_dir: str | Path,
        profiles_dir: str | Path,
        output_path: str | Path,
        variance_threshold: float = 0.95,
        max_pca_components: int = 20,
        k: int = 3,
    ) -> "Recommender":
        """
        Build an MKBStore from the filesystem layout, save it, and return a
        ready-to-use Recommender.

        Parameters
        ----------
        benchmark_dir :
            Root of ``LID_experiments/model_benchmarking/`` (contains sub-dirs
            per model family, each with per-dataset result folders).
        profiles_dir :
            Directory of ``.pkl`` files — one per dataset, each a
            ``pd.DataFrame`` (features × languages) from ``DeepProfiler``.
        output_path :
            Where to save the finished ``MKBStore`` (e.g. ``"mkb.pkl"``).
        """
        store = MKBStore.build_from_filesystem(
            benchmark_dir=benchmark_dir,
            profiles_dir=profiles_dir,
            variance_threshold=variance_threshold,
            max_pca_components=max_pca_components,
        )
        store.save(output_path)
        return cls(store, k=k)

    @staticmethod
    def profile_and_save_historical(
        datasets_root: str | Path,
        output_dir: str | Path,
        n_samples: int = 50,
    ) -> None:
        """
        Profile all historical datasets and save the language profiles as .pkl files.

        This utility walks ``datasets_root``, locates text files per dataset,
        runs ``DeepProfiler.get_multilingual_profile()``, and serialises the
        resulting DataFrame to ``output_dir/<dataset_name>.pkl``.

        Parameters
        ----------
        datasets_root :
            Root directory containing sub-folders per dataset, each containing
            language-labelled text files (parquet or CSV with a ``text`` column).
        output_dir :
            Where to write the ``.pkl`` profile files.
        n_samples :
            Maximum text samples to profile per language (default 50).
        """
        from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler

        root    = Path(datasets_root)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        profiler = DeepProfiler()

        for dataset_dir in sorted(root.iterdir()):
            if not dataset_dir.is_dir():
                continue
            dataset_name = dataset_dir.name
            out_path = out_dir / f"{dataset_name}.pkl"
            if out_path.exists():
                logger.info("Profile for '%s' already exists, skipping.", dataset_name)
                continue

            logger.info("Profiling '%s' (building mode)...", dataset_name)
            try:
                lang_profile = profiler.run_profile("building", parquet_dir=dataset_dir)
                if lang_profile.empty:
                    logger.warning("Empty profile for '%s', skipping.", dataset_name)
                    continue
                with open(out_path, "wb") as fh:
                    pickle.dump(lang_profile, fh, protocol=pickle.HIGHEST_PROTOCOL)
                logger.info(
                    "  Saved to %s  (%d features, %d languages).",
                    out_path, lang_profile.shape[0], lang_profile.shape[1],
                )
            except Exception as exc:
                logger.error("Profiling failed for '%s': %s", dataset_name, exc)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def summary(self) -> pd.DataFrame:
        """Return the MKB store summary (datasets, languages, best scores)."""
        return self.store.summary()

    def stratifier_summary(self) -> pd.DataFrame:
        """Return per-stratum PCA statistics."""
        return self.store.stratifier.stratum_summary()
