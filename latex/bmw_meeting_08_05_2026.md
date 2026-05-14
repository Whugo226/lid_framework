# LID Toolkit — BMW Project's Meeting

**Date:** 2026-05-08  
**Author:** Masters Student, 25167626@sun.ac.za  
**Document scope:** Architecture, methodology, experimental setup, and validation results for the Language Identification (LID) Recommendation Toolkit.


## 1. Executive Summary

The LID Toolkit addresses a core practical challenge in Natural Language Processing (NLP): **given a new, unlabelled multilingual dataset, which Language Identification (LID) model is most likely to perform best on it?** Manually benchmarking every candidate model for every new dataset is computationally expensive and impractical at scale. The toolkit automates this selection through a retrieval-based recommendation system grounded in deep linguistic profiling.

**Core idea.** The toolkit first builds a *Meta-Knowledge Base* (MKB) offline by profiling a collection of historical datasets with a linguistic feature extractor (the `DeepProfiler`), compressing the resulting feature vectors into compact fingerprints via per-stratum PCA, and storing paired performance records from a comprehensive model benchmarking sweep. At query time, a user's new dataset is profiled in the same way, its fingerprint is computed, and a $k$-nearest-neighbour search over the MKB is performed. The best-performing model from the retrieved historical analogues is then recommended via inverse-distance-weighted (IDW) voting.

---

## 2. Toolkit Architecture & Inner Workings

### 2.1 System Overview

The toolkit consists of four principal components that are connected in a two-phase workflow.

| Component | Role |
|-----------|------|
| `DeepProfiler` | Extracts ~2,726 raw linguistic features from 100 samples of text per language (e.g. Singular Word Count, Proper Noun Count, Adverb Concentration, Adjective Burstiness, Past tense word position SD, Verb avg position, PoS overlap count) |
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


Features are organised into five linguistically motivated groups, detailed below using `FeatureStratifier` .

#### Stratum S1 — Morphological Richness

Captures the inflectional complexity of each language as evidenced by the text sample.

#### Stratum S2 — Lexical Diversity

Quantifies the richness and variety of the vocabulary used.

#### Stratum S3 — Structural / Syntactic

Captures the surface structural organisation of the text.

#### Stratum S4 — Information-Theoretic

Characterises the information content and distributional properties of the text.

#### Stratum S5 — Cross-Level Cohesion

Measures the degree of lexical and semantic overlap *across* discourse units (paragraph↔document, sentence↔paragraph, etc.). 


#### Stratum S6 — Categorical Typological Flags

This stratum is **never subjected to PCA**. It captures discrete properties of the language set present in a dataset, sourced from WALS (World Atlas of Language Structures), Ethnologue, and Glottolog. The 24 languages supported by the `DeepProfiler` each have an associated `LanguageTypology` record with four categorical properties: tonality, script type (latin, cyrillic, greek, cjk, hangul), morphological type (fusional, agglutinative, isolating, mixed), and language family.

From these, 17 dataset-level summary flags are derived:

| Key | Type | Description |
|-----|------|-------------|
| `cat__n_languages` | integer | Number of distinct languages in the dataset |
| `cat__n_tonal` | integer | Count of tonal languages |
| `cat__has_tonal` | binary | Dataset contains at least one tonal language |
| `cat__n_script_types` | integer | Number of distinct writing scripts |
| `cat__has_cjk` | binary | CJK script present |
| `cat__has_cyrillic` | binary | Cyrillic script present |
| `cat__has_greek` | binary | Greek script present |
| `cat__has_hangul` | binary | Hangul script present |
| `cat__has_latin` | binary | Latin script present |
| `cat__n_agglutinative` | integer | Number of agglutinative languages |
| `cat__frac_agglutinative` | float | Fraction of languages that are agglutinative |
| `cat__n_isolating` | integer | Number of isolating languages |
| `cat__n_polysyllabic` | integer | Number of predominantly polysyllabic languages |
| `cat__n_language_families` | integer | Number of distinct language families represented |
| `cat__frac_germanic` | float | Fraction of Germanic languages |
| `cat__frac_romance` | float | Fraction of Romance languages |
| `cat__frac_slavic` | float | Fraction of Slavic languages |

---

### 2.3  & PCA Compression & Dataset Fingerprint Construction

Using the `FingerprintBuilder`, Principal Component Analysis is then used to turn the massive 2,726-feature matrix into a small number of PCs. We then aggregate across L - languages per PC using  5 statistics (mean, std, min, max and heterogeneity) to create standardised fingerprint vector of 262, this allows different datasets with varying number of languages in them to be compared to one another on a linguistic level. 

A single dataset contains multiple languages. We need one fixed-length vector to represent the distribution of linguistic properties across those languages. For each PC within each stratum, we record five aggregate statistics: the mean, spread (std), extremes (min, max), and heterogeneity 

Now that we can generate a standardised linguistic profile for any multilingual dataset we can move on to the datasets that were used to create the meta-knowledge base.


## 3. MKB Pipeline (Meta-Knowledge Base)

 ### 3.1 Datasets 

A total of **17 multilingual datasets** were profiled and benchmarked. These span a broad range of domains, language coverage, and text register — from formal parliamentary proceedings to informal social media posts.

| # | Dataset | Domain / Characteristics |
|---|---------|--------------------------|
| 1 | **OpenLID-v2** | General multilingual, broad language coverage; widely used LID benchmark |
| 2 | **flores_plus** | High-quality professional translations; 200+ languages; formal register |
| 3 | **wikipedia** | Encyclopaedic text; clean, formal, topic-diverse; broad language coverage |
| 4 | **europarl** | European Parliament proceedings; formal, institutionally translated |
| 5 | **xlsum** | Multilingual news summarisation; BBC news; medium register |
| 6 | **multilingual_cc_news** | Scraped news articles from CommonCrawl; noisy, informal variants |
| 7 | **xnli** | Natural Language Inference cross-lingual dataset; translated hypotheses |
| 8 | **massive** | Conversational/NLU data (intent detection); short utterances |
| 9 | **mmarco** | Multilingual machine-translated MS MARCO passages; mixed register |
| 10 | **tydiqa** | Typologically diverse QA; natural, information-seeking language |
| 11 | **amazon_reviews_multi** | Product reviews; informal, opinion-heavy; 6 languages |
| 12 | **tweet_sentiment_multilingual** | Social media tweets; highly informal, noisy, emoji-heavy |
| 13 | **exorde-social-media-december-2024-week1** | Web-scraped social media (Dec 2024); contemporary informal text |
| 14 | **multilingual_toxicity_dataset** | Toxic/hateful speech; informal, noisy, code-mixed |
| 15 | **language-identification** | Curated LID benchmark; multiple language coverage |
| 16 | **multi_eurlex** | EU legislative texts; highly formal, domain-specific legal terminology |
| 17 | **stsb_multi_mt** | Semantic Textual Similarity (machine-translated); short sentence pairs |


Each dataset was split into structured partitions:
- `01a_knowledge_train_50`: Used to train fasttext, logistic regression and naive bayes models
- `01b_knowledge_benchmark_20`: Used for the historical fingerprints to fill the meta-knowledge base and for benchmark results (also included in the meta-knowledge base) 
- `02_evaluation_15` / `03_validation_15`: (used to evaluate and validate the toolkit)
---

### 3.2 Language Identification Models

Three broad families of LID models were benchmarked, each producing multiple dataset-specific variants:

**Family 1: FastText Subword Models** (`fasttext_subword_*`) & (`fasttext_word_*`) 
Custom FastText models trained from scratch on the training split (`01a_knowledge_train_50`) of each specific historical dataset using subword (character n-gram) representations and word representations. 


**Family 2: Off-the-Shelf**  (`lid.176`) & (`cld3`)
Facebook's FastText pre-trained `lid.176.bin` model supports 176 languages. 
Google's `cld3` pre-trained model supports 107 languages

**Family 3: Classical Machine Learning Baselines**  
Multiple Scikit-learn pipeline variants combining different vectorisation strategies with Logistic Regression and Naive Bayes:

| Variant prefix | Vectoriser | Notes |
|----------------|-----------|-------|
| `tfidf_lr_char_ngram_3_5_*` | TF-IDF, char n-grams (3,4,5) | L2-normalised, Logistic Regression classifier |
| `bow_char_ngram_3_5_*` | Bag-of-Words, char n-grams (3,4,5) | Count-based features, Naive Bayes classifier |
| `bow_maxabs_lr_char_ngram_3_5_*` | BoW + MaxAbsScaler, char n-grams | Scaled BoW, Logistic Regression classifier |
| `tfidf_char_ngram_3_5_*` | TF-IDF, char n-grams (3,4,5) | Naive Bayes classifier |

### 3.3 Benchmark metrics

The model benchmark metrics that are included in the MKB are: 

    "accuracy": 
    "f1_macro":
    "f1_weighted": 
    "precision_macro": 
    "precision_weighted": 
    "recall_macro": 
    "recall_weighted": 
    "inference_time_total_s": 
    "inference_time_ms_per_sample": 
    "throughput_samples_per_sec": 
    "n_samples": 



## 4. Query Time

What happens when the toolkit is applied to an unseen dataset? The same 4 main components are utilised ( `DeepProfiler`, `FeatureStratifier`, `FingerprintBuilder` and `SimilarityEngine` )

Following the 3 first three components the unseen dataset now has its 262 vector fingerprint. Linguistically, what is the most similiar datasets from the MKB to this unseen dataset




## 5. Validation Process & Results

### 5.1 Validation Methodology

The validation protocol addresses the question: *does the toolkit recommend a model that, when applied to the corresponding evaluation set, achieves performance close to (or better than) the  ground-truth best model?*

**Setup:**
- Using the datasets from `02_evaluation_15` folder (unseen dataset)
- The toolkit's recommendation is compared against the ground-truth best model (identified by scanning all benchmark results for the highest `f1_weighted` score on the same dataset's evaluation split).
- Both the recommended model's score and the ground-truth best model's score are obtained from the stored benchmark metadata, ensuring a fair comparison on an identically split evaluation set.

**Primary metric:** `f1_weighted`  
**Evaluation dimensions:**
1. **Recommendation accuracy**: whether the exact recommended model matches the ground-truth best model (top-1 exact match).
2. **Performance gap** $\Delta$: how much `f1_weighted` the recommendation sacrifices relative to the ground truth:


## Per-Dataset Results

| Dataset | Recommended | Ground Truth | Match | GT score | Rec score | Δ f1_weighted | Confidence |
|---------|-------------|-------------|-------|----------|-----------|---------------|------------|
| OpenLID-v2 | `fasttext_subword_OpenLID-v2` | `fasttext_subword_OpenLID-v2` | ✓ | 0.9940 | 0.9940 | +0.0000 | 0.33 |
| amazon_reviews_multi | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_amazon_reviews_multi` | ✗ | 0.9998 | 0.9990 | +0.0009 | 0.00 |
| europarl | `fasttext_subword_exorde-social-media-december-2024-week1` | `bow_char_ngram_3_5_europarl` | ✗ | 0.9995 | 0.9979 | +0.0017 | 0.00 |
| exorde-social-media-december-2024-week1 | `fasttext_subword_exorde-social-media-december-2024-week1` | `lid.176_exorde-social-media-december-2024-week1` | ✗ | 0.9779 | 0.9688 | +0.0091 | 0.33 |
| flores_plus | `fasttext_subword_wikipedia` | `fasttext_subword_OpenLID-v2` | ✗ | 0.9951 | 0.9924 | +0.0027 | 0.00 |
| language-identification | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_language-identification` | ✗ | 0.9979 | 0.9958 | +0.0021 | 0.00 |
| massive | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_massive` | ✗ | 0.9974 | 0.9881 | +0.0093 | 0.33 |
| mmarco | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_mmarco` | ✗ | 0.9975 | 0.9802 | +0.0173 | 0.00 |
| multi_eurlex | `fasttext_subword_wikipedia` | `bow_maxabs_lr_char_ngram_3_5_multi_eurlex` | ✗ | 0.9998 | 0.9959 | +0.0039 | 0.33 |
| multilingual_cc_news | `fasttext_subword_wikipedia` | `fasttext_subword_multilingual_cc_news` | ✗ | 0.9971 | 0.9787 | +0.0185 | 0.33 |
| multilingual_toxicity_dataset | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_multilingual_toxicity_dataset` | ✗ | 0.9937 | 0.9899 | +0.0037 | 0.00 |
| stsb_multi_mt | `fasttext_subword_exorde-social-media-december-2024-week1` | `tfidf_lr_char_ngram_3_5_stsb_multi_mt` | ✗ | 0.9942 | 0.9916 | +0.0026 | 0.00 |
| tweet_sentiment_multilingual | `fasttext_subword_exorde-social-media-december-2024-week1` | `bow_char_ngram_3_5_tweet_sentiment_multilingual` | ✗ | 0.9981 | 0.9827 | +0.0154 | 0.33 |
| tydiqa | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_tydiqa` | ✗ | 0.9999 | 0.9856 | +0.0143 | 0.00 |
| wikipedia | `fasttext_subword_wikipedia` | `fasttext_subword_wikipedia` | ✓ | 0.9964 | 0.9964 | +0.0000 | 0.33 |
| xlsum | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_xlsum` | ✗ | 0.9989 | 0.9986 | +0.0002 | 0.00 |
| xnli | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_xnli` | ✗ | 0.9996 | 0.9975 | +0.0022 | 0.33 |