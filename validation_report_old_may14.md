# LID Toolkit — Recommendation Validation Report

**Generated:** 2026-05-02 12:37:14  
**Priority metric:** `f1_weighted`  
**Datasets evaluated:** 17

---

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Recommendation accuracy | **47.1%** (8/17 correct) |
| Δ `f1_weighted` mean   | +0.0271 |
| Δ `f1_weighted` std    | 0.0490 |
| Δ `f1_weighted` median | +0.0000 |
| Δ `f1_weighted` min    | +0.0000 |
| Δ `f1_weighted` max    | +0.1481 |

---

## Per-Dataset Results

| Dataset | Recommended | Ground Truth | ✓ | GT score | Rec score | Δ `f1_weighted` | Confidence |
|---------|-------------|-------------|---|----------|-----------|------------|------------|
| OpenLID-v2 | `fasttext_subword_OpenLID-v2` | `fasttext_subword_OpenLID-v2` | ✓ | 0.9940 | 0.9940 | +0.0000 | 0.33 |
| amazon_reviews_multi | `fasttext_subword_amazon_reviews_multi` | `fasttext_subword_amazon_reviews_multi` | ✓ | 0.9998 | 0.9998 | +0.0000 | 0.33 |
| europarl | `tfidf_char_ngram_3_5_europarl` | `bow_char_ngram_3_5_europarl` | ✗ | 0.9995 | 0.9995 | +0.0000 | 0.33 |
| exorde-social-media-december-2024-week1 | `lid.176_exorde-social-media-december-2024-week1` | `lid.176_exorde-social-media-december-2024-week1` | ✓ | 0.9779 | 0.9779 | +0.0000 | 0.33 |
| flores_plus | `tfidf_lr_char_ngram_3_5_flores_plus` | `fasttext_subword_OpenLID-v2` | ✗ | 0.9951 | 0.9828 | +0.0123 | 0.33 |
| language-identification | `tfidf_char_ngram_3_5_language-identification` | `fasttext_subword_language-identification` | ✗ | 0.9979 | 0.9979 | +0.0000 | 0.33 |
| massive | `fasttext_subword_massive` | `fasttext_subword_massive` | ✓ | 0.9974 | 0.9974 | +0.0000 | 0.33 |
| mmarco | `fasttext_subword_massive` | `fasttext_subword_mmarco` | ✗ | 0.9975 | 0.9668 | +0.0307 | 0.33 |
| multi_eurlex | `tfidf_char_ngram_3_5_multi_eurlex` | `bow_maxabs_lr_char_ngram_3_5_multi_eurlex` | ✗ | 0.9998 | 0.9998 | +0.0000 | 0.33 |
| multilingual_cc_news | `fasttext_subword_multilingual_cc_news` | `fasttext_subword_multilingual_cc_news` | ✓ | 0.9971 | 0.9971 | +0.0000 | 0.33 |
| multilingual_toxicity_dataset | `fasttext_subword_OpenLID-v2` | `fasttext_subword_multilingual_toxicity_dataset` | ✗ | 0.9937 | 0.8553 | +0.1384 | 0.33 |
| stsb_multi_mt | `fasttext_subword_OpenLID-v2` | `tfidf_lr_char_ngram_3_5_stsb_multi_mt` | ✗ | 0.9942 | 0.8929 | +0.1013 | 0.33 |
| tweet_sentiment_multilingual | `fasttext_subword_OpenLID-v2` | `bow_char_ngram_3_5_tweet_sentiment_multilingual` | ✗ | 0.9981 | 0.9684 | +0.0297 | 0.33 |
| tydiqa | `fasttext_subword_tydiqa` | `fasttext_subword_tydiqa` | ✓ | 0.9999 | 0.9999 | +0.0000 | 0.33 |
| wikipedia | `fasttext_subword_wikipedia` | `fasttext_subword_wikipedia` | ✓ | 0.9964 | 0.9964 | +0.0000 | 0.33 |
| xlsum | `fasttext_subword_xlsum` | `fasttext_subword_xlsum` | ✓ | 0.9989 | 0.9989 | +0.0000 | 0.33 |
| xnli | `fasttext_subword_OpenLID-v2` | `fasttext_subword_xnli` | ✗ | 0.9996 | 0.8515 | +0.1481 | 0.33 |

---

## Failure Mode Analysis

Datasets where the top-1 recommendation did not match ground truth (9/17), sorted by performance loss:

- **xnli**: toolkit recommended `fasttext_subword_OpenLID-v2` (score 0.8515), but ground truth was `fasttext_subword_xnli` (score 0.9996); performance gap = +0.1481
  - Neighbours: OpenLID-v2 (90.1%, best=`fasttext_subword_OpenLID-v2`) | language-identification (89.1%, best=`tfidf_char_ngram_3_5_language-identification`) | xnli (89.0%, best=`fasttext_subword_xnli`)
- **multilingual_toxicity_dataset**: toolkit recommended `fasttext_subword_OpenLID-v2` (score 0.8553), but ground truth was `fasttext_subword_multilingual_toxicity_dataset` (score 0.9937); performance gap = +0.1384
  - Neighbours: multilingual_toxicity_dataset (84.1%, best=`fasttext_subword_multilingual_toxicity_dataset`) | OpenLID-v2 (83.4%, best=`fasttext_subword_OpenLID-v2`) | language-identification (82.2%, best=`tfidf_char_ngram_3_5_language-identification`)
- **stsb_multi_mt**: toolkit recommended `fasttext_subword_OpenLID-v2` (score 0.8929), but ground truth was `tfidf_lr_char_ngram_3_5_stsb_multi_mt` (score 0.9942); performance gap = +0.1013
  - Neighbours: OpenLID-v2 (51.5%, best=`fasttext_subword_OpenLID-v2`) | stsb_multi_mt (49.1%, best=`tfidf_lr_char_ngram_3_5_stsb_multi_mt`) | mmarco (49.0%, best=`fasttext_subword_mmarco`)
- **mmarco**: toolkit recommended `fasttext_subword_massive` (score 0.9668), but ground truth was `fasttext_subword_mmarco` (score 0.9975); performance gap = +0.0307
  - Neighbours: massive (92.0%, best=`fasttext_subword_massive`) | mmarco (91.9%, best=`fasttext_subword_mmarco`) | OpenLID-v2 (91.7%, best=`fasttext_subword_OpenLID-v2`)
- **tweet_sentiment_multilingual**: toolkit recommended `fasttext_subword_OpenLID-v2` (score 0.9684), but ground truth was `bow_char_ngram_3_5_tweet_sentiment_multilingual` (score 0.9981); performance gap = +0.0297
  - Neighbours: tweet_sentiment_multilingual (94.6%, best=`bow_char_ngram_3_5_tweet_sentiment_multilingual`) | OpenLID-v2 (94.2%, best=`fasttext_subword_OpenLID-v2`) | multilingual_cc_news (94.1%, best=`fasttext_subword_multilingual_cc_news`)
- **flores_plus**: toolkit recommended `tfidf_lr_char_ngram_3_5_flores_plus` (score 0.9828), but ground truth was `fasttext_subword_OpenLID-v2` (score 0.9951); performance gap = +0.0123
  - Neighbours: flores_plus (98.9%, best=`tfidf_lr_char_ngram_3_5_flores_plus`) | europarl (96.2%, best=`tfidf_char_ngram_3_5_europarl`) | xnli (96.1%, best=`fasttext_subword_xnli`)
- **multi_eurlex**: toolkit recommended `tfidf_char_ngram_3_5_multi_eurlex` (score 0.9998), but ground truth was `bow_maxabs_lr_char_ngram_3_5_multi_eurlex` (score 0.9998); performance gap = +0.0000
  - Neighbours: multi_eurlex (90.2%, best=`tfidf_char_ngram_3_5_multi_eurlex`) | multilingual_cc_news (86.3%, best=`fasttext_subword_multilingual_cc_news`) | OpenLID-v2 (85.4%, best=`fasttext_subword_OpenLID-v2`)
- **europarl**: toolkit recommended `tfidf_char_ngram_3_5_europarl` (score 0.9995), but ground truth was `bow_char_ngram_3_5_europarl` (score 0.9995); performance gap = +0.0000
  - Neighbours: europarl (99.1%, best=`tfidf_char_ngram_3_5_europarl`) | flores_plus (96.3%, best=`tfidf_lr_char_ngram_3_5_flores_plus`) | xnli (95.9%, best=`fasttext_subword_xnli`)
- **language-identification**: toolkit recommended `tfidf_char_ngram_3_5_language-identification` (score 0.9979), but ground truth was `fasttext_subword_language-identification` (score 0.9979); performance gap = +0.0000
  - Neighbours: language-identification (99.0%, best=`tfidf_char_ngram_3_5_language-identification`) | amazon_reviews_multi (96.9%, best=`fasttext_subword_amazon_reviews_multi`) | xnli (96.0%, best=`fasttext_subword_xnli`)
