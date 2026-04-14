"""
LID Model Recommender — Stratified Meta-Knowledge Base (SMKB).

Public API::

    from lid_toolkit.recommender import Recommender
    rec = Recommender.from_store("mkb.pkl")
    result = rec.recommend(text_series, priority_metric="f1_macro")
"""

from .recommender import Recommender

__all__ = ["Recommender"]
