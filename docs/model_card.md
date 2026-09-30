---
license: cc-by-nc-sa-4.0
library_name: fasttext
pipeline_tag: text-classification
tags:
  - language-identification
  - short-text
  - fasttext
  - scikit-learn
  - model-selection
language:
  - ca
  - da
  - de
  - el
  - en
  - es
  - fi
  - fr
  - hr
  - it
  - ja
  - ko
  - lt
  - mk
  - nb
  - nl
  - pl
  - pt
  - ro
  - ru
  - sl
  - sv
  - uk
  - zh
---

# LID framework: trained candidate models

These are the 102 trained language identification (LID) models that populate the
Meta-Knowledge Base of the LID model selection framework
([GitHub: Whugo226/lid_framework](https://github.com/Whugo226/lid_framework)),
developed for the MEng thesis *An Interactive Framework for Language
Identification Model Recommendation* (Werner Hugo, Stellenbosch University, 2026).

The framework profiles an unlabelled short-text corpus and recommends one of
these models (or one of three off-the-shelf detectors). Its dashboard downloads
only the model it is asked to run, so you do not need to download this whole
repository.

## Contents

Six configurations were trained on each of 17 benchmark corpora
(6 × 17 = 102 models):

| Configuration | Family | Features | File |
|---|---|---|---|
| `bow_char_ngram_3_5` | Multinomial Naive Bayes | character 3–5-grams, raw counts | `best_pipeline.pkl` |
| `tfidf_char_ngram_3_5` | Multinomial Naive Bayes | character 3–5-grams, TF-IDF | `best_pipeline.pkl` |
| `bow_maxabs_lr_char_ngram_3_5` | Logistic regression | character 3–5-grams, max-abs scaled counts | `best_pipeline.pkl` |
| `tfidf_lr_char_ngram_3_5` | Logistic regression | character 3–5-grams, TF-IDF | `best_pipeline.pkl` |
| `fasttext_word` | FastText | word unigrams, no subwords | `model.bin` |
| `fasttext_subword` | FastText | word bigrams + character subwords (2–4) | `model.bin` |

Files are laid out as `{family}/{training_corpus}/{configuration}/`, where
`{family}` is `naive_bayes`, `logistic_regression` or `fasttext`. Each folder
also holds `run_metadata.json` (selected hyperparameters and training-split
metrics), `classification_report.txt`, and the hyperparameter search results.

Every model predicts ISO 639-1 codes for the subset of the 24 languages below
that its training corpus contains. The FastText models are large (up to about
2.3 GB each); the Naive Bayes and logistic regression pipelines are 1–63 MB.

## Usage

With the framework installed, the dashboard's *Run model* tab downloads and runs
a model on demand. Programmatically:

```python
from lid_toolkit.explainer.model_runner import ModelRunner

# store_datasets: the training-corpus names the variant names may end in
runner = ModelRunner(store_datasets=["xnli"])
runner.predict("fasttext_subword_xnli", ["Dit is een korte zin."])  # downloads on first use
```

Without the framework, the files load directly:

```python
from huggingface_hub import hf_hub_download
import fasttext, pickle

ft = fasttext.load_model(hf_hub_download(
    "werner1hugo/lid-framework-models", "fasttext/xnli/fasttext_subword/model.bin"))
ft.predict("Dit is een korte zin.")

with open(hf_hub_download(
        "werner1hugo/lid-framework-models",
        "logistic_regression/xnli/tfidf_lr_char_ngram_3_5/best_pipeline.pkl"), "rb") as fh:
    lr = pickle.load(fh)
lr.predict(["Dit is een korte zin."])
```

The scikit-learn pipelines were saved with scikit-learn 1.8.0. The framework pins
1.7.2 (the version its Meta-Knowledge Base was built with); under 1.7.2 the
pipelines load and predict correctly but scikit-learn prints an
`InconsistentVersionWarning`. Only unpickle files from sources you trust.

## Training

- Every source document was truncated at a word boundary to at most 120
  characters (40 for Chinese, Japanese and Korean); documents shorter than 30
  characters (10 for CJK) were discarded.
- Each corpus was split into four disjoint row-level parts under a fixed seed:
  50% knowledge-training, 20% knowledge-benchmarking, 15% evaluation and
  15% validation. Models were trained on the knowledge-training split only.
- Hyperparameters were selected by macro-F1 on a stratified 80/20 split of the
  training data: randomised search with 5-fold (Naive Bayes) or 3-fold
  (logistic regression) cross-validation, and a grid over epochs and learning
  rate on a 90/10 split for FastText.

## Performance and limitations

In-domain (evaluated on the same corpus they were trained on), mean weighted F1
ranges from 0.939 (FastText word) to 0.995 (FastText subword). Cross-domain
performance collapses to a mean of about 0.55–0.61, with worst cases below 0.06:
a model trained on one corpus can be unusable on another. That is why the
framework recommends a model per corpus rather than one model for everything.

- Only 24 high-resource languages are covered; any other language is misclassified.
- The models were trained and evaluated on short text (30–120 characters).
- They assign one language per document and do not handle code-switching.

## Training corpora and licences

These models are derived from the corpora below. They are released under
**CC BY-NC-SA 4.0** (non-commercial, share-alike), the most restrictive terms
among the corpora with stated licences. Use of an individual model is also
subject to the terms of the corpus it was trained on. Licences are as stated on
each dataset card at the time of release; "not stated" means the card gives none.

| Training corpus (folder name) | Hugging Face dataset | Languages | Licence on dataset card |
|---|---|---|---|
| `OpenLID-v2` | laurievb/OpenLID-v2 | 23 | other (gated) |
| `amazon_reviews_multi` | neonwatty/amazon_reviews_multi | 6 | not stated |
| `europarl` | Helsinki-NLP/europarl | 13 | unknown |
| `exorde-social-media-december-2024-week1` | Exorde/exorde-social-media-december-2024-week1 | 24 | MIT |
| `flores_plus` | openlanguagedata/flores_plus | 23 | CC BY-SA 4.0 (gated) |
| `language-identification` | papluca/language-identification | 12 | not stated |
| `massive` | AmazonScience/massive | 18 | CC BY 4.0 |
| `mmarco` | unicamp-dl/mmarco | 10 | not stated |
| `multi_eurlex` | coastalcph/multi_eurlex | 16 | CC BY-SA 4.0 |
| `multilingual_cc_news` | hotchpotch/multilingual_cc_news | 21 | not stated |
| `multilingual_toxicity_dataset` | textdetox/multilingual_toxicity_dataset | 9 | OpenRAIL++ |
| `stsb_multi_mt` | PhilipMay/stsb_multi_mt | 10 | other |
| `tweet_sentiment_multilingual` | cardiffnlp/tweet_sentiment_multilingual | 6 | not stated |
| `tydiqa` | google-research-datasets/tydiqa | 5 | Apache 2.0 |
| `wikipedia` | wikimedia/wikipedia | 24 | CC BY-SA 3.0, GFDL |
| `xlsum` | csebuetnlp/xlsum | 9 | CC BY-NC-SA 4.0 |
| `xnli` | facebook/xnli | 7 | not stated |

*Languages* counts the in-scope languages each corpus contains after filtering
to the 24 supported languages.

## Citation

If you use these models, please cite the thesis and the software archive (see
`CITATION.cff` in the GitHub repository).
