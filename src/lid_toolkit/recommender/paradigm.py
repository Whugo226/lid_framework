"""
paradigm.py — architectural paradigm of a candidate model variant.

The thesis assigns every candidate to one of two architectural paradigms
(Chapter 3, tab:paradigm_assignment): the four character n-gram Multinomial
Naive Bayes and Logistic Regression configurations are traditional machine
learning (TML); FastText (word and subword), lid.176, CLD3 and XLM-V Base are
neural.  Trained variants carry a ``_<training-corpus>`` suffix, so the
assignment is made on the configuration prefix alone.

The same rule is used by analysis/paradigm_regret.py and
analysis/paradigm_recommendation_sweep.py.
"""
from __future__ import annotations

TML = "TML"
NEURAL = "neural"

# Configuration prefixes of the four TML pipelines.  None is a prefix of
# another (tfidf_char_ vs tfidf_lr_char_, bow_char_ vs bow_maxabs_lr_char_).
TML_CONFIGURATIONS: tuple[str, ...] = (
    "bow_char_ngram_3_5",
    "tfidf_char_ngram_3_5",
    "bow_maxabs_lr_char_ngram_3_5",
    "tfidf_lr_char_ngram_3_5",
)


def model_paradigm(model_key: str) -> str:
    """Return ``"TML"`` or ``"neural"`` for a benchmark variant key."""
    for cfg in TML_CONFIGURATIONS:
        if model_key == cfg or model_key.startswith(cfg + "_"):
            return TML
    return NEURAL
