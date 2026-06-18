from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lid_toolkit.recommender.mkb_similarity import Recommendation


@dataclass
class ExplainerConfig:
    recommendation: Recommendation
    trace: dict
    priority_metric: str
    store_path: Path

    def __post_init__(self):
        self.store_path = Path(self.store_path)

    @property
    def neighbours(self):
        return self.recommendation.neighbours

    @property
    def all_model_scores(self):
        return self.recommendation.all_model_scores

    @property
    def query_iso_codes(self) -> list[str]:
        return self.trace.get("query_iso_codes", [])

    @property
    def recommended_model(self) -> str:
        return self.recommendation.recommended_model

    @property
    def confidence(self) -> float:
        return self.recommendation.confidence
