# LID model selection framework

An interactive framework that recommends a language identification (LID) model
for a short-text corpus, without needing any language labels for that corpus.

You give it an unlabelled sample of your text. It builds a linguistic profile of
the sample, finds the most similar corpora in a knowledge base of 17 benchmarked
corpora, and recommends the candidate model that performed best on those
neighbours. With the recommendation it returns a ranked shortlist, a consensus
index showing how far the neighbours agree, and an explanation of which
linguistic properties made each neighbour similar.

This repository accompanies the MEng thesis *An Interactive Framework for
Language Identification Model Recommendation* (Werner Hugo, Stellenbosch
University, 2026). The version described in the thesis is archived on Zenodo;
see [Citation](#citation).

## How it works

1. **Profile.** The `DeepProfiler` assigns each document to a language with
   fastText lid.176, then computes 2,726 linguistic meta-features per language
   (adapted from Lingualyzer) using spaCy.
2. **Compress.** The meta-features are split into five linguistic strata
   (morphology, lexical diversity, structure, information theory, cohesion),
   each compressed separately with PCA. Together with a block of typological
   flags this gives a 332-dimensional dataset fingerprint.
3. **Retrieve.** The fingerprint is compared with the 17 stored fingerprints by
   a weighted per-stratum distance, and the 3 nearest corpora are retrieved.
4. **Recommend.** The benchmark records of those neighbours are combined by
   inverse-distance-weighted voting under your chosen priority metric (for
   example weighted F1, or inference latency), with a penalty for models that
   do not cover all your languages.

The knowledge base (`mkb.pkl`) holds 1,785 performance records: 105 candidate
models on 17 corpora. The candidates are six trained configurations
(multinomial Naive Bayes and logistic regression over character 3–5-grams, and
two FastText variants) for each corpus, plus three off-the-shelf detectors
(lid.176, CLD3 and XLM-V Base).

## Scope

- 24 high-resource languages: ca, da, de, el, en, es, fi, fr, hr, it, ja, ko,
  lt, mk, nb, nl, pl, pt, ro, ru, sl, sv, uk, zh.
- Short text: documents of 30 to 120 characters (10 to 40 for Chinese, Japanese
  and Korean). Longer documents are truncated.
- One language per document; code-switched text is out of scope.
- Recommendations are most reliable for corpora that resemble one already in
  the knowledge base. For a very different corpus the recommendation is still
  near-optimal on the thesis evaluation, but no better than always using a
  strong general-purpose detector.

## Installation

The framework needs Python 3.10 or later (the thesis used 3.10). It runs on
CPU; no GPU is needed.

**With conda (recommended).** This recreates the environment used for the
thesis, including all 24 spaCy pipelines:

```sh
git clone https://github.com/Whugo226/lid_framework.git
cd lid_framework
conda env create -f environment.yml
conda activate thesis_final
```

**With pip:**

```sh
git clone https://github.com/Whugo226/lid_framework.git
cd lid_framework
pip install ".[spacy-models]"
```

The repository is named `lid_framework`; the Python package it installs is
`lid_toolkit`.

## Usage

### Interactive dashboard

From the repository root:

```sh
streamlit run src/lid_toolkit/explainer/dashboard.py
```

Upload a CSV file with a `text` column (the column name can be changed in the
sidebar) and click **Profile corpus**. Profiling takes a few minutes: roughly
14 seconds per language on a laptop CPU. After that, changing the priority
metric re-queries the knowledge base in well under a second. The six tabs show
the corpus profile, the recommendation and shortlist, a step-by-step account of
how it was reached, a way to run any candidate model on your data, a comparison
with simple baselines, and each candidate's language coverage.

### Python

```python
import pandas as pd
from lid_toolkit import LID_Recommender

lid = LID_Recommender("mkb.pkl", seed=42)       # seed makes profiling repeatable
texts = pd.read_csv("my_corpus.csv")["text"]

profile = lid.profile(texts)                     # the slow step; do it once
rec, _ = lid.explain_from_profile(profile, metric="f1_weighted")

print(rec.recommended_model, rec.recommended_paradigm)
print(rec.explanation)                           # neighbours, per-stratum distances, shortlist
```

`metric` can be any metric in the knowledge base: `accuracy`, `f1_macro`,
`f1_weighted`, `precision_macro`, `precision_weighted`, `recall_macro`,
`recall_weighted`, `inference_time_total_s`, `inference_time_ms_per_sample` or
`throughput_samples_per_sec`.

The consensus index (`rec.confidence`) is the fraction of the retrieved
neighbours whose own best model is the recommended one. It measures agreement,
not the probability that the recommendation is correct. When it is low, look at
the whole shortlist (`rec.all_model_scores`).

## Models and downloads

The repository does not contain the trained models. They are downloaded when
first needed and cached:

| What | Source | Size |
|---|---|---|
| fastText lid.176 (language census; also a candidate) | official fastText download | 126 MB |
| Compressed fastText word vectors (cohesion measures) | [werner1hugo/compressed-fasttext-models](https://huggingface.co/werner1hugo/compressed-fasttext-models) | small, per language |
| The 102 trained candidate models | [werner1hugo/lid-framework-models](https://huggingface.co/werner1hugo/lid-framework-models) | 1 MB to 2.3 GB each |

Only the model you run is downloaded, not all 27 GB. CLD3 and XLM-V Base are
not bundled; the dashboard explains how to run them separately.

Environment variables:

| Variable | Purpose |
|---|---|
| `LID_STORE_PATH` | Path to `mkb.pkl` (default: `./mkb.pkl`) |
| `LID_MODELS_REPO` | Hugging Face repo for the trained models |
| `LID_MODELS_REVISION` | Branch, tag or commit of that repo (default: the commit holding the models evaluated in the thesis) |
| `LID_EXPERIMENTS_DIR` | Local copy of the experiments folder; models found there are used instead of downloading |
| `LID_CACHE_DIR` | Where lid.176 is cached (default: `~/.cache/lid_toolkit`) |

**scikit-learn version.** The environment pins scikit-learn 1.7.2, the version
`mkb.pkl` was built with. The Naive Bayes and logistic regression models were
saved with scikit-learn 1.8.0. They load and predict correctly under 1.7.2, but
scikit-learn prints an `InconsistentVersionWarning` when they are loaded.

## Repository layout

| Path | Contents |
|---|---|
| `src/lid_toolkit/logic/` | The `DeepProfiler` (Phase 1). `profiler_knowledge_base.py` is the one the framework uses; the other profiler modules are earlier versions |
| `src/lid_toolkit/recommender/` | Stratification and PCA, fingerprints, the knowledge-base store, retrieval and voting (Phases 2 to 4) |
| `src/lid_toolkit/explainer/` | The Streamlit dashboard and the model runner |
| `mkb.pkl` | The Meta-Knowledge Base used in the thesis |
| `analysis/` | Scripts that produced the thesis tables and figures, with their dated result files (`*.json`) |
| `validate_recommendations*.py` | The held-out evaluation on the evaluation and validation splits |
| `tests/` | Profiler checks against the Lingualyzer reference values |
| `docs/model_card.md` | Model card of the trained models |
| `scripts/upload_models_to_hf.py` | Publishes the trained models to Hugging Face |

## Reproducing the thesis results

The dated JSON files in `analysis/` are the saved results behind the numbers in
the thesis, and each script there regenerates one of them. Rerunning the
evaluation needs the benchmark corpus splits and cross-benchmark records, which
are not in this repository: the corpora come from the Hugging Face Hub (listed
in `docs/model_card.md`) and are too large to redistribute. Several analysis
scripts still contain absolute paths from the author's machine that must be
edited before they run elsewhere.

## Licence

The code is released under the MIT licence (`LICENSE`). The trained models are
released under CC BY-NC-SA 4.0 and are also subject to the terms of the corpora
they were trained on; see `docs/model_card.md`. fastText lid.176 is distributed
by the fastText project under CC BY-SA 3.0.

## Citation

If you use this framework, please cite it using `CITATION.cff` (GitHub shows it
under *Cite this repository*).
