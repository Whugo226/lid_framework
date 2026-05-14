# LID Toolkit — Recommendation Validation Report

**Generated:** 2026-05-05 18:07:34  
**Priority metric:** `f1_weighted`  
**Datasets evaluated:** 17

---

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Recommendation accuracy | **11.8%** (2/17 correct) |
| Δ `f1_weighted` mean   | +0.0061 |
| Δ `f1_weighted` std    | 0.0063 |
| Δ `f1_weighted` median | +0.0027 |
| Δ `f1_weighted` min    | +0.0000 |
| Δ `f1_weighted` max    | +0.0185 |
| Confidence–accuracy Pearson r | 0.387 (p = 0.1246) |

---

## Per-Dataset Results

| Dataset | Recommended | Ground Truth | ✓ | GT score | Rec score | Δ `f1_weighted` | Confidence |
|---------|-------------|-------------|---|----------|-----------|------------|------------|
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

---

## Failure Mode Analysis

Datasets where the top-1 recommendation did not match ground truth (15/17), sorted by performance loss:

- **multilingual_cc_news** (21 langs): toolkit recommended `fasttext_subword_wikipedia` (score 0.9787), but ground truth was `fasttext_subword_multilingual_cc_news` (score 0.9971); performance gap = +0.0185
  - Neighbours: multilingual_cc_news (21 langs, 78.7%, best=`fasttext_subword_multilingual_cc_news`) | wikipedia (24 langs, 73.5%, best=`fasttext_subword_wikipedia`) | xlsum (9 langs, 72.6%, best=`fasttext_subword_xlsum`)

- **mmarco** (10 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9802), but ground truth was `fasttext_subword_mmarco` (score 0.9975); performance gap = +0.0173
  - Neighbours: OpenLID-v2 (23 langs, 63.8%, best=`fasttext_subword_OpenLID-v2`) | mmarco (10 langs, 62.7%, best=`fasttext_subword_mmarco`) | tydiqa (5 langs, 59.4%, best=`fasttext_subword_tydiqa`)

- **tweet_sentiment_multilingual** (6 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9827), but ground truth was `bow_char_ngram_3_5_tweet_sentiment_multilingual` (score 0.9981); performance gap = +0.0154
  - Neighbours: tweet_sentiment_multilingual (6 langs, 74.4%, best=`bow_char_ngram_3_5_tweet_sentiment_multilingual`) | exorde-social-media-december-2024-week1 (24 langs, 69.5%, best=`fasttext_subword_exorde-social-media-december-2024-week1`) | OpenLID-v2 (23 langs, 68.5%, best=`fasttext_subword_OpenLID-v2`)

- **tydiqa** (5 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9856), but ground truth was `fasttext_subword_tydiqa` (score 0.9999); performance gap = +0.0143
  - Neighbours: tydiqa (5 langs, 90.1%, best=`fasttext_subword_tydiqa`) | mmarco (10 langs, 80.3%, best=`fasttext_subword_mmarco`) | stsb_multi_mt (10 langs, 74.6%, best=`tfidf_lr_char_ngram_3_5_stsb_multi_mt`)

- **massive** (18 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9881), but ground truth was `fasttext_subword_massive` (score 0.9974); performance gap = +0.0093
  - Neighbours: massive (18 langs, 85.9%, best=`fasttext_subword_massive`) | exorde-social-media-december-2024-week1 (24 langs, 61.9%, best=`fasttext_subword_exorde-social-media-december-2024-week1`) | multilingual_toxicity_dataset (9 langs, 54.0%, best=`fasttext_subword_multilingual_toxicity_dataset`)

- **exorde-social-media-december-2024-week1** (24 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9688), but ground truth was `lid.176_exorde-social-media-december-2024-week1` (score 0.9779); performance gap = +0.0091
  - Neighbours: multilingual_toxicity_dataset (9 langs, 76.1%, best=`fasttext_subword_multilingual_toxicity_dataset`) | exorde-social-media-december-2024-week1 (24 langs, 74.5%, best=`fasttext_subword_exorde-social-media-december-2024-week1`) | tweet_sentiment_multilingual (6 langs, 72.9%, best=`bow_char_ngram_3_5_tweet_sentiment_multilingual`)

- **multi_eurlex** (16 langs): toolkit recommended `fasttext_subword_wikipedia` (score 0.9959), but ground truth was `bow_maxabs_lr_char_ngram_3_5_multi_eurlex` (score 0.9998); performance gap = +0.0039
  - Neighbours: multi_eurlex (16 langs, 73.5%, best=`tfidf_char_ngram_3_5_multi_eurlex`) | wikipedia (24 langs, 58.5%, best=`fasttext_subword_wikipedia`) | multilingual_cc_news (21 langs, 58.3%, best=`fasttext_subword_multilingual_cc_news`)

- **multilingual_toxicity_dataset** (9 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9899), but ground truth was `fasttext_subword_multilingual_toxicity_dataset` (score 0.9937); performance gap = +0.0037
  - Neighbours: OpenLID-v2 (23 langs, 59.7%, best=`fasttext_subword_OpenLID-v2`) | multilingual_toxicity_dataset (9 langs, 55.0%, best=`fasttext_subword_multilingual_toxicity_dataset`) | language-identification (12 langs, 48.2%, best=`tfidf_char_ngram_3_5_language-identification`)

- **flores_plus** (23 langs): toolkit recommended `fasttext_subword_wikipedia` (score 0.9924), but ground truth was `fasttext_subword_OpenLID-v2` (score 0.9951); performance gap = +0.0027
  - Neighbours: flores_plus (23 langs, 92.7%, best=`fasttext_subword_OpenLID-v2`) | europarl (13 langs, 77.8%, best=`tfidf_char_ngram_3_5_europarl`) | multilingual_cc_news (21 langs, 74.7%, best=`fasttext_subword_multilingual_cc_news`)

- **stsb_multi_mt** (10 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9916), but ground truth was `tfidf_lr_char_ngram_3_5_stsb_multi_mt` (score 0.9942); performance gap = +0.0026
  - Neighbours: OpenLID-v2 (23 langs, 53.8%, best=`fasttext_subword_OpenLID-v2`) | wikipedia (24 langs, 52.4%, best=`fasttext_subword_wikipedia`) | mmarco (10 langs, 52.3%, best=`fasttext_subword_mmarco`)

- **xnli** (7 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9975), but ground truth was `fasttext_subword_xnli` (score 0.9996); performance gap = +0.0022
  - Neighbours: xnli (7 langs, 55.9%, best=`fasttext_subword_xnli`) | massive (18 langs, 51.0%, best=`fasttext_subword_massive`) | exorde-social-media-december-2024-week1 (24 langs, 44.6%, best=`fasttext_subword_exorde-social-media-december-2024-week1`)

- **language-identification** (12 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9958), but ground truth was `fasttext_subword_language-identification` (score 0.9979); performance gap = +0.0021
  - Neighbours: language-identification (12 langs, 92.6%, best=`tfidf_char_ngram_3_5_language-identification`) | amazon_reviews_multi (6 langs, 78.9%, best=`fasttext_subword_amazon_reviews_multi`) | xlsum (9 langs, 68.3%, best=`fasttext_subword_xlsum`)

- **europarl** (13 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9979), but ground truth was `bow_char_ngram_3_5_europarl` (score 0.9995); performance gap = +0.0017
  - Neighbours: europarl (13 langs, 91.4%, best=`tfidf_char_ngram_3_5_europarl`) | flores_plus (23 langs, 75.6%, best=`fasttext_subword_OpenLID-v2`) | language-identification (12 langs, 64.7%, best=`tfidf_char_ngram_3_5_language-identification`)

- **amazon_reviews_multi** (6 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9990), but ground truth was `fasttext_subword_amazon_reviews_multi` (score 0.9998); performance gap = +0.0009
  - Neighbours: amazon_reviews_multi (6 langs, 83.9%, best=`fasttext_subword_amazon_reviews_multi`) | language-identification (12 langs, 81.8%, best=`tfidf_char_ngram_3_5_language-identification`) | europarl (13 langs, 63.6%, best=`tfidf_char_ngram_3_5_europarl`)

- **xlsum** (9 langs): toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9986), but ground truth was `fasttext_subword_xlsum` (score 0.9989); performance gap = +0.0002
  - Neighbours: xlsum (9 langs, 92.6%, best=`fasttext_subword_xlsum`) | multilingual_cc_news (21 langs, 83.5%, best=`fasttext_subword_multilingual_cc_news`) | flores_plus (23 langs, 78.1%, best=`fasttext_subword_OpenLID-v2`)

---

## Confidence Calibration

Pearson *r* between the toolkit's confidence score and prediction correctness: **0.387** (p = 0.1246).

There is a moderate positive correlation — high-confidence recommendations are more likely to be correct.
