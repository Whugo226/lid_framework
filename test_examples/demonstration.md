# LID Toolkit Demonstration Report

---

## 1. Dataset Overview

The input dataset contains text in **20 languages**, covering a broad range of language families and writing systems:

Arabic (ar), Bulgarian (bg), German (de), Modern Greek (el), English (en), Spanish (es), French (fr), Hindi (hi), Italian (it), Japanese (ja), Dutch (nl), Polish (pl), Portuguese (pt), Russian (ru), Swahili (sw), Thai (th), Turkish (tr), Urdu (ur), Vietnamese (vi), and Chinese (zh).

---

## 2. Recommendation

| Field | Value |
|---|---|
| **Recommended model** | **fasttext_subword_exorde-social-media-december-2024-week1** |
| **Confidence** | 67% (2/3 neighbours agree) |
| **Optimised metric** | **f1_weighted** |

---

## 3. Nearest Neighbour Analysis

The recommendation is derived by comparing the query dataset's linguistic profile against 17 historical datasets using a multi-stratum similarity measure.

### Top-3 Most Similar Historical Datasets

| Rank | Dataset | Similarity | Best Model | F1 (weighted) | Coverage |
|------|---------|-----------|-----------|--------------|----------|
| 1 | exorde-social-media-december-2024-week1 | 21.1% | **lid.176_exorde-social-media-december-2024-week1** | 0.9774 | Full |
| 2 | language-identification | 20.7% | **fasttext_subword_exorde-social-media-december-2024-week1** | 0.9965 | Full |
| 3 | OpenLID-v2 | 20.2% | **fasttext_subword_exorde-social-media-december-2024-week1** | 0.9304 | Full |

### Similarity Stratum Distances (Query vs. Nearest Neighbour)

| Stratum | Distance |
|---------|---------|
| Typological flags (script, tonality, family) | 0.3529 |
| Morphological richness | 48.6295 |
| Information-theoretic profile | 61.8441 |
| Cross-level cohesion | 89.3375 |
| Lexical diversity | 235.8656 |
| Structural / syntactic structure | 351.7579 |

---

## 4. Full Model Rankings

All models ranked by IDW-weighted **f1_weighted** score (coverage-penalised). Models marked **[full coverage]** support all 20 query languages.

| Rank | Model | Score | Coverage |
|------|-------|-------|----------|
| 1 | **fasttext_subword_exorde-social-media-december-2024-week1** ← **recommended** | 0.9651 | Full |
| 2 | **tfidf_lr_char_ngram_3_5_exorde-social-media-december-2024-week1** | 0.9352 | Full |
| 3 | **fasttext_subword_wikipedia** | 0.9290 | Full |
| 4 | **bow_maxabs_lr_char_ngram_3_5_exorde-social-media-december-2024-week1** | 0.9250 | Full |
| 5 | **bow_char_ngram_3_5_exorde-social-media-december-2024-week1** | 0.9238 | Full |
| 6 | **tfidf_char_ngram_3_5_exorde-social-media-december-2024-week1** | 0.9226 | Full |
| 7 | **fasttext_word_exorde-social-media-december-2024-week1** | 0.8588 | Full |
| 8 | **fasttext_subword_OpenLID-v2** | 0.8496 | avg gap: 1.0 langs |
| 9 | **tfidf_lr_char_ngram_3_5_wikipedia** | 0.8431 | Full |
| 10 | **bow_maxabs_lr_char_ngram_3_5_OpenLID-v2** | 0.8393 | avg gap: 1.0 langs |
| 11 | **tfidf_lr_char_ngram_3_5_OpenLID-v2** | 0.8381 | avg gap: 1.0 langs |
| 12 | **bow_char_ngram_3_5_wikipedia** | 0.8365 | Full |
| 13 | **tfidf_char_ngram_3_5_wikipedia** | 0.8360 | Full |
| 14 | **bow_char_ngram_3_5_flores_plus** | 0.8347 | avg gap: 1.0 langs |
| 15 | **xlm_v_base_language_id** | 0.8306 | avg gap: 2.3 langs |
| 16 | **tfidf_char_ngram_3_5_flores_plus** | 0.8305 | avg gap: 1.0 langs |
| 17 | **tfidf_char_ngram_3_5_OpenLID-v2** | 0.8271 | avg gap: 1.0 langs |
| 18 | **bow_char_ngram_3_5_OpenLID-v2** | 0.8267 | avg gap: 1.0 langs |
| 19 | **fasttext_word_OpenLID-v2** | 0.8224 | avg gap: 1.0 langs |
| 20 | **bow_maxabs_lr_char_ngram_3_5_wikipedia** | 0.8193 | Full |
| 21 | **tfidf_lr_char_ngram_3_5_flores_plus** | 0.8175 | avg gap: 1.0 langs |
| 22 | **fasttext_subword_flores_plus** | 0.7964 | avg gap: 1.0 langs |
| 23 | **fasttext_word_wikipedia** | 0.7917 | Full |
| 24 | **bow_maxabs_lr_char_ngram_3_5_flores_plus** | 0.7744 | avg gap: 1.0 langs |
| 25 | **fasttext_word_flores_plus** | 0.7183 | avg gap: 1.0 langs |
| 26 | **fasttext_subword_massive** | 0.6416 | avg gap: 4.0 langs |
| 27 | **tfidf_lr_char_ngram_3_5_massive** | 0.6195 | avg gap: 4.0 langs |
| 28 | **bow_maxabs_lr_char_ngram_3_5_massive** | 0.6081 | avg gap: 4.0 langs |
| 29 | **tfidf_char_ngram_3_5_massive** | 0.6003 | avg gap: 4.0 langs |
| 30 | **bow_char_ngram_3_5_massive** | 0.5999 | avg gap: 4.0 langs |
| 31 | **fasttext_subword_multilingual_cc_news** | 0.5761 | avg gap: 3.0 langs |
| 32 | **fasttext_word_massive** | 0.5473 | avg gap: 4.0 langs |
| 33 | **tfidf_char_ngram_3_5_multilingual_cc_news** | 0.5303 | avg gap: 3.0 langs |
| 34 | **bow_char_ngram_3_5_multilingual_cc_news** | 0.5303 | avg gap: 3.0 langs |
| 35 | **tfidf_lr_char_ngram_3_5_multilingual_cc_news** | 0.5194 | avg gap: 3.0 langs |
| 36 | **fasttext_word_multilingual_cc_news** | 0.5040 | avg gap: 3.0 langs |
| 37 | **bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news** | 0.4941 | avg gap: 3.0 langs |
| 38 | **bow_char_ngram_3_5_language-identification** | 0.4549 | avg gap: 6.0 langs |
| 39 | **tfidf_char_ngram_3_5_language-identification** | 0.4549 | avg gap: 6.0 langs |
| 40 | **tfidf_lr_char_ngram_3_5_language-identification** | 0.4544 | avg gap: 6.0 langs |
| 41 | **fasttext_subword_language-identification** | 0.4535 | avg gap: 6.0 langs |
| 42 | **bow_maxabs_lr_char_ngram_3_5_language-identification** | 0.4421 | avg gap: 6.0 langs |
| 43 | **bow_char_ngram_3_5_multi_eurlex** | 0.4378 | avg gap: 5.0 langs |
| 44 | **tfidf_char_ngram_3_5_multi_eurlex** | 0.4370 | avg gap: 5.0 langs |
| 45 | **fasttext_word_language-identification** | 0.3994 | avg gap: 6.0 langs |
| 46 | **bow_maxabs_lr_char_ngram_3_5_multi_eurlex** | 0.3664 | avg gap: 5.0 langs |
| 47 | **fasttext_word_europarl** | 0.3606 | avg gap: 7.0 langs |
| 48 | **fasttext_subword_multi_eurlex** | 0.3555 | avg gap: 5.0 langs |
| 49 | **tfidf_lr_char_ngram_3_5_europarl** | 0.3549 | avg gap: 7.0 langs |
| 50 | **bow_maxabs_lr_char_ngram_3_5_europarl** | 0.3534 | avg gap: 7.0 langs |
| 51 | **bow_char_ngram_3_5_europarl** | 0.3428 | avg gap: 7.0 langs |
| 52 | **tfidf_char_ngram_3_5_europarl** | 0.3428 | avg gap: 7.0 langs |
| 53 | **fasttext_subword_europarl** | 0.3423 | avg gap: 7.0 langs |
| 54 | **lid.176_exorde-social-media-december-2024-week1** | 0.3277 | Full |
| 55 | **tfidf_lr_char_ngram_3_5_multi_eurlex** | 0.3240 | avg gap: 5.0 langs |
| 56 | **fasttext_subword_mmarco** | 0.3143 | avg gap: 8.0 langs |
| 57 | **bow_maxabs_lr_char_ngram_3_5_stsb_multi_mt** | 0.3094 | avg gap: 8.0 langs |
| 58 | **tfidf_lr_char_ngram_3_5_stsb_multi_mt** | 0.3091 | avg gap: 8.0 langs |
| 59 | **tfidf_lr_char_ngram_3_5_mmarco** | 0.3091 | avg gap: 8.0 langs |
| 60 | **cld3_exorde-social-media-december-2024-week1** | 0.3067 | Full |
| 61 | **fasttext_subword_stsb_multi_mt** | 0.3052 | avg gap: 8.0 langs |
| 62 | **bow_maxabs_lr_char_ngram_3_5_mmarco** | 0.3049 | avg gap: 8.0 langs |
| 63 | **fasttext_word_stsb_multi_mt** | 0.3049 | avg gap: 8.0 langs |
| 64 | **cld3_OpenLID-v2** | 0.2939 | avg gap: 0.3 langs |
| 65 | **bow_char_ngram_3_5_mmarco** | 0.2896 | avg gap: 8.0 langs |
| 66 | **tfidf_char_ngram_3_5_mmarco** | 0.2895 | avg gap: 8.0 langs |
| 67 | **fasttext_word_mmarco** | 0.2866 | avg gap: 8.0 langs |
| 68 | **lid.176_OpenLID-v2** | 0.2822 | avg gap: 0.3 langs |
| 69 | **fasttext_word_multi_eurlex** | 0.2801 | avg gap: 5.0 langs |
| 70 | **tfidf_char_ngram_3_5_stsb_multi_mt** | 0.2791 | avg gap: 8.0 langs |
| 71 | **bow_char_ngram_3_5_stsb_multi_mt** | 0.2789 | avg gap: 8.0 langs |
| 72 | **lid.176_language-identification** | 0.2213 | avg gap: 2.0 langs |
| 73 | **tfidf_lr_char_ngram_3_5_multilingual_toxicity_dataset** | 0.2208 | avg gap: 9.0 langs |
| 74 | **cld3_language-identification** | 0.2188 | avg gap: 2.0 langs |
| 75 | **fasttext_subword_multilingual_toxicity_dataset** | 0.2155 | avg gap: 9.0 langs |
| 76 | **bow_maxabs_lr_char_ngram_3_5_multilingual_toxicity_dataset** | 0.2137 | avg gap: 9.0 langs |
| 77 | **tfidf_char_ngram_3_5_multilingual_toxicity_dataset** | 0.2068 | avg gap: 9.0 langs |
| 78 | **bow_char_ngram_3_5_multilingual_toxicity_dataset** | 0.2065 | avg gap: 9.0 langs |
| 79 | **fasttext_word_multilingual_toxicity_dataset** | 0.1797 | avg gap: 9.0 langs |
| 80 | **fasttext_subword_xlsum** | 0.1572 | avg gap: 10.0 langs |
| 81 | **tfidf_lr_char_ngram_3_5_xlsum** | 0.1464 | avg gap: 10.0 langs |
| 82 | **tfidf_char_ngram_3_5_xlsum** | 0.1435 | avg gap: 10.0 langs |
| 83 | **bow_char_ngram_3_5_xlsum** | 0.1412 | avg gap: 10.0 langs |
| 84 | **bow_maxabs_lr_char_ngram_3_5_xlsum** | 0.1410 | avg gap: 10.0 langs |
| 85 | **fasttext_word_xlsum** | 0.1394 | avg gap: 10.0 langs |
| 86 | **bow_maxabs_lr_char_ngram_3_5_xnli** | 0.1264 | avg gap: 11.0 langs |
| 87 | **fasttext_subword_xnli** | 0.1259 | avg gap: 11.0 langs |
| 88 | **tfidf_lr_char_ngram_3_5_xnli** | 0.1252 | avg gap: 11.0 langs |
| 89 | **fasttext_word_xnli** | 0.1247 | avg gap: 11.0 langs |
| 90 | **tfidf_char_ngram_3_5_xnli** | 0.1057 | avg gap: 11.0 langs |
| 91 | **bow_char_ngram_3_5_xnli** | 0.1056 | avg gap: 11.0 langs |
| 92 | **fasttext_word_tweet_sentiment_multilingual** | 0.0983 | avg gap: 12.0 langs |
| 93 | **bow_maxabs_lr_char_ngram_3_5_tweet_sentiment_multilingual** | 0.0959 | avg gap: 12.0 langs |
| 94 | **fasttext_subword_tweet_sentiment_multilingual** | 0.0956 | avg gap: 12.0 langs |
| 95 | **tfidf_lr_char_ngram_3_5_tweet_sentiment_multilingual** | 0.0938 | avg gap: 12.0 langs |
| 96 | **tfidf_lr_char_ngram_3_5_amazon_reviews_multi** | 0.0937 | avg gap: 12.0 langs |
| 97 | **fasttext_subword_amazon_reviews_multi** | 0.0920 | avg gap: 12.0 langs |
| 98 | **bow_char_ngram_3_5_tweet_sentiment_multilingual** | 0.0916 | avg gap: 12.0 langs |
| 99 | **bow_maxabs_lr_char_ngram_3_5_amazon_reviews_multi** | 0.0914 | avg gap: 12.0 langs |
| 100 | **tfidf_char_ngram_3_5_tweet_sentiment_multilingual** | 0.0914 | avg gap: 12.0 langs |
| 101 | **tfidf_char_ngram_3_5_amazon_reviews_multi** | 0.0883 | avg gap: 12.0 langs |
| 102 | **bow_char_ngram_3_5_amazon_reviews_multi** | 0.0882 | avg gap: 12.0 langs |
| 103 | **fasttext_word_amazon_reviews_multi** | 0.0786 | avg gap: 12.0 langs |
| 104 | **bow_char_ngram_3_5_tydiqa** | 0.0309 | avg gap: 14.0 langs |
| 105 | **tfidf_char_ngram_3_5_tydiqa** | 0.0302 | avg gap: 14.0 langs |
| 106 | **fasttext_subword_tydiqa** | 0.0288 | avg gap: 14.0 langs |
| 107 | **tfidf_lr_char_ngram_3_5_tydiqa** | 0.0269 | avg gap: 14.0 langs |
| 108 | **bow_maxabs_lr_char_ngram_3_5_tydiqa** | 0.0248 | avg gap: 14.0 langs |
| 109 | **fasttext_word_tydiqa** | 0.0246 | avg gap: 14.0 langs |

---

## 5. Recommendation Validation Report

**Generated:** 2026-05-14 11:48:53  
**Priority metric:** **f1_weighted**  
**Datasets evaluated:** 17

### Aggregate Metrics

| Metric | Value |
|--------|-------|
| Recommendation accuracy | **17.6%** (3/17 correct) |
| Mean Δ **f1_weighted** | +0.0078 |
| Std Δ **f1_weighted** | 0.0125 |
| Median Δ **f1_weighted** | +0.0022 |
| Min Δ **f1_weighted** | +0.0000 |
| Max Δ **f1_weighted** | +0.0489 |
| |

> **Note:** Although exact-match accuracy is 17.6%, the mean performance gap is only +0.0078 F1, indicating that the recommended model remains near-optimal even when it does not match the strict ground truth.

### Per-Dataset Results

| Dataset | Recommended | Ground Truth | Correct | GT Score | Rec Score | Δ **f1_weighted** | Confidence |
|---------|-------------|-------------|:-------:|----------|-----------|-----------------|-----------|
| OpenLID-v2 | **fasttext_subword_OpenLID-v2** | **fasttext_subword_OpenLID-v2** | ✓ | 0.9940 | 0.9940 | +0.0000 | 0.67 |
| amazon_reviews_multi | **fasttext_subword_exorde-social-media-december-2024-week1** | **fasttext_subword_amazon_reviews_multi** | ✗ | 0.9998 | 0.9990 | +0.0009 | 0.00 |
| europarl | **xlm_v_base_language_id** | **bow_char_ngram_3_5_europarl** | ✗ | 0.9995 | 0.9984 | +0.0011 | 0.00 |
| exorde-social-media-december-2024-week1 | **fasttext_subword_exorde-social-media-december-2024-week1** | **lid.176_exorde-social-media-december-2024-week1** | ✗ | 0.9779 | 0.9688 | +0.0091 | 0.00 |
| flores_plus | **xlm_v_base_language_id** | **xlm_v_base_language_id** | ✓ | 0.9952 | 0.9952 | +0.0000 | 0.00 |
| language-identification | **fasttext_subword_exorde-social-media-december-2024-week1** | **fasttext_subword_language-identification** | ✗ | 0.9979 | 0.9958 | +0.0021 | 0.00 |
| massive | **xlm_v_base_language_id** | **fasttext_subword_massive** | ✗ | 0.9974 | 0.9782 | +0.0192 | 0.00 |
| mmarco | **xlm_v_base_language_id** | **fasttext_subword_mmarco** | ✗ | 0.9975 | 0.9715 | +0.0259 | 0.00 |
| multi_eurlex | **fasttext_subword_wikipedia** | **bow_maxabs_lr_char_ngram_3_5_multi_eurlex** | ✗ | 0.9998 | 0.9959 | +0.0039 | 0.00 |
| multilingual_cc_news | **fasttext_subword_exorde-social-media-december-2024-week1** | **fasttext_subword_multilingual_cc_news** | ✗ | 0.9971 | 0.9860 | +0.0112 | 0.00 |
| multilingual_toxicity_dataset | **fasttext_subword_exorde-social-media-december-2024-week1** | **fasttext_subword_multilingual_toxicity_dataset** | ✗ | 0.9937 | 0.9899 | +0.0037 | 0.00 |
| stsb_multi_mt | **xlm_v_base_language_id** | **tfidf_lr_char_ngram_3_5_stsb_multi_mt** | ✗ | 0.9942 | 0.9912 | +0.0029 | 0.00 |
| tweet_sentiment_multilingual | **xlm_v_base_language_id** | **bow_char_ngram_3_5_tweet_sentiment_multilingual** | ✗ | 0.9981 | 0.9492 | +0.0489 | 0.00 |
| tydiqa | **xlm_v_base_language_id** | **fasttext_subword_tydiqa** | ✗ | 0.9999 | 0.9986 | +0.0013 | 0.00 |
| wikipedia | **fasttext_subword_wikipedia** | **fasttext_subword_wikipedia** | ✓ | 0.9964 | 0.9964 | +0.0000 | 0.33 |
| xlsum | **fasttext_subword_exorde-social-media-december-2024-week1** | **fasttext_subword_xlsum** | ✗ | 0.9989 | 0.9986 | +0.0002 | 0.00 |
| xnli | **fasttext_subword_exorde-social-media-december-2024-week1** | **fasttext_subword_xnli** | ✗ | 0.9996 | 0.9975 | +0.0022 | 0.00 |
