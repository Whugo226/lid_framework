from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pandas as pd

from lid_toolkit.recommender import Recommender
from lid_toolkit.recommender.mkb_similarity import Recommendation

if TYPE_CHECKING:
    from lid_toolkit.explainer.config import ExplainerConfig


class LID_Recommender:
    def __init__(
        self,
        store_path: str | Path,
        stratum_weights: dict[str, float] | None = None,
        k: int = 3,
        seed: int | None = None,
    ):
        self.store_path = Path(store_path)
        self._rec = Recommender.from_store(self.store_path, stratum_weights=stratum_weights, k=k)
        self._k = k
        self._seed = seed
        self._profiler = None

    @property
    def store(self):
        """The loaded Meta-Knowledge Base store backing this recommender."""
        return self._rec.store

    def profile(self, texts: pd.Series) -> pd.DataFrame:
        """Profile ``texts`` once and return the language profile DataFrame.

        This is the expensive phase of the pipeline.  Callers that intend to
        issue several queries over the same corpus (for example an interactive
        client re-querying under a different priority metric) should call this
        once and pass the result to :meth:`explain_from_profile`, which is a
        nearest-neighbour lookup over the Meta-Knowledge Base and costs
        milliseconds.

        Profiling samples documents per language, so it is reproducible only if
        this recommender was constructed with a ``seed``.
        """
        if self._profiler is None:
            from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler
            self._profiler = DeepProfiler(seed=self._seed)
        profile = self._profiler.get_multilingual_profile(texts)
        if profile.empty:
            raise ValueError(
                "DeepProfiler returned an empty profile. "
                "Ensure texts contains valid, non-trivial text."
            )
        return profile

    # Backwards-compatible alias for the pre-2026-08 private name.
    _profile = profile

    def explain_from_profile(
        self,
        lang_profile_df: pd.DataFrame,
        metric: str = "f1_macro",
    ) -> tuple[Recommendation, ExplainerConfig]:
        """Query the MKB from an already-computed profile (no re-profiling)."""
        from lid_toolkit.explainer.config import ExplainerConfig

        rec, trace = self._rec.recommend_from_profile_traced(
            lang_profile_df, priority_metric=metric, k=self._k
        )
        config = ExplainerConfig(
            recommendation=rec,
            trace=trace,
            priority_metric=metric,
            store_path=self.store_path,
        )
        return rec, config

    def recommend(
        self,
        texts: pd.Series,
        metric: str = "f1_macro",
        mode: Literal["recommend", "explain"] = "recommend",
    ) -> Recommendation | tuple[Recommendation, ExplainerConfig]:
        if mode not in ("recommend", "explain"):
            raise ValueError(f"mode must be 'recommend' or 'explain', got {mode!r}")

        if mode == "recommend":
            return self._rec.recommend(texts, priority_metric=metric)

        return self.explain_from_profile(self.profile(texts), metric=metric)
