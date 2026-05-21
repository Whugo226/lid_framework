# LID Toolkit — Recommendation Validation Report

**Generated:** 2026-05-14 11:48:53  
**Priority metric:** `f1_weighted`  
**Datasets evaluated:** 17

---

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Recommendation accuracy | **17.6%** (3/17 correct) |
| Δ `f1_weighted` mean   | +0.0078 |
| Δ `f1_weighted` std    | 0.0125 |
| Δ `f1_weighted` median | +0.0022 |
| Δ `f1_weighted` min    | +0.0000 |
| Δ `f1_weighted` max    | +0.0489 |
| Confidence–accuracy Pearson r | 0.743 (p = 0.0006) |

---

## Per-Dataset Results

| Dataset | Recommended | Ground Truth | ✓ | GT score | Rec score | Δ `f1_weighted` | Confidence |
|---------|-------------|-------------|---|----------|-----------|------------|------------|
| OpenLID-v2 | `fasttext_subword_OpenLID-v2` | `fasttext_subword_OpenLID-v2` | ✓ | 0.9940 | 0.9940 | +0.0000 | 0.67 |
| amazon_reviews_multi | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_amazon_reviews_multi` | ✗ | 0.9998 | 0.9990 | +0.0009 | 0.00 |
| europarl | `xlm_v_base_language_id` | `bow_char_ngram_3_5_europarl` | ✗ | 0.9995 | 0.9984 | +0.0011 | 0.00 |
| exorde-social-media-december-2024-week1 | `fasttext_subword_exorde-social-media-december-2024-week1` | `lid.176_exorde-social-media-december-2024-week1` | ✗ | 0.9779 | 0.9688 | +0.0091 | 0.00 |
| flores_plus | `xlm_v_base_language_id` | `xlm_v_base_language_id` | ✓ | 0.9952 | 0.9952 | +0.0000 | 0.00 |
| language-identification | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_language-identification` | ✗ | 0.9979 | 0.9958 | +0.0021 | 0.00 |
| massive | `xlm_v_base_language_id` | `fasttext_subword_massive` | ✗ | 0.9974 | 0.9782 | +0.0192 | 0.00 |
| mmarco | `xlm_v_base_language_id` | `fasttext_subword_mmarco` | ✗ | 0.9975 | 0.9715 | +0.0259 | 0.00 |
| multi_eurlex | `fasttext_subword_wikipedia` | `bow_maxabs_lr_char_ngram_3_5_multi_eurlex` | ✗ | 0.9998 | 0.9959 | +0.0039 | 0.00 |
| multilingual_cc_news | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_multilingual_cc_news` | ✗ | 0.9971 | 0.9860 | +0.0112 | 0.00 |
| multilingual_toxicity_dataset | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_multilingual_toxicity_dataset` | ✗ | 0.9937 | 0.9899 | +0.0037 | 0.00 |
| stsb_multi_mt | `xlm_v_base_language_id` | `tfidf_lr_char_ngram_3_5_stsb_multi_mt` | ✗ | 0.9942 | 0.9912 | +0.0029 | 0.00 |
| tweet_sentiment_multilingual | `xlm_v_base_language_id` | `bow_char_ngram_3_5_tweet_sentiment_multilingual` | ✗ | 0.9981 | 0.9492 | +0.0489 | 0.00 |
| tydiqa | `xlm_v_base_language_id` | `fasttext_subword_tydiqa` | ✗ | 0.9999 | 0.9986 | +0.0013 | 0.00 |
| wikipedia | `fasttext_subword_wikipedia` | `fasttext_subword_wikipedia` | ✓ | 0.9964 | 0.9964 | +0.0000 | 0.33 |
| xlsum | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_xlsum` | ✗ | 0.9989 | 0.9986 | +0.0002 | 0.00 |
| xnli | `fasttext_subword_exorde-social-media-december-2024-week1` | `fasttext_subword_xnli` | ✗ | 0.9996 | 0.9975 | +0.0022 | 0.00 |

---

## Failure Mode Analysis

Datasets where the top-1 recommendation did not match ground truth (14/17), sorted by performance loss:

- **tweet_sentiment_multilingual**: toolkit recommended `xlm_v_base_language_id` (score 0.9492), but ground truth was `bow_char_ngram_3_5_tweet_sentiment_multilingual` (score 0.9981); performance gap = +0.0489
  - Neighbours: OpenLID-v2 (47.3%, best=`fasttext_subword_OpenLID-v2`) | tweet_sentiment_multilingual (46.4%, best=`bow_char_ngram_3_5_tweet_sentiment_multilingual`) | multilingual_toxicity_dataset (44.7%, best=`fasttext_subword_multilingual_toxicity_dataset`)
- **mmarco**: toolkit recommended `xlm_v_base_language_id` (score 0.9715), but ground truth was `fasttext_subword_mmarco` (score 0.9975); performance gap = +0.0259
  - Neighbours: OpenLID-v2 (44.9%, best=`fasttext_subword_OpenLID-v2`) | tydiqa (44.1%, best=`fasttext_subword_tydiqa`) | massive (40.8%, best=`fasttext_subword_massive`)
- **massive**: toolkit recommended `xlm_v_base_language_id` (score 0.9782), but ground truth was `fasttext_subword_massive` (score 0.9974); performance gap = +0.0192
  - Neighbours: massive (62.9%, best=`fasttext_subword_massive`) | OpenLID-v2 (57.9%, best=`fasttext_subword_OpenLID-v2`) | stsb_multi_mt (55.0%, best=`tfidf_lr_char_ngram_3_5_stsb_multi_mt`)
- **multilingual_cc_news**: toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9860), but ground truth was `fasttext_subword_multilingual_cc_news` (score 0.9971); performance gap = +0.0112
  - Neighbours: multilingual_cc_news (62.1%, best=`fasttext_subword_multilingual_cc_news`) | xlsum (51.6%, best=`fasttext_subword_xlsum`) | exorde-social-media-december-2024-week1 (48.9%, best=`lid.176_exorde-social-media-december-2024-week1`)
- **exorde-social-media-december-2024-week1**: toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9688), but ground truth was `lid.176_exorde-social-media-december-2024-week1` (score 0.9779); performance gap = +0.0091
  - Neighbours: exorde-social-media-december-2024-week1 (82.0%, best=`lid.176_exorde-social-media-december-2024-week1`) | multilingual_cc_news (64.1%, best=`fasttext_subword_multilingual_cc_news`) | multilingual_toxicity_dataset (59.5%, best=`fasttext_subword_multilingual_toxicity_dataset`)
- **multi_eurlex**: toolkit recommended `fasttext_subword_wikipedia` (score 0.9959), but ground truth was `bow_maxabs_lr_char_ngram_3_5_multi_eurlex` (score 0.9998); performance gap = +0.0039
  - Neighbours: multi_eurlex (58.7%, best=`tfidf_char_ngram_3_5_multi_eurlex`) | multilingual_cc_news (36.3%, best=`fasttext_subword_multilingual_cc_news`) | xlsum (30.3%, best=`fasttext_subword_xlsum`)
- **multilingual_toxicity_dataset**: toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9899), but ground truth was `fasttext_subword_multilingual_toxicity_dataset` (score 0.9937); performance gap = +0.0037
  - Neighbours: OpenLID-v2 (51.4%, best=`fasttext_subword_OpenLID-v2`) | exorde-social-media-december-2024-week1 (47.8%, best=`lid.176_exorde-social-media-december-2024-week1`) | language-identification (46.4%, best=`tfidf_char_ngram_3_5_language-identification`)
- **stsb_multi_mt**: toolkit recommended `xlm_v_base_language_id` (score 0.9912), but ground truth was `tfidf_lr_char_ngram_3_5_stsb_multi_mt` (score 0.9942); performance gap = +0.0029
  - Neighbours: tydiqa (21.8%, best=`fasttext_subword_tydiqa`) | OpenLID-v2 (21.0%, best=`fasttext_subword_OpenLID-v2`) | stsb_multi_mt (19.5%, best=`tfidf_lr_char_ngram_3_5_stsb_multi_mt`)
- **xnli**: toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9975), but ground truth was `fasttext_subword_xnli` (score 0.9996); performance gap = +0.0022
  - Neighbours: OpenLID-v2 (41.1%, best=`fasttext_subword_OpenLID-v2`) | exorde-social-media-december-2024-week1 (39.8%, best=`lid.176_exorde-social-media-december-2024-week1`) | language-identification (37.9%, best=`tfidf_char_ngram_3_5_language-identification`)
- **language-identification**: toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9958), but ground truth was `fasttext_subword_language-identification` (score 0.9979); performance gap = +0.0021
  - Neighbours: language-identification (87.7%, best=`tfidf_char_ngram_3_5_language-identification`) | multilingual_toxicity_dataset (71.2%, best=`fasttext_subword_multilingual_toxicity_dataset`) | amazon_reviews_multi (63.3%, best=`fasttext_subword_amazon_reviews_multi`)
- **tydiqa**: toolkit recommended `xlm_v_base_language_id` (score 0.9986), but ground truth was `fasttext_subword_tydiqa` (score 0.9999); performance gap = +0.0013
  - Neighbours: tydiqa (76.5%, best=`fasttext_subword_tydiqa`) | stsb_multi_mt (49.6%, best=`tfidf_lr_char_ngram_3_5_stsb_multi_mt`) | mmarco (47.6%, best=`fasttext_subword_mmarco`)
- **europarl**: toolkit recommended `xlm_v_base_language_id` (score 0.9984), but ground truth was `bow_char_ngram_3_5_europarl` (score 0.9995); performance gap = +0.0011
  - Neighbours: europarl (85.9%, best=`tfidf_char_ngram_3_5_europarl`) | flores_plus (57.7%, best=`fasttext_subword_OpenLID-v2`) | xnli (57.1%, best=`fasttext_subword_xnli`)
- **amazon_reviews_multi**: toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9990), but ground truth was `fasttext_subword_amazon_reviews_multi` (score 0.9998); performance gap = +0.0009
  - Neighbours: amazon_reviews_multi (88.1%, best=`fasttext_subword_amazon_reviews_multi`) | language-identification (63.3%, best=`tfidf_char_ngram_3_5_language-identification`) | multilingual_toxicity_dataset (58.0%, best=`fasttext_subword_multilingual_toxicity_dataset`)
- **xlsum**: toolkit recommended `fasttext_subword_exorde-social-media-december-2024-week1` (score 0.9986), but ground truth was `fasttext_subword_xlsum` (score 0.9989); performance gap = +0.0002
  - Neighbours: xlsum (88.2%, best=`fasttext_subword_xlsum`) | multilingual_cc_news (70.4%, best=`fasttext_subword_multilingual_cc_news`) | multilingual_toxicity_dataset (56.9%, best=`fasttext_subword_multilingual_toxicity_dataset`)

---

## Confidence Calibration

Pearson *r* between the toolkit's confidence score and prediction correctness: **0.743** (p = 0.0006).

There is a strong positive correlation — high-confidence recommendations are more likely to be correct.
