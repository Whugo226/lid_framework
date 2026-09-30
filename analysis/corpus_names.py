"""
Display names for the 17 benchmark corpora, keyed by the dataset keys used in
the MKB and the results artefacts.

These are the names in the thesis's benchmark-portfolio table
(tab:benchmark_datasets, Chapter 4). Every generator that prints a corpus name
into the thesis takes it from here, so that tables and figures agree with the
prose. Model identifiers (e.g. fasttext_subword_wikipedia) are not corpus names
and are left as they are.
"""

DISPLAY = {
    "OpenLID-v2": "OpenLID-v2",
    "amazon_reviews_multi": "Amazon Reviews Multi",
    "europarl": "Europarl",
    "exorde-social-media-december-2024-week1": "Exorde Social Media",
    "flores_plus": "FLORES+",
    "language-identification": "Language Identification",
    "massive": "MASSIVE",
    "mmarco": "mMARCO",
    "multi_eurlex": "Multi EurLex",
    "multilingual_cc_news": "Multilingual CC News",
    "multilingual_toxicity_dataset": "Multilingual Toxicity",
    "stsb_multi_mt": "STS-B Multi MT",
    "tweet_sentiment_multilingual": "Tweet Sentiment",
    "tydiqa": "TyDiQA",
    "wikipedia": "Wikipedia",
    "xlsum": "XLSum",
    "xnli": "XNLI",
}


def display(key: str) -> str:
    """Display name of a corpus key; fails loudly on an unknown key."""
    return DISPLAY[key]
