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
    ):
        self.store_path = Path(store_path)
        self._rec = Recommender.from_store(self.store_path, stratum_weights=stratum_weights, k=k)
        self._k = k
        self._profiler = None

    def _profile(self, texts: pd.Series) -> pd.DataFrame:
        if self._profiler is None:
            from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler
            self._profiler = DeepProfiler()
        return self._profiler.get_multilingual_profile(texts)

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

        from lid_toolkit.explainer.config import ExplainerConfig

        lang_profile_df = self._profile(texts)
        if lang_profile_df.empty:
            raise ValueError(
                "DeepProfiler returned an empty profile. "
                "Ensure texts contains valid, non-trivial text."
            )
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
