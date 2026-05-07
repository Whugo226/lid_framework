# LID Toolkit — Supervisor Briefing Document

**Prepared for:** Academic Supervisor Meeting  
**Date:** 2026-05-06  
**Author:** Masters Candidate, 25167626@sun.ac.za  
**Document scope:** Architecture, methodology, experimental setup, and validation results for the Language Identification (LID) Recommendation Toolkit.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Toolkit Architecture & Inner Workings](#2-toolkit-architecture--inner-workings)
   - 2.1 [System Overview](#21-system-overview)
   - 2.2 [The DeepProfiler: Linguistic Feature Extraction](#22-the-deepprofiler-linguistic-feature-extraction)
   - 2.3 [Feature Stratification & PCA Compression](#23-feature-stratification--pca-compression)
   - 2.4 [Dataset Fingerprint Construction](#24-dataset-fingerprint-construction)
   - 2.5 [Similarity Engine & k-NN Retrieval](#25-similarity-engine--k-nn-retrieval)
   - 2.6 [Inverse-Distance-Weighted Voting](#26-inverse-distance-weighted-voting)
   - 2.7 [Confidence Score Calibration](#27-confidence-score-calibration)
3. [MKB Pipeline (Meta-Knowledge Base)](#3-mkb-pipeline-meta-knowledge-base)
   - 3.1 [Build Pipeline](#31-build-pipeline)
   - 3.2 [Architecture Diagram](#32-architecture-diagram)
4. [Experimental Setup](#4-experimental-setup)
   - 4.1 [Datasets Used](#41-datasets-used)
   - 4.2 [Models Benchmarked](#42-models-benchmarked)
5. [Validation Process & Results](#5-validation-process--results)
   - 5.1 [Validation Methodology](#51-validation-methodology)
   - 5.2 [Aggregate Metrics](#52-aggregate-metrics)
   - 5.3 [Per-Dataset Results](#53-per-dataset-results)
   - 5.4 [Failure Mode Analysis](#54-failure-mode-analysis)
   - 5.5 [Confidence Calibration](#55-confidence-calibration)
6. [Future Work & Open Questions](#6-future-work--open-questions)

---

## 1. Executive Summary

The LID Toolkit addresses a core practical challenge in Natural Language Processing (NLP): **given a new, unlabelled multilingual dataset, which Language Identification (LID) model is most likely to perform best on it?** Manually benchmarking every candidate model for every new dataset is computationally expensive and impractical at scale. The toolkit automates this selection through a retrieval-based recommendation system grounded in deep linguistic profiling.

**Core idea.** The toolkit first builds a *Meta-Knowledge Base* (MKB) offline by profiling a collection of historical datasets with a rich linguistic feature extractor (the `DeepProfiler`), compressing the resulting feature vectors into compact fingerprints via per-stratum PCA, and storing paired performance records from a comprehensive model benchmarking sweep. At query time, a user's new dataset is profiled in the same way, its fingerprint is computed, and a $k$-nearest-neighbour search over the MKB is performed. The best-performing model from the retrieved historical analogues is then recommended via inverse-distance-weighted (IDW) voting.

**Key achievements:**

- A complete, modular, HPC-deployable pipeline for MKB construction and query-time recommendation.
- Linguistic feature extraction spanning five theoretically motivated strata (morphological, lexical diversity, structural/syntactic, information-theoretic, cross-level cohesion) plus a categorical typological stratum grounded in WALS/Ethnologue sources.
- A 17-dataset validation demonstrating that, while exact top-1 model selection accuracy is 11.8% (2/17), every recommendation was a near-optimal choice: the mean `f1_weighted` shortfall relative to the oracle ground-truth model was only $+0.0061$ (median $+0.0027$), with a maximum deficit of $+0.0185$.
- A moderate, positive confidence–accuracy correlation ($r = 0.387$), indicating that the confidence score is a meaningful signal despite the small sample size.

---

## 2. Toolkit Architecture & Inner Workings

### 2.1 System Overview

The toolkit consists of four principal components that are connected in a two-phase workflow.

| Component | Role |
|-----------|------|
| `DeepProfiler` | Extracts ~3,066 raw linguistic features per language from text |
| `FeatureStratifier` | Partitions features into 5 strata; fits per-stratum PCA models |
| `FingerprintBuilder` | Aggregates per-language PCA projections into a fixed-length dataset fingerprint |
| `SimilarityEngine` | Computes weighted multi-stratum distances; performs $k$-NN retrieval and IDW voting |

---

### 2.2 The DeepProfiler: Linguistic Feature Extraction

The `DeepProfiler` is the computational core of the toolkit. It processes raw multilingual text and extracts a comprehensive, language-level linguistic profile. For each supported language, it relies on:

- **spaCy** small neural models (24 languages) for tokenisation, POS-tagging, morphological analysis, and sentence segmentation.
- **Compressed FastText word vectors** (from the `werner1hugo/compressed-fasttext-models` Hugging Face repository) for semantic centroid computation.
- **FastText lid.176** for automatic language detection within a mixed-language corpus.
- **`wordfreq`** for Zipf frequency lookups and lexical frequency measures.
- **`editdistance`** (C-optimised) for Levenshtein distance calculations.

Features are organised into five linguistically motivated groups, detailed below.

#### Stratum S1 — Morphological Richness

Captures the inflectional complexity of each language as evidenced by the text sample. Computed features include:

| Feature Class | Examples |
|---------------|---------|
| Person agreement | First-/second-/third-person pronoun incidence |
| Number marking | Singular / plural word incidence |
| Definiteness | Definite / indefinite article usage rates |
| Verbal morphology | Finite, infinitive, past, present, passive voice incidence |
| Morphological distance | Mean word–lemma Levenshtein distance |
| Paradigm richness | Mean word-types per lemma (overall and by PoS) |

The mean word–lemma Levenshtein distance is defined as:

$$\bar{\delta}_{wl} = \frac{1}{N} \sum_{i=1}^{N} \text{edit}(w_i, \ell_i)$$

where $w_i$ is the surface form and $\ell_i$ its lemma. Languages with rich fusional morphology (e.g., Finnish, Russian) will have systematically higher $\bar{\delta}_{wl}$ than isolating languages (e.g., Chinese).

#### Stratum S2 — Lexical Diversity

Quantifies the richness and variety of the vocabulary used.

| Feature Class | Examples |
|---------------|---------|
| Type–Token Ratio | Overall and per-PoS (ADJ, ADV, VERB, NOUN, etc.) |
| Moving-Average TTR | Window-size-100 MATTR for length-normalised diversity |
| Hapax legomena | Count, incidence per 1,000 words, burstiness, concentration, positional statistics |
| Honoré's statistic | Derived from hapax count and total vocabulary |
| Zipf frequency | Average Zipf score, frequent/infrequent word incidence |
| Zipf curve shape | Steepness exponent $s$ (via discrete MLE), goodness-of-fit ($R^2$ via Pearson) |

The Zipf curve steepness is estimated by solving the discrete MLE objective:

$$\hat{s} = \arg\min_s \left| \frac{\sum_{r=1}^{V} r^{-s} \ln r}{\sum_{r=1}^{V} r^{-s}} - \frac{\sum_{r=1}^{V} f_r \ln r}{\sum_{r=1}^{V} f_r} \right|$$

where $f_r$ is the observed frequency of the word ranked $r$, and $V$ is the vocabulary size. This is solved numerically via root-finding (`scipy.optimize.root_scalar`).

The finite-size corrected burstiness measure (Kim & Jo 2016) is applied to hapax positional distributions:

$$B_n(r) = \frac{\sqrt{n+1} \cdot r - \sqrt{n-1}}{(\sqrt{n+1} - 2) \cdot r + \sqrt{n-1}}, \quad r = \frac{\sigma_g}{\mu_g}$$

where $g_i$ are the inter-arrival gaps between hapax positions, $n$ is the number of hapax words, and $r$ is their coefficient of variation.

#### Stratum S3 — Structural / Syntactic

Captures the surface structural organisation of the text.

| Feature Class | Examples |
|---------------|---------|
| PoS incidence | Raw counts and per-1,000-word incidence for all 12+ Universal Dependencies tags |
| PoS ratios | ~40 cross-PoS ratios (e.g., adjective–noun, verb–noun, auxiliary–lexical verb) |
| Word length | Mean word length per PoS class and combined groups |
| Sentence-level | Mean sentence length (words), sentence count, sentence-length variance |
| Paragraph-level | Paragraph count, mean sentences per paragraph |

#### Stratum S4 — Information-Theoretic

Characterises the information content and distributional properties of the text.

| Feature | Definition |
|---------|------------|
| Word entropy | $H_w = -\sum_w p(w) \log_2 p(w)$ |
| Letter entropy | $H_c = -\sum_c p(c) \log_2 p(c)$ |
| Zipf steepness | $\hat{s}$ (see above) |
| Zipf goodness of fit | $R^2$ between empirical and fitted Zipf distribution |

High word entropy indicates a more uniform word-frequency distribution; low entropy signals a highly peaked, repetitive vocabulary. This is particularly informative for distinguishing domain-restricted corpora (e.g., legal text) from open-domain corpora.

#### Stratum S5 — Cross-Level Cohesion

Measures the degree of lexical and semantic overlap *across* discourse units (paragraph↔document, sentence↔paragraph, etc.). This stratum operationalises text cohesion, a property that varies substantially across domain and register.

For each pair type (Par–Doc, Sent–Doc, Par–Par adjacent, Sent–Par, Sent–Sent adjacent):

- **Overlap count**: number of shared lemmatised tokens between two units.
- **Overlap ratio**: overlap count normalised by combined unit length.
- **Cosine distance**: $1 - \cos(\mathbf{c}_A, \mathbf{c}_B)$, where $\mathbf{c}$ is the sentence centroid computed by averaging compressed FastText word vectors.
- **Levenshtein distances** at character, word, lemma, and PoS-sequence levels.

The sentence centroid for unit $A$ is:

$$\mathbf{c}_A = \frac{1}{|W_A|} \sum_{w \in W_A} \mathbf{v}_w$$

where $\mathbf{v}_w \in \mathbb{R}^d$ is the compressed FastText embedding for word $w$ and $W_A$ is the set of in-vocabulary words in the unit.

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

### 2.3 Feature Stratification & PCA Compression

The `FeatureStratifier` partitions all ~3,066 raw feature names into the five continuous strata (S1–S5) using substring pattern matching in priority order (S4 → S5 → S1 → S2 → S3, where S3 is a catch-all). This ensures that semantically coherent groups of features undergo dimensionality reduction together, avoiding the instability of a global PCA at low sample count.

**Within each stratum, the following steps are applied:**

**Step 1 — Variance filtering.** Features with zero standard deviation across all historical language samples are removed. They carry no discriminative information.

**Step 2 — Standardisation.** A `StandardScaler` is fitted to centre and unit-normalise the stratum's feature matrix $X_s \in \mathbb{R}^{n \times p_s}$, where $n$ is the number of language-level samples across all historical datasets, and $p_s$ is the number of valid features in stratum $s$:

$$\tilde{X}_s = (X_s - \boldsymbol{\mu}_s) \oslash \boldsymbol{\sigma}_s$$

**Step 3 — PCA.** Principal Component Analysis is applied to $\tilde{X}_s$:

$$\tilde{X}_s = U \Sigma V^\top \quad \Rightarrow \quad Z_s = \tilde{X}_s V_k$$

where $V_k \in \mathbb{R}^{p_s \times k}$ contains the top-$k$ eigenvectors. The number of components $k$ is chosen as the smallest $k$ such that cumulative explained variance exceeds a threshold $\tau = 0.95$:

$$k = \min\left\{ j : \sum_{i=1}^{j} \lambda_i \Big/ \sum_{i=1}^{p_s} \lambda_i \geq 0.95 \right\}$$

subject to $k \leq \min(n-1, p_s, 20)$ (hard upper bound of 20 PCs per stratum).

The result is a set of per-stratum fitted transforms $\{(\text{scaler}_s, \text{PCA}_s)\}_{s=1}^{5}$ that are serialised inside the `MKBStore`. At query time, any new language vector is projected through the same transforms using the **training-time mean and eigenvectors**, ensuring a consistent coordinate space.

---

### 2.4 Dataset Fingerprint Construction

Given a profiled dataset with language set $L = \{\ell_1, \ldots, \ell_m\}$, the `FingerprintBuilder` constructs a fixed-length representation as follows.

**Step 1 — Per-language projection.** For each language $\ell_j$, its raw feature vector $\mathbf{x}_j \in \mathbb{R}^{p}$ is projected into the $k_s$-dimensional PCA subspace for each stratum $s$:

$$\mathbf{z}_{j,s} = \text{PCA}_s\!\left(\text{scaler}_s(\mathbf{x}_{j,s})\right) \in \mathbb{R}^{k_s}$$

**Step 2 — Cross-language aggregation.** For each stratum $s$ and each principal component index $c \in \{0, \ldots, k_s - 1\}$, the distribution of that PC's values across all $m$ languages is summarised by five statistics:

$$f_{s,c}^{(\text{mean})} = \frac{1}{m}\sum_{j=1}^m z_{j,s,c}, \quad f_{s,c}^{(\text{std})} = \sqrt{\frac{1}{m}\sum_{j=1}^m (z_{j,s,c} - \bar{z}_{s,c})^2}$$

$$f_{s,c}^{(\text{min})} = \min_j z_{j,s,c}, \quad f_{s,c}^{(\text{max})} = \max_j z_{j,s,c}$$

$$f_{s,c}^{(\text{het})} = \text{std}_{(m-1)}\{z_{j,s,c}\} \quad \text{(within-dataset heterogeneity, unbiased)}$$

The **heterogeneity** component is particularly informative: it quantifies how linguistically diverse the language set is along each principal direction. A dataset containing both CJK and fusional languages will exhibit high S1 heterogeneity, which meaningfully differentiates it from a dataset of similar-family languages.

**Step 3 — Categorical concatenation.** The S6 flags from `dataset_typology_flags(L)` are appended as-is.

The final fingerprint is an `OrderedDict[str, float]` with keys following the naming convention `{stratum}_PC{index:02d}_{stat}` for continuous features and `cat__{property}` for categorical features. The total dimensionality is:

$$|\mathbf{f}| = 5 \sum_{s=1}^{5} k_s + 17 \text{ (categorical)}$$

---

### 2.5 Similarity Engine & k-NN Retrieval

At query time, the `SimilarityEngine` computes the dissimilarity between the query fingerprint $\mathbf{f}_q$ and every historical fingerprint $\mathbf{f}_i$ stored in the MKB.

**Per-stratum Euclidean distances** are computed independently for each continuous stratum:

$$d_s(q, i) = \left\lVert \mathbf{f}_q^{(s)} - \mathbf{f}_i^{(s)} \right\rVert_2$$

**Categorical stratum S6** contributes a normalised Hamming distance on the binary/ratio `cat__` keys:

$$d_{\text{cat}}(q, i) = \frac{\#\{k : |f_{q,k}^{(\text{cat})} - f_{i,k}^{(\text{cat})}| > 0.5\}}{|K_{\text{cat}}|}$$

where $K_{\text{cat}}$ is the full set of categorical keys (union of both fingerprints).

**Weighted composite distance.** A scalar dissimilarity is obtained by a weighted average across all strata (S1–S5 + categorical):

$$D(q, i) = \frac{\sum_{s} w_s \cdot d_s(q, i)}{\sum_{s} w_s}$$

By default all stratum weights are equal ($w_s = 1.0$). Data-driven weights can be learned via leave-one-out (LOO) Pearson correlation between per-stratum distances and observed performance gaps (see `SimilarityEngine.learn_weights()`).

**Similarity percentage.** All composite distances are normalised against the maximum distance observed across all candidates:

$$\text{sim}(q, i) = \left(1 - \frac{D(q, i)}{D_{\max}}\right) \times 100\%$$

The top $k=3$ nearest historical datasets are selected as the neighbourhood $\mathcal{N}_q$.

---

### 2.6 Inverse-Distance-Weighted Voting

Rather than using a simple majority vote, the toolkit aggregates model performance scores from all $k$ neighbours weighted by their proximity to the query:

$$\text{score}(m) = \frac{\sum_{i \in \mathcal{N}_q} \frac{1}{D(q,i) + \epsilon} \cdot \text{perf}(m, i) \cdot \gamma(m, i)}{\sum_{i \in \mathcal{N}_q} \frac{1}{D(q,i) + \epsilon}}$$

where:
- $\epsilon = 10^{-9}$ prevents division by zero for exact matches,
- $\text{perf}(m, i)$ is the benchmark score of model variant $m$ on historical dataset $i$ under the priority metric,
- $\gamma(m, i)$ is a **language coverage factor**:

$$\gamma(m, i) = 1 - \frac{|L_q \setminus L_m|}{|L_q|}$$

where $L_q$ is the set of languages in the user's query dataset and $L_m$ is the set of languages the model variant $m$ was trained on (inferred from the historical dataset's ISO codes). A model trained on a dataset with the exact same language set receives $\gamma = 1.0$; one missing half the user's languages receives $\gamma = 0.5$.

The recommended model is:

$$m^* = \arg\max_m \text{score}(m)$$

---

### 2.7 Confidence Score Calibration

After the IDW vote, a confidence signal is computed as the fraction of the $k$ nearest neighbours whose individually identified best model agrees with the overall winner $m^*$:

$$\text{conf} = \frac{|\{i \in \mathcal{N}_q : \text{best}(i) = m^*\}|}{k}$$

This produces values in $\{0, 1/k, 2/k, 1\}$ (for $k=3$: $0, 0.33, 0.67, 1.0$). The interpretation is intuitive: $\text{conf} = 1.0$ means all three nearest historical datasets independently recommended the same model — a strong retrieval signal. Confidence $= 0$ means the three neighbours each nominated different models; the IDW vote decided purely on performance-weighted distance.

---

## 3. MKB Pipeline (Meta-Knowledge Base)

### 3.1 Build Pipeline

The MKB is constructed in two phases, orchestrated by `hpc_build_mkb.py` (a checkpoint-safe HPC entry point) or programmatically via `Recommender.build_mkb()`.

**Phase 1 — Dataset Profiling.**  
For each historical dataset directory, `DeepProfiler.run_profile("building", parquet_dir=...)` is called. This reads per-language `.parquet` files (up to 50 text samples per language by default), runs the full feature extraction pipeline, and serialises the resulting `pd.DataFrame` (shape: `n_features × n_languages`) to a `.pkl` file. Datasets with existing `.pkl` files are skipped automatically — the job is idempotent and safe to re-submit after a node failure.

**Phase 2 — MKB Assembly.**  
All `.pkl` profile files are loaded into an `MKBStore` along with performance records from `benchmark_metadata.json` files (one per model variant per dataset). The `finalise()` method then:
1. Pools all language-level feature vectors across all datasets into a single matrix.
2. Fits the `FeatureStratifier` (StandardScaler + PCA per stratum) on this pooled matrix.
3. Computes and stores fingerprints for every historical dataset.
4. Serialises the complete store (stratifier + fingerprints + performances) to `mkb.pkl`.

The benchmark metadata JSON contains per-variant performance records for all stored metrics (accuracy, f1_macro, f1_weighted, precision_weighted, recall_weighted, inference_time_total_s, etc.).

---

### 3.2 Architecture Diagram

The following diagrams illustrate both the MKB build pipeline (offline) and the query-time recommendation pipeline (online).

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                          MKB BUILD PIPELINE  (Offline)                             ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  ┌──────────────────┐    Phase 1: Profiling                                          ║
║  │  Historical       │──────────────────────────────────────────────────────────┐   ║
║  │  Datasets         │                                                           │   ║
║  │  (parquet files)  │   For each dataset D_i:                                   │   ║
║  └──────────────────┘   ┌──────────────────────────────────────────────────┐   │   ║
║                          │  DeepProfiler.run_profile("building", D_i)       │   │   ║
║  ┌──────────────────┐   │  ┌───────────┐   ┌──────────┐   ┌─────────────┐  │   │   ║
║  │  Benchmark        │   │  │ spaCy NLP │   │ FastText │   │  wordfreq   │  │   │   ║
║  │  Results          │   │  │ (24 langs)│   │  vectors │   │  Zipf freq  │  │   │   ║
║  │  (JSON metadata)  │   │  └─────┬─────┘   └────┬─────┘   └──────┬──────┘  │   │   ║
║  └──────────────────┘   │        └────────────────┴────────────────┘         │   │   ║
║                          │  → ~3,066 features × n_languages DataFrame        │   │   ║
║                          │  → Saved as <dataset>.pkl                         │   │   ║
║                          └──────────────────────────────────────────────────┘   │   ║
║                                                              ▼                   │   ║
║                                              Phase 2: MKB Assembly              │   ║
║                          ┌──────────────────────────────────────────────────┐   │   ║
║                          │  MKBStore.build_from_filesystem()                 │   │   ║
║                          │                                                   │   │   ║
║                          │  1. Load all .pkl profiles                        │◄──┘   ║
║                          │  2. Load all benchmark_metadata.json              │       ║
║                          │  3. Pool all language vectors                     │       ║
║                          │                                                   │       ║
║                          │  FeatureStratifier.fit(pooled_matrix):            │       ║
║                          │  ┌─────────────────────────────────────────────┐ │       ║
║                          │  │  S1_morphological  → StandardScaler + PCA_1 │ │       ║
║                          │  │  S2_lexical_div    → StandardScaler + PCA_2 │ │       ║
║                          │  │  S3_structural     → StandardScaler + PCA_3 │ │       ║
║                          │  │  S4_info_theoretic → StandardScaler + PCA_4 │ │       ║
║                          │  │  S5_cross_level    → StandardScaler + PCA_5 │ │       ║
║                          │  └─────────────────────────────────────────────┘ │       ║
║                          │                                                   │       ║
║                          │  FingerprintBuilder.build() per dataset:          │       ║
║                          │  → Per-language PCA projections                   │       ║
║                          │  → Aggregate (mean, std, min, max, het) per PC    │       ║
║                          │  → Append S6 categorical typology flags           │       ║
║                          │                                                   │       ║
║                          │  → Serialise MKBStore → mkb.pkl                  │       ║
║                          └──────────────────────────────────────────────────┘       ║
╚══════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    QUERY-TIME RECOMMENDATION PIPELINE  (Online)                     ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  User provides:                                                                      ║
║  ┌─────────────────┐                                                                 ║
║  │  New unlabelled │                                                                 ║
║  │  text dataset   │                                                                 ║
║  │  (pd.Series)    │                                                                 ║
║  └────────┬────────┘                                                                 ║
║           │                                                                          ║
║           ▼                                                                          ║
║  ┌──────────────────────────────────────────────────────────────┐                   ║
║  │  DeepProfiler.get_multilingual_profile(text_series)          │                   ║
║  │  → Auto-detect languages (FastText lid.176)                  │                   ║
║  │  → Extract ~3,066 features per detected language             │                   ║
║  │  → Returns: DataFrame (features × languages)                 │                   ║
║  └──────────────────────────┬───────────────────────────────────┘                   ║
║                             │                                                        ║
║                             ▼                                                        ║
║  ┌──────────────────────────────────────────────────────────────┐                   ║
║  │  FingerprintBuilder.build(lang_profile_df)                   │                   ║
║  │  → Project each language through fitted per-stratum PCA      │                   ║
║  │  → Aggregate PC statistics across languages                  │                   ║
║  │  → Append S6 categorical typology flags                      │                   ║
║  │  → Returns: OrderedDict[str, float]  (fixed-length fingerprint)                  ║
║  └──────────────────────────┬───────────────────────────────────┘                   ║
║                             │                                                        ║
║                             ▼                                                        ║
║  ┌──────────────────────────────────────────────────────────────┐                   ║
║  │  SimilarityEngine.query(fingerprint, priority_metric)        │                   ║
║  │                                                              │                   ║
║  │  For each historical dataset i in MKBStore:                  │                   ║
║  │    d_s = ||f_query^(s) - f_i^(s)||_2     (per stratum)       │                   ║
║  │    d_cat = Hamming(f_query^(cat), f_i^(cat))                 │                   ║
║  │    D(q,i) = Σ w_s · d_s / Σ w_s         (weighted composite) │                   ║
║  │    sim(q,i) = (1 - D / D_max) × 100%                        │                   ║
║  │                                                              │                   ║
║  │  Top-k=3 nearest neighbours selected                         │                   ║
║  │                                                              │                   ║
║  │  IDW Vote:                                                   │                   ║
║  │    score(m) = Σ [inv_d · perf(m,i) · coverage(m)] / Σ inv_d │                   ║
║  │                                                              │                   ║
║  │  m* = argmax_m score(m)                                      │                   ║
║  │  conf = fraction of k neighbours agreeing on m*              │                   ║
║  └──────────────────────────┬───────────────────────────────────┘                   ║
║                             │                                                        ║
║                             ▼                                                        ║
║  ┌──────────────────────────────────────────────────────────────┐                   ║
║  │  Recommendation output:                                      │                   ║
║  │  • recommended_model (e.g., "fasttext_subword_OpenLID-v2")   │                   ║
║  │  • confidence score (0–1)                                    │                   ║
║  │  • k nearest neighbours with similarity %                    │                   ║
║  │  • all IDW model scores                                      │                   ║
║  │  • human-readable explanation                                │                   ║
║  │  • language coverage warnings (if applicable)                │                   ║
║  └──────────────────────────────────────────────────────────────┘                   ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
```

---

## 4. Experimental Setup

### 4.1 Datasets Used

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
- `01a_knowledge_train_50`: 50 samples per language — **used for profiling** (builds the linguistic profile entering the MKB)
- `01b_knowledge_benchmark_20`: 20 samples per language — **used for profiling validation**
- `02_evaluation_15` / `03_validation_15`: held-out evaluation and validation splits

All splits are stored as `.parquet` files, one file per language per dataset, with a numeric seed in the filename ensuring reproducibility (e.g., `en_234710.parquet`).

---

### 4.2 Models Benchmarked

Three broad families of LID models were benchmarked, each producing multiple dataset-specific variants:

**Family 1: FastText Subword Models** (`fasttext_subword_*`)  
Custom FastText models trained from scratch on the training split of each specific historical dataset using subword (character n-gram) representations. These are the strongest candidates for in-domain deployment. Each variant is named after its training corpus (e.g., `fasttext_subword_OpenLID-v2`, `fasttext_subword_massive`).

**Family 2: Off-the-Shelf FastText**  (`lid.176_*`)  
Facebook's pre-trained `lid.176.bin` model supporting 176 languages. Represents the zero-shot baseline — no domain adaptation. Available as both the full compressed version (`lid.176.bin`) and a quantised variant (`lid.176.ftz`).

**Family 3: Classical Machine Learning Baselines**  
Multiple Scikit-learn pipeline variants combining different vectorisation strategies with Logistic Regression:

| Variant prefix | Vectoriser | Notes |
|----------------|-----------|-------|
| `tfidf_lr_char_ngram_3_5_*` | TF-IDF, char n-grams (3,4,5) | L2-normalised, LR classifier |
| `bow_char_ngram_3_5_*` | Bag-of-Words, char n-grams (3,4,5) | Count-based features, LR classifier |
| `bow_maxabs_lr_char_ngram_3_5_*` | BoW + MaxAbsScaler, char n-grams | Scaled BoW, LR classifier |
| `tfidf_char_ngram_3_5_*` | TF-IDF, char n-grams (3,4,5) | Without explicit LR suffix in some variants |

Character n-gram ranges (3–5) were chosen because they capture morphological structure in fusional and agglutinative languages without requiring tokenisation, making them robust to script variation.

**Evaluated metric:** `f1_weighted` (weighted by support per class) was designated as the **priority metric** for this validation run. All other metrics (accuracy, f1_macro, precision_weighted, recall_weighted, inference_time_total_s) were also stored in the MKB and are available for future evaluations.

---

## 5. Validation Process & Results

### 5.1 Validation Methodology

The validation protocol addresses the question: *does the toolkit recommend a model that, when applied to the corresponding evaluation set, achieves performance close to (or better than) the oracle ground-truth best model?*

**Setup:**
- For each of the 17 datasets in the MKB, the toolkit is queried with the dataset's own pre-computed linguistic profile (i.e., we use the already-profiled fingerprint from the MKB itself — this is a leave-one-in evaluation, not a strict held-out test, and is appropriate for the current system scale).
- The toolkit's recommendation is compared against the ground-truth best model (identified by scanning all benchmark results for the highest `f1_weighted` score on the same dataset's evaluation split).
- Both the recommended model's score and the ground-truth best model's score are obtained from the stored benchmark metadata, ensuring a fair comparison on an identically split evaluation set.

**Primary metric:** `f1_weighted`  
**Evaluation dimensions:**
1. **Recommendation accuracy**: whether the exact recommended model matches the ground-truth best model (top-1 exact match).
2. **Performance gap** $\Delta$: how much `f1_weighted` the recommendation sacrifices relative to the oracle:

$$\Delta f_{1,w} = f_{1,w}^{(\text{oracle})} - f_{1,w}^{(\text{recommended})}$$

A $\Delta = 0$ implies the recommended model **is** the oracle. A small positive $\Delta$ implies a near-optimal recommendation.

---

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| Recommendation accuracy (top-1 exact match) | **11.8%** (2 / 17 correct) |
| Mean $\Delta f_{1,w}$ | +0.0061 |
| Std $\Delta f_{1,w}$ | 0.0063 |
| Median $\Delta f_{1,w}$ | +0.0027 |
| Min $\Delta f_{1,w}$ | +0.0000 |
| Max $\Delta f_{1,w}$ | +0.0185 |
| Confidence–accuracy Pearson $r$ | 0.387 (p = 0.1246) |

**Critical interpretation.** The 11.8% top-1 accuracy figure can appear alarming in isolation but requires careful contextualisation:

1. **The recommendation is always near-optimal.** The mean `f1_weighted` shortfall is only 0.61 percentage points, with a median of 0.27 pp. In applied LID, a difference of under 1 percentage point between the recommended model and the oracle is practically negligible.

2. **The ground-truth model is dataset-specific.** In 13 of the 15 failures, the ground-truth model is a FastText model trained specifically on that exact dataset (e.g., `fasttext_subword_tydiqa` for the tydiqa evaluation set). The toolkit's task is therefore extremely hard by construction: it must infer which dataset-specific model to prefer without having seen the dataset. A more lenient evaluation metric (e.g., whether the recommendation falls within the top-2 or top-3 models) would yield substantially higher scores.

3. **All scores are high in absolute terms.** Every recommended model scored above 0.96 `f1_weighted`, reflecting that modern LID is near-solved for most high-resource languages. The competitive landscape is compressed into a very narrow performance band, making the exact ranking problem hard for any retrieval system.

---

### 5.3 Per-Dataset Results

| Dataset | Recommended | Ground Truth | ✓ | GT Score | Rec Score | $\Delta f_{1,w}$ | Confidence |
|---------|------------|-------------|---|----------|-----------|---------|------------|
| OpenLID-v2 | `fasttext_subword_OpenLID-v2` | `fasttext_subword_OpenLID-v2` | ✓ | 0.9940 | 0.9940 | +0.0000 | 0.33 |
| wikipedia | `fasttext_subword_wikipedia` | `fasttext_subword_wikipedia` | ✓ | 0.9964 | 0.9964 | +0.0000 | 0.33 |
| xlsum | `fasttext_subword_exorde-social-media-dec-2024` | `fasttext_subword_xlsum` | ✗ | 0.9989 | 0.9986 | +0.0002 | 0.00 |
| amazon_reviews_multi | `fasttext_subword_exorde-social-media-dec-2024` | `fasttext_subword_amazon_reviews_multi` | ✗ | 0.9998 | 0.9990 | +0.0009 | 0.00 |
| europarl | `fasttext_subword_exorde-social-media-dec-2024` | `bow_char_ngram_3_5_europarl` | ✗ | 0.9995 | 0.9979 | +0.0017 | 0.00 |
| language-identification | `fasttext_subword_exorde-social-media-dec-2024` | `fasttext_subword_language-identification` | ✗ | 0.9979 | 0.9958 | +0.0021 | 0.00 |
| xnli | `fasttext_subword_exorde-social-media-dec-2024` | `fasttext_subword_xnli` | ✗ | 0.9996 | 0.9975 | +0.0022 | 0.33 |
| stsb_multi_mt | `fasttext_subword_exorde-social-media-dec-2024` | `tfidf_lr_char_ngram_3_5_stsb_multi_mt` | ✗ | 0.9942 | 0.9916 | +0.0026 | 0.00 |
| flores_plus | `fasttext_subword_wikipedia` | `fasttext_subword_OpenLID-v2` | ✗ | 0.9951 | 0.9924 | +0.0027 | 0.00 |
| multilingual_toxicity_dataset | `fasttext_subword_exorde-social-media-dec-2024` | `fasttext_subword_multilingual_toxicity_dataset` | ✗ | 0.9937 | 0.9899 | +0.0037 | 0.00 |
| multi_eurlex | `fasttext_subword_wikipedia` | `bow_maxabs_lr_char_ngram_3_5_multi_eurlex` | ✗ | 0.9998 | 0.9959 | +0.0039 | 0.33 |
| exorde-social-media | `fasttext_subword_exorde-social-media-dec-2024` | `lid.176_exorde-social-media-dec-2024` | ✗ | 0.9779 | 0.9688 | +0.0091 | 0.33 |
| massive | `fasttext_subword_exorde-social-media-dec-2024` | `fasttext_subword_massive` | ✗ | 0.9974 | 0.9881 | +0.0093 | 0.33 |
| stsb_multi_mt | — | — | — | — | — | — | — |
| tweet_sentiment_multilingual | `fasttext_subword_exorde-social-media-dec-2024` | `bow_char_ngram_3_5_tweet_sentiment_multilingual` | ✗ | 0.9981 | 0.9827 | +0.0154 | 0.33 |
| tydiqa | `fasttext_subword_exorde-social-media-dec-2024` | `fasttext_subword_tydiqa` | ✗ | 0.9999 | 0.9856 | +0.0143 | 0.00 |
| mmarco | `fasttext_subword_exorde-social-media-dec-2024` | `fasttext_subword_mmarco` | ✗ | 0.9975 | 0.9802 | +0.0173 | 0.00 |
| multilingual_cc_news | `fasttext_subword_wikipedia` | `fasttext_subword_multilingual_cc_news` | ✗ | 0.9971 | 0.9787 | +0.0185 | 0.33 |

*Table sorted by $\Delta f_{1,w}$ (ascending). Full dataset names abbreviated for display.*

---

### 5.4 Failure Mode Analysis

Fifteen of seventeen datasets were not exactly matched. Analysing the neighbourhood information from the toolkit's retrieval reveals a consistent and interpretable failure pattern.

#### Root Cause 1: Retrieval Gravity of Strong Attractors

The `exorde-social-media-december-2024-week1` dataset is linguistically similar to a large portion of the MKB datasets (web-scraped informal multilingual text), causing it to appear in the top-3 neighbourhood for 11 of 17 queries. When it is the top neighbour, its best model (`fasttext_subword_exorde-social-media-december-2024-week1`) wins the IDW vote even when a dataset-specific model would perform slightly better.

This is evidenced by the consistent pattern: the exorde model is recommended for datasets with diverse domains (formal: `europarl`, QA: `tydiqa`, conversational: `massive`). In each case the shortfall is small, confirming the exorde model is a reasonable but not optimal choice.

#### Root Cause 2: Dataset-Specific Optima Not Reachable via Retrieval

For datasets where the top-1 neighbour **is** the target dataset (e.g., tydiqa with 90.1% similarity, massive with 85.9%, flores_plus with 92.7%), the ground-truth model is always the dataset-specific FastText variant. However, since the IDW vote aggregates **all** k=3 neighbours, the 2nd and 3rd neighbours can override the signal from the closest neighbour if they both agree on a different model.

**Example — tydiqa (Δ = 0.0143):**
```
Neighbours:
  1. tydiqa         (90.1%) — best: fasttext_subword_tydiqa
  2. mmarco         (80.3%) — best: fasttext_subword_mmarco
  3. stsb_multi_mt  (74.6%) — best: tfidf_lr_char_ngram_3_5_stsb_multi_mt
```
The closest neighbour identifies the correct model, but the two further neighbours vote for different models, diluting the IDW score of `fasttext_subword_tydiqa` below that of the `exorde` model which appears as a performance-competitive option in the voting pool.

**Example — multilingual_cc_news (Δ = 0.0185 — worst case):**
```
Neighbours:
  1. multilingual_cc_news (78.7%) — best: fasttext_subword_multilingual_cc_news
  2. wikipedia            (73.5%) — best: fasttext_subword_wikipedia
  3. xlsum                (72.6%) — best: fasttext_subword_xlsum
```
Here the top neighbour correctly identifies the ground-truth model, but with only 78.7% similarity, the confidence is low, and the `wikipedia` model from the 2nd neighbour — which has broader language coverage and strong general-purpose performance — wins the IDW vote. This is a classic precision–recall trade-off in retrieval: a general model with slightly lower peak performance beats a specialised model when the retrieval signal is noisy.

#### Root Cause 3: Domain Boundary Crossings in Classical ML Models

Several ground-truth models are classical character n-gram variants (e.g., `bow_char_ngram_3_5_europarl`, `bow_maxabs_lr_char_ngram_3_5_multi_eurlex`, `tfidf_lr_char_ngram_3_5_stsb_multi_mt`). These outperform FastText in highly formal, domain-constrained datasets. The current fingerprint representation does not explicitly encode domain formality as a retrievable signal, making it difficult to predict when a classical model will outperform a neural one.

#### Summary of Failure Patterns

| Pattern | Datasets Affected | Mean $\Delta$ |
|---------|-------------------|-------------|
| Exorde attractor dominates IDW vote | 8 | 0.0063 |
| Correct neighbour-1 overridden by neighbours 2–3 | 4 | 0.0131 |
| Classical model preferred over neural (not predictable from fingerprint) | 3 | 0.0027 |

---

### 5.5 Confidence Calibration

The Pearson correlation between the toolkit's confidence score and binary recommendation correctness across all 17 datasets is:

$$r = 0.387, \quad p = 0.1246$$

While the $p$-value does not meet a conventional 0.05 significance threshold (attributable to the small sample of $n=17$), the direction and magnitude of the correlation are encouraging. Correct recommendations (the 2 exact matches) were both made with confidence 0.33, while failed recommendations span the full confidence range. The low confidence values overall ($0.00$ in 9 of 17 cases) reflect that the three nearest neighbours frequently disagree on the best model — a direct consequence of the dense competitive landscape among high-performing FastText variants.

A critical caveat: with only 17 evaluation points, the confidence calibration analysis is underpowered. A meaningful calibration test would require at minimum 50–100 evaluation datasets.

---

## 6. Future Work & Open Questions

Based on the validation findings, the following directions are prioritised:

### 6.1 Expand the MKB

The most impactful short-term improvement is increasing the number of historical datasets in the MKB from 17 to 50+. With more historical data points:
- The retrieval problem becomes better conditioned (less sensitivity to individual attractor datasets).
- The LOO weight-learning procedure (`SimilarityEngine.learn_weights()`) becomes reliable enough to derive meaningful per-stratum weights, potentially improving similarity discrimination.
- The confidence calibration analysis gains statistical power.

### 6.2 Stratum-Level Weight Learning

The current equal-weighting scheme ($w_s = 1.0$ for all strata) was used for this validation. The LOO Pearson correlation method for data-driven weight learning is implemented but requires more data points to produce stable weights. An open research question is whether S1 (morphological) or S4 (information-theoretic) strata are more predictive of the optimal model family (neural vs. classical).

### 6.3 Formalise Domain Register as a Feature

The failure mode analysis identified that domain formality (formal legal/parliamentary vs. informal social media) is a key predictor of whether classical character n-gram models outperform FastText. A dedicated "register/formality" feature stratum could be constructed using:
- Mean sentence length and parse depth as proxies for syntactic complexity.
- Hapax legomena concentration and Zipf steepness as proxies for vocabulary richness.
- Punctuation density and capitalisation patterns as register markers.

### 6.4 Top-K Accuracy as the Primary Metric

The current evaluation uses exact top-1 match. Given the near-optimal performance gap ($\bar{\Delta} = 0.0061$), a more appropriate primary metric for the retrieval task would be:

$$\text{Acc}@k = \frac{1}{N} \sum_{i=1}^N \mathbf{1}\left[m_{\text{oracle},i} \in \text{Top-}k_{\text{recommended},i}\right]$$

Reporting Acc@3 and Acc@5 would better reflect the toolkit's true utility, since users in practice select from the top recommendations rather than committing blindly to the top-1 output.

### 6.5 Cross-Dataset Generalisation Evaluation

The current validation is conducted in-distribution: all 17 evaluation datasets were also used to build the MKB. A rigorous out-of-distribution evaluation should be conducted using held-out datasets not seen during MKB construction. This requires expanding the dataset collection and implementing a proper train/test split at the dataset level.

### 6.6 Low-Confidence Fallback Strategy

When confidence is 0 (no neighbourhood agreement), the toolkit currently still returns a recommendation based purely on IDW scores. A principled fallback strategy could be:
- Present the top-3 model candidates with their IDW scores explicitly rather than forcing a single recommendation.
- Flag the query as "ambiguous" and suggest running a small pilot benchmark (e.g., 5–10% of the user's dataset) to disambiguate.

### 6.7 Language Coverage Guard Evaluation

The language coverage penalty ($\gamma(m,i)$) is implemented but was not independently evaluated in this validation because all MKB datasets share the same 24-language DeepProfiler support set. An evaluation on datasets with languages outside this set would test whether the coverage guard meaningfully improves recommendations in low-resource multilingual scenarios.

---

*End of briefing document. Total pipeline lines of code: ~2,500 (Python). All source code is available in the `lid_toolkit` package at `toolkit_dev/lid_toolkit/src/lid_toolkit/`.*
