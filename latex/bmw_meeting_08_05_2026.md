# LID Toolkit — BMW Project's Meeting

**Date:** 2026-05-08  
**Author:** Masters Student, 25167626@sun.ac.za  
**Document scope:** Architecture, methodology, experimental setup, and validation results for the Language Identification (LID) Recommendation Toolkit.


## 1. Executive Summary

The LID Toolkit addresses a core practical challenge in Natural Language Processing (NLP): **given a new, unlabelled multilingual dataset, which Language Identification (LID) model is most likely to perform best on it?** Manually benchmarking every candidate model for every new dataset is computationally expensive and impractical at scale. The toolkit automates this selection through a retrieval-based recommendation system grounded in deep linguistic profiling.

**Core idea.** The toolkit first builds a *Meta-Knowledge Base* (MKB) offline by profiling a collection of historical datasets with a rich linguistic feature extractor (the `DeepProfiler`), compressing the resulting feature vectors into compact fingerprints via per-stratum PCA, and storing paired performance records from a comprehensive model benchmarking sweep. At query time, a user's new dataset is profiled in the same way, its fingerprint is computed, and a $k$-nearest-neighbour search over the MKB is performed. The best-performing model from the retrieved historical analogues is then recommended via inverse-distance-weighted (IDW) voting.

---

## 2. Toolkit Architecture & Inner Workings

### 2.1 System Overview

The toolkit consists of four principal components that are connected in a two-phase workflow.

| Component | Role |
|-----------|------|
| `DeepProfiler` | Extracts ~2,726 raw linguistic features per language from text | Some Examples of features: Singular Word Count, Proper Noun Count, Adverb Count, Adverb Concentration, Adjective Burstiness, Past tense word position SD, Verb avg position, PoS overlap count etc

| `FeatureStratifier` | Partitions features into 5 strata; fits per-stratum PCA models |
| `FingerprintBuilder` | Aggregates per-language PCA projections into a fixed-length dataset fingerprint |
| `SimilarityEngine` | Computes weighted multi-stratum distances; performs $k$-NN retrieval and IDW voting |


### 2.2 The DeepProfiler: Linguistic Feature Extraction

The `DeepProfiler` is the computational core of the toolkit. It processes raw multilingual text and extracts a comprehensive, language-level linguistic profile. For each supported language, it relies on:

- **spaCy** small neural models (24 languages) for tokenisation, POS-tagging, morphological analysis, and sentence segmentation.
- **Compressed FastText word vectors** for semantic centroid computation.
- **FastText lid.176** for automatic language detection within a mixed-language corpus.
- **`wordfreq`** for Zipf frequency lookups and lexical frequency measures.
- **`editdistance`** for Levenshtein distance calculations.


self.SPACY_MODELS = {
            'en': 'en_core_web_sm',   # English
            'ca': 'ca_core_news_sm',  # Catalan
            'zh': 'zh_core_web_sm',   # Chinese
            'hr': 'hr_core_news_sm',  # Croatian
            'da': 'da_core_news_sm',  # Danish
            'nl': 'nl_core_news_sm',  # Dutch
            'fi': 'fi_core_news_sm',  # Finnish
            'fr': 'fr_core_news_sm',  # French
            'de': 'de_core_news_sm',  # German
            'el': 'el_core_news_sm',  # Greek
            'it': 'it_core_news_sm',  # Italian
            'ja': 'ja_ginza',         # Japanese
            'ko': 'ko_core_news_sm',  # Korean
            'lt': 'lt_core_news_sm',  # Lithuanian
            'mk': 'mk_core_news_sm',  # Macedonian
            'nb': 'nb_core_news_sm',  # Norwegian Bokmål
            'pl': 'pl_core_news_sm',  # Polish
            'pt': 'pt_core_news_sm',  # Portuguese
            'ro': 'ro_core_news_sm',  # Romanian
            'ru': 'ru_core_news_sm',  # Russian
            'sl': 'sl_core_news_sm',  # Slovenian
            'es': 'es_core_news_sm',  # Spanish
            'sv': 'sv_core_news_sm',  # Swedish
            'uk': 'uk_core_news_sm'   # Ukrainian
        }


Features are organised into five linguistically motivated groups, detailed below.