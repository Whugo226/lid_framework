# LID Toolkit — Recommendation Validation Report

**Generated:** 2026-04-23 21:52:26  
**Priority metric:** `f1_weighted`  
**Datasets evaluated:** 17

---

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Recommendation accuracy | **76.5%** (13/17 correct) |
| Δ `f1_weighted` mean   | +0.0003 |
| Δ `f1_weighted` std    | 0.0009 |
| Δ `f1_weighted` median | +0.0000 |
| Δ `f1_weighted` min    | +0.0000 |
| Δ `f1_weighted` max    | +0.0039 |
| Confidence–accuracy Pearson r | 0.314 (p = 0.22) |

---

## Per-Dataset Results

| Dataset | Recommended | Ground Truth | ✓ | GT score | Rec score | Δ `f1_weighted` | Confidence |
|---------|-------------|-------------|---|----------|-----------|------------|------------|
| OpenLID-v2 | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9940 | 0.9940 | +0.0000 | 0.67 |
| amazon_reviews_multi | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9998 | 0.9998 | +0.0000 | 0.67 |
| europarl | `tfidf_lr_char_ngram_3_5` | `bow_char_ngram_3_5` | ✗ | 0.9995 | 0.9994 | +0.0001 | 0.33 |
| exorde-social-media-december-2024-week1 | `lid.176` | `lid.176` | ✓ | 0.9779 | 0.9779 | +0.0000 | 0.33 |
| flores_plus | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9834 | 0.9834 | +0.0000 | 0.33 |
| language-identification | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9979 | 0.9979 | +0.0000 | 0.67 |
| massive | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9974 | 0.9974 | +0.0000 | 1.00 |
| mmarco | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9975 | 0.9975 | +0.0000 | 1.00 |
| multi_eurlex | `fasttext_subword` | `bow_maxabs_lr_char_ngram_3_5` | ✗ | 0.9998 | 0.9998 | +0.0000 | 0.67 |
| multilingual_cc_news | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9971 | 0.9971 | +0.0000 | 1.00 |
| multilingual_toxicity_dataset | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9937 | 0.9937 | +0.0000 | 0.33 |
| stsb_multi_mt | `fasttext_subword` | `tfidf_lr_char_ngram_3_5` | ✗ | 0.9942 | 0.9933 | +0.0009 | 0.67 |
| tweet_sentiment_multilingual | `fasttext_subword` | `bow_char_ngram_3_5` | ✗ | 0.9981 | 0.9942 | +0.0039 | 0.33 |
| tydiqa | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9999 | 0.9999 | +0.0000 | 0.67 |
| wikipedia | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9964 | 0.9964 | +0.0000 | 0.67 |
| xlsum | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9989 | 0.9989 | +0.0000 | 0.67 |
| xnli | `fasttext_subword` | `fasttext_subword` | ✓ | 0.9996 | 0.9996 | +0.0000 | 0.67 |

---

## Failure Mode Analysis

Datasets where the top-1 recommendation did not match ground truth (4/17), sorted by performance loss:

- **tweet_sentiment_multilingual**: toolkit recommended `fasttext_subword` (score 0.9942), but ground truth was `bow_char_ngram_3_5` (score 0.9981); performance gap = +0.0039
  - Neighbours: tweet_sentiment_multilingual (50.2%, best=`bow_char_ngram_3_5`) | OpenLID-v2 (44.8%, best=`fasttext_subword`) | exorde-social-media-december-2024-week1 (38.9%, best=`lid.176`)
- **stsb_multi_mt**: toolkit recommended `fasttext_subword` (score 0.9933), but ground truth was `tfidf_lr_char_ngram_3_5` (score 0.9942); performance gap = +0.0009
  - Neighbours: mmarco (11.0%, best=`fasttext_subword`) | stsb_multi_mt (10.9%, best=`tfidf_lr_char_ngram_3_5`) | massive (9.6%, best=`fasttext_subword`)
- **europarl**: toolkit recommended `tfidf_lr_char_ngram_3_5` (score 0.9994), but ground truth was `bow_char_ngram_3_5` (score 0.9995); performance gap = +0.0001
  - Neighbours: europarl (91.3%, best=`tfidf_char_ngram_3_5`) | flores_plus (76.0%, best=`tfidf_lr_char_ngram_3_5`) | xnli (63.7%, best=`fasttext_subword`)
- **multi_eurlex**: toolkit recommended `fasttext_subword` (score 0.9998), but ground truth was `bow_maxabs_lr_char_ngram_3_5` (score 0.9998); performance gap = +0.0000
  - Neighbours: multi_eurlex (52.1%, best=`tfidf_char_ngram_3_5`) | multilingual_cc_news (32.1%, best=`fasttext_subword`) | xlsum (21.4%, best=`fasttext_subword`)

---

## Confidence Calibration

Pearson *r* between the toolkit's confidence score and prediction correctness: **0.314** (p = 0.22).

There is a moderate positive correlation — high-confidence recommendations are more likely to be correct.
