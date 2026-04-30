# Math Trace Report

Step-by-step verification of the recommendation math for each dataset.

---

## Dataset: `OpenLID-v2`

**Query languages:** `['ca', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'hr', 'it', 'ja', 'ko', 'lt', 'mk', 'nl', 'pl', 'pt', 'ro', 'ru', 'sl', 'sv', 'uk', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.626130` |
| S5_cross_level | `63.968517` |
| S1_morphological | `45.583936` |
| S2_lexical_diversity | `81.416015` |
| S3_structural | `98.157916` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.626130 | 10.626130 |
| S5_cross_level | 1.0 | 63.968517 | 63.968517 |
| S1_morphological | 1.0 | 45.583936 | 45.583936 |
| S2_lexical_diversity | 1.0 | 81.416015 | 81.416015 |
| S3_structural | 1.0 | 98.157916 | 98.157916 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 50.027380** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.776147` |
| S5_cross_level | `37.000006` |
| S1_morphological | `29.237243` |
| S2_lexical_diversity | `74.828901` |
| S3_structural | `68.794066` |
| cat (Hamming) | `0.176471` (3/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.776147 | 12.776147 |
| S5_cross_level | 1.0 | 37.000006 | 37.000006 |
| S1_morphological | 1.0 | 29.237243 | 29.237243 |
| S2_lexical_diversity | 1.0 | 74.828901 | 74.828901 |
| S3_structural | 1.0 | 68.794066 | 68.794066 |
| cat | 1.0 | 0.176471 | 0.176471 |
| **Total** | Σw = 6.0000 | | **D = 37.135472** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.158411` |
| S5_cross_level | `50.428969` |
| S1_morphological | `20.832448` |
| S2_lexical_diversity | `73.951519` |
| S3_structural | `63.979553` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.158411 | 11.158411 |
| S5_cross_level | 1.0 | 50.428969 | 50.428969 |
| S1_morphological | 1.0 | 20.832448 | 20.832448 |
| S2_lexical_diversity | 1.0 | 73.951519 | 73.951519 |
| S3_structural | 1.0 | 63.979553 | 63.979553 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 36.774170** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `13.367893` |
| S5_cross_level | `53.450892` |
| S1_morphological | `34.986544` |
| S2_lexical_diversity | `78.408563` |
| S3_structural | `68.459609` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 13.367893 | 13.367893 |
| S5_cross_level | 1.0 | 53.450892 | 53.450892 |
| S1_morphological | 1.0 | 34.986544 | 34.986544 |
| S2_lexical_diversity | 1.0 | 78.408563 | 78.408563 |
| S3_structural | 1.0 | 68.459609 | 68.459609 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 41.504407** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.130324` |
| S5_cross_level | `38.796776` |
| S1_morphological | `33.846786` |
| S2_lexical_diversity | `76.668269` |
| S3_structural | `71.861703` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.130324 | 14.130324 |
| S5_cross_level | 1.0 | 38.796776 | 38.796776 |
| S1_morphological | 1.0 | 33.846786 | 33.846786 |
| S2_lexical_diversity | 1.0 | 76.668269 | 76.668269 |
| S3_structural | 1.0 | 71.861703 | 71.861703 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 39.285937** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `200.178423` |
| S5_cross_level | `1230.362911` |
| S1_morphological | `317.918532` |
| S2_lexical_diversity | `826.739258` |
| S3_structural | `1250.853790` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 200.178423 | 200.178423 |
| S5_cross_level | 1.0 | 1230.362911 | 1230.362911 |
| S1_morphological | 1.0 | 317.918532 | 317.918532 |
| S2_lexical_diversity | 1.0 | 826.739258 | 826.739258 |
| S3_structural | 1.0 | 1250.853790 | 1250.853790 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 637.695094** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `13.573738` |
| S5_cross_level | `57.661945` |
| S1_morphological | `54.875171` |
| S2_lexical_diversity | `86.057544` |
| S3_structural | `90.082850` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 13.573738 | 13.573738 |
| S5_cross_level | 1.0 | 57.661945 | 57.661945 |
| S1_morphological | 1.0 | 54.875171 | 54.875171 |
| S2_lexical_diversity | 1.0 | 86.057544 | 86.057544 |
| S3_structural | 1.0 | 90.082850 | 90.082850 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 50.453639** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `13.775553` |
| S5_cross_level | `47.913421` |
| S1_morphological | `36.244586` |
| S2_lexical_diversity | `77.948316` |
| S3_structural | `79.154417` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 13.775553 | 13.775553 |
| S5_cross_level | 1.0 | 47.913421 | 47.913421 |
| S1_morphological | 1.0 | 36.244586 | 36.244586 |
| S2_lexical_diversity | 1.0 | 77.948316 | 77.948316 |
| S3_structural | 1.0 | 79.154417 | 79.154417 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 42.584480** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `73.583548` |
| S5_cross_level | `407.401453` |
| S1_morphological | `147.506513` |
| S2_lexical_diversity | `316.406301` |
| S3_structural | `471.502688` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 73.583548 | 73.583548 |
| S5_cross_level | 1.0 | 407.401453 | 407.401453 |
| S1_morphological | 1.0 | 147.506513 | 147.506513 |
| S2_lexical_diversity | 1.0 | 316.406301 | 316.406301 |
| S3_structural | 1.0 | 471.502688 | 471.502688 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 236.086358** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `15.076069` |
| S5_cross_level | `58.896462` |
| S1_morphological | `41.513844` |
| S2_lexical_diversity | `88.542939` |
| S3_structural | `112.121491` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 15.076069 | 15.076069 |
| S5_cross_level | 1.0 | 58.896462 | 58.896462 |
| S1_morphological | 1.0 | 41.513844 | 41.513844 |
| S2_lexical_diversity | 1.0 | 88.542939 | 88.542939 |
| S3_structural | 1.0 | 112.121491 | 112.121491 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 52.799644** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.035922` |
| S5_cross_level | `62.283606` |
| S1_morphological | `52.165292` |
| S2_lexical_diversity | `82.414983` |
| S3_structural | `100.617743` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.035922 | 12.035922 |
| S5_cross_level | 1.0 | 62.283606 | 62.283606 |
| S1_morphological | 1.0 | 52.165292 | 52.165292 |
| S2_lexical_diversity | 1.0 | 82.414983 | 82.414983 |
| S3_structural | 1.0 | 100.617743 | 100.617743 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 51.703905** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `1.797545` |
| S5_cross_level | `45.785163` |
| S1_morphological | `22.043432` |
| S2_lexical_diversity | `12.120155` |
| S3_structural | `27.354582` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 1.797545 | 1.797545 |
| S5_cross_level | 1.0 | 45.785163 | 45.785163 |
| S1_morphological | 1.0 | 22.043432 | 22.043432 |
| S2_lexical_diversity | 1.0 | 12.120155 | 12.120155 |
| S3_structural | 1.0 | 27.354582 | 27.354582 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 18.232499** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.940555` |
| S5_cross_level | `56.439281` |
| S1_morphological | `29.381668` |
| S2_lexical_diversity | `74.899550` |
| S3_structural | `60.312732` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.940555 | 12.940555 |
| S5_cross_level | 1.0 | 56.439281 | 56.439281 |
| S1_morphological | 1.0 | 29.381668 | 29.381668 |
| S2_lexical_diversity | 1.0 | 74.899550 | 74.899550 |
| S3_structural | 1.0 | 60.312732 | 60.312732 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 39.064258** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.466938` |
| S5_cross_level | `59.835772` |
| S1_morphological | `46.008562` |
| S2_lexical_diversity | `81.557455` |
| S3_structural | `94.897350` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.466938 | 11.466938 |
| S5_cross_level | 1.0 | 59.835772 | 59.835772 |
| S1_morphological | 1.0 | 46.008562 | 46.008562 |
| S2_lexical_diversity | 1.0 | 81.557455 | 81.557455 |
| S3_structural | 1.0 | 94.897350 | 94.897350 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 49.068856** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.449722` |
| S5_cross_level | `52.251826` |
| S1_morphological | `37.556176` |
| S2_lexical_diversity | `71.278501` |
| S3_structural | `58.971971` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.449722 | 10.449722 |
| S5_cross_level | 1.0 | 52.251826 | 52.251826 |
| S1_morphological | 1.0 | 37.556176 | 37.556176 |
| S2_lexical_diversity | 1.0 | 71.278501 | 71.278501 |
| S3_structural | 1.0 | 58.971971 | 58.971971 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 38.437641** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.988275` |
| S5_cross_level | `50.061919` |
| S1_morphological | `26.909693` |
| S2_lexical_diversity | `77.684105` |
| S3_structural | `83.036733` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.988275 | 12.988275 |
| S5_cross_level | 1.0 | 50.061919 | 50.061919 |
| S1_morphological | 1.0 | 26.909693 | 26.909693 |
| S2_lexical_diversity | 1.0 | 77.684105 | 77.684105 |
| S3_structural | 1.0 | 83.036733 | 83.036733 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 41.838944** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.203889` |
| S5_cross_level | `49.087198` |
| S1_morphological | `43.778147` |
| S2_lexical_diversity | `71.149604` |
| S3_structural | `70.590565` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.203889 | 10.203889 |
| S5_cross_level | 1.0 | 49.087198 | 49.087198 |
| S1_morphological | 1.0 | 43.778147 | 43.778147 |
| S2_lexical_diversity | 1.0 | 71.149604 | 71.149604 |
| S3_structural | 1.0 | 70.590565 | 70.590565 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 40.860391** |

### §§ 4–5 · Similarity % (max_D = `637.695094`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | OpenLID-v2 | `18.232499` | 97.1% | ← yes |
| 2 | flores_plus | `36.774170` | 94.2% | ← yes |
| 3 | massive | `37.135472` | 94.2% | ← yes |
| 4 | multilingual_cc_news | `38.437641` | 94.0% |  |
| 5 | stsb_multi_mt | `39.064258` | 93.9% |  |
| 6 | mmarco | `39.285937` | 93.8% |  |
| 7 | language-identification | `40.860391` | 93.6% |  |
| 8 | xlsum | `41.504407` | 93.5% |  |
| 9 | xnli | `41.838944` | 93.4% |  |
| 10 | tydiqa | `42.584480` | 93.3% |  |
| 11 | europarl | `49.068856` | 92.3% |  |
| 12 | multilingual_toxicity_dataset | `50.027380` | 92.2% |  |
| 13 | amazon_reviews_multi | `50.453639` | 92.1% |  |
| 14 | tweet_sentiment_multilingual | `51.703905` | 91.9% |  |
| 15 | multi_eurlex | `52.799644` | 91.7% |  |
| 16 | exorde-social-media-december-2024-week1 | `236.086358` | 63.0% |  |
| 17 | wikipedia | `637.695094` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `OpenLID-v2`** — inv_d = `0.054847`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.980663 | 1 | 0.9565 | 0.051448 |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.981227 | 1 | 0.9565 | 0.051478 |
| fasttext_subword_OpenLID-v2 | 0.993905 | 1 | 0.9565 | 0.052143 |
| fasttext_word_OpenLID-v2 | 0.947366 | 1 | 0.9565 | 0.049701 |
| lid.176_OpenLID-v2 | 0.901862 | 1 | 0.9565 | 0.047314 |
| cld3_OpenLID-v2 | 0.939038 | 1 | 0.9565 | 0.049264 |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.981563 | 1 | 0.9565 | 0.051495 |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.983798 | 1 | 0.9565 | 0.051612 |

**Neighbour: `flores_plus`** — inv_d = `0.027193`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_flores_plus | 0.981840 | 1 | 0.9565 | 0.025538 |
| tfidf_char_ngram_3_5_flores_plus | 0.983247 | 1 | 0.9565 | 0.025575 |
| fasttext_subword_flores_plus | 0.983486 | 1 | 0.9565 | 0.025581 |
| fasttext_word_flores_plus | 0.927359 | 1 | 0.9565 | 0.024121 |
| lid.176_flores_plus | 0.939262 | 1 | 0.9565 | 0.024431 |
| cld3_flores_plus | 0.979305 | 1 | 0.9565 | 0.025472 |
| bow_maxabs_lr_char_ngram_3_5_flores_plus | 0.981447 | 1 | 0.9565 | 0.025528 |
| tfidf_lr_char_ngram_3_5_flores_plus | 0.987288 | 1 | 0.9565 | 0.025680 |

**Neighbour: `massive`** — inv_d = `0.026928`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_massive | 0.990937 | 5 | 0.7826 | 0.020883 |
| tfidf_char_ngram_3_5_massive | 0.991145 | 5 | 0.7826 | 0.020888 |
| fasttext_subword_massive | 0.997546 | 5 | 0.7826 | 0.021023 |
| fasttext_word_massive | 0.934868 | 5 | 0.7826 | 0.019702 |
| lid.176_massive | 0.979587 | 5 | 0.7826 | 0.020644 |
| cld3_massive | 0.958160 | 5 | 0.7826 | 0.020193 |
| bow_maxabs_lr_char_ngram_3_5_massive | 0.986331 | 5 | 0.7826 | 0.020786 |
| tfidf_lr_char_ngram_3_5_massive | 0.990836 | 5 | 0.7826 | 0.020881 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.051448 | 0.054847 | **0.938025** |
| bow_char_ngram_3_5_flores_plus | 0.025538 | 0.027193 | **0.939151** |
| bow_char_ngram_3_5_massive | 0.020883 | 0.026928 | **0.775516** |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.051495 | 0.054847 | **0.938886** |
| bow_maxabs_lr_char_ngram_3_5_flores_plus | 0.025528 | 0.027193 | **0.938775** |
| bow_maxabs_lr_char_ngram_3_5_massive | 0.020786 | 0.026928 | **0.771911** |
| cld3_OpenLID-v2 | 0.049264 | 0.054847 | **0.898210** |
| cld3_flores_plus | 0.025472 | 0.027193 | **0.936727** |
| cld3_massive | 0.020193 | 0.026928 | **0.749864** |
| fasttext_subword_OpenLID-v2 | 0.052143 | 0.054847 | **0.950692** |
| fasttext_subword_flores_plus | 0.025581 | 0.027193 | **0.940726** |
| fasttext_subword_massive | 0.021023 | 0.026928 | **0.780688** |
| fasttext_word_OpenLID-v2 | 0.049701 | 0.054847 | **0.906176** |
| fasttext_word_flores_plus | 0.024121 | 0.027193 | **0.887039** |
| fasttext_word_massive | 0.019702 | 0.026928 | **0.731636** |
| lid.176_OpenLID-v2 | 0.047314 | 0.054847 | **0.862651** |
| lid.176_flores_plus | 0.024431 | 0.027193 | **0.898425** |
| lid.176_massive | 0.020644 | 0.026928 | **0.766633** |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.051478 | 0.054847 | **0.938565** |
| tfidf_char_ngram_3_5_flores_plus | 0.025575 | 0.027193 | **0.940497** |
| tfidf_char_ngram_3_5_massive | 0.020888 | 0.026928 | **0.775679** |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.051612 | 0.054847 | **0.941024** |
| tfidf_lr_char_ngram_3_5_flores_plus | 0.025680 | 0.027193 | **0.944362** |
| tfidf_lr_char_ngram_3_5_massive | 0.020881 | 0.026928 | **0.775437** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_OpenLID-v2`

---

## Dataset: `amazon_reviews_multi`

**Query languages:** `['de', 'en', 'es', 'fr', 'ja', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `6.379680` |
| S5_cross_level | `41.366615` |
| S1_morphological | `40.229002` |
| S2_lexical_diversity | `37.463674` |
| S3_structural | `57.940889` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 6.379680 | 6.379680 |
| S5_cross_level | 1.0 | 41.366615 | 41.366615 |
| S1_morphological | 1.0 | 40.229002 | 40.229002 |
| S2_lexical_diversity | 1.0 | 37.463674 | 37.463674 |
| S3_structural | 1.0 | 57.940889 | 57.940889 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 30.612330** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.528998` |
| S5_cross_level | `49.822840` |
| S1_morphological | `67.074463` |
| S2_lexical_diversity | `60.319280` |
| S3_structural | `87.713416` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.528998 | 16.528998 |
| S5_cross_level | 1.0 | 49.822840 | 49.822840 |
| S1_morphological | 1.0 | 67.074463 | 67.074463 |
| S2_lexical_diversity | 1.0 | 60.319280 | 60.319280 |
| S3_structural | 1.0 | 87.713416 | 87.713416 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 46.988264** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.109488` |
| S5_cross_level | `32.237768` |
| S1_morphological | `55.685082` |
| S2_lexical_diversity | `42.097692` |
| S3_structural | `72.461947` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.109488 | 9.109488 |
| S5_cross_level | 1.0 | 32.237768 | 32.237768 |
| S1_morphological | 1.0 | 55.685082 | 55.685082 |
| S2_lexical_diversity | 1.0 | 42.097692 | 42.097692 |
| S3_structural | 1.0 | 72.461947 | 72.461947 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 35.373173** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `5.805624` |
| S5_cross_level | `16.724102` |
| S1_morphological | `39.995492` |
| S2_lexical_diversity | `39.740049` |
| S3_structural | `75.257420` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 5.805624 | 5.805624 |
| S5_cross_level | 1.0 | 16.724102 | 16.724102 |
| S1_morphological | 1.0 | 39.995492 | 39.995492 |
| S2_lexical_diversity | 1.0 | 39.740049 | 39.740049 |
| S3_structural | 1.0 | 75.257420 | 75.257420 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 29.655742** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.372408` |
| S5_cross_level | `50.889786` |
| S1_morphological | `69.577966` |
| S2_lexical_diversity | `57.642578` |
| S3_structural | `90.589575` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.372408 | 16.372408 |
| S5_cross_level | 1.0 | 50.889786 | 50.889786 |
| S1_morphological | 1.0 | 69.577966 | 69.577966 |
| S2_lexical_diversity | 1.0 | 57.642578 | 57.642578 |
| S3_structural | 1.0 | 90.589575 | 90.589575 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 47.561072** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `204.711641` |
| S5_cross_level | `1239.305806` |
| S1_morphological | `315.593256` |
| S2_lexical_diversity | `829.875704` |
| S3_structural | `1244.349686` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 204.711641 | 204.711641 |
| S5_cross_level | 1.0 | 1239.305806 | 1239.305806 |
| S1_morphological | 1.0 | 315.593256 | 315.593256 |
| S2_lexical_diversity | 1.0 | 829.875704 | 829.875704 |
| S3_structural | 1.0 | 1244.349686 | 1244.349686 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 639.051114** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `1.247258` |
| S5_cross_level | `4.306339` |
| S1_morphological | `10.975912` |
| S2_lexical_diversity | `7.299925` |
| S3_structural | `12.970165` |
| cat (Hamming) | `0.000000` (0/17 flags differ) |

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 1.247258 | 1.247258 |
| S5_cross_level | 1.0 | 4.306339 | 4.306339 |
| S1_morphological | 1.0 | 10.975912 | 10.975912 |
| S2_lexical_diversity | 1.0 | 7.299925 | 7.299925 |
| S3_structural | 1.0 | 12.970165 | 12.970165 |
| cat | 1.0 | 0.000000 | 0.000000 |
| **Total** | Σw = 6.0000 | | **D = 6.133267** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `17.064607` |
| S5_cross_level | `59.322324` |
| S1_morphological | `71.631147` |
| S2_lexical_diversity | `60.736460` |
| S3_structural | `96.506085` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 17.064607 | 17.064607 |
| S5_cross_level | 1.0 | 59.322324 | 59.322324 |
| S1_morphological | 1.0 | 71.631147 | 71.631147 |
| S2_lexical_diversity | 1.0 | 60.736460 | 60.736460 |
| S3_structural | 1.0 | 96.506085 | 96.506085 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 50.965006** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `78.185891` |
| S5_cross_level | `414.116744` |
| S1_morphological | `138.924073` |
| S2_lexical_diversity | `314.020609` |
| S3_structural | `461.461991` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 78.185891 | 78.185891 |
| S5_cross_level | 1.0 | 414.116744 | 414.116744 |
| S1_morphological | 1.0 | 138.924073 | 138.924073 |
| S2_lexical_diversity | 1.0 | 314.020609 | 314.020609 |
| S3_structural | 1.0 | 461.461991 | 461.461991 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 234.529983** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.522105` |
| S5_cross_level | `30.146302` |
| S1_morphological | `74.752991` |
| S2_lexical_diversity | `83.548179` |
| S3_structural | `164.509231` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.522105 | 10.522105 |
| S5_cross_level | 1.0 | 30.146302 | 30.146302 |
| S1_morphological | 1.0 | 74.752991 | 74.752991 |
| S2_lexical_diversity | 1.0 | 83.548179 | 83.548179 |
| S3_structural | 1.0 | 164.509231 | 164.509231 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 60.658233** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.393468` |
| S5_cross_level | `23.615320` |
| S1_morphological | `46.588709` |
| S2_lexical_diversity | `46.598949` |
| S3_structural | `96.006980` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.393468 | 10.393468 |
| S5_cross_level | 1.0 | 23.615320 | 23.615320 |
| S1_morphological | 1.0 | 46.588709 | 46.588709 |
| S2_lexical_diversity | 1.0 | 46.598949 | 46.598949 |
| S3_structural | 1.0 | 96.006980 | 96.006980 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 37.279002** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.748817` |
| S5_cross_level | `44.296601` |
| S1_morphological | `48.887061` |
| S2_lexical_diversity | `83.672452` |
| S3_structural | `89.794454` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.748817 | 12.748817 |
| S5_cross_level | 1.0 | 44.296601 | 44.296601 |
| S1_morphological | 1.0 | 48.887061 | 48.887061 |
| S2_lexical_diversity | 1.0 | 83.672452 | 83.672452 |
| S3_structural | 1.0 | 89.794454 | 89.794454 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 46.674407** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.070859` |
| S5_cross_level | `33.896789` |
| S1_morphological | `65.033598` |
| S2_lexical_diversity | `51.381818` |
| S3_structural | `88.818502` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_cyrillic', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.070859 | 12.070859 |
| S5_cross_level | 1.0 | 33.896789 | 33.896789 |
| S1_morphological | 1.0 | 65.033598 | 65.033598 |
| S2_lexical_diversity | 1.0 | 51.381818 | 51.381818 |
| S3_structural | 1.0 | 88.818502 | 88.818502 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 41.915947** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `7.101130` |
| S5_cross_level | `31.664140` |
| S1_morphological | `60.918493` |
| S2_lexical_diversity | `46.212448` |
| S3_structural | `90.759800` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 7.101130 | 7.101130 |
| S5_cross_level | 1.0 | 31.664140 | 31.664140 |
| S1_morphological | 1.0 | 60.918493 | 60.918493 |
| S2_lexical_diversity | 1.0 | 46.212448 | 46.212448 |
| S3_structural | 1.0 | 90.759800 | 90.759800 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 39.521100** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `5.509564` |
| S5_cross_level | `28.650627` |
| S1_morphological | `41.997987` |
| S2_lexical_diversity | `43.560042` |
| S3_structural | `85.949182` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 5.509564 | 5.509564 |
| S5_cross_level | 1.0 | 28.650627 | 28.650627 |
| S1_morphological | 1.0 | 41.997987 | 41.997987 |
| S2_lexical_diversity | 1.0 | 43.560042 | 43.560042 |
| S3_structural | 1.0 | 85.949182 | 85.949182 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 34.356332** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `7.333350` |
| S5_cross_level | `27.791766` |
| S1_morphological | `40.537427` |
| S2_lexical_diversity | `36.412486` |
| S3_structural | `68.951843` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 7.333350 | 7.333350 |
| S5_cross_level | 1.0 | 27.791766 | 27.791766 |
| S1_morphological | 1.0 | 40.537427 | 40.537427 |
| S2_lexical_diversity | 1.0 | 36.412486 | 36.412486 |
| S3_structural | 1.0 | 68.951843 | 68.951843 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 30.239773** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `6.096230` |
| S5_cross_level | `17.143858` |
| S1_morphological | `25.166490` |
| S2_lexical_diversity | `28.698947` |
| S3_structural | `41.586697` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 6.096230 | 6.096230 |
| S5_cross_level | 1.0 | 17.143858 | 17.143858 |
| S1_morphological | 1.0 | 25.166490 | 25.166490 |
| S2_lexical_diversity | 1.0 | 28.698947 | 28.698947 |
| S3_structural | 1.0 | 41.586697 | 41.586697 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 19.840861** |

### §§ 4–5 · Similarity % (max_D = `639.051114`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | amazon_reviews_multi | `6.133267` | 99.0% | ← yes |
| 2 | language-identification | `19.840861` | 96.9% | ← yes |
| 3 | xlsum | `29.655742` | 95.4% | ← yes |
| 4 | xnli | `30.239773` | 95.3% |  |
| 5 | multilingual_toxicity_dataset | `30.612330` | 95.2% |  |
| 6 | multilingual_cc_news | `34.356332` | 94.6% |  |
| 7 | flores_plus | `35.373173` | 94.5% |  |
| 8 | tweet_sentiment_multilingual | `37.279002` | 94.2% |  |
| 9 | europarl | `39.521100` | 93.8% |  |
| 10 | stsb_multi_mt | `41.915947` | 93.4% |  |
| 11 | OpenLID-v2 | `46.674407` | 92.7% |  |
| 12 | massive | `46.988264` | 92.6% |  |
| 13 | mmarco | `47.561072` | 92.6% |  |
| 14 | tydiqa | `50.965006` | 92.0% |  |
| 15 | multi_eurlex | `60.658233` | 90.5% |  |
| 16 | exorde-social-media-december-2024-week1 | `234.529983` | 63.3% |  |
| 17 | wikipedia | `639.051114` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `amazon_reviews_multi`** — inv_d = `0.163045`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_amazon_reviews_multi | 0.997985 | 0 | 1.0000 | 0.162717 |
| tfidf_char_ngram_3_5_amazon_reviews_multi | 0.998090 | 0 | 1.0000 | 0.162734 |
| fasttext_subword_amazon_reviews_multi | 0.999846 | 0 | 1.0000 | 0.163020 |
| fasttext_word_amazon_reviews_multi | 0.797855 | 0 | 1.0000 | 0.130086 |
| lid.176_amazon_reviews_multi | 0.999025 | 0 | 1.0000 | 0.162886 |
| cld3_amazon_reviews_multi | 0.995041 | 0 | 1.0000 | 0.162237 |
| bow_maxabs_lr_char_ngram_3_5_amazon_reviews_multi | 0.996443 | 0 | 1.0000 | 0.162465 |
| tfidf_lr_char_ngram_3_5_amazon_reviews_multi | 0.999060 | 0 | 1.0000 | 0.162892 |

**Neighbour: `language-identification`** — inv_d = `0.050401`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_language-identification | 0.997934 | 0 | 1.0000 | 0.050297 |
| tfidf_char_ngram_3_5_language-identification | 0.998033 | 0 | 1.0000 | 0.050302 |
| fasttext_subword_language-identification | 0.996164 | 0 | 1.0000 | 0.050208 |
| fasttext_word_language-identification | 0.870988 | 0 | 1.0000 | 0.043899 |
| lid.176_language-identification | 0.995624 | 0 | 1.0000 | 0.050180 |
| cld3_language-identification | 0.984446 | 0 | 1.0000 | 0.049617 |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.984950 | 0 | 1.0000 | 0.049643 |
| tfidf_lr_char_ngram_3_5_language-identification | 0.995288 | 0 | 1.0000 | 0.050164 |

**Neighbour: `xlsum`** — inv_d = `0.033720`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_xlsum | 0.981335 | 1 | 0.8333 | 0.027576 |
| tfidf_char_ngram_3_5_xlsum | 0.981388 | 1 | 0.8333 | 0.027577 |
| fasttext_subword_xlsum | 0.998764 | 1 | 0.8333 | 0.028066 |
| fasttext_word_xlsum | 0.974218 | 1 | 0.8333 | 0.027376 |
| lid.176_xlsum | 0.998587 | 1 | 0.8333 | 0.028061 |
| cld3_xlsum | 0.994289 | 1 | 0.8333 | 0.027940 |
| bow_maxabs_lr_char_ngram_3_5_xlsum | 0.979869 | 1 | 0.8333 | 0.027535 |
| tfidf_lr_char_ngram_3_5_xlsum | 0.981645 | 1 | 0.8333 | 0.027584 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_amazon_reviews_multi | 0.162717 | 0.163045 | **0.997985** |
| bow_char_ngram_3_5_language-identification | 0.050297 | 0.050401 | **0.997934** |
| bow_char_ngram_3_5_xlsum | 0.027576 | 0.033720 | **0.817779** |
| bow_maxabs_lr_char_ngram_3_5_amazon_reviews_multi | 0.162465 | 0.163045 | **0.996443** |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.049643 | 0.050401 | **0.984950** |
| bow_maxabs_lr_char_ngram_3_5_xlsum | 0.027535 | 0.033720 | **0.816558** |
| cld3_amazon_reviews_multi | 0.162237 | 0.163045 | **0.995041** |
| cld3_language-identification | 0.049617 | 0.050401 | **0.984446** |
| cld3_xlsum | 0.027940 | 0.033720 | **0.828574** |
| fasttext_subword_amazon_reviews_multi | 0.163020 | 0.163045 | **0.999846** |
| fasttext_subword_language-identification | 0.050208 | 0.050401 | **0.996164** |
| fasttext_subword_xlsum | 0.028066 | 0.033720 | **0.832303** |
| fasttext_word_amazon_reviews_multi | 0.130086 | 0.163045 | **0.797855** |
| fasttext_word_language-identification | 0.043899 | 0.050401 | **0.870988** |
| fasttext_word_xlsum | 0.027376 | 0.033720 | **0.811848** |
| lid.176_amazon_reviews_multi | 0.162886 | 0.163045 | **0.999025** |
| lid.176_language-identification | 0.050180 | 0.050401 | **0.995624** |
| lid.176_xlsum | 0.028061 | 0.033720 | **0.832156** |
| tfidf_char_ngram_3_5_amazon_reviews_multi | 0.162734 | 0.163045 | **0.998090** |
| tfidf_char_ngram_3_5_language-identification | 0.050302 | 0.050401 | **0.998033** |
| tfidf_char_ngram_3_5_xlsum | 0.027577 | 0.033720 | **0.817823** |
| tfidf_lr_char_ngram_3_5_amazon_reviews_multi | 0.162892 | 0.163045 | **0.999060** |
| tfidf_lr_char_ngram_3_5_language-identification | 0.050164 | 0.050401 | **0.995288** |
| tfidf_lr_char_ngram_3_5_xlsum | 0.027584 | 0.033720 | **0.818037** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_amazon_reviews_multi`

---

## Dataset: `europarl`

**Query languages:** `['da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'it', 'nl', 'pl', 'pt', 'ro', 'sv']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `6.557981` |
| S5_cross_level | `50.831811` |
| S1_morphological | `53.735627` |
| S2_lexical_diversity | `50.365895` |
| S3_structural | `91.944000` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 6.557981 | 6.557981 |
| S5_cross_level | 1.0 | 50.831811 | 50.831811 |
| S1_morphological | 1.0 | 53.735627 | 53.735627 |
| S2_lexical_diversity | 1.0 | 50.365895 | 50.365895 |
| S3_structural | 1.0 | 91.944000 | 91.944000 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 42.327454** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.715356` |
| S5_cross_level | `51.283048` |
| S1_morphological | `51.244874` |
| S2_lexical_diversity | `41.291653` |
| S3_structural | `72.715488` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.715356 | 10.715356 |
| S5_cross_level | 1.0 | 51.283048 | 51.283048 |
| S1_morphological | 1.0 | 51.244874 | 51.244874 |
| S2_lexical_diversity | 1.0 | 41.291653 | 41.291653 |
| S3_structural | 1.0 | 72.715488 | 72.715488 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 37.982913** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.040976` |
| S5_cross_level | `20.671159` |
| S1_morphological | `41.757810` |
| S2_lexical_diversity | `26.396831` |
| S3_structural | `50.648524` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.040976 | 9.040976 |
| S5_cross_level | 1.0 | 20.671159 | 20.671159 |
| S1_morphological | 1.0 | 41.757810 | 41.757810 |
| S2_lexical_diversity | 1.0 | 26.396831 | 26.396831 |
| S3_structural | 1.0 | 50.648524 | 50.648524 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 24.830982** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.266059` |
| S5_cross_level | `32.466267` |
| S1_morphological | `56.970389` |
| S2_lexical_diversity | `43.798647` |
| S3_structural | `81.079092` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.266059 | 11.266059 |
| S5_cross_level | 1.0 | 32.466267 | 32.466267 |
| S1_morphological | 1.0 | 56.970389 | 56.970389 |
| S2_lexical_diversity | 1.0 | 43.798647 | 43.798647 |
| S3_structural | 1.0 | 81.079092 | 81.079092 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 37.714390** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.536843` |
| S5_cross_level | `52.542971` |
| S1_morphological | `62.009889` |
| S2_lexical_diversity | `43.192570` |
| S3_structural | `72.224719` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.536843 | 10.536843 |
| S5_cross_level | 1.0 | 52.542971 | 52.542971 |
| S1_morphological | 1.0 | 62.009889 | 62.009889 |
| S2_lexical_diversity | 1.0 | 43.192570 | 43.192570 |
| S3_structural | 1.0 | 72.224719 | 72.224719 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 40.172734** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `204.701687` |
| S5_cross_level | `1247.426404` |
| S1_morphological | `318.093924` |
| S2_lexical_diversity | `842.805463` |
| S3_structural | `1269.899694` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 204.701687 | 204.701687 |
| S5_cross_level | 1.0 | 1247.426404 | 1247.426404 |
| S1_morphological | 1.0 | 318.093924 | 318.093924 |
| S2_lexical_diversity | 1.0 | 842.805463 | 842.805463 |
| S3_structural | 1.0 | 1269.899694 | 1269.899694 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 647.262372** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `8.232841` |
| S5_cross_level | `34.652968` |
| S1_morphological | `62.633601` |
| S2_lexical_diversity | `46.287047` |
| S3_structural | `85.314186` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 8.232841 | 8.232841 |
| S5_cross_level | 1.0 | 34.652968 | 34.652968 |
| S1_morphological | 1.0 | 62.633601 | 62.633601 |
| S2_lexical_diversity | 1.0 | 46.287047 | 46.287047 |
| S3_structural | 1.0 | 85.314186 | 85.314186 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 39.598538** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.647872` |
| S5_cross_level | `61.620219` |
| S1_morphological | `63.852396` |
| S2_lexical_diversity | `49.478364` |
| S3_structural | `72.962429` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__frac_agglutinative', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.647872 | 11.647872 |
| S5_cross_level | 1.0 | 61.620219 | 61.620219 |
| S1_morphological | 1.0 | 63.852396 | 63.852396 |
| S2_lexical_diversity | 1.0 | 49.478364 | 49.478364 |
| S3_structural | 1.0 | 72.962429 | 72.962429 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 43.348448** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `77.715477` |
| S5_cross_level | `423.048839` |
| S1_morphological | `148.486059` |
| S2_lexical_diversity | `327.094968` |
| S3_structural | `484.380293` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 77.715477 | 77.715477 |
| S5_cross_level | 1.0 | 423.048839 | 423.048839 |
| S1_morphological | 1.0 | 148.486059 | 148.486059 |
| S2_lexical_diversity | 1.0 | 327.094968 | 327.094968 |
| S3_structural | 1.0 | 484.380293 | 484.380293 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 243.562116** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.559431` |
| S5_cross_level | `37.617120` |
| S1_morphological | `56.867940` |
| S2_lexical_diversity | `101.369987` |
| S3_structural | `176.335111` |
| cat (Hamming) | `0.176471` (3/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.559431 | 12.559431 |
| S5_cross_level | 1.0 | 37.617120 | 37.617120 |
| S1_morphological | 1.0 | 56.867940 | 56.867940 |
| S2_lexical_diversity | 1.0 | 101.369987 | 101.369987 |
| S3_structural | 1.0 | 176.335111 | 176.335111 |
| cat | 1.0 | 0.176471 | 0.176471 |
| **Total** | Σw = 6.0000 | | **D = 64.154343** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.980640` |
| S5_cross_level | `35.094917` |
| S1_morphological | `46.256069` |
| S2_lexical_diversity | `40.622542` |
| S3_structural | `75.279890` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.980640 | 9.980640 |
| S5_cross_level | 1.0 | 35.094917 | 35.094917 |
| S1_morphological | 1.0 | 46.256069 | 46.256069 |
| S2_lexical_diversity | 1.0 | 40.622542 | 40.622542 |
| S3_structural | 1.0 | 75.279890 | 75.279890 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 34.597833** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.103268` |
| S5_cross_level | `37.216256` |
| S1_morphological | `39.798239` |
| S2_lexical_diversity | `81.521073` |
| S3_structural | `84.861642` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.103268 | 11.103268 |
| S5_cross_level | 1.0 | 37.216256 | 37.216256 |
| S1_morphological | 1.0 | 39.798239 | 39.798239 |
| S2_lexical_diversity | 1.0 | 81.521073 | 81.521073 |
| S3_structural | 1.0 | 84.861642 | 84.861642 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 42.495178** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `6.013113` |
| S5_cross_level | `24.455946` |
| S1_morphological | `58.984637` |
| S2_lexical_diversity | `34.131983` |
| S3_structural | `71.889504` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 6.013113 | 6.013113 |
| S5_cross_level | 1.0 | 24.455946 | 24.455946 |
| S1_morphological | 1.0 | 58.984637 | 58.984637 |
| S2_lexical_diversity | 1.0 | 34.131983 | 34.131983 |
| S3_structural | 1.0 | 71.889504 | 71.889504 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 32.687040** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `1.210059` |
| S5_cross_level | `6.929985` |
| S1_morphological | `10.281483` |
| S2_lexical_diversity | `7.512230` |
| S3_structural | `11.299501` |
| cat (Hamming) | `0.000000` (0/17 flags differ) |

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 1.210059 | 1.210059 |
| S5_cross_level | 1.0 | 6.929985 | 6.929985 |
| S1_morphological | 1.0 | 10.281483 | 10.281483 |
| S2_lexical_diversity | 1.0 | 7.512230 | 7.512230 |
| S3_structural | 1.0 | 11.299501 | 11.299501 |
| cat | 1.0 | 0.000000 | 0.000000 |
| **Total** | Σw = 6.0000 | | **D = 6.205543** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `7.995996` |
| S5_cross_level | `42.248505` |
| S1_morphological | `53.547179` |
| S2_lexical_diversity | `53.297284` |
| S3_structural | `95.873803` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 7.995996 | 7.995996 |
| S5_cross_level | 1.0 | 42.248505 | 42.248505 |
| S1_morphological | 1.0 | 53.547179 | 53.547179 |
| S2_lexical_diversity | 1.0 | 53.297284 | 53.297284 |
| S3_structural | 1.0 | 95.873803 | 95.873803 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 42.268304** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `2.582429` |
| S5_cross_level | `20.807843` |
| S1_morphological | `44.607928` |
| S2_lexical_diversity | `26.420179` |
| S3_structural | `66.706166` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 2.582429 | 2.582429 |
| S5_cross_level | 1.0 | 20.807843 | 20.807843 |
| S1_morphological | 1.0 | 44.607928 | 44.607928 |
| S2_lexical_diversity | 1.0 | 26.420179 | 26.420179 |
| S3_structural | 1.0 | 66.706166 | 66.706166 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 26.942326** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `6.176051` |
| S5_cross_level | `28.437542` |
| S1_morphological | `51.948100` |
| S2_lexical_diversity | `42.579480` |
| S3_structural | `82.885091` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 6.176051 | 6.176051 |
| S5_cross_level | 1.0 | 28.437542 | 28.437542 |
| S1_morphological | 1.0 | 51.948100 | 51.948100 |
| S2_lexical_diversity | 1.0 | 42.579480 | 42.579480 |
| S3_structural | 1.0 | 82.885091 | 82.885091 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 35.425946** |

### §§ 4–5 · Similarity % (max_D = `647.262372`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | europarl | `6.205543` | 99.0% | ← yes |
| 2 | flores_plus | `24.830982` | 96.2% | ← yes |
| 3 | xnli | `26.942326` | 95.8% | ← yes |
| 4 | stsb_multi_mt | `32.687040` | 94.9% |  |
| 5 | tweet_sentiment_multilingual | `34.597833` | 94.7% |  |
| 6 | language-identification | `35.425946` | 94.5% |  |
| 7 | xlsum | `37.714390` | 94.2% |  |
| 8 | massive | `37.982913` | 94.1% |  |
| 9 | amazon_reviews_multi | `39.598538` | 93.9% |  |
| 10 | mmarco | `40.172734` | 93.8% |  |
| 11 | multilingual_cc_news | `42.268304` | 93.5% |  |
| 12 | multilingual_toxicity_dataset | `42.327454` | 93.5% |  |
| 13 | OpenLID-v2 | `42.495178` | 93.4% |  |
| 14 | tydiqa | `43.348448` | 93.3% |  |
| 15 | multi_eurlex | `64.154343` | 90.1% |  |
| 16 | exorde-social-media-december-2024-week1 | `243.562116` | 62.4% |  |
| 17 | wikipedia | `647.262372` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `europarl`** — inv_d = `0.161146`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_europarl | 0.999530 | 0 | 1.0000 | 0.161071 |
| tfidf_char_ngram_3_5_europarl | 0.999532 | 0 | 1.0000 | 0.161071 |
| fasttext_subword_europarl | 0.999388 | 0 | 1.0000 | 0.161048 |
| fasttext_word_europarl | 0.998640 | 0 | 1.0000 | 0.160927 |
| lid.176_europarl | 0.997159 | 0 | 1.0000 | 0.160688 |
| cld3_europarl | 0.993509 | 0 | 1.0000 | 0.160100 |
| bow_maxabs_lr_char_ngram_3_5_europarl | 0.999411 | 0 | 1.0000 | 0.161051 |
| tfidf_lr_char_ngram_3_5_europarl | 0.999417 | 0 | 1.0000 | 0.161052 |

**Neighbour: `flores_plus`** — inv_d = `0.040272`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_flores_plus | 0.981840 | 0 | 1.0000 | 0.039541 |
| tfidf_char_ngram_3_5_flores_plus | 0.983247 | 0 | 1.0000 | 0.039598 |
| fasttext_subword_flores_plus | 0.983486 | 0 | 1.0000 | 0.039607 |
| fasttext_word_flores_plus | 0.927359 | 0 | 1.0000 | 0.037347 |
| lid.176_flores_plus | 0.939262 | 0 | 1.0000 | 0.037826 |
| cld3_flores_plus | 0.979305 | 0 | 1.0000 | 0.039439 |
| bow_maxabs_lr_char_ngram_3_5_flores_plus | 0.981447 | 0 | 1.0000 | 0.039525 |
| tfidf_lr_char_ngram_3_5_flores_plus | 0.987288 | 0 | 1.0000 | 0.039760 |

**Neighbour: `xnli`** — inv_d = `0.037116`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_xnli | 0.995875 | 8 | 0.3846 | 0.014217 |
| tfidf_char_ngram_3_5_xnli | 0.995832 | 8 | 0.3846 | 0.014216 |
| fasttext_subword_xnli | 0.999558 | 8 | 0.3846 | 0.014269 |
| fasttext_word_xnli | 0.998835 | 8 | 0.3846 | 0.014259 |
| lid.176_xnli | 0.998968 | 8 | 0.3846 | 0.014261 |
| cld3_xnli | 0.989093 | 8 | 0.3846 | 0.014120 |
| bow_maxabs_lr_char_ngram_3_5_xnli | 0.999195 | 8 | 0.3846 | 0.014264 |
| tfidf_lr_char_ngram_3_5_xnli | 0.999401 | 8 | 0.3846 | 0.014267 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_europarl | 0.161071 | 0.161146 | **0.999530** |
| bow_char_ngram_3_5_flores_plus | 0.039541 | 0.040272 | **0.981840** |
| bow_char_ngram_3_5_xnli | 0.014217 | 0.037116 | **0.383029** |
| bow_maxabs_lr_char_ngram_3_5_europarl | 0.161051 | 0.161146 | **0.999411** |
| bow_maxabs_lr_char_ngram_3_5_flores_plus | 0.039525 | 0.040272 | **0.981447** |
| bow_maxabs_lr_char_ngram_3_5_xnli | 0.014264 | 0.037116 | **0.384306** |
| cld3_europarl | 0.160100 | 0.161146 | **0.993509** |
| cld3_flores_plus | 0.039439 | 0.040272 | **0.979305** |
| cld3_xnli | 0.014120 | 0.037116 | **0.380420** |
| fasttext_subword_europarl | 0.161048 | 0.161146 | **0.999388** |
| fasttext_subword_flores_plus | 0.039607 | 0.040272 | **0.983486** |
| fasttext_subword_xnli | 0.014269 | 0.037116 | **0.384445** |
| fasttext_word_europarl | 0.160927 | 0.161146 | **0.998640** |
| fasttext_word_flores_plus | 0.037347 | 0.040272 | **0.927359** |
| fasttext_word_xnli | 0.014259 | 0.037116 | **0.384167** |
| lid.176_europarl | 0.160688 | 0.161146 | **0.997159** |
| lid.176_flores_plus | 0.037826 | 0.040272 | **0.939262** |
| lid.176_xnli | 0.014261 | 0.037116 | **0.384218** |
| tfidf_char_ngram_3_5_europarl | 0.161071 | 0.161146 | **0.999532** |
| tfidf_char_ngram_3_5_flores_plus | 0.039598 | 0.040272 | **0.983247** |
| tfidf_char_ngram_3_5_xnli | 0.014216 | 0.037116 | **0.383012** |
| tfidf_lr_char_ngram_3_5_europarl | 0.161052 | 0.161146 | **0.999417** |
| tfidf_lr_char_ngram_3_5_flores_plus | 0.039760 | 0.040272 | **0.987288** |
| tfidf_lr_char_ngram_3_5_xnli | 0.014267 | 0.037116 | **0.384385** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `tfidf_char_ngram_3_5_europarl`

---

## Dataset: `exorde-social-media-december-2024-week1`

**Query languages:** `['ca', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'hr', 'it', 'ja', 'ko', 'lt', 'mk', 'nl', 'pl', 'pt', 'ro', 'ru', 'sl', 'sv', 'uk', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `70.855901` |
| S5_cross_level | `329.462751` |
| S1_morphological | `149.043359` |
| S2_lexical_diversity | `291.492485` |
| S3_structural | `478.188420` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 70.855901 | 70.855901 |
| S5_cross_level | 1.0 | 329.462751 | 329.462751 |
| S1_morphological | 1.0 | 149.043359 | 149.043359 |
| S2_lexical_diversity | 1.0 | 291.492485 | 291.492485 |
| S3_structural | 1.0 | 478.188420 | 478.188420 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 219.909114** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `76.533347` |
| S5_cross_level | `367.456124` |
| S1_morphological | `176.357667` |
| S2_lexical_diversity | `320.248648` |
| S3_structural | `527.719737` |
| cat (Hamming) | `0.176471` (3/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 76.533347 | 76.533347 |
| S5_cross_level | 1.0 | 367.456124 | 367.456124 |
| S1_morphological | 1.0 | 176.357667 | 176.357667 |
| S2_lexical_diversity | 1.0 | 320.248648 | 320.248648 |
| S3_structural | 1.0 | 527.719737 | 527.719737 |
| cat | 1.0 | 0.176471 | 0.176471 |
| **Total** | Σw = 6.0000 | | **D = 244.748666** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `73.912733` |
| S5_cross_level | `364.843080` |
| S1_morphological | `173.298319` |
| S2_lexical_diversity | `316.126094` |
| S3_structural | `526.001278` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 73.912733 | 73.912733 |
| S5_cross_level | 1.0 | 364.843080 | 364.843080 |
| S1_morphological | 1.0 | 173.298319 | 173.298319 |
| S2_lexical_diversity | 1.0 | 316.126094 | 316.126094 |
| S3_structural | 1.0 | 526.001278 | 526.001278 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 242.412604** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `73.340018` |
| S5_cross_level | `354.434383` |
| S1_morphological | `168.440126` |
| S2_lexical_diversity | `314.515075` |
| S3_structural | `517.675893` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 73.340018 | 73.340018 |
| S5_cross_level | 1.0 | 354.434383 | 354.434383 |
| S1_morphological | 1.0 | 168.440126 | 168.440126 |
| S2_lexical_diversity | 1.0 | 314.515075 | 314.515075 |
| S3_structural | 1.0 | 517.675893 | 517.675893 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 238.126406** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `77.200302` |
| S5_cross_level | `369.659984` |
| S1_morphological | `183.065121` |
| S2_lexical_diversity | `324.470243` |
| S3_structural | `532.447808` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 77.200302 | 77.200302 |
| S5_cross_level | 1.0 | 369.659984 | 369.659984 |
| S1_morphological | 1.0 | 183.065121 | 183.065121 |
| S2_lexical_diversity | 1.0 | 324.470243 | 324.470243 |
| S3_structural | 1.0 | 532.447808 | 532.447808 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 247.875870** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `130.551796` |
| S5_cross_level | `878.427214` |
| S1_morphological | `164.864506` |
| S2_lexical_diversity | `522.000894` |
| S3_structural | `749.223435` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 130.551796 | 130.551796 |
| S5_cross_level | 1.0 | 878.427214 | 878.427214 |
| S1_morphological | 1.0 | 164.864506 | 164.864506 |
| S2_lexical_diversity | 1.0 | 522.000894 | 522.000894 |
| S3_structural | 1.0 | 749.223435 | 749.223435 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 407.530915** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `75.446501` |
| S5_cross_level | `362.955871` |
| S1_morphological | `162.520378` |
| S2_lexical_diversity | `311.961979` |
| S3_structural | `508.208691` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 75.446501 | 75.446501 |
| S5_cross_level | 1.0 | 362.955871 | 362.955871 |
| S1_morphological | 1.0 | 162.520378 | 162.520378 |
| S2_lexical_diversity | 1.0 | 311.961979 | 311.961979 |
| S3_structural | 1.0 | 508.208691 | 508.208691 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 236.927335** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `76.949619` |
| S5_cross_level | `369.956508` |
| S1_morphological | `189.667623` |
| S2_lexical_diversity | `322.366734` |
| S3_structural | `530.120049` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 76.949619 | 76.949619 |
| S5_cross_level | 1.0 | 369.956508 | 369.956508 |
| S1_morphological | 1.0 | 189.667623 | 189.667623 |
| S2_lexical_diversity | 1.0 | 322.366734 | 322.366734 |
| S3_structural | 1.0 | 530.120049 | 530.120049 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 248.255187** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `7.798368` |
| S5_cross_level | `61.617948` |
| S1_morphological | `41.965165` |
| S2_lexical_diversity | `30.048751` |
| S3_structural | `61.817873` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 7.798368 | 7.798368 |
| S5_cross_level | 1.0 | 61.617948 | 61.617948 |
| S1_morphological | 1.0 | 41.965165 | 41.965165 |
| S2_lexical_diversity | 1.0 | 30.048751 | 30.048751 |
| S3_structural | 1.0 | 61.817873 | 61.817873 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 33.894292** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `72.279121` |
| S5_cross_level | `360.002953` |
| S1_morphological | `169.574383` |
| S2_lexical_diversity | `314.042721` |
| S3_structural | `519.654115` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 72.279121 | 72.279121 |
| S5_cross_level | 1.0 | 360.002953 | 360.002953 |
| S1_morphological | 1.0 | 169.574383 | 169.574383 |
| S2_lexical_diversity | 1.0 | 314.042721 | 314.042721 |
| S3_structural | 1.0 | 519.654115 | 519.654115 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 239.366725** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `73.157253` |
| S5_cross_level | `367.309834` |
| S1_morphological | `172.767793` |
| S2_lexical_diversity | `314.632461` |
| S3_structural | `515.096125` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 73.157253 | 73.157253 |
| S5_cross_level | 1.0 | 367.309834 | 367.309834 |
| S1_morphological | 1.0 | 172.767793 | 172.767793 |
| S2_lexical_diversity | 1.0 | 314.632461 | 314.632461 |
| S3_structural | 1.0 | 515.096125 | 515.096125 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 240.611558** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `70.999965` |
| S5_cross_level | `357.800218` |
| S1_morphological | `168.199724` |
| S2_lexical_diversity | `311.287203` |
| S3_structural | `513.556798` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 70.999965 | 70.999965 |
| S5_cross_level | 1.0 | 357.800218 | 357.800218 |
| S1_morphological | 1.0 | 168.199724 | 168.199724 |
| S2_lexical_diversity | 1.0 | 311.287203 | 311.287203 |
| S3_structural | 1.0 | 513.556798 | 513.556798 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 237.023004** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `76.667522` |
| S5_cross_level | `369.679715` |
| S1_morphological | `183.910045` |
| S2_lexical_diversity | `327.070686` |
| S3_structural | `537.001739` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 76.667522 | 76.667522 |
| S5_cross_level | 1.0 | 369.679715 | 369.679715 |
| S1_morphological | 1.0 | 183.910045 | 183.910045 |
| S2_lexical_diversity | 1.0 | 327.070686 | 327.070686 |
| S3_structural | 1.0 | 537.001739 | 537.001739 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 249.123579** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `75.040677` |
| S5_cross_level | `368.550888` |
| S1_morphological | `171.174765` |
| S2_lexical_diversity | `322.818278` |
| S3_structural | `529.313922` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 75.040677 | 75.040677 |
| S5_cross_level | 1.0 | 368.550888 | 368.550888 |
| S1_morphological | 1.0 | 171.174765 | 171.174765 |
| S2_lexical_diversity | 1.0 | 322.818278 | 322.818278 |
| S3_structural | 1.0 | 529.313922 | 529.313922 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 244.590932** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `71.955105` |
| S5_cross_level | `347.092234` |
| S1_morphological | `163.207850` |
| S2_lexical_diversity | `310.622349` |
| S3_structural | `507.875536` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 71.955105 | 71.955105 |
| S5_cross_level | 1.0 | 347.092234 | 347.092234 |
| S1_morphological | 1.0 | 163.207850 | 163.207850 |
| S2_lexical_diversity | 1.0 | 310.622349 | 310.622349 |
| S3_structural | 1.0 | 507.875536 | 507.875536 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 233.478454** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `75.229430` |
| S5_cross_level | `363.012759` |
| S1_morphological | `171.244275` |
| S2_lexical_diversity | `320.673754` |
| S3_structural | `524.802463` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 75.229430 | 75.229430 |
| S5_cross_level | 1.0 | 363.012759 | 363.012759 |
| S1_morphological | 1.0 | 171.244275 | 171.244275 |
| S2_lexical_diversity | 1.0 | 320.673754 | 320.673754 |
| S3_structural | 1.0 | 524.802463 | 524.802463 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 242.552604** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `73.755828` |
| S5_cross_level | `358.769093` |
| S1_morphological | `157.110433` |
| S2_lexical_diversity | `309.777718` |
| S3_structural | `502.211111` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 73.755828 | 73.755828 |
| S5_cross_level | 1.0 | 358.769093 | 358.769093 |
| S1_morphological | 1.0 | 157.110433 | 157.110433 |
| S2_lexical_diversity | 1.0 | 309.777718 | 309.777718 |
| S3_structural | 1.0 | 502.211111 | 502.211111 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 233.662854** |

### §§ 4–5 · Similarity % (max_D = `407.530915`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | exorde-social-media-december-2024-week1 | `33.894292` | 91.7% | ← yes |
| 2 | multilingual_toxicity_dataset | `219.909114` | 46.0% | ← yes |
| 3 | multilingual_cc_news | `233.478454` | 42.7% | ← yes |
| 4 | language-identification | `233.662854` | 42.7% |  |
| 5 | amazon_reviews_multi | `236.927335` | 41.9% |  |
| 6 | OpenLID-v2 | `237.023004` | 41.8% |  |
| 7 | xlsum | `238.126406` | 41.6% |  |
| 8 | multi_eurlex | `239.366725` | 41.3% |  |
| 9 | tweet_sentiment_multilingual | `240.611558` | 41.0% |  |
| 10 | flores_plus | `242.412604` | 40.5% |  |
| 11 | xnli | `242.552604` | 40.5% |  |
| 12 | europarl | `244.590932` | 40.0% |  |
| 13 | massive | `244.748666` | 39.9% |  |
| 14 | mmarco | `247.875870` | 39.2% |  |
| 15 | tydiqa | `248.255187` | 39.1% |  |
| 16 | stsb_multi_mt | `249.123579` | 38.9% |  |
| 17 | wikipedia | `407.530915` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `exorde-social-media-december-2024-week1`** — inv_d = `0.029503`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.901701 | 0 | 1.0000 | 0.026603 |
| tfidf_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.903643 | 0 | 1.0000 | 0.026661 |
| fasttext_subword_exorde-social-media-december-2024-week1 | 0.968330 | 0 | 1.0000 | 0.028569 |
| fasttext_word_exorde-social-media-december-2024-week1 | 0.895768 | 0 | 1.0000 | 0.026428 |
| lid.176_exorde-social-media-december-2024-week1 | 0.977396 | 0 | 1.0000 | 0.028837 |
| cld3_exorde-social-media-december-2024-week1 | 0.914822 | 0 | 1.0000 | 0.026990 |
| bow_maxabs_lr_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.913583 | 0 | 1.0000 | 0.026954 |
| tfidf_lr_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.922312 | 0 | 1.0000 | 0.027211 |

**Neighbour: `multilingual_toxicity_dataset`** — inv_d = `0.004547`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multilingual_toxicity_dataset | 0.955714 | 14 | 0.3913 | 0.001701 |
| tfidf_char_ngram_3_5_multilingual_toxicity_dataset | 0.956080 | 14 | 0.3913 | 0.001701 |
| fasttext_subword_multilingual_toxicity_dataset | 0.995558 | 14 | 0.3913 | 0.001771 |
| fasttext_word_multilingual_toxicity_dataset | 0.838982 | 14 | 0.3913 | 0.001493 |
| lid.176_multilingual_toxicity_dataset | 0.990585 | 14 | 0.3913 | 0.001763 |
| cld3_multilingual_toxicity_dataset | 0.979348 | 14 | 0.3913 | 0.001743 |
| bow_maxabs_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.970372 | 14 | 0.3913 | 0.001727 |
| tfidf_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.985689 | 14 | 0.3913 | 0.001754 |

**Neighbour: `multilingual_cc_news`** — inv_d = `0.004283`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multilingual_cc_news | 0.975398 | 3 | 0.8696 | 0.003633 |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.976358 | 3 | 0.8696 | 0.003636 |
| fasttext_subword_multilingual_cc_news | 0.997083 | 3 | 0.8696 | 0.003714 |
| fasttext_word_multilingual_cc_news | 0.985130 | 3 | 0.8696 | 0.003669 |
| lid.176_multilingual_cc_news | 0.928836 | 3 | 0.8696 | 0.003459 |
| cld3_multilingual_cc_news | 0.955450 | 3 | 0.8696 | 0.003558 |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.975948 | 3 | 0.8696 | 0.003635 |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.979512 | 3 | 0.8696 | 0.003648 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.026603 | 0.029503 | **0.901701** |
| bow_char_ngram_3_5_multilingual_cc_news | 0.003633 | 0.004283 | **0.848172** |
| bow_char_ngram_3_5_multilingual_toxicity_dataset | 0.001701 | 0.004547 | **0.373975** |
| bow_maxabs_lr_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.026954 | 0.029503 | **0.913583** |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.003635 | 0.004283 | **0.848650** |
| bow_maxabs_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.001727 | 0.004547 | **0.379711** |
| cld3_exorde-social-media-december-2024-week1 | 0.026990 | 0.029503 | **0.914822** |
| cld3_multilingual_cc_news | 0.003558 | 0.004283 | **0.830826** |
| cld3_multilingual_toxicity_dataset | 0.001743 | 0.004547 | **0.383223** |
| fasttext_subword_exorde-social-media-december-2024-week1 | 0.028569 | 0.029503 | **0.968330** |
| fasttext_subword_multilingual_cc_news | 0.003714 | 0.004283 | **0.867029** |
| fasttext_subword_multilingual_toxicity_dataset | 0.001771 | 0.004547 | **0.389566** |
| fasttext_word_exorde-social-media-december-2024-week1 | 0.026428 | 0.029503 | **0.895768** |
| fasttext_word_multilingual_cc_news | 0.003669 | 0.004283 | **0.856635** |
| fasttext_word_multilingual_toxicity_dataset | 0.001493 | 0.004547 | **0.328297** |
| lid.176_exorde-social-media-december-2024-week1 | 0.028837 | 0.029503 | **0.977396** |
| lid.176_multilingual_cc_news | 0.003459 | 0.004283 | **0.807683** |
| lid.176_multilingual_toxicity_dataset | 0.001763 | 0.004547 | **0.387620** |
| tfidf_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.026661 | 0.029503 | **0.903643** |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.003636 | 0.004283 | **0.849007** |
| tfidf_char_ngram_3_5_multilingual_toxicity_dataset | 0.001701 | 0.004547 | **0.374118** |
| tfidf_lr_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.027211 | 0.029503 | **0.922312** |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.003648 | 0.004283 | **0.851750** |
| tfidf_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.001754 | 0.004547 | **0.385704** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `lid.176_exorde-social-media-december-2024-week1`

---

## Dataset: `flores_plus`

**Query languages:** `['ca', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'hr', 'it', 'ja', 'ko', 'lt', 'mk', 'nl', 'pl', 'pt', 'ro', 'ru', 'sl', 'sv', 'uk']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.707312` |
| S5_cross_level | `50.147888` |
| S1_morphological | `47.671374` |
| S2_lexical_diversity | `46.662716` |
| S3_structural | `82.203516` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.707312 | 9.707312 |
| S5_cross_level | 1.0 | 50.147888 | 50.147888 |
| S1_morphological | 1.0 | 47.671374 | 47.671374 |
| S2_lexical_diversity | 1.0 | 46.662716 | 46.662716 |
| S3_structural | 1.0 | 82.203516 | 82.203516 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 39.496840** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.361995` |
| S5_cross_level | `37.450429` |
| S1_morphological | `40.995069` |
| S2_lexical_diversity | `39.021816` |
| S3_structural | `57.738629` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.361995 | 16.361995 |
| S5_cross_level | 1.0 | 37.450429 | 37.450429 |
| S1_morphological | 1.0 | 40.995069 | 40.995069 |
| S2_lexical_diversity | 1.0 | 39.021816 | 39.021816 |
| S3_structural | 1.0 | 57.738629 | 57.738629 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 31.977009** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `1.363275` |
| S5_cross_level | `9.452688` |
| S1_morphological | `8.859481` |
| S2_lexical_diversity | `9.438839` |
| S3_structural | `13.900093` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 1.363275 | 1.363275 |
| S5_cross_level | 1.0 | 9.452688 | 9.452688 |
| S1_morphological | 1.0 | 8.859481 | 8.859481 |
| S2_lexical_diversity | 1.0 | 9.438839 | 9.438839 |
| S3_structural | 1.0 | 13.900093 | 13.900093 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 7.188670** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.212787` |
| S5_cross_level | `31.003817` |
| S1_morphological | `35.815517` |
| S2_lexical_diversity | `34.423817` |
| S3_structural | `59.907374` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.212787 | 9.212787 |
| S5_cross_level | 1.0 | 31.003817 | 31.003817 |
| S1_morphological | 1.0 | 35.815517 | 35.815517 |
| S2_lexical_diversity | 1.0 | 34.423817 | 34.423817 |
| S3_structural | 1.0 | 59.907374 | 59.907374 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 28.482121** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.996931` |
| S5_cross_level | `38.492096` |
| S1_morphological | `46.146241` |
| S2_lexical_diversity | `40.362920` |
| S3_structural | `54.701359` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.996931 | 16.996931 |
| S5_cross_level | 1.0 | 38.492096 | 38.492096 |
| S1_morphological | 1.0 | 46.146241 | 46.146241 |
| S2_lexical_diversity | 1.0 | 40.362920 | 40.362920 |
| S3_structural | 1.0 | 54.701359 | 54.701359 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 32.881297** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `202.882170` |
| S5_cross_level | `1241.977347` |
| S1_morphological | `321.780073` |
| S2_lexical_diversity | `834.215548` |
| S3_structural | `1264.769079` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 202.882170 | 202.882170 |
| S5_cross_level | 1.0 | 1241.977347 | 1241.977347 |
| S1_morphological | 1.0 | 321.780073 | 321.780073 |
| S2_lexical_diversity | 1.0 | 834.215548 | 834.215548 |
| S3_structural | 1.0 | 1264.769079 | 1264.769079 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 644.329526** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.181709` |
| S5_cross_level | `34.168928` |
| S1_morphological | `54.872608` |
| S2_lexical_diversity | `44.276107` |
| S3_structural | `72.359413` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.181709 | 10.181709 |
| S5_cross_level | 1.0 | 34.168928 | 34.168928 |
| S1_morphological | 1.0 | 54.872608 | 54.872608 |
| S2_lexical_diversity | 1.0 | 44.276107 | 44.276107 |
| S3_structural | 1.0 | 72.359413 | 72.359413 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 36.084304** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `17.044491` |
| S5_cross_level | `47.733797` |
| S1_morphological | `43.040265` |
| S2_lexical_diversity | `46.199831` |
| S3_structural | `56.633874` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 17.044491 | 17.044491 |
| S5_cross_level | 1.0 | 47.733797 | 47.733797 |
| S1_morphological | 1.0 | 43.040265 | 43.040265 |
| S2_lexical_diversity | 1.0 | 46.199831 | 46.199831 |
| S3_structural | 1.0 | 56.633874 | 56.633874 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 35.157729** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `77.024040` |
| S5_cross_level | `417.756900` |
| S1_morphological | `150.574418` |
| S2_lexical_diversity | `318.887293` |
| S3_structural | `481.657190` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 77.024040 | 77.024040 |
| S5_cross_level | 1.0 | 417.756900 | 417.756900 |
| S1_morphological | 1.0 | 150.574418 | 150.574418 |
| S2_lexical_diversity | 1.0 | 318.887293 | 318.887293 |
| S3_structural | 1.0 | 481.657190 | 481.657190 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 241.042130** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `17.533152` |
| S5_cross_level | `40.888485` |
| S1_morphological | `49.363692` |
| S2_lexical_diversity | `90.377204` |
| S3_structural | `156.127405` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 17.533152 | 17.533152 |
| S5_cross_level | 1.0 | 40.888485 | 40.888485 |
| S1_morphological | 1.0 | 49.363692 | 49.363692 |
| S2_lexical_diversity | 1.0 | 90.377204 | 90.377204 |
| S3_structural | 1.0 | 156.127405 | 156.127405 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 59.126754** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.627739` |
| S5_cross_level | `40.632877` |
| S1_morphological | `52.784140` |
| S2_lexical_diversity | `47.274423` |
| S3_structural | `84.328589` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.627739 | 16.627739 |
| S5_cross_level | 1.0 | 40.632877 | 40.632877 |
| S1_morphological | 1.0 | 52.784140 | 52.784140 |
| S2_lexical_diversity | 1.0 | 47.274423 | 47.274423 |
| S3_structural | 1.0 | 84.328589 | 84.328589 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 40.362863** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.316694` |
| S5_cross_level | `33.920461` |
| S1_morphological | `23.793625` |
| S2_lexical_diversity | `75.498672` |
| S3_structural | `61.540234` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.316694 | 11.316694 |
| S5_cross_level | 1.0 | 33.920461 | 33.920461 |
| S1_morphological | 1.0 | 23.793625 | 23.793625 |
| S2_lexical_diversity | 1.0 | 75.498672 | 75.498672 |
| S3_structural | 1.0 | 61.540234 | 61.540234 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 34.364556** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.969343` |
| S5_cross_level | `22.226785` |
| S1_morphological | `37.311979` |
| S2_lexical_diversity | `30.896105` |
| S3_structural | `53.044345` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.969343 | 12.969343 |
| S5_cross_level | 1.0 | 22.226785 | 22.226785 |
| S1_morphological | 1.0 | 37.311979 | 37.311979 |
| S2_lexical_diversity | 1.0 | 30.896105 | 30.896105 |
| S3_structural | 1.0 | 53.044345 | 53.044345 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 26.172799** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.365164` |
| S5_cross_level | `21.480037` |
| S1_morphological | `43.795569` |
| S2_lexical_diversity | `23.405819` |
| S3_structural | `48.127506` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.365164 | 9.365164 |
| S5_cross_level | 1.0 | 21.480037 | 21.480037 |
| S1_morphological | 1.0 | 43.795569 | 43.795569 |
| S2_lexical_diversity | 1.0 | 23.405819 | 23.405819 |
| S3_structural | 1.0 | 48.127506 | 48.127506 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 24.440780** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.406711` |
| S5_cross_level | `39.961977` |
| S1_morphological | `36.530124` |
| S2_lexical_diversity | `44.086161` |
| S3_structural | `75.160532` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.406711 | 10.406711 |
| S5_cross_level | 1.0 | 39.961977 | 39.961977 |
| S1_morphological | 1.0 | 36.530124 | 36.530124 |
| S2_lexical_diversity | 1.0 | 44.086161 | 44.086161 |
| S3_structural | 1.0 | 75.160532 | 75.160532 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 34.416408** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.392793` |
| S5_cross_level | `18.796363` |
| S1_morphological | `29.570701` |
| S2_lexical_diversity | `30.454187` |
| S3_structural | `60.723280` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.392793 | 11.392793 |
| S5_cross_level | 1.0 | 18.796363 | 18.796363 |
| S1_morphological | 1.0 | 29.570701 | 29.570701 |
| S2_lexical_diversity | 1.0 | 30.454187 | 30.454187 |
| S3_structural | 1.0 | 60.723280 | 60.723280 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 25.244456** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `8.625176` |
| S5_cross_level | `24.423543` |
| S1_morphological | `42.279238` |
| S2_lexical_diversity | `34.333082` |
| S3_structural | `61.140328` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 8.625176 | 8.625176 |
| S5_cross_level | 1.0 | 24.423543 | 24.423543 |
| S1_morphological | 1.0 | 42.279238 | 42.279238 |
| S2_lexical_diversity | 1.0 | 34.333082 | 34.333082 |
| S3_structural | 1.0 | 61.140328 | 61.140328 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 28.555130** |

### §§ 4–5 · Similarity % (max_D = `644.329526`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | flores_plus | `7.188670` | 98.9% | ← yes |
| 2 | europarl | `24.440780` | 96.2% | ← yes |
| 3 | xnli | `25.244456` | 96.1% | ← yes |
| 4 | stsb_multi_mt | `26.172799` | 95.9% |  |
| 5 | xlsum | `28.482121` | 95.6% |  |
| 6 | language-identification | `28.555130` | 95.6% |  |
| 7 | massive | `31.977009` | 95.0% |  |
| 8 | mmarco | `32.881297` | 94.9% |  |
| 9 | OpenLID-v2 | `34.364556` | 94.7% |  |
| 10 | multilingual_cc_news | `34.416408` | 94.7% |  |
| 11 | tydiqa | `35.157729` | 94.5% |  |
| 12 | amazon_reviews_multi | `36.084304` | 94.4% |  |
| 13 | multilingual_toxicity_dataset | `39.496840` | 93.9% |  |
| 14 | tweet_sentiment_multilingual | `40.362863` | 93.7% |  |
| 15 | multi_eurlex | `59.126754` | 90.8% |  |
| 16 | exorde-social-media-december-2024-week1 | `241.042130` | 62.6% |  |
| 17 | wikipedia | `644.329526` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `flores_plus`** — inv_d = `0.139108`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_flores_plus | 0.981840 | 0 | 1.0000 | 0.136582 |
| tfidf_char_ngram_3_5_flores_plus | 0.983247 | 0 | 1.0000 | 0.136777 |
| fasttext_subword_flores_plus | 0.983486 | 0 | 1.0000 | 0.136811 |
| fasttext_word_flores_plus | 0.927359 | 0 | 1.0000 | 0.129003 |
| lid.176_flores_plus | 0.939262 | 0 | 1.0000 | 0.130659 |
| cld3_flores_plus | 0.979305 | 0 | 1.0000 | 0.136229 |
| bow_maxabs_lr_char_ngram_3_5_flores_plus | 0.981447 | 0 | 1.0000 | 0.136527 |
| tfidf_lr_char_ngram_3_5_flores_plus | 0.987288 | 0 | 1.0000 | 0.137339 |

**Neighbour: `europarl`** — inv_d = `0.040915`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_europarl | 0.999530 | 9 | 0.5909 | 0.024166 |
| tfidf_char_ngram_3_5_europarl | 0.999532 | 9 | 0.5909 | 0.024166 |
| fasttext_subword_europarl | 0.999388 | 9 | 0.5909 | 0.024162 |
| fasttext_word_europarl | 0.998640 | 9 | 0.5909 | 0.024144 |
| lid.176_europarl | 0.997159 | 9 | 0.5909 | 0.024108 |
| cld3_europarl | 0.993509 | 9 | 0.5909 | 0.024020 |
| bow_maxabs_lr_char_ngram_3_5_europarl | 0.999411 | 9 | 0.5909 | 0.024163 |
| tfidf_lr_char_ngram_3_5_europarl | 0.999417 | 9 | 0.5909 | 0.024163 |

**Neighbour: `xnli`** — inv_d = `0.039613`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_xnli | 0.995875 | 16 | 0.2727 | 0.010759 |
| tfidf_char_ngram_3_5_xnli | 0.995832 | 16 | 0.2727 | 0.010758 |
| fasttext_subword_xnli | 0.999558 | 16 | 0.2727 | 0.010799 |
| fasttext_word_xnli | 0.998835 | 16 | 0.2727 | 0.010791 |
| lid.176_xnli | 0.998968 | 16 | 0.2727 | 0.010792 |
| cld3_xnli | 0.989093 | 16 | 0.2727 | 0.010686 |
| bow_maxabs_lr_char_ngram_3_5_xnli | 0.999195 | 16 | 0.2727 | 0.010795 |
| tfidf_lr_char_ngram_3_5_xnli | 0.999401 | 16 | 0.2727 | 0.010797 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_europarl | 0.024166 | 0.040915 | **0.590631** |
| bow_char_ngram_3_5_flores_plus | 0.136582 | 0.139108 | **0.981840** |
| bow_char_ngram_3_5_xnli | 0.010759 | 0.039613 | **0.271602** |
| bow_maxabs_lr_char_ngram_3_5_europarl | 0.024163 | 0.040915 | **0.590561** |
| bow_maxabs_lr_char_ngram_3_5_flores_plus | 0.136527 | 0.139108 | **0.981447** |
| bow_maxabs_lr_char_ngram_3_5_xnli | 0.010795 | 0.039613 | **0.272508** |
| cld3_europarl | 0.024020 | 0.040915 | **0.587073** |
| cld3_flores_plus | 0.136229 | 0.139108 | **0.979305** |
| cld3_xnli | 0.010686 | 0.039613 | **0.269753** |
| fasttext_subword_europarl | 0.024162 | 0.040915 | **0.590547** |
| fasttext_subword_flores_plus | 0.136811 | 0.139108 | **0.983486** |
| fasttext_subword_xnli | 0.010799 | 0.039613 | **0.272607** |
| fasttext_word_europarl | 0.024144 | 0.040915 | **0.590105** |
| fasttext_word_flores_plus | 0.129003 | 0.139108 | **0.927359** |
| fasttext_word_xnli | 0.010791 | 0.039613 | **0.272410** |
| lid.176_europarl | 0.024108 | 0.040915 | **0.589230** |
| lid.176_flores_plus | 0.130659 | 0.139108 | **0.939262** |
| lid.176_xnli | 0.010792 | 0.039613 | **0.272446** |
| tfidf_char_ngram_3_5_europarl | 0.024166 | 0.040915 | **0.590633** |
| tfidf_char_ngram_3_5_flores_plus | 0.136777 | 0.139108 | **0.983247** |
| tfidf_char_ngram_3_5_xnli | 0.010758 | 0.039613 | **0.271591** |
| tfidf_lr_char_ngram_3_5_europarl | 0.024163 | 0.040915 | **0.590565** |
| tfidf_lr_char_ngram_3_5_flores_plus | 0.137339 | 0.139108 | **0.987288** |
| tfidf_lr_char_ngram_3_5_xnli | 0.010797 | 0.039613 | **0.272564** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `tfidf_lr_char_ngram_3_5_flores_plus`

---

## Dataset: `language-identification`

**Query languages:** `['de', 'el', 'en', 'es', 'fr', 'it', 'ja', 'nl', 'pl', 'pt', 'ru', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `5.292085` |
| S5_cross_level | `37.117083` |
| S1_morphological | `39.508352` |
| S2_lexical_diversity | `30.979349` |
| S3_structural | `43.549132` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 5.292085 | 5.292085 |
| S5_cross_level | 1.0 | 37.117083 | 37.117083 |
| S1_morphological | 1.0 | 39.508352 | 39.508352 |
| S2_lexical_diversity | 1.0 | 30.979349 | 30.979349 |
| S3_structural | 1.0 | 43.549132 | 43.549132 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 26.123353** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.095892` |
| S5_cross_level | `45.401326` |
| S1_morphological | `61.786643` |
| S2_lexical_diversity | `46.175899` |
| S3_structural | `71.430131` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.095892 | 14.095892 |
| S5_cross_level | 1.0 | 45.401326 | 45.401326 |
| S1_morphological | 1.0 | 61.786643 | 61.786643 |
| S2_lexical_diversity | 1.0 | 46.175899 | 46.175899 |
| S3_structural | 1.0 | 71.430131 | 71.430131 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 39.873805** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `7.008818` |
| S5_cross_level | `23.046769` |
| S1_morphological | `48.346956` |
| S2_lexical_diversity | `30.770420` |
| S3_structural | `61.540070` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 7.008818 | 7.008818 |
| S5_cross_level | 1.0 | 23.046769 | 23.046769 |
| S1_morphological | 1.0 | 48.346956 | 48.346956 |
| S2_lexical_diversity | 1.0 | 30.770420 | 30.770420 |
| S3_structural | 1.0 | 61.540070 | 61.540070 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 28.540408** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `7.795680` |
| S5_cross_level | `15.201656` |
| S1_morphological | `41.921911` |
| S2_lexical_diversity | `30.529068` |
| S3_structural | `58.140670` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 7.795680 | 7.795680 |
| S5_cross_level | 1.0 | 15.201656 | 15.201656 |
| S1_morphological | 1.0 | 41.921911 | 41.921911 |
| S2_lexical_diversity | 1.0 | 30.529068 | 30.529068 |
| S3_structural | 1.0 | 58.140670 | 58.140670 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 25.647184** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.745887` |
| S5_cross_level | `46.915525` |
| S1_morphological | `69.622413` |
| S2_lexical_diversity | `46.568148` |
| S3_structural | `78.236711` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.745887 | 14.745887 |
| S5_cross_level | 1.0 | 46.915525 | 46.915525 |
| S1_morphological | 1.0 | 69.622413 | 69.622413 |
| S2_lexical_diversity | 1.0 | 46.568148 | 46.568148 |
| S3_structural | 1.0 | 78.236711 | 78.236711 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 42.730467** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `203.082842` |
| S5_cross_level | `1236.709346` |
| S1_morphological | `310.628282` |
| S2_lexical_diversity | `828.667864` |
| S3_structural | `1236.465659` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 203.082842 | 203.082842 |
| S5_cross_level | 1.0 | 1236.709346 | 1236.709346 |
| S1_morphological | 1.0 | 310.628282 | 310.628282 |
| S2_lexical_diversity | 1.0 | 828.667864 | 828.667864 |
| S3_structural | 1.0 | 1236.465659 | 1236.465659 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 635.984489** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `5.614995` |
| S5_cross_level | `17.536573` |
| S1_morphological | `28.034783` |
| S2_lexical_diversity | `29.493616` |
| S3_structural | `43.704203` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 5.614995 | 5.614995 |
| S5_cross_level | 1.0 | 17.536573 | 17.536573 |
| S1_morphological | 1.0 | 28.034783 | 28.034783 |
| S2_lexical_diversity | 1.0 | 29.493616 | 29.493616 |
| S3_structural | 1.0 | 43.704203 | 43.704203 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 20.789518** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.923121` |
| S5_cross_level | `55.798731` |
| S1_morphological | `70.392070` |
| S2_lexical_diversity | `48.468004` |
| S3_structural | `82.011067` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__frac_agglutinative', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.923121 | 14.923121 |
| S5_cross_level | 1.0 | 55.798731 | 55.798731 |
| S1_morphological | 1.0 | 70.392070 | 70.392070 |
| S2_lexical_diversity | 1.0 | 48.468004 | 48.468004 |
| S3_structural | 1.0 | 82.011067 | 82.011067 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 45.363538** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `76.269847` |
| S5_cross_level | `411.768938` |
| S1_morphological | `135.137246` |
| S2_lexical_diversity | `312.347851` |
| S3_structural | `452.502896` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 76.269847 | 76.269847 |
| S5_cross_level | 1.0 | 411.768938 | 411.768938 |
| S1_morphological | 1.0 | 135.137246 | 135.137246 |
| S2_lexical_diversity | 1.0 | 312.347851 | 312.347851 |
| S3_structural | 1.0 | 452.502896 | 452.502896 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 231.396620** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.654399` |
| S5_cross_level | `27.518214` |
| S1_morphological | `67.108485` |
| S2_lexical_diversity | `82.311347` |
| S3_structural | `153.746736` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.654399 | 11.654399 |
| S5_cross_level | 1.0 | 27.518214 | 27.518214 |
| S1_morphological | 1.0 | 67.108485 | 67.108485 |
| S2_lexical_diversity | 1.0 | 82.311347 | 82.311347 |
| S3_structural | 1.0 | 153.746736 | 153.746736 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 57.134961** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.154104` |
| S5_cross_level | `28.400123` |
| S1_morphological | `50.632170` |
| S2_lexical_diversity | `43.997610` |
| S3_structural | `85.136858` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.154104 | 10.154104 |
| S5_cross_level | 1.0 | 28.400123 | 28.400123 |
| S1_morphological | 1.0 | 50.632170 | 50.632170 |
| S2_lexical_diversity | 1.0 | 43.997610 | 43.997610 |
| S3_structural | 1.0 | 85.136858 | 85.136858 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 36.494654** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.118421` |
| S5_cross_level | `36.039713` |
| S1_morphological | `42.922617` |
| S2_lexical_diversity | `70.138367` |
| S3_structural | `74.008664` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.118421 | 9.118421 |
| S5_cross_level | 1.0 | 36.039713 | 36.039713 |
| S1_morphological | 1.0 | 42.922617 | 42.922617 |
| S2_lexical_diversity | 1.0 | 70.138367 | 70.138367 |
| S3_structural | 1.0 | 74.008664 | 74.008664 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 38.792866** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.403873` |
| S5_cross_level | `27.403911` |
| S1_morphological | `64.791696` |
| S2_lexical_diversity | `42.362727` |
| S3_structural | `78.364715` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.403873 | 11.403873 |
| S5_cross_level | 1.0 | 27.403911 | 27.403911 |
| S1_morphological | 1.0 | 64.791696 | 64.791696 |
| S2_lexical_diversity | 1.0 | 42.362727 | 42.362727 |
| S3_structural | 1.0 | 78.364715 | 78.364715 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 37.446644** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `6.217463` |
| S5_cross_level | `24.078860` |
| S1_morphological | `52.448253` |
| S2_lexical_diversity | `38.266773` |
| S3_structural | `80.411942` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 6.217463 | 6.217463 |
| S5_cross_level | 1.0 | 24.078860 | 24.078860 |
| S1_morphological | 1.0 | 52.448253 | 52.448253 |
| S2_lexical_diversity | 1.0 | 38.266773 | 38.266773 |
| S3_structural | 1.0 | 80.411942 | 80.411942 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 33.658784** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `5.753303` |
| S5_cross_level | `24.345687` |
| S1_morphological | `35.955805` |
| S2_lexical_diversity | `34.034014` |
| S3_structural | `67.509573` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 5.753303 | 5.753303 |
| S5_cross_level | 1.0 | 24.345687 | 24.345687 |
| S1_morphological | 1.0 | 35.955805 | 35.955805 |
| S2_lexical_diversity | 1.0 | 34.034014 | 34.034014 |
| S3_structural | 1.0 | 67.509573 | 67.509573 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 27.991887** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `8.020470` |
| S5_cross_level | `20.072388` |
| S1_morphological | `36.637326` |
| S2_lexical_diversity | `32.819119` |
| S3_structural | `53.340243` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 8.020470 | 8.020470 |
| S5_cross_level | 1.0 | 20.072388 | 20.072388 |
| S1_morphological | 1.0 | 36.637326 | 36.637326 |
| S2_lexical_diversity | 1.0 | 32.819119 | 32.819119 |
| S3_structural | 1.0 | 53.340243 | 53.340243 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 25.187473** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `1.667575` |
| S5_cross_level | `3.970770` |
| S1_morphological | `13.209524` |
| S2_lexical_diversity | `7.731198` |
| S3_structural | `16.130102` |
| cat (Hamming) | `0.000000` (0/17 flags differ) |

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 1.667575 | 1.667575 |
| S5_cross_level | 1.0 | 3.970770 | 3.970770 |
| S1_morphological | 1.0 | 13.209524 | 13.209524 |
| S2_lexical_diversity | 1.0 | 7.731198 | 7.731198 |
| S3_structural | 1.0 | 16.130102 | 16.130102 |
| cat | 1.0 | 0.000000 | 0.000000 |
| **Total** | Σw = 6.0000 | | **D = 7.118195** |

### §§ 4–5 · Similarity % (max_D = `635.984489`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | language-identification | `7.118195` | 98.9% | ← yes |
| 2 | amazon_reviews_multi | `20.789518` | 96.7% | ← yes |
| 3 | xnli | `25.187473` | 96.0% | ← yes |
| 4 | xlsum | `25.647184` | 96.0% |  |
| 5 | multilingual_toxicity_dataset | `26.123353` | 95.9% |  |
| 6 | multilingual_cc_news | `27.991887` | 95.6% |  |
| 7 | flores_plus | `28.540408` | 95.5% |  |
| 8 | europarl | `33.658784` | 94.7% |  |
| 9 | tweet_sentiment_multilingual | `36.494654` | 94.3% |  |
| 10 | stsb_multi_mt | `37.446644` | 94.1% |  |
| 11 | OpenLID-v2 | `38.792866` | 93.9% |  |
| 12 | massive | `39.873805` | 93.7% |  |
| 13 | mmarco | `42.730467` | 93.3% |  |
| 14 | tydiqa | `45.363538` | 92.9% |  |
| 15 | multi_eurlex | `57.134961` | 91.0% |  |
| 16 | exorde-social-media-december-2024-week1 | `231.396620` | 63.6% |  |
| 17 | wikipedia | `635.984489` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `language-identification`** — inv_d = `0.140485`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_language-identification | 0.997934 | 0 | 1.0000 | 0.140195 |
| tfidf_char_ngram_3_5_language-identification | 0.998033 | 0 | 1.0000 | 0.140209 |
| fasttext_subword_language-identification | 0.996164 | 0 | 1.0000 | 0.139946 |
| fasttext_word_language-identification | 0.870988 | 0 | 1.0000 | 0.122361 |
| lid.176_language-identification | 0.995624 | 0 | 1.0000 | 0.139870 |
| cld3_language-identification | 0.984446 | 0 | 1.0000 | 0.138300 |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.984950 | 0 | 1.0000 | 0.138371 |
| tfidf_lr_char_ngram_3_5_language-identification | 0.995288 | 0 | 1.0000 | 0.139823 |

**Neighbour: `amazon_reviews_multi`** — inv_d = `0.048101`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_amazon_reviews_multi | 0.997985 | 6 | 0.5000 | 0.024002 |
| tfidf_char_ngram_3_5_amazon_reviews_multi | 0.998090 | 6 | 0.5000 | 0.024005 |
| fasttext_subword_amazon_reviews_multi | 0.999846 | 6 | 0.5000 | 0.024047 |
| fasttext_word_amazon_reviews_multi | 0.797855 | 6 | 0.5000 | 0.019189 |
| lid.176_amazon_reviews_multi | 0.999025 | 6 | 0.5000 | 0.024027 |
| cld3_amazon_reviews_multi | 0.995041 | 6 | 0.5000 | 0.023931 |
| bow_maxabs_lr_char_ngram_3_5_amazon_reviews_multi | 0.996443 | 6 | 0.5000 | 0.023965 |
| tfidf_lr_char_ngram_3_5_amazon_reviews_multi | 0.999060 | 6 | 0.5000 | 0.024028 |

**Neighbour: `xnli`** — inv_d = `0.039702`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_xnli | 0.995875 | 5 | 0.5833 | 0.023064 |
| tfidf_char_ngram_3_5_xnli | 0.995832 | 5 | 0.5833 | 0.023063 |
| fasttext_subword_xnli | 0.999558 | 5 | 0.5833 | 0.023149 |
| fasttext_word_xnli | 0.998835 | 5 | 0.5833 | 0.023133 |
| lid.176_xnli | 0.998968 | 5 | 0.5833 | 0.023136 |
| cld3_xnli | 0.989093 | 5 | 0.5833 | 0.022907 |
| bow_maxabs_lr_char_ngram_3_5_xnli | 0.999195 | 5 | 0.5833 | 0.023141 |
| tfidf_lr_char_ngram_3_5_xnli | 0.999401 | 5 | 0.5833 | 0.023146 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_amazon_reviews_multi | 0.024002 | 0.048101 | **0.498993** |
| bow_char_ngram_3_5_language-identification | 0.140195 | 0.140485 | **0.997934** |
| bow_char_ngram_3_5_xnli | 0.023064 | 0.039702 | **0.580927** |
| bow_maxabs_lr_char_ngram_3_5_amazon_reviews_multi | 0.023965 | 0.048101 | **0.498221** |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.138371 | 0.140485 | **0.984950** |
| bow_maxabs_lr_char_ngram_3_5_xnli | 0.023141 | 0.039702 | **0.582864** |
| cld3_amazon_reviews_multi | 0.023931 | 0.048101 | **0.497520** |
| cld3_language-identification | 0.138300 | 0.140485 | **0.984446** |
| cld3_xnli | 0.022907 | 0.039702 | **0.576971** |
| fasttext_subword_amazon_reviews_multi | 0.024047 | 0.048101 | **0.499923** |
| fasttext_subword_language-identification | 0.139946 | 0.140485 | **0.996164** |
| fasttext_subword_xnli | 0.023149 | 0.039702 | **0.583075** |
| fasttext_word_amazon_reviews_multi | 0.019189 | 0.048101 | **0.398927** |
| fasttext_word_language-identification | 0.122361 | 0.140485 | **0.870988** |
| fasttext_word_xnli | 0.023133 | 0.039702 | **0.582654** |
| lid.176_amazon_reviews_multi | 0.024027 | 0.048101 | **0.499512** |
| lid.176_language-identification | 0.139870 | 0.140485 | **0.995624** |
| lid.176_xnli | 0.023136 | 0.039702 | **0.582731** |
| tfidf_char_ngram_3_5_amazon_reviews_multi | 0.024005 | 0.048101 | **0.499045** |
| tfidf_char_ngram_3_5_language-identification | 0.140209 | 0.140485 | **0.998033** |
| tfidf_char_ngram_3_5_xnli | 0.023063 | 0.039702 | **0.580902** |
| tfidf_lr_char_ngram_3_5_amazon_reviews_multi | 0.024028 | 0.048101 | **0.499530** |
| tfidf_lr_char_ngram_3_5_language-identification | 0.139823 | 0.140485 | **0.995288** |
| tfidf_lr_char_ngram_3_5_xnli | 0.023146 | 0.039702 | **0.582984** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `tfidf_char_ngram_3_5_language-identification`

---

## Dataset: `massive`

**Query languages:** `['ca', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'hr', 'it', 'ja', 'ko', 'lt', 'nl', 'pl', 'pt', 'ro', 'ru', 'sl', 'sv', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `15.659760` |
| S5_cross_level | `61.023116` |
| S1_morphological | `52.350488` |
| S2_lexical_diversity | `57.228280` |
| S3_structural | `86.068974` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 15.659760 | 15.659760 |
| S5_cross_level | 1.0 | 61.023116 | 61.023116 |
| S1_morphological | 1.0 | 52.350488 | 52.350488 |
| S2_lexical_diversity | 1.0 | 57.228280 | 57.228280 |
| S3_structural | 1.0 | 86.068974 | 86.068974 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 45.457064** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.784105` |
| S5_cross_level | `19.289878` |
| S1_morphological | `7.837021` |
| S2_lexical_diversity | `22.142939` |
| S3_structural | `34.742026` |
| cat (Hamming) | `0.176471` (3/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.784105 | 14.784105 |
| S5_cross_level | 1.0 | 19.289878 | 19.289878 |
| S1_morphological | 1.0 | 7.837021 | 7.837021 |
| S2_lexical_diversity | 1.0 | 22.142939 | 22.142939 |
| S3_structural | 1.0 | 34.742026 | 34.742026 |
| cat | 1.0 | 0.176471 | 0.176471 |
| **Total** | Σw = 6.0000 | | **D = 16.495407** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `20.147121` |
| S5_cross_level | `49.218180` |
| S1_morphological | `40.934066` |
| S2_lexical_diversity | `46.785499` |
| S3_structural | `68.199376` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 20.147121 | 20.147121 |
| S5_cross_level | 1.0 | 49.218180 | 49.218180 |
| S1_morphological | 1.0 | 40.934066 | 40.934066 |
| S2_lexical_diversity | 1.0 | 46.785499 | 46.785499 |
| S3_structural | 1.0 | 68.199376 | 68.199376 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 37.606197** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `20.001463` |
| S5_cross_level | `51.266279` |
| S1_morphological | `50.174615` |
| S2_lexical_diversity | `60.262331` |
| S3_structural | `87.716275` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 20.001463 | 20.001463 |
| S5_cross_level | 1.0 | 51.266279 | 51.266279 |
| S1_morphological | 1.0 | 50.174615 | 50.174615 |
| S2_lexical_diversity | 1.0 | 60.262331 | 60.262331 |
| S3_structural | 1.0 | 87.716275 | 87.716275 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 44.962317** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `15.829984` |
| S5_cross_level | `22.312471` |
| S1_morphological | `26.616774` |
| S2_lexical_diversity | `31.013417` |
| S3_structural | `57.776166` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 15.829984 | 15.829984 |
| S5_cross_level | 1.0 | 22.312471 | 22.312471 |
| S1_morphological | 1.0 | 26.616774 | 26.616774 |
| S2_lexical_diversity | 1.0 | 31.013417 | 31.013417 |
| S3_structural | 1.0 | 57.776166 | 57.776166 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 25.660096** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `200.677385` |
| S5_cross_level | `1232.567165` |
| S1_morphological | `319.903254` |
| S2_lexical_diversity | `832.192690` |
| S3_structural | `1249.650254` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 200.677385 | 200.677385 |
| S5_cross_level | 1.0 | 1232.567165 | 1232.567165 |
| S1_morphological | 1.0 | 319.903254 | 319.903254 |
| S2_lexical_diversity | 1.0 | 832.192690 | 832.192690 |
| S3_structural | 1.0 | 1249.650254 | 1249.650254 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 639.184732** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `19.981705` |
| S5_cross_level | `51.684172` |
| S1_morphological | `68.295998` |
| S2_lexical_diversity | `66.066246` |
| S3_structural | `92.349593` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 19.981705 | 19.981705 |
| S5_cross_level | 1.0 | 51.684172 | 51.684172 |
| S1_morphological | 1.0 | 68.295998 | 68.295998 |
| S2_lexical_diversity | 1.0 | 66.066246 | 66.066246 |
| S3_structural | 1.0 | 92.349593 | 92.349593 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 49.808050** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `15.796207` |
| S5_cross_level | `28.007356` |
| S1_morphological | `34.906528` |
| S2_lexical_diversity | `33.529072` |
| S3_structural | `65.580415` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 15.796207 | 15.796207 |
| S5_cross_level | 1.0 | 28.007356 | 28.007356 |
| S1_morphological | 1.0 | 34.906528 | 34.906528 |
| S2_lexical_diversity | 1.0 | 33.529072 | 33.529072 |
| S3_structural | 1.0 | 65.580415 | 65.580415 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 29.715028** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `73.863756` |
| S5_cross_level | `409.465595` |
| S1_morphological | `152.268708` |
| S2_lexical_diversity | `318.263192` |
| S3_structural | `468.189202` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 73.863756 | 73.863756 |
| S5_cross_level | 1.0 | 409.465595 | 409.465595 |
| S1_morphological | 1.0 | 152.268708 | 152.268708 |
| S2_lexical_diversity | 1.0 | 318.263192 | 318.263192 |
| S3_structural | 1.0 | 468.189202 | 468.189202 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 237.028017** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.387015` |
| S5_cross_level | `56.368500` |
| S1_morphological | `46.515499` |
| S2_lexical_diversity | `100.244691` |
| S3_structural | `160.045774` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.387015 | 16.387015 |
| S5_cross_level | 1.0 | 56.368500 | 56.368500 |
| S1_morphological | 1.0 | 46.515499 | 46.515499 |
| S2_lexical_diversity | 1.0 | 100.244691 | 100.244691 |
| S3_structural | 1.0 | 160.045774 | 160.045774 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 63.368090** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.637150` |
| S5_cross_level | `59.519144` |
| S1_morphological | `57.076929` |
| S2_lexical_diversity | `58.082866` |
| S3_structural | `99.922721` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.637150 | 12.637150 |
| S5_cross_level | 1.0 | 59.519144 | 59.519144 |
| S1_morphological | 1.0 | 57.076929 | 57.076929 |
| S2_lexical_diversity | 1.0 | 58.082866 | 58.082866 |
| S3_structural | 1.0 | 99.922721 | 99.922721 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 47.990782** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.651294` |
| S5_cross_level | `58.527212` |
| S1_morphological | `38.814897` |
| S2_lexical_diversity | `68.137239` |
| S3_structural | `63.362251` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.651294 | 12.651294 |
| S5_cross_level | 1.0 | 58.527212 | 58.527212 |
| S1_morphological | 1.0 | 38.814897 | 38.814897 |
| S2_lexical_diversity | 1.0 | 68.137239 | 68.137239 |
| S3_structural | 1.0 | 63.362251 | 63.362251 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 40.307639** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.469928` |
| S5_cross_level | `50.464356` |
| S1_morphological | `33.029597` |
| S2_lexical_diversity | `42.078293` |
| S3_structural | `73.429729` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.469928 | 16.469928 |
| S5_cross_level | 1.0 | 50.464356 | 50.464356 |
| S1_morphological | 1.0 | 33.029597 | 33.029597 |
| S2_lexical_diversity | 1.0 | 42.078293 | 42.078293 |
| S3_structural | 1.0 | 73.429729 | 73.429729 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 35.980611** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.929623` |
| S5_cross_level | `54.854550` |
| S1_morphological | `54.098139` |
| S2_lexical_diversity | `49.317285` |
| S3_structural | `85.361769` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.929623 | 16.929623 |
| S5_cross_level | 1.0 | 54.854550 | 54.854550 |
| S1_morphological | 1.0 | 54.098139 | 54.098139 |
| S2_lexical_diversity | 1.0 | 49.317285 | 49.317285 |
| S3_structural | 1.0 | 85.361769 | 85.361769 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 43.534737** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.146532` |
| S5_cross_level | `56.673575` |
| S1_morphological | `53.631676` |
| S2_lexical_diversity | `58.759843` |
| S3_structural | `88.923031` |
| cat (Hamming) | `0.000000` (0/17 flags differ) |

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.146532 | 16.146532 |
| S5_cross_level | 1.0 | 56.673575 | 56.673575 |
| S1_morphological | 1.0 | 53.631676 | 53.631676 |
| S2_lexical_diversity | 1.0 | 58.759843 | 58.759843 |
| S3_structural | 1.0 | 88.923031 | 88.923031 |
| cat | 1.0 | 0.000000 | 0.000000 |
| **Total** | Σw = 6.0000 | | **D = 45.689110** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `17.684241` |
| S5_cross_level | `48.404981` |
| S1_morphological | `44.603468` |
| S2_lexical_diversity | `54.241917` |
| S3_structural | `72.471248` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 17.684241 | 17.684241 |
| S5_cross_level | 1.0 | 48.404981 | 48.404981 |
| S1_morphological | 1.0 | 44.603468 | 44.603468 |
| S2_lexical_diversity | 1.0 | 54.241917 | 54.241917 |
| S3_structural | 1.0 | 72.471248 | 72.471248 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 39.626466** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.546558` |
| S5_cross_level | `44.565205` |
| S1_morphological | `57.431049` |
| S2_lexical_diversity | `48.316757` |
| S3_structural | `70.803732` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.546558 | 16.546558 |
| S5_cross_level | 1.0 | 44.565205 | 44.565205 |
| S1_morphological | 1.0 | 57.431049 | 57.431049 |
| S2_lexical_diversity | 1.0 | 48.316757 | 48.316757 |
| S3_structural | 1.0 | 70.803732 | 70.803732 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 39.669374** |

### §§ 4–5 · Similarity % (max_D = `639.184732`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | massive | `16.495407` | 97.4% | ← yes |
| 2 | mmarco | `25.660096` | 96.0% | ← yes |
| 3 | tydiqa | `29.715028` | 95.4% | ← yes |
| 4 | stsb_multi_mt | `35.980611` | 94.4% |  |
| 5 | flores_plus | `37.606197` | 94.1% |  |
| 6 | xnli | `39.626466` | 93.8% |  |
| 7 | language-identification | `39.669374` | 93.8% |  |
| 8 | OpenLID-v2 | `40.307639` | 93.7% |  |
| 9 | europarl | `43.534737` | 93.2% |  |
| 10 | xlsum | `44.962317` | 93.0% |  |
| 11 | multilingual_toxicity_dataset | `45.457064` | 92.9% |  |
| 12 | multilingual_cc_news | `45.689110` | 92.9% |  |
| 13 | tweet_sentiment_multilingual | `47.990782` | 92.5% |  |
| 14 | amazon_reviews_multi | `49.808050` | 92.2% |  |
| 15 | multi_eurlex | `63.368090` | 90.1% |  |
| 16 | exorde-social-media-december-2024-week1 | `237.028017` | 62.9% |  |
| 17 | wikipedia | `639.184732` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `massive`** — inv_d = `0.060623`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_massive | 0.990937 | 3 | 0.8571 | 0.051492 |
| tfidf_char_ngram_3_5_massive | 0.991145 | 3 | 0.8571 | 0.051502 |
| fasttext_subword_massive | 0.997546 | 3 | 0.8571 | 0.051835 |
| fasttext_word_massive | 0.934868 | 3 | 0.8571 | 0.048578 |
| lid.176_massive | 0.979587 | 3 | 0.8571 | 0.050902 |
| cld3_massive | 0.958160 | 3 | 0.8571 | 0.049788 |
| bow_maxabs_lr_char_ngram_3_5_massive | 0.986331 | 3 | 0.8571 | 0.051252 |
| tfidf_lr_char_ngram_3_5_massive | 0.990836 | 3 | 0.8571 | 0.051486 |

**Neighbour: `mmarco`** — inv_d = `0.038971`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_mmarco | 0.974607 | 11 | 0.4762 | 0.018086 |
| tfidf_char_ngram_3_5_mmarco | 0.973939 | 11 | 0.4762 | 0.018074 |
| fasttext_subword_mmarco | 0.997353 | 11 | 0.4762 | 0.018509 |
| fasttext_word_mmarco | 0.894916 | 11 | 0.4762 | 0.016608 |
| lid.176_mmarco | 0.986219 | 11 | 0.4762 | 0.018302 |
| cld3_mmarco | 0.945066 | 11 | 0.4762 | 0.017538 |
| bow_maxabs_lr_char_ngram_3_5_mmarco | 0.983976 | 11 | 0.4762 | 0.018260 |
| tfidf_lr_char_ngram_3_5_mmarco | 0.987481 | 11 | 0.4762 | 0.018325 |

**Neighbour: `tydiqa`** — inv_d = `0.033653`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_tydiqa | 0.998541 | 16 | 0.2381 | 0.008001 |
| tfidf_char_ngram_3_5_tydiqa | 0.998386 | 16 | 0.2381 | 0.008000 |
| fasttext_subword_tydiqa | 0.999769 | 16 | 0.2381 | 0.008011 |
| fasttext_word_tydiqa | 0.986141 | 16 | 0.2381 | 0.007902 |
| lid.176_tydiqa | 0.998998 | 16 | 0.2381 | 0.008005 |
| cld3_tydiqa | 0.968602 | 16 | 0.2381 | 0.007761 |
| bow_maxabs_lr_char_ngram_3_5_tydiqa | 0.996303 | 16 | 0.2381 | 0.007983 |
| tfidf_lr_char_ngram_3_5_tydiqa | 0.998230 | 16 | 0.2381 | 0.007998 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_massive | 0.051492 | 0.060623 | **0.849375** |
| bow_char_ngram_3_5_mmarco | 0.018086 | 0.038971 | **0.464099** |
| bow_char_ngram_3_5_tydiqa | 0.008001 | 0.033653 | **0.237748** |
| bow_maxabs_lr_char_ngram_3_5_massive | 0.051252 | 0.060623 | **0.845427** |
| bow_maxabs_lr_char_ngram_3_5_mmarco | 0.018260 | 0.038971 | **0.468560** |
| bow_maxabs_lr_char_ngram_3_5_tydiqa | 0.007983 | 0.033653 | **0.237215** |
| cld3_massive | 0.049788 | 0.060623 | **0.821280** |
| cld3_mmarco | 0.017538 | 0.038971 | **0.450031** |
| cld3_tydiqa | 0.007761 | 0.033653 | **0.230620** |
| fasttext_subword_massive | 0.051835 | 0.060623 | **0.855039** |
| fasttext_subword_mmarco | 0.018509 | 0.038971 | **0.474930** |
| fasttext_subword_tydiqa | 0.008011 | 0.033653 | **0.238040** |
| fasttext_word_massive | 0.048578 | 0.060623 | **0.801315** |
| fasttext_word_mmarco | 0.016608 | 0.038971 | **0.426150** |
| fasttext_word_tydiqa | 0.007902 | 0.033653 | **0.234795** |
| lid.176_massive | 0.050902 | 0.060623 | **0.839646** |
| lid.176_mmarco | 0.018302 | 0.038971 | **0.469628** |
| lid.176_tydiqa | 0.008005 | 0.033653 | **0.237857** |
| tfidf_char_ngram_3_5_massive | 0.051502 | 0.060623 | **0.849553** |
| tfidf_char_ngram_3_5_mmarco | 0.018074 | 0.038971 | **0.463780** |
| tfidf_char_ngram_3_5_tydiqa | 0.008000 | 0.033653 | **0.237711** |
| tfidf_lr_char_ngram_3_5_massive | 0.051486 | 0.060623 | **0.849288** |
| tfidf_lr_char_ngram_3_5_mmarco | 0.018325 | 0.038971 | **0.470229** |
| tfidf_lr_char_ngram_3_5_tydiqa | 0.007998 | 0.033653 | **0.237674** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_massive`

---

## Dataset: `mmarco`

**Query languages:** `['de', 'el', 'en', 'es', 'fr', 'it', 'ja', 'nl', 'pt', 'ru', 'sv', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `18.156800` |
| S5_cross_level | `63.471636` |
| S1_morphological | `52.051951` |
| S2_lexical_diversity | `192.820795` |
| S3_structural | `88.230842` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 18.156800 | 18.156800 |
| S5_cross_level | 1.0 | 63.471636 | 63.471636 |
| S1_morphological | 1.0 | 52.051951 | 52.051951 |
| S2_lexical_diversity | 1.0 | 192.820795 | 192.820795 |
| S3_structural | 1.0 | 88.230842 | 88.230842 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 69.171024** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.087319` |
| S5_cross_level | `34.633582` |
| S1_morphological | `38.807230` |
| S2_lexical_diversity | `187.426713` |
| S3_structural | `34.607741` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.087319 | 12.087319 |
| S5_cross_level | 1.0 | 34.633582 | 34.633582 |
| S1_morphological | 1.0 | 38.807230 | 38.807230 |
| S2_lexical_diversity | 1.0 | 187.426713 | 187.426713 |
| S3_structural | 1.0 | 34.607741 | 34.607741 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 51.319254** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `20.769871` |
| S5_cross_level | `58.214165` |
| S1_morphological | `48.415153` |
| S2_lexical_diversity | `192.982371` |
| S3_structural | `61.903704` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 20.769871 | 20.769871 |
| S5_cross_level | 1.0 | 58.214165 | 58.214165 |
| S1_morphological | 1.0 | 48.415153 | 48.415153 |
| S2_lexical_diversity | 1.0 | 192.982371 | 192.982371 |
| S3_structural | 1.0 | 61.903704 | 61.903704 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 63.802446** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `23.043418` |
| S5_cross_level | `55.511784` |
| S1_morphological | `41.472312` |
| S2_lexical_diversity | `196.432120` |
| S3_structural | `86.442620` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 23.043418 | 23.043418 |
| S5_cross_level | 1.0 | 55.511784 | 55.511784 |
| S1_morphological | 1.0 | 41.472312 | 41.472312 |
| S2_lexical_diversity | 1.0 | 196.432120 | 196.432120 |
| S3_structural | 1.0 | 86.442620 | 86.442620 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 67.199395** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.281727` |
| S5_cross_level | `37.378320` |
| S1_morphological | `34.832120` |
| S2_lexical_diversity | `188.058149` |
| S3_structural | `37.028180` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.281727 | 14.281727 |
| S5_cross_level | 1.0 | 37.378320 | 37.378320 |
| S1_morphological | 1.0 | 34.832120 | 34.832120 |
| S2_lexical_diversity | 1.0 | 188.058149 | 188.058149 |
| S3_structural | 1.0 | 37.028180 | 37.028180 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 51.978769** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `202.193629` |
| S5_cross_level | `1227.485837` |
| S1_morphological | `317.615282` |
| S2_lexical_diversity | `823.986286` |
| S3_structural | `1260.386238` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 202.193629 | 202.193629 |
| S5_cross_level | 1.0 | 1227.485837 | 1227.485837 |
| S1_morphological | 1.0 | 317.615282 | 317.615282 |
| S2_lexical_diversity | 1.0 | 823.986286 | 823.986286 |
| S3_structural | 1.0 | 1260.386238 | 1260.386238 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 638.670035** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `22.159561` |
| S5_cross_level | `57.490510` |
| S1_morphological | `65.434118` |
| S2_lexical_diversity | `198.751075` |
| S3_structural | `82.423694` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 22.159561 | 22.159561 |
| S5_cross_level | 1.0 | 57.490510 | 57.490510 |
| S1_morphological | 1.0 | 65.434118 | 65.434118 |
| S2_lexical_diversity | 1.0 | 198.751075 | 198.751075 |
| S3_structural | 1.0 | 82.423694 | 82.423694 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 71.101983** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `13.012463` |
| S5_cross_level | `38.013266` |
| S1_morphological | `44.831870` |
| S2_lexical_diversity | `188.334313` |
| S3_structural | `54.061657` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__frac_agglutinative', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 13.012463 | 13.012463 |
| S5_cross_level | 1.0 | 38.013266 | 38.013266 |
| S1_morphological | 1.0 | 44.831870 | 44.831870 |
| S2_lexical_diversity | 1.0 | 188.334313 | 188.334313 |
| S3_structural | 1.0 | 54.061657 | 54.061657 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 56.473634** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `75.550803` |
| S5_cross_level | `404.305435` |
| S1_morphological | `147.482288` |
| S2_lexical_diversity | `344.632020` |
| S3_structural | `479.254343` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 75.550803 | 75.550803 |
| S5_cross_level | 1.0 | 404.305435 | 404.305435 |
| S1_morphological | 1.0 | 147.482288 | 147.482288 |
| S2_lexical_diversity | 1.0 | 344.632020 | 344.632020 |
| S3_structural | 1.0 | 479.254343 | 479.254343 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 241.929638** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `21.638542` |
| S5_cross_level | `57.343757` |
| S1_morphological | `48.749333` |
| S2_lexical_diversity | `183.625505` |
| S3_structural | `165.715778` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 21.638542 | 21.638542 |
| S5_cross_level | 1.0 | 57.343757 | 57.343757 |
| S1_morphological | 1.0 | 48.749333 | 48.749333 |
| S2_lexical_diversity | 1.0 | 183.625505 | 183.625505 |
| S3_structural | 1.0 | 165.715778 | 165.715778 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 79.590584** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.390651` |
| S5_cross_level | `61.001370` |
| S1_morphological | `58.253515` |
| S2_lexical_diversity | `194.295750` |
| S3_structural | `106.621235` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.390651 | 16.390651 |
| S5_cross_level | 1.0 | 61.001370 | 61.001370 |
| S1_morphological | 1.0 | 58.253515 | 58.253515 |
| S2_lexical_diversity | 1.0 | 194.295750 | 194.295750 |
| S3_structural | 1.0 | 106.621235 | 106.621235 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 72.868263** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.759654` |
| S5_cross_level | `62.145767` |
| S1_morphological | `46.185632` |
| S2_lexical_diversity | `125.934394` |
| S3_structural | `69.897586` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.759654 | 12.759654 |
| S5_cross_level | 1.0 | 62.145767 | 62.145767 |
| S1_morphological | 1.0 | 46.185632 | 46.185632 |
| S2_lexical_diversity | 1.0 | 125.934394 | 125.934394 |
| S3_structural | 1.0 | 69.897586 | 69.897586 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 52.908741** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `17.068606` |
| S5_cross_level | `61.782310` |
| S1_morphological | `38.567711` |
| S2_lexical_diversity | `192.185007` |
| S3_structural | `64.646336` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 17.068606 | 17.068606 |
| S5_cross_level | 1.0 | 61.782310 | 61.782310 |
| S1_morphological | 1.0 | 38.567711 | 38.567711 |
| S2_lexical_diversity | 1.0 | 192.185007 | 192.185007 |
| S3_structural | 1.0 | 64.646336 | 64.646336 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 62.433819** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `18.092387` |
| S5_cross_level | `64.611322` |
| S1_morphological | `62.499905` |
| S2_lexical_diversity | `197.112162` |
| S3_structural | `85.107253` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 18.092387 | 18.092387 |
| S5_cross_level | 1.0 | 64.611322 | 64.611322 |
| S1_morphological | 1.0 | 62.499905 | 62.499905 |
| S2_lexical_diversity | 1.0 | 197.112162 | 197.112162 |
| S3_structural | 1.0 | 85.107253 | 85.107253 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 71.325407** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `19.375742` |
| S5_cross_level | `57.556728` |
| S1_morphological | `49.121073` |
| S2_lexical_diversity | `187.289926` |
| S3_structural | `93.963949` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 19.375742 | 19.375742 |
| S5_cross_level | 1.0 | 57.556728 | 57.556728 |
| S1_morphological | 1.0 | 49.121073 | 49.121073 |
| S2_lexical_diversity | 1.0 | 187.289926 | 187.289926 |
| S3_structural | 1.0 | 93.963949 | 93.963949 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 67.943393** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `19.794171` |
| S5_cross_level | `58.739955` |
| S1_morphological | `50.283929` |
| S2_lexical_diversity | `194.015765` |
| S3_structural | `80.541786` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 19.794171 | 19.794171 |
| S5_cross_level | 1.0 | 58.739955 | 58.739955 |
| S1_morphological | 1.0 | 50.283929 | 50.283929 |
| S2_lexical_diversity | 1.0 | 194.015765 | 194.015765 |
| S3_structural | 1.0 | 80.541786 | 80.541786 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 67.268483** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `17.177457` |
| S5_cross_level | `50.740162` |
| S1_morphological | `57.140497` |
| S2_lexical_diversity | `188.106737` |
| S3_structural | `67.112635` |
| cat (Hamming) | `0.000000` (0/17 flags differ) |

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 17.177457 | 17.177457 |
| S5_cross_level | 1.0 | 50.740162 | 50.740162 |
| S1_morphological | 1.0 | 57.140497 | 57.140497 |
| S2_lexical_diversity | 1.0 | 188.106737 | 188.106737 |
| S3_structural | 1.0 | 67.112635 | 67.112635 |
| cat | 1.0 | 0.000000 | 0.000000 |
| **Total** | Σw = 6.0000 | | **D = 63.379581** |

### §§ 4–5 · Similarity % (max_D = `638.670035`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | massive | `51.319254` | 92.0% | ← yes |
| 2 | mmarco | `51.978769` | 91.9% | ← yes |
| 3 | OpenLID-v2 | `52.908741` | 91.7% | ← yes |
| 4 | tydiqa | `56.473634` | 91.2% |  |
| 5 | stsb_multi_mt | `62.433819` | 90.2% |  |
| 6 | language-identification | `63.379581` | 90.1% |  |
| 7 | flores_plus | `63.802446` | 90.0% |  |
| 8 | xlsum | `67.199395` | 89.5% |  |
| 9 | xnli | `67.268483` | 89.5% |  |
| 10 | multilingual_cc_news | `67.943393` | 89.4% |  |
| 11 | multilingual_toxicity_dataset | `69.171024` | 89.2% |  |
| 12 | amazon_reviews_multi | `71.101983` | 88.9% |  |
| 13 | europarl | `71.325407` | 88.8% |  |
| 14 | tweet_sentiment_multilingual | `72.868263` | 88.6% |  |
| 15 | multi_eurlex | `79.590584` | 87.5% |  |
| 16 | exorde-social-media-december-2024-week1 | `241.929638` | 62.1% |  |
| 17 | wikipedia | `638.670035` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `massive`** — inv_d = `0.019486`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_massive | 0.990937 | 0 | 1.0000 | 0.019309 |
| tfidf_char_ngram_3_5_massive | 0.991145 | 0 | 1.0000 | 0.019313 |
| fasttext_subword_massive | 0.997546 | 0 | 1.0000 | 0.019438 |
| fasttext_word_massive | 0.934868 | 0 | 1.0000 | 0.018217 |
| lid.176_massive | 0.979587 | 0 | 1.0000 | 0.019088 |
| cld3_massive | 0.958160 | 0 | 1.0000 | 0.018671 |
| bow_maxabs_lr_char_ngram_3_5_massive | 0.986331 | 0 | 1.0000 | 0.019220 |
| tfidf_lr_char_ngram_3_5_massive | 0.990836 | 0 | 1.0000 | 0.019307 |

**Neighbour: `mmarco`** — inv_d = `0.019239`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_mmarco | 0.974607 | 2 | 0.8333 | 0.015625 |
| tfidf_char_ngram_3_5_mmarco | 0.973939 | 2 | 0.8333 | 0.015614 |
| fasttext_subword_mmarco | 0.997353 | 2 | 0.8333 | 0.015990 |
| fasttext_word_mmarco | 0.894916 | 2 | 0.8333 | 0.014347 |
| lid.176_mmarco | 0.986219 | 2 | 0.8333 | 0.015811 |
| cld3_mmarco | 0.945066 | 2 | 0.8333 | 0.015151 |
| bow_maxabs_lr_char_ngram_3_5_mmarco | 0.983976 | 2 | 0.8333 | 0.015775 |
| tfidf_lr_char_ngram_3_5_mmarco | 0.987481 | 2 | 0.8333 | 0.015831 |

**Neighbour: `OpenLID-v2`** — inv_d = `0.018900`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.980663 | 1 | 0.9167 | 0.016990 |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.981227 | 1 | 0.9167 | 0.017000 |
| fasttext_subword_OpenLID-v2 | 0.993905 | 1 | 0.9167 | 0.017220 |
| fasttext_word_OpenLID-v2 | 0.947366 | 1 | 0.9167 | 0.016414 |
| lid.176_OpenLID-v2 | 0.901862 | 1 | 0.9167 | 0.015625 |
| cld3_OpenLID-v2 | 0.939038 | 1 | 0.9167 | 0.016269 |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.981563 | 1 | 0.9167 | 0.017006 |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.983798 | 1 | 0.9167 | 0.017045 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.016990 | 0.018900 | **0.898941** |
| bow_char_ngram_3_5_massive | 0.019309 | 0.019486 | **0.990937** |
| bow_char_ngram_3_5_mmarco | 0.015625 | 0.019239 | **0.812172** |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.017006 | 0.018900 | **0.899766** |
| bow_maxabs_lr_char_ngram_3_5_massive | 0.019220 | 0.019486 | **0.986331** |
| bow_maxabs_lr_char_ngram_3_5_mmarco | 0.015775 | 0.019239 | **0.819980** |
| cld3_OpenLID-v2 | 0.016269 | 0.018900 | **0.860785** |
| cld3_massive | 0.018671 | 0.019486 | **0.958160** |
| cld3_mmarco | 0.015151 | 0.019239 | **0.787555** |
| fasttext_subword_OpenLID-v2 | 0.017220 | 0.018900 | **0.911080** |
| fasttext_subword_massive | 0.019438 | 0.019486 | **0.997546** |
| fasttext_subword_mmarco | 0.015990 | 0.019239 | **0.831128** |
| fasttext_word_OpenLID-v2 | 0.016414 | 0.018900 | **0.868419** |
| fasttext_word_massive | 0.018217 | 0.019486 | **0.934868** |
| fasttext_word_mmarco | 0.014347 | 0.019239 | **0.745763** |
| lid.176_OpenLID-v2 | 0.015625 | 0.018900 | **0.826707** |
| lid.176_massive | 0.019088 | 0.019486 | **0.979587** |
| lid.176_mmarco | 0.015811 | 0.019239 | **0.821849** |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.017000 | 0.018900 | **0.899458** |
| tfidf_char_ngram_3_5_massive | 0.019313 | 0.019486 | **0.991145** |
| tfidf_char_ngram_3_5_mmarco | 0.015614 | 0.019239 | **0.811616** |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.017045 | 0.018900 | **0.901815** |
| tfidf_lr_char_ngram_3_5_massive | 0.019307 | 0.019486 | **0.990836** |
| tfidf_lr_char_ngram_3_5_mmarco | 0.015831 | 0.019239 | **0.822901** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_massive`

---

## Dataset: `multi_eurlex`

**Query languages:** `['da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'hr', 'it', 'lt', 'nl', 'pl', 'pt', 'ro', 'sl', 'sv', 'uk']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `48.442041` |
| S5_cross_level | `53.584398` |
| S1_morphological | `60.079718` |
| S2_lexical_diversity | `226.980810` |
| S3_structural | `251.578905` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 48.442041 | 48.442041 |
| S5_cross_level | 1.0 | 53.584398 | 53.584398 |
| S1_morphological | 1.0 | 60.079718 | 60.079718 |
| S2_lexical_diversity | 1.0 | 226.980810 | 226.980810 |
| S3_structural | 1.0 | 251.578905 | 251.578905 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 106.856077** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `50.890425` |
| S5_cross_level | `49.485974` |
| S1_morphological | `42.688074` |
| S2_lexical_diversity | `229.678819` |
| S3_structural | `247.766557` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 50.890425 | 50.890425 |
| S5_cross_level | 1.0 | 49.485974 | 49.485974 |
| S1_morphological | 1.0 | 42.688074 | 42.688074 |
| S2_lexical_diversity | 1.0 | 229.678819 | 229.678819 |
| S3_structural | 1.0 | 247.766557 | 247.766557 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 103.506543** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `51.012401` |
| S5_cross_level | `50.945731` |
| S1_morphological | `44.662687` |
| S2_lexical_diversity | `220.429090` |
| S3_structural | `237.021930` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 51.012401 | 51.012401 |
| S5_cross_level | 1.0 | 50.945731 | 50.945731 |
| S1_morphological | 1.0 | 44.662687 | 44.662687 |
| S2_lexical_diversity | 1.0 | 220.429090 | 220.429090 |
| S3_structural | 1.0 | 237.021930 | 237.021930 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 100.747267** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `50.442957` |
| S5_cross_level | `43.448190` |
| S1_morphological | `45.823547` |
| S2_lexical_diversity | `209.626131` |
| S3_structural | `218.081262` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 50.442957 | 50.442957 |
| S5_cross_level | 1.0 | 43.448190 | 43.448190 |
| S1_morphological | 1.0 | 45.823547 | 45.823547 |
| S2_lexical_diversity | 1.0 | 209.626131 | 209.626131 |
| S3_structural | 1.0 | 218.081262 | 218.081262 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 94.668387** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `52.695614` |
| S5_cross_level | `52.705348` |
| S1_morphological | `46.652363` |
| S2_lexical_diversity | `235.217062` |
| S3_structural | `252.976300` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 52.695614 | 52.695614 |
| S5_cross_level | 1.0 | 52.705348 | 52.705348 |
| S1_morphological | 1.0 | 46.652363 | 46.652363 |
| S2_lexical_diversity | 1.0 | 235.217062 | 235.217062 |
| S3_structural | 1.0 | 252.976300 | 252.976300 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 106.786213** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `198.889702` |
| S5_cross_level | `1229.330396` |
| S1_morphological | `309.510757` |
| S2_lexical_diversity | `812.323692` |
| S3_structural | `1232.320550` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 198.889702 | 198.889702 |
| S5_cross_level | 1.0 | 1229.330396 | 1229.330396 |
| S1_morphological | 1.0 | 309.510757 | 309.510757 |
| S2_lexical_diversity | 1.0 | 812.323692 | 812.323692 |
| S3_structural | 1.0 | 1232.320550 | 1232.320550 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 630.493889** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `51.606345` |
| S5_cross_level | `46.451459` |
| S1_morphological | `67.504071` |
| S2_lexical_diversity | `215.106650` |
| S3_structural | `241.354173` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 51.606345 | 51.606345 |
| S5_cross_level | 1.0 | 46.451459 | 46.451459 |
| S1_morphological | 1.0 | 67.504071 | 67.504071 |
| S2_lexical_diversity | 1.0 | 215.106650 | 215.106650 |
| S3_structural | 1.0 | 241.354173 | 241.354173 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 103.768489** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `52.650970` |
| S5_cross_level | `59.320947` |
| S1_morphological | `48.237755` |
| S2_lexical_diversity | `232.371962` |
| S3_structural | `256.841231` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_languages', 'cat__has_greek', 'cat__frac_agglutinative', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 52.650970 | 52.650970 |
| S5_cross_level | 1.0 | 59.320947 | 59.320947 |
| S1_morphological | 1.0 | 48.237755 | 48.237755 |
| S2_lexical_diversity | 1.0 | 232.371962 | 232.371962 |
| S3_structural | 1.0 | 256.841231 | 256.841231 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 108.325380** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `79.504790` |
| S5_cross_level | `405.378725` |
| S1_morphological | `144.192316` |
| S2_lexical_diversity | `342.848598` |
| S3_structural | `493.068024` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 79.504790 | 79.504790 |
| S5_cross_level | 1.0 | 405.378725 | 405.378725 |
| S1_morphological | 1.0 | 144.192316 | 144.192316 |
| S2_lexical_diversity | 1.0 | 342.848598 | 342.848598 |
| S3_structural | 1.0 | 493.068024 | 493.068024 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 244.263448** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `46.171196` |
| S5_cross_level | `36.053963` |
| S1_morphological | `15.155972` |
| S2_lexical_diversity | `157.352749` |
| S3_structural | `113.815521` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_cyrillic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 46.171196 | 46.171196 |
| S5_cross_level | 1.0 | 36.053963 | 36.053963 |
| S1_morphological | 1.0 | 15.155972 | 15.155972 |
| S2_lexical_diversity | 1.0 | 157.352749 | 157.352749 |
| S3_structural | 1.0 | 113.815521 | 113.815521 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 61.464116** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `47.528254` |
| S5_cross_level | `48.756414` |
| S1_morphological | `66.051434` |
| S2_lexical_diversity | `228.789794` |
| S3_structural | `244.764440` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 47.528254 | 47.528254 |
| S5_cross_level | 1.0 | 48.756414 | 48.756414 |
| S1_morphological | 1.0 | 66.051434 | 66.051434 |
| S2_lexical_diversity | 1.0 | 228.789794 | 228.789794 |
| S3_structural | 1.0 | 244.764440 | 244.764440 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 106.050350** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `47.167394` |
| S5_cross_level | `57.551455` |
| S1_morphological | `45.373799` |
| S2_lexical_diversity | `206.233144` |
| S3_structural | `197.309416` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 47.167394 | 47.167394 |
| S5_cross_level | 1.0 | 57.551455 | 57.551455 |
| S1_morphological | 1.0 | 45.373799 | 45.373799 |
| S2_lexical_diversity | 1.0 | 206.233144 | 206.233144 |
| S3_structural | 1.0 | 197.309416 | 197.309416 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 92.341162** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `52.315480` |
| S5_cross_level | `60.669534` |
| S1_morphological | `47.071016` |
| S2_lexical_diversity | `224.353968` |
| S3_structural | `230.117537` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 52.315480 | 52.315480 |
| S5_cross_level | 1.0 | 60.669534 | 60.669534 |
| S1_morphological | 1.0 | 47.071016 | 47.071016 |
| S2_lexical_diversity | 1.0 | 224.353968 | 224.353968 |
| S3_structural | 1.0 | 230.117537 | 230.117537 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 102.509491** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `50.399571` |
| S5_cross_level | `54.031382` |
| S1_morphological | `59.518729` |
| S2_lexical_diversity | `234.779856` |
| S3_structural | `264.492683` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 50.399571 | 50.399571 |
| S5_cross_level | 1.0 | 54.031382 | 54.031382 |
| S1_morphological | 1.0 | 59.518729 | 59.518729 |
| S2_lexical_diversity | 1.0 | 234.779856 | 234.779856 |
| S3_structural | 1.0 | 264.492683 | 264.492683 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 110.586056** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `48.300953` |
| S5_cross_level | `40.155806` |
| S1_morphological | `41.650353` |
| S2_lexical_diversity | `196.072656` |
| S3_structural | `191.830032` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 48.300953 | 48.300953 |
| S5_cross_level | 1.0 | 40.155806 | 40.155806 |
| S1_morphological | 1.0 | 41.650353 | 41.650353 |
| S2_lexical_diversity | 1.0 | 196.072656 | 196.072656 |
| S3_structural | 1.0 | 191.830032 | 191.830032 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 86.433006** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `51.427883` |
| S5_cross_level | `50.425313` |
| S1_morphological | `52.707558` |
| S2_lexical_diversity | `224.702378` |
| S3_structural | `247.800928` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 51.427883 | 51.427883 |
| S5_cross_level | 1.0 | 50.425313 | 50.425313 |
| S1_morphological | 1.0 | 52.707558 | 52.707558 |
| S2_lexical_diversity | 1.0 | 224.702378 | 224.702378 |
| S3_structural | 1.0 | 247.800928 | 247.800928 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 104.598912** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `48.326498` |
| S5_cross_level | `41.315551` |
| S1_morphological | `58.390993` |
| S2_lexical_diversity | `214.251141` |
| S3_structural | `229.396841` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 48.326498 | 48.326498 |
| S5_cross_level | 1.0 | 41.315551 | 41.315551 |
| S1_morphological | 1.0 | 58.390993 | 58.390993 |
| S2_lexical_diversity | 1.0 | 214.251141 | 214.251141 |
| S3_structural | 1.0 | 229.396841 | 229.396841 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 98.682132** |

### §§ 4–5 · Similarity % (max_D = `630.493889`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | multi_eurlex | `61.464116` | 90.3% | ← yes |
| 2 | multilingual_cc_news | `86.433006` | 86.3% | ← yes |
| 3 | OpenLID-v2 | `92.341162` | 85.4% | ← yes |
| 4 | xlsum | `94.668387` | 85.0% |  |
| 5 | language-identification | `98.682132` | 84.3% |  |
| 6 | flores_plus | `100.747267` | 84.0% |  |
| 7 | stsb_multi_mt | `102.509491` | 83.7% |  |
| 8 | massive | `103.506543` | 83.6% |  |
| 9 | amazon_reviews_multi | `103.768489` | 83.5% |  |
| 10 | xnli | `104.598912` | 83.4% |  |
| 11 | tweet_sentiment_multilingual | `106.050350` | 83.2% |  |
| 12 | mmarco | `106.786213` | 83.1% |  |
| 13 | multilingual_toxicity_dataset | `106.856077` | 83.1% |  |
| 14 | tydiqa | `108.325380` | 82.8% |  |
| 15 | europarl | `110.586056` | 82.5% |  |
| 16 | exorde-social-media-december-2024-week1 | `244.263448` | 61.3% |  |
| 17 | wikipedia | `630.493889` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `multi_eurlex`** — inv_d = `0.016270`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multi_eurlex | 0.999861 | 1 | 0.9412 | 0.015310 |
| tfidf_char_ngram_3_5_multi_eurlex | 0.999873 | 1 | 0.9412 | 0.015311 |
| fasttext_subword_multi_eurlex | 0.999855 | 1 | 0.9412 | 0.015310 |
| fasttext_word_multi_eurlex | 0.999782 | 1 | 0.9412 | 0.015309 |
| lid.176_multi_eurlex | 0.993527 | 1 | 0.9412 | 0.015213 |
| cld3_multi_eurlex | 0.982966 | 1 | 0.9412 | 0.015052 |
| bow_maxabs_lr_char_ngram_3_5_multi_eurlex | 0.999861 | 1 | 0.9412 | 0.015310 |
| tfidf_lr_char_ngram_3_5_multi_eurlex | 0.999849 | 1 | 0.9412 | 0.015310 |

**Neighbour: `multilingual_cc_news`** — inv_d = `0.011570`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multilingual_cc_news | 0.975398 | 3 | 0.8235 | 0.009294 |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.976358 | 3 | 0.8235 | 0.009303 |
| fasttext_subword_multilingual_cc_news | 0.997083 | 3 | 0.8235 | 0.009500 |
| fasttext_word_multilingual_cc_news | 0.985130 | 3 | 0.8235 | 0.009386 |
| lid.176_multilingual_cc_news | 0.928836 | 3 | 0.8235 | 0.008850 |
| cld3_multilingual_cc_news | 0.955450 | 3 | 0.8235 | 0.009103 |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.975948 | 3 | 0.8235 | 0.009299 |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.979512 | 3 | 0.8235 | 0.009333 |

**Neighbour: `OpenLID-v2`** — inv_d = `0.010829`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.980663 | 0 | 1.0000 | 0.010620 |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.981227 | 0 | 1.0000 | 0.010626 |
| fasttext_subword_OpenLID-v2 | 0.993905 | 0 | 1.0000 | 0.010763 |
| fasttext_word_OpenLID-v2 | 0.947366 | 0 | 1.0000 | 0.010259 |
| lid.176_OpenLID-v2 | 0.901862 | 0 | 1.0000 | 0.009767 |
| cld3_OpenLID-v2 | 0.939038 | 0 | 1.0000 | 0.010169 |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.981563 | 0 | 1.0000 | 0.010630 |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.983798 | 0 | 1.0000 | 0.010654 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.010620 | 0.010829 | **0.980663** |
| bow_char_ngram_3_5_multi_eurlex | 0.015310 | 0.016270 | **0.941046** |
| bow_char_ngram_3_5_multilingual_cc_news | 0.009294 | 0.011570 | **0.803269** |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.010630 | 0.010829 | **0.981563** |
| bow_maxabs_lr_char_ngram_3_5_multi_eurlex | 0.015310 | 0.016270 | **0.941046** |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.009299 | 0.011570 | **0.803722** |
| cld3_OpenLID-v2 | 0.010169 | 0.010829 | **0.939038** |
| cld3_multi_eurlex | 0.015052 | 0.016270 | **0.925144** |
| cld3_multilingual_cc_news | 0.009103 | 0.011570 | **0.786841** |
| fasttext_subword_OpenLID-v2 | 0.010763 | 0.010829 | **0.993905** |
| fasttext_subword_multi_eurlex | 0.015310 | 0.016270 | **0.941040** |
| fasttext_subword_multilingual_cc_news | 0.009500 | 0.011570 | **0.821127** |
| fasttext_word_OpenLID-v2 | 0.010259 | 0.010829 | **0.947366** |
| fasttext_word_multi_eurlex | 0.015309 | 0.016270 | **0.940971** |
| fasttext_word_multilingual_cc_news | 0.009386 | 0.011570 | **0.811284** |
| lid.176_OpenLID-v2 | 0.009767 | 0.010829 | **0.901862** |
| lid.176_multi_eurlex | 0.015213 | 0.016270 | **0.935084** |
| lid.176_multilingual_cc_news | 0.008850 | 0.011570 | **0.764924** |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.010626 | 0.010829 | **0.981227** |
| tfidf_char_ngram_3_5_multi_eurlex | 0.015311 | 0.016270 | **0.941057** |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.009303 | 0.011570 | **0.804060** |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.010654 | 0.010829 | **0.983798** |
| tfidf_lr_char_ngram_3_5_multi_eurlex | 0.015310 | 0.016270 | **0.941034** |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.009333 | 0.011570 | **0.806657** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_OpenLID-v2`

---

## Dataset: `multilingual_cc_news`

**Query languages:** `['ca', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'hr', 'it', 'ja', 'ko', 'lt', 'mk', 'nl', 'pl', 'pt', 'ro', 'ru', 'sl', 'sv', 'uk', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `8.507910` |
| S5_cross_level | `51.578714` |
| S1_morphological | `44.738279` |
| S2_lexical_diversity | `95.378980` |
| S3_structural | `113.696108` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 8.507910 | 8.507910 |
| S5_cross_level | 1.0 | 51.578714 | 51.578714 |
| S1_morphological | 1.0 | 44.738279 | 44.738279 |
| S2_lexical_diversity | 1.0 | 95.378980 | 95.378980 |
| S3_structural | 1.0 | 113.696108 | 113.696108 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 52.385292** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `19.339267` |
| S5_cross_level | `53.967248` |
| S1_morphological | `54.215025` |
| S2_lexical_diversity | `105.499842` |
| S3_structural | `119.822859` |
| cat (Hamming) | `0.176471` (3/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 19.339267 | 19.339267 |
| S5_cross_level | 1.0 | 53.967248 | 53.967248 |
| S1_morphological | 1.0 | 54.215025 | 54.215025 |
| S2_lexical_diversity | 1.0 | 105.499842 | 105.499842 |
| S3_structural | 1.0 | 119.822859 | 119.822859 |
| cat | 1.0 | 0.176471 | 0.176471 |
| **Total** | Σw = 6.0000 | | **D = 58.836785** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `13.129888` |
| S5_cross_level | `55.495204` |
| S1_morphological | `38.765670` |
| S2_lexical_diversity | `95.961048` |
| S3_structural | `100.125924` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 13.129888 | 13.129888 |
| S5_cross_level | 1.0 | 55.495204 | 55.495204 |
| S1_morphological | 1.0 | 38.765670 | 38.765670 |
| S2_lexical_diversity | 1.0 | 95.961048 | 95.961048 |
| S3_structural | 1.0 | 100.125924 | 100.125924 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 50.628642** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `8.868502` |
| S5_cross_level | `45.000854` |
| S1_morphological | `27.619666` |
| S2_lexical_diversity | `84.371637` |
| S3_structural | `69.341768` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 8.868502 | 8.868502 |
| S5_cross_level | 1.0 | 45.000854 | 45.000854 |
| S1_morphological | 1.0 | 27.619666 | 27.619666 |
| S2_lexical_diversity | 1.0 | 84.371637 | 84.371637 |
| S3_structural | 1.0 | 69.341768 | 69.341768 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 39.259228** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `19.911191` |
| S5_cross_level | `56.755521` |
| S1_morphological | `61.746282` |
| S2_lexical_diversity | `110.145887` |
| S3_structural | `124.801306` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 19.911191 | 19.911191 |
| S5_cross_level | 1.0 | 56.755521 | 56.755521 |
| S1_morphological | 1.0 | 61.746282 | 61.746282 |
| S2_lexical_diversity | 1.0 | 110.145887 | 110.145887 |
| S3_structural | 1.0 | 124.801306 | 124.801306 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 62.295325** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `199.753495` |
| S5_cross_level | `1221.228270` |
| S1_morphological | `311.922798` |
| S2_lexical_diversity | `830.591952` |
| S3_structural | `1234.087472` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 199.753495 | 199.753495 |
| S5_cross_level | 1.0 | 1221.228270 | 1221.228270 |
| S1_morphological | 1.0 | 311.922798 | 311.922798 |
| S2_lexical_diversity | 1.0 | 830.591952 | 830.591952 |
| S3_structural | 1.0 | 1234.087472 | 1234.087472 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 632.950272** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.730268` |
| S5_cross_level | `49.768921` |
| S1_morphological | `40.671072` |
| S2_lexical_diversity | `91.673273` |
| S3_structural | `112.603667` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.730268 | 10.730268 |
| S5_cross_level | 1.0 | 49.768921 | 49.768921 |
| S1_morphological | 1.0 | 40.671072 | 40.671072 |
| S2_lexical_diversity | 1.0 | 91.673273 | 91.673273 |
| S3_structural | 1.0 | 112.603667 | 112.603667 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 50.986298** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `20.524013` |
| S5_cross_level | `63.563666` |
| S1_morphological | `60.097565` |
| S2_lexical_diversity | `104.840313` |
| S3_structural | `118.838366` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 20.524013 | 20.524013 |
| S5_cross_level | 1.0 | 63.563666 | 63.563666 |
| S1_morphological | 1.0 | 60.097565 | 60.097565 |
| S2_lexical_diversity | 1.0 | 104.840313 | 104.840313 |
| S3_structural | 1.0 | 118.838366 | 118.838366 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 61.389085** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `73.097364` |
| S5_cross_level | `397.128323` |
| S1_morphological | `139.743672` |
| S2_lexical_diversity | `322.589046` |
| S3_structural | `455.674153` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 73.097364 | 73.097364 |
| S5_cross_level | 1.0 | 397.128323 | 397.128323 |
| S1_morphological | 1.0 | 139.743672 | 139.743672 |
| S2_lexical_diversity | 1.0 | 322.589046 | 322.589046 |
| S3_structural | 1.0 | 455.674153 | 455.674153 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 231.391701** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `7.732264` |
| S5_cross_level | `41.168280` |
| S1_morphological | `49.362718` |
| S2_lexical_diversity | `75.178805` |
| S3_structural | `91.511118` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 7.732264 | 7.732264 |
| S5_cross_level | 1.0 | 41.168280 | 41.168280 |
| S1_morphological | 1.0 | 49.362718 | 49.362718 |
| S2_lexical_diversity | 1.0 | 75.178805 | 75.178805 |
| S3_structural | 1.0 | 91.511118 | 91.511118 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 44.266707** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.344693` |
| S5_cross_level | `50.680082` |
| S1_morphological | `56.693091` |
| S2_lexical_diversity | `96.536420` |
| S3_structural | `92.332111` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.344693 | 10.344693 |
| S5_cross_level | 1.0 | 50.680082 | 50.680082 |
| S1_morphological | 1.0 | 56.693091 | 56.693091 |
| S2_lexical_diversity | 1.0 | 96.536420 | 96.536420 |
| S3_structural | 1.0 | 92.332111 | 92.332111 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 51.215380** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.551243` |
| S5_cross_level | `55.629218` |
| S1_morphological | `40.535981` |
| S2_lexical_diversity | `104.912730` |
| S3_structural | `83.985605` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.551243 | 12.551243 |
| S5_cross_level | 1.0 | 55.629218 | 55.629218 |
| S1_morphological | 1.0 | 40.535981 | 40.535981 |
| S2_lexical_diversity | 1.0 | 104.912730 | 104.912730 |
| S3_structural | 1.0 | 83.985605 | 83.985605 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 49.651482** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.393696` |
| S5_cross_level | `65.242552` |
| S1_morphological | `55.470189` |
| S2_lexical_diversity | `101.431787` |
| S3_structural | `107.356294` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.393696 | 16.393696 |
| S5_cross_level | 1.0 | 65.242552 | 65.242552 |
| S1_morphological | 1.0 | 55.470189 | 55.470189 |
| S2_lexical_diversity | 1.0 | 101.431787 | 101.431787 |
| S3_structural | 1.0 | 107.356294 | 107.356294 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 57.717714** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.216751` |
| S5_cross_level | `60.569712` |
| S1_morphological | `54.088906` |
| S2_lexical_diversity | `102.658019` |
| S3_structural | `123.873286` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.216751 | 12.216751 |
| S5_cross_level | 1.0 | 60.569712 | 60.569712 |
| S1_morphological | 1.0 | 54.088906 | 54.088906 |
| S2_lexical_diversity | 1.0 | 102.658019 | 102.658019 |
| S3_structural | 1.0 | 123.873286 | 123.873286 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 59.008956** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `6.410877` |
| S5_cross_level | `38.266893` |
| S1_morphological | `13.465415` |
| S2_lexical_diversity | `72.963849` |
| S3_structural | `43.881533` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 6.410877 | 6.410877 |
| S5_cross_level | 1.0 | 38.266893 | 38.266893 |
| S1_morphological | 1.0 | 13.465415 | 13.465415 |
| S2_lexical_diversity | 1.0 | 72.963849 | 72.963849 |
| S3_structural | 1.0 | 43.881533 | 43.881533 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 29.184369** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.852241` |
| S5_cross_level | `55.279094` |
| S1_morphological | `38.478180` |
| S2_lexical_diversity | `95.298574` |
| S3_structural | `108.142690` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.852241 | 12.852241 |
| S5_cross_level | 1.0 | 55.279094 | 55.279094 |
| S1_morphological | 1.0 | 38.478180 | 38.478180 |
| S2_lexical_diversity | 1.0 | 95.298574 | 95.298574 |
| S3_structural | 1.0 | 108.142690 | 108.142690 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 51.733953** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.318291` |
| S5_cross_level | `45.008328` |
| S1_morphological | `32.710122` |
| S2_lexical_diversity | `86.401506` |
| S3_structural | `93.666188` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.318291 | 10.318291 |
| S5_cross_level | 1.0 | 45.008328 | 45.008328 |
| S1_morphological | 1.0 | 32.710122 | 32.710122 |
| S2_lexical_diversity | 1.0 | 86.401506 | 86.401506 |
| S3_structural | 1.0 | 93.666188 | 93.666188 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 44.742896** |

### §§ 4–5 · Similarity % (max_D = `632.950272`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | multilingual_cc_news | `29.184369` | 95.4% | ← yes |
| 2 | xlsum | `39.259228` | 93.8% | ← yes |
| 3 | multi_eurlex | `44.266707` | 93.0% | ← yes |
| 4 | language-identification | `44.742896` | 92.9% |  |
| 5 | OpenLID-v2 | `49.651482` | 92.2% |  |
| 6 | flores_plus | `50.628642` | 92.0% |  |
| 7 | amazon_reviews_multi | `50.986298` | 91.9% |  |
| 8 | tweet_sentiment_multilingual | `51.215380` | 91.9% |  |
| 9 | xnli | `51.733953` | 91.8% |  |
| 10 | multilingual_toxicity_dataset | `52.385292` | 91.7% |  |
| 11 | stsb_multi_mt | `57.717714` | 90.9% |  |
| 12 | massive | `58.836785` | 90.7% |  |
| 13 | europarl | `59.008956` | 90.7% |  |
| 14 | tydiqa | `61.389085` | 90.3% |  |
| 15 | mmarco | `62.295325` | 90.2% |  |
| 16 | exorde-social-media-december-2024-week1 | `231.391701` | 63.4% |  |
| 17 | wikipedia | `632.950272` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `multilingual_cc_news`** — inv_d = `0.034265`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multilingual_cc_news | 0.975398 | 3 | 0.8696 | 0.029063 |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.976358 | 3 | 0.8696 | 0.029091 |
| fasttext_subword_multilingual_cc_news | 0.997083 | 3 | 0.8696 | 0.029709 |
| fasttext_word_multilingual_cc_news | 0.985130 | 3 | 0.8696 | 0.029353 |
| lid.176_multilingual_cc_news | 0.928836 | 3 | 0.8696 | 0.027675 |
| cld3_multilingual_cc_news | 0.955450 | 3 | 0.8696 | 0.028468 |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.975948 | 3 | 0.8696 | 0.029079 |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.979512 | 3 | 0.8696 | 0.029185 |

**Neighbour: `xlsum`** — inv_d = `0.025472`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_xlsum | 0.981335 | 14 | 0.3913 | 0.009781 |
| tfidf_char_ngram_3_5_xlsum | 0.981388 | 14 | 0.3913 | 0.009782 |
| fasttext_subword_xlsum | 0.998764 | 14 | 0.3913 | 0.009955 |
| fasttext_word_xlsum | 0.974218 | 14 | 0.3913 | 0.009710 |
| lid.176_xlsum | 0.998587 | 14 | 0.3913 | 0.009953 |
| cld3_xlsum | 0.994289 | 14 | 0.3913 | 0.009910 |
| bow_maxabs_lr_char_ngram_3_5_xlsum | 0.979869 | 14 | 0.3913 | 0.009767 |
| tfidf_lr_char_ngram_3_5_xlsum | 0.981645 | 14 | 0.3913 | 0.009784 |

**Neighbour: `multi_eurlex`** — inv_d = `0.022590`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multi_eurlex | 0.999861 | 7 | 0.6957 | 0.015713 |
| tfidf_char_ngram_3_5_multi_eurlex | 0.999873 | 7 | 0.6957 | 0.015713 |
| fasttext_subword_multi_eurlex | 0.999855 | 7 | 0.6957 | 0.015713 |
| fasttext_word_multi_eurlex | 0.999782 | 7 | 0.6957 | 0.015712 |
| lid.176_multi_eurlex | 0.993527 | 7 | 0.6957 | 0.015613 |
| cld3_multi_eurlex | 0.982966 | 7 | 0.6957 | 0.015447 |
| bow_maxabs_lr_char_ngram_3_5_multi_eurlex | 0.999861 | 7 | 0.6957 | 0.015713 |
| tfidf_lr_char_ngram_3_5_multi_eurlex | 0.999849 | 7 | 0.6957 | 0.015713 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_multi_eurlex | 0.015713 | 0.022590 | **0.695555** |
| bow_char_ngram_3_5_multilingual_cc_news | 0.029063 | 0.034265 | **0.848172** |
| bow_char_ngram_3_5_xlsum | 0.009781 | 0.025472 | **0.384001** |
| bow_maxabs_lr_char_ngram_3_5_multi_eurlex | 0.015713 | 0.022590 | **0.695555** |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.029079 | 0.034265 | **0.848650** |
| bow_maxabs_lr_char_ngram_3_5_xlsum | 0.009767 | 0.025472 | **0.383427** |
| cld3_multi_eurlex | 0.015447 | 0.022590 | **0.683802** |
| cld3_multilingual_cc_news | 0.028468 | 0.034265 | **0.830826** |
| cld3_xlsum | 0.009910 | 0.025472 | **0.389070** |
| fasttext_subword_multi_eurlex | 0.015713 | 0.022590 | **0.695551** |
| fasttext_subword_multilingual_cc_news | 0.029709 | 0.034265 | **0.867029** |
| fasttext_subword_xlsum | 0.009955 | 0.025472 | **0.390821** |
| fasttext_word_multi_eurlex | 0.015712 | 0.022590 | **0.695501** |
| fasttext_word_multilingual_cc_news | 0.029353 | 0.034265 | **0.856635** |
| fasttext_word_xlsum | 0.009710 | 0.025472 | **0.381216** |
| lid.176_multi_eurlex | 0.015613 | 0.022590 | **0.691149** |
| lid.176_multilingual_cc_news | 0.027675 | 0.034265 | **0.807683** |
| lid.176_xlsum | 0.009953 | 0.025472 | **0.390751** |
| tfidf_char_ngram_3_5_multi_eurlex | 0.015713 | 0.022590 | **0.695564** |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.029091 | 0.034265 | **0.849007** |
| tfidf_char_ngram_3_5_xlsum | 0.009782 | 0.025472 | **0.384021** |
| tfidf_lr_char_ngram_3_5_multi_eurlex | 0.015713 | 0.022590 | **0.695547** |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.029185 | 0.034265 | **0.851750** |
| tfidf_lr_char_ngram_3_5_xlsum | 0.009784 | 0.025472 | **0.384122** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_multilingual_cc_news`

---

## Dataset: `multilingual_toxicity_dataset`

**Query languages:** `['de', 'el', 'en', 'es', 'fr', 'it', 'ja', 'nl', 'pt', 'ru', 'uk', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `30.817761` |
| S5_cross_level | `111.958000` |
| S1_morphological | `39.209737` |
| S2_lexical_diversity | `192.081940` |
| S3_structural | `100.978651` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 30.817761 | 30.817761 |
| S5_cross_level | 1.0 | 111.958000 | 111.958000 |
| S1_morphological | 1.0 | 39.209737 | 39.209737 |
| S2_lexical_diversity | 1.0 | 192.081940 | 192.081940 |
| S3_structural | 1.0 | 100.978651 | 100.978651 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 79.223368** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `30.974214` |
| S5_cross_level | `132.623299` |
| S1_morphological | `70.204386` |
| S2_lexical_diversity | `200.758587` |
| S3_structural | `147.257757` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 30.974214 | 30.974214 |
| S5_cross_level | 1.0 | 132.623299 | 132.623299 |
| S1_morphological | 1.0 | 70.204386 | 70.204386 |
| S2_lexical_diversity | 1.0 | 200.758587 | 200.758587 |
| S3_structural | 1.0 | 147.257757 | 147.257757 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 97.028531** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `32.762559` |
| S5_cross_level | `130.615483` |
| S1_morphological | `70.191987` |
| S2_lexical_diversity | `200.478069` |
| S3_structural | `150.723319` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 32.762559 | 32.762559 |
| S5_cross_level | 1.0 | 130.615483 | 130.615483 |
| S1_morphological | 1.0 | 70.191987 | 70.191987 |
| S2_lexical_diversity | 1.0 | 200.478069 | 200.478069 |
| S3_structural | 1.0 | 150.723319 | 150.723319 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 97.550138** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `34.613163` |
| S5_cross_level | `124.989610` |
| S1_morphological | `66.328932` |
| S2_lexical_diversity | `201.769874` |
| S3_structural | `143.426110` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 34.613163 | 34.613163 |
| S5_cross_level | 1.0 | 124.989610 | 124.989610 |
| S1_morphological | 1.0 | 66.328932 | 66.328932 |
| S2_lexical_diversity | 1.0 | 201.769874 | 201.769874 |
| S3_structural | 1.0 | 143.426110 | 143.426110 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 95.236968** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `33.303115` |
| S5_cross_level | `135.014484` |
| S1_morphological | `80.173845` |
| S2_lexical_diversity | `202.051106` |
| S3_structural | `156.819051` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 33.303115 | 33.303115 |
| S5_cross_level | 1.0 | 135.014484 | 135.014484 |
| S1_morphological | 1.0 | 80.173845 | 80.173845 |
| S2_lexical_diversity | 1.0 | 202.051106 | 202.051106 |
| S3_structural | 1.0 | 156.819051 | 156.819051 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 101.275953** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `190.574238` |
| S5_cross_level | `1157.268911` |
| S1_morphological | `268.543809` |
| S2_lexical_diversity | `768.467404` |
| S3_structural | `1141.428573` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 190.574238 | 190.574238 |
| S5_cross_level | 1.0 | 1157.268911 | 1157.268911 |
| S1_morphological | 1.0 | 268.543809 | 268.543809 |
| S2_lexical_diversity | 1.0 | 768.467404 | 768.467404 |
| S3_structural | 1.0 | 1141.428573 | 1141.428573 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 587.772646** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `35.371836` |
| S5_cross_level | `136.129401` |
| S1_morphological | `65.864605` |
| S2_lexical_diversity | `202.842479` |
| S3_structural | `140.237415` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 35.371836 | 35.371836 |
| S5_cross_level | 1.0 | 136.129401 | 136.129401 |
| S1_morphological | 1.0 | 65.864605 | 65.864605 |
| S2_lexical_diversity | 1.0 | 202.842479 | 202.842479 |
| S3_structural | 1.0 | 140.237415 | 140.237415 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 96.799780** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `32.094317` |
| S5_cross_level | `137.384762` |
| S1_morphological | `86.919014` |
| S2_lexical_diversity | `201.639789` |
| S3_structural | `152.248901` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__frac_agglutinative', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 32.094317 | 32.094317 |
| S5_cross_level | 1.0 | 137.384762 | 137.384762 |
| S1_morphological | 1.0 | 86.919014 | 86.919014 |
| S2_lexical_diversity | 1.0 | 201.639789 | 201.639789 |
| S3_structural | 1.0 | 152.248901 | 152.248901 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 101.812503** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `66.150324` |
| S5_cross_level | `340.027291` |
| S1_morphological | `94.145912` |
| S2_lexical_diversity | `294.078669` |
| S3_structural | `357.504061` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 66.150324 | 66.150324 |
| S5_cross_level | 1.0 | 340.027291 | 340.027291 |
| S1_morphological | 1.0 | 94.145912 | 94.145912 |
| S2_lexical_diversity | 1.0 | 294.078669 | 294.078669 |
| S3_structural | 1.0 | 357.504061 | 357.504061 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 192.043200** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `34.001719` |
| S5_cross_level | `128.198851` |
| S1_morphological | `80.283663` |
| S2_lexical_diversity | `185.201169` |
| S3_structural | `191.468785` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 34.001719 | 34.001719 |
| S5_cross_level | 1.0 | 128.198851 | 128.198851 |
| S1_morphological | 1.0 | 80.283663 | 80.283663 |
| S2_lexical_diversity | 1.0 | 185.201169 | 185.201169 |
| S3_structural | 1.0 | 191.468785 | 191.468785 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 103.270796** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `31.923702` |
| S5_cross_level | `134.433026` |
| S1_morphological | `72.475362` |
| S2_lexical_diversity | `202.973483` |
| S3_structural | `148.674305` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 31.923702 | 31.923702 |
| S5_cross_level | 1.0 | 134.433026 | 134.433026 |
| S1_morphological | 1.0 | 72.475362 | 72.475362 |
| S2_lexical_diversity | 1.0 | 202.973483 | 202.973483 |
| S3_structural | 1.0 | 148.674305 | 148.674305 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 98.521156** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `27.722308` |
| S5_cross_level | `112.430374` |
| S1_morphological | `64.243714` |
| S2_lexical_diversity | `143.048914` |
| S3_structural | `143.048380` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 27.722308 | 27.722308 |
| S5_cross_level | 1.0 | 112.430374 | 112.430374 |
| S1_morphological | 1.0 | 64.243714 | 64.243714 |
| S2_lexical_diversity | 1.0 | 143.048914 | 143.048914 |
| S3_structural | 1.0 | 143.048380 | 143.048380 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 81.837184** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `34.522095` |
| S5_cross_level | `141.412533` |
| S1_morphological | `80.657866` |
| S2_lexical_diversity | `206.131395` |
| S3_structural | `164.637621` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 34.522095 | 34.522095 |
| S5_cross_level | 1.0 | 141.412533 | 141.412533 |
| S1_morphological | 1.0 | 80.657866 | 80.657866 |
| S2_lexical_diversity | 1.0 | 206.131395 | 206.131395 |
| S3_structural | 1.0 | 164.637621 | 164.637621 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 104.619075** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `33.021314` |
| S5_cross_level | `138.750731` |
| S1_morphological | `74.332656` |
| S2_lexical_diversity | `207.393363` |
| S3_structural | `160.709989` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 33.021314 | 33.021314 |
| S5_cross_level | 1.0 | 138.750731 | 138.750731 |
| S1_morphological | 1.0 | 74.332656 | 74.332656 |
| S2_lexical_diversity | 1.0 | 207.393363 | 207.393363 |
| S3_structural | 1.0 | 160.709989 | 160.709989 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 102.456244** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `32.191228` |
| S5_cross_level | `112.927018` |
| S1_morphological | `65.039754` |
| S2_lexical_diversity | `191.865264` |
| S3_structural | `138.627318` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 32.191228 | 32.191228 |
| S5_cross_level | 1.0 | 112.927018 | 112.927018 |
| S1_morphological | 1.0 | 65.039754 | 65.039754 |
| S2_lexical_diversity | 1.0 | 191.865264 | 191.865264 |
| S3_structural | 1.0 | 138.627318 | 138.627318 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 90.167254** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `35.186892` |
| S5_cross_level | `131.446657` |
| S1_morphological | `64.493502` |
| S2_lexical_diversity | `204.232000` |
| S3_structural | `146.580421` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 35.186892 | 35.186892 |
| S5_cross_level | 1.0 | 131.446657 | 131.446657 |
| S1_morphological | 1.0 | 64.493502 | 64.493502 |
| S2_lexical_diversity | 1.0 | 204.232000 | 204.232000 |
| S3_structural | 1.0 | 146.580421 | 146.580421 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 97.029128** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `30.239077` |
| S5_cross_level | `127.983626` |
| S1_morphological | `55.730929` |
| S2_lexical_diversity | `192.473272` |
| S3_structural | `123.044015` |
| cat (Hamming) | `0.000000` (0/17 flags differ) |

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 30.239077 | 30.239077 |
| S5_cross_level | 1.0 | 127.983626 | 127.983626 |
| S1_morphological | 1.0 | 55.730929 | 55.730929 |
| S2_lexical_diversity | 1.0 | 192.473272 | 192.473272 |
| S3_structural | 1.0 | 123.044015 | 123.044015 |
| cat | 1.0 | 0.000000 | 0.000000 |
| **Total** | Σw = 6.0000 | | **D = 88.245153** |

### §§ 4–5 · Similarity % (max_D = `587.772646`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | multilingual_toxicity_dataset | `79.223368` | 86.5% | ← yes |
| 2 | OpenLID-v2 | `81.837184` | 86.1% | ← yes |
| 3 | language-identification | `88.245153` | 85.0% | ← yes |
| 4 | multilingual_cc_news | `90.167254` | 84.7% |  |
| 5 | xlsum | `95.236968` | 83.8% |  |
| 6 | amazon_reviews_multi | `96.799780` | 83.5% |  |
| 7 | massive | `97.028531` | 83.5% |  |
| 8 | xnli | `97.029128` | 83.5% |  |
| 9 | flores_plus | `97.550138` | 83.4% |  |
| 10 | tweet_sentiment_multilingual | `98.521156` | 83.2% |  |
| 11 | mmarco | `101.275953` | 82.8% |  |
| 12 | tydiqa | `101.812503` | 82.7% |  |
| 13 | europarl | `102.456244` | 82.6% |  |
| 14 | multi_eurlex | `103.270796` | 82.4% |  |
| 15 | stsb_multi_mt | `104.619075` | 82.2% |  |
| 16 | exorde-social-media-december-2024-week1 | `192.043200` | 67.3% |  |
| 17 | wikipedia | `587.772646` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `multilingual_toxicity_dataset`** — inv_d = `0.012623`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multilingual_toxicity_dataset | 0.955714 | 3 | 0.7500 | 0.009048 |
| tfidf_char_ngram_3_5_multilingual_toxicity_dataset | 0.956080 | 3 | 0.7500 | 0.009051 |
| fasttext_subword_multilingual_toxicity_dataset | 0.995558 | 3 | 0.7500 | 0.009425 |
| fasttext_word_multilingual_toxicity_dataset | 0.838982 | 3 | 0.7500 | 0.007943 |
| lid.176_multilingual_toxicity_dataset | 0.990585 | 3 | 0.7500 | 0.009378 |
| cld3_multilingual_toxicity_dataset | 0.979348 | 3 | 0.7500 | 0.009271 |
| bow_maxabs_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.970372 | 3 | 0.7500 | 0.009186 |
| tfidf_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.985689 | 3 | 0.7500 | 0.009331 |

**Neighbour: `OpenLID-v2`** — inv_d = `0.012219`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.980663 | 1 | 0.9167 | 0.010985 |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.981227 | 1 | 0.9167 | 0.010991 |
| fasttext_subword_OpenLID-v2 | 0.993905 | 1 | 0.9167 | 0.011133 |
| fasttext_word_OpenLID-v2 | 0.947366 | 1 | 0.9167 | 0.010612 |
| lid.176_OpenLID-v2 | 0.901862 | 1 | 0.9167 | 0.010102 |
| cld3_OpenLID-v2 | 0.939038 | 1 | 0.9167 | 0.010518 |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.981563 | 1 | 0.9167 | 0.010995 |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.983798 | 1 | 0.9167 | 0.011020 |

**Neighbour: `language-identification`** — inv_d = `0.011332`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_language-identification | 0.997934 | 1 | 0.9167 | 0.010366 |
| tfidf_char_ngram_3_5_language-identification | 0.998033 | 1 | 0.9167 | 0.010367 |
| fasttext_subword_language-identification | 0.996164 | 1 | 0.9167 | 0.010348 |
| fasttext_word_language-identification | 0.870988 | 1 | 0.9167 | 0.009048 |
| lid.176_language-identification | 0.995624 | 1 | 0.9167 | 0.010342 |
| cld3_language-identification | 0.984446 | 1 | 0.9167 | 0.010226 |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.984950 | 1 | 0.9167 | 0.010231 |
| tfidf_lr_char_ngram_3_5_language-identification | 0.995288 | 1 | 0.9167 | 0.010339 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.010985 | 0.012219 | **0.898941** |
| bow_char_ngram_3_5_language-identification | 0.010366 | 0.011332 | **0.914773** |
| bow_char_ngram_3_5_multilingual_toxicity_dataset | 0.009048 | 0.012623 | **0.716785** |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.010995 | 0.012219 | **0.899766** |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.010231 | 0.011332 | **0.902871** |
| bow_maxabs_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.009186 | 0.012623 | **0.727779** |
| cld3_OpenLID-v2 | 0.010518 | 0.012219 | **0.860785** |
| cld3_language-identification | 0.010226 | 0.011332 | **0.902409** |
| cld3_multilingual_toxicity_dataset | 0.009271 | 0.012623 | **0.734511** |
| fasttext_subword_OpenLID-v2 | 0.011133 | 0.012219 | **0.911080** |
| fasttext_subword_language-identification | 0.010348 | 0.011332 | **0.913150** |
| fasttext_subword_multilingual_toxicity_dataset | 0.009425 | 0.012623 | **0.746668** |
| fasttext_word_OpenLID-v2 | 0.010612 | 0.012219 | **0.868419** |
| fasttext_word_language-identification | 0.009048 | 0.011332 | **0.798406** |
| fasttext_word_multilingual_toxicity_dataset | 0.007943 | 0.012623 | **0.629237** |
| lid.176_OpenLID-v2 | 0.010102 | 0.012219 | **0.826707** |
| lid.176_language-identification | 0.010342 | 0.011332 | **0.912655** |
| lid.176_multilingual_toxicity_dataset | 0.009378 | 0.012623 | **0.742939** |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.010991 | 0.012219 | **0.899458** |
| tfidf_char_ngram_3_5_language-identification | 0.010367 | 0.011332 | **0.914864** |
| tfidf_char_ngram_3_5_multilingual_toxicity_dataset | 0.009051 | 0.012623 | **0.717060** |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.011020 | 0.012219 | **0.901815** |
| tfidf_lr_char_ngram_3_5_language-identification | 0.010339 | 0.011332 | **0.912347** |
| tfidf_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.009331 | 0.012623 | **0.739267** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `tfidf_char_ngram_3_5_language-identification`

---

## Dataset: `stsb_multi_mt`

**Query languages:** `['ca', 'de', 'el', 'en', 'es', 'fr', 'it', 'ja', 'nl', 'pl', 'pt', 'ru', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `52.223209` |
| S5_cross_level | `1133.060741` |
| S1_morphological | `54.853683` |
| S2_lexical_diversity | `259.942308` |
| S3_structural | `99.930306` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 52.223209 | 52.223209 |
| S5_cross_level | 1.0 | 1133.060741 | 1133.060741 |
| S1_morphological | 1.0 | 54.853683 | 54.853683 |
| S2_lexical_diversity | 1.0 | 259.942308 | 259.942308 |
| S3_structural | 1.0 | 99.930306 | 99.930306 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 266.717394** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `50.613102` |
| S5_cross_level | `1169.599901` |
| S1_morphological | `31.037834` |
| S2_lexical_diversity | `264.958144` |
| S3_structural | `61.837820` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 50.613102 | 50.613102 |
| S5_cross_level | 1.0 | 1169.599901 | 1169.599901 |
| S1_morphological | 1.0 | 31.037834 | 31.037834 |
| S2_lexical_diversity | 1.0 | 264.958144 | 264.958144 |
| S3_structural | 1.0 | 61.837820 | 61.837820 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 263.066624** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `54.514265` |
| S5_cross_level | `1169.523986` |
| S1_morphological | `36.885343` |
| S2_lexical_diversity | `263.395481` |
| S3_structural | `65.142251` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 54.514265 | 54.514265 |
| S5_cross_level | 1.0 | 1169.523986 | 1169.523986 |
| S1_morphological | 1.0 | 36.885343 | 36.885343 |
| S2_lexical_diversity | 1.0 | 263.395481 | 263.395481 |
| S3_structural | 1.0 | 65.142251 | 65.142251 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 264.998456** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `55.516552` |
| S5_cross_level | `1159.977421` |
| S1_morphological | `41.999649` |
| S2_lexical_diversity | `263.956072` |
| S3_structural | `71.242768` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 55.516552 | 55.516552 |
| S5_cross_level | 1.0 | 1159.977421 | 1159.977421 |
| S1_morphological | 1.0 | 41.999649 | 41.999649 |
| S2_lexical_diversity | 1.0 | 263.956072 | 263.956072 |
| S3_structural | 1.0 | 71.242768 | 71.242768 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 265.497763** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `52.706279` |
| S5_cross_level | `1171.780696` |
| S1_morphological | `22.926316` |
| S2_lexical_diversity | `266.473116` |
| S3_structural | `63.091959` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 52.706279 | 52.706279 |
| S5_cross_level | 1.0 | 1171.780696 | 1171.780696 |
| S1_morphological | 1.0 | 22.926316 | 22.926316 |
| S2_lexical_diversity | 1.0 | 266.473116 | 266.473116 |
| S3_structural | 1.0 | 63.091959 | 63.091959 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 262.878747** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `201.188089` |
| S5_cross_level | `473.285383` |
| S1_morphological | `325.021883` |
| S2_lexical_diversity | `833.698097` |
| S3_structural | `1260.372744` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 201.188089 | 201.188089 |
| S5_cross_level | 1.0 | 473.285383 | 473.285383 |
| S1_morphological | 1.0 | 325.021883 | 325.021883 |
| S2_lexical_diversity | 1.0 | 833.698097 | 833.698097 |
| S3_structural | 1.0 | 1260.372744 | 1260.372744 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 515.653190** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `56.106223` |
| S5_cross_level | `1169.061695` |
| S1_morphological | `63.119413` |
| S2_lexical_diversity | `265.767159` |
| S3_structural | `95.965431` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 56.106223 | 56.106223 |
| S5_cross_level | 1.0 | 1169.061695 | 1169.061695 |
| S1_morphological | 1.0 | 63.119413 | 63.119413 |
| S2_lexical_diversity | 1.0 | 265.767159 | 265.767159 |
| S3_structural | 1.0 | 95.965431 | 95.965431 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 275.062144** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `51.899013` |
| S5_cross_level | `1170.279829` |
| S1_morphological | `28.253429` |
| S2_lexical_diversity | `266.118467` |
| S3_structural | `62.995574` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__frac_agglutinative', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 51.899013 | 51.899013 |
| S5_cross_level | 1.0 | 1170.279829 | 1170.279829 |
| S1_morphological | 1.0 | 28.253429 | 28.253429 |
| S2_lexical_diversity | 1.0 | 266.118467 | 266.118467 |
| S3_structural | 1.0 | 62.995574 | 62.995574 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 263.355758** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `82.901469` |
| S5_cross_level | `788.834260` |
| S1_morphological | `155.168328` |
| S2_lexical_diversity | `379.494031` |
| S3_structural | `480.475390` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 82.901469 | 82.901469 |
| S5_cross_level | 1.0 | 788.834260 | 788.834260 |
| S1_morphological | 1.0 | 155.168328 | 155.168328 |
| S2_lexical_diversity | 1.0 | 379.494031 | 379.494031 |
| S3_structural | 1.0 | 480.475390 | 480.475390 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 314.537737** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `52.881440` |
| S5_cross_level | `1164.967111` |
| S1_morphological | `49.951548` |
| S2_lexical_diversity | `244.165161` |
| S3_structural | `133.821518` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 52.881440 | 52.881440 |
| S5_cross_level | 1.0 | 1164.967111 | 1164.967111 |
| S1_morphological | 1.0 | 49.951548 | 49.951548 |
| S2_lexical_diversity | 1.0 | 244.165161 | 244.165161 |
| S3_structural | 1.0 | 133.821518 | 133.821518 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 274.376228** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `51.486471` |
| S5_cross_level | `1173.508804` |
| S1_morphological | `53.875001` |
| S2_lexical_diversity | `263.518154` |
| S3_structural | `100.143145` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 51.486471 | 51.486471 |
| S5_cross_level | 1.0 | 1173.508804 | 1173.508804 |
| S1_morphological | 1.0 | 53.875001 | 53.875001 |
| S2_lexical_diversity | 1.0 | 263.518154 | 263.518154 |
| S3_structural | 1.0 | 100.143145 | 100.143145 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 273.863106** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `49.458849` |
| S5_cross_level | `1159.059632` |
| S1_morphological | `34.708146` |
| S2_lexical_diversity | `197.536874` |
| S3_structural | `57.696582` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 49.458849 | 49.458849 |
| S5_cross_level | 1.0 | 1159.059632 | 1159.059632 |
| S1_morphological | 1.0 | 34.708146 | 34.708146 |
| S2_lexical_diversity | 1.0 | 197.536874 | 197.536874 |
| S3_structural | 1.0 | 57.696582 | 57.696582 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 249.831582** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `54.240925` |
| S5_cross_level | `1175.295715` |
| S1_morphological | `20.367545` |
| S2_lexical_diversity | `266.302049` |
| S3_structural | `60.196253` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 54.240925 | 54.240925 |
| S5_cross_level | 1.0 | 1175.295715 | 1175.295715 |
| S1_morphological | 1.0 | 20.367545 | 20.367545 |
| S2_lexical_diversity | 1.0 | 266.302049 | 266.302049 |
| S3_structural | 1.0 | 60.196253 | 60.196253 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 262.792572** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `53.659446` |
| S5_cross_level | `1174.523319` |
| S1_morphological | `56.843082` |
| S2_lexical_diversity | `267.694009` |
| S3_structural | `95.634225` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 53.659446 | 53.659446 |
| S5_cross_level | 1.0 | 1174.523319 | 1174.523319 |
| S1_morphological | 1.0 | 56.843082 | 56.843082 |
| S2_lexical_diversity | 1.0 | 267.694009 | 267.694009 |
| S3_structural | 1.0 | 95.634225 | 95.634225 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 274.804111** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `53.242554` |
| S5_cross_level | `1150.747030` |
| S1_morphological | `52.687887` |
| S2_lexical_diversity | `254.812551` |
| S3_structural | `72.364635` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 53.242554 | 53.242554 |
| S5_cross_level | 1.0 | 1150.747030 | 1150.747030 |
| S1_morphological | 1.0 | 52.687887 | 52.687887 |
| S2_lexical_diversity | 1.0 | 254.812551 | 254.812551 |
| S3_structural | 1.0 | 72.364635 | 72.364635 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 264.034600** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `55.352102` |
| S5_cross_level | `1167.623645` |
| S1_morphological | `40.702135` |
| S2_lexical_diversity | `260.882595` |
| S3_structural | `85.195028` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 55.352102 | 55.352102 |
| S5_cross_level | 1.0 | 1167.623645 | 1167.623645 |
| S1_morphological | 1.0 | 40.702135 | 40.702135 |
| S2_lexical_diversity | 1.0 | 260.882595 | 260.882595 |
| S3_structural | 1.0 | 85.195028 | 85.195028 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 268.331800** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `51.603970` |
| S5_cross_level | `1163.590928` |
| S1_morphological | `56.212262` |
| S2_lexical_diversity | `257.085290` |
| S3_structural | `74.988037` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 51.603970 | 51.603970 |
| S5_cross_level | 1.0 | 1163.590928 | 1163.590928 |
| S1_morphological | 1.0 | 56.212262 | 56.212262 |
| S2_lexical_diversity | 1.0 | 257.085290 | 257.085290 |
| S3_structural | 1.0 | 74.988037 | 74.988037 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 267.266356** |

### §§ 4–5 · Similarity % (max_D = `515.653190`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | OpenLID-v2 | `249.831582` | 51.6% | ← yes |
| 2 | stsb_multi_mt | `262.792572` | 49.0% | ← yes |
| 3 | mmarco | `262.878747` | 49.0% | ← yes |
| 4 | massive | `263.066624` | 49.0% |  |
| 5 | tydiqa | `263.355758` | 48.9% |  |
| 6 | multilingual_cc_news | `264.034600` | 48.8% |  |
| 7 | flores_plus | `264.998456` | 48.6% |  |
| 8 | xlsum | `265.497763` | 48.5% |  |
| 9 | multilingual_toxicity_dataset | `266.717394` | 48.3% |  |
| 10 | language-identification | `267.266356` | 48.2% |  |
| 11 | xnli | `268.331800` | 48.0% |  |
| 12 | tweet_sentiment_multilingual | `273.863106` | 46.9% |  |
| 13 | multi_eurlex | `274.376228` | 46.8% |  |
| 14 | europarl | `274.804111` | 46.7% |  |
| 15 | amazon_reviews_multi | `275.062144` | 46.7% |  |
| 16 | exorde-social-media-december-2024-week1 | `314.537737` | 39.0% |  |
| 17 | wikipedia | `515.653190` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `OpenLID-v2`** — inv_d = `0.004003`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.980663 | 1 | 0.9231 | 0.003623 |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.981227 | 1 | 0.9231 | 0.003625 |
| fasttext_subword_OpenLID-v2 | 0.993905 | 1 | 0.9231 | 0.003672 |
| fasttext_word_OpenLID-v2 | 0.947366 | 1 | 0.9231 | 0.003500 |
| lid.176_OpenLID-v2 | 0.901862 | 1 | 0.9231 | 0.003332 |
| cld3_OpenLID-v2 | 0.939038 | 1 | 0.9231 | 0.003470 |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.981563 | 1 | 0.9231 | 0.003627 |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.983798 | 1 | 0.9231 | 0.003635 |

**Neighbour: `stsb_multi_mt`** — inv_d = `0.003805`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_stsb_multi_mt | 0.965403 | 3 | 0.7692 | 0.002826 |
| tfidf_char_ngram_3_5_stsb_multi_mt | 0.966275 | 3 | 0.7692 | 0.002828 |
| fasttext_subword_stsb_multi_mt | 0.992631 | 3 | 0.7692 | 0.002906 |
| fasttext_word_stsb_multi_mt | 0.975124 | 3 | 0.7692 | 0.002854 |
| lid.176_stsb_multi_mt | 0.993022 | 3 | 0.7692 | 0.002907 |
| cld3_stsb_multi_mt | 0.961883 | 3 | 0.7692 | 0.002816 |
| bow_maxabs_lr_char_ngram_3_5_stsb_multi_mt | 0.991859 | 3 | 0.7692 | 0.002903 |
| tfidf_lr_char_ngram_3_5_stsb_multi_mt | 0.994068 | 3 | 0.7692 | 0.002910 |

**Neighbour: `mmarco`** — inv_d = `0.003804`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_mmarco | 0.974607 | 3 | 0.7692 | 0.002852 |
| tfidf_char_ngram_3_5_mmarco | 0.973939 | 3 | 0.7692 | 0.002850 |
| fasttext_subword_mmarco | 0.997353 | 3 | 0.7692 | 0.002918 |
| fasttext_word_mmarco | 0.894916 | 3 | 0.7692 | 0.002619 |
| lid.176_mmarco | 0.986219 | 3 | 0.7692 | 0.002886 |
| cld3_mmarco | 0.945066 | 3 | 0.7692 | 0.002765 |
| bow_maxabs_lr_char_ngram_3_5_mmarco | 0.983976 | 3 | 0.7692 | 0.002879 |
| tfidf_lr_char_ngram_3_5_mmarco | 0.987481 | 3 | 0.7692 | 0.002890 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.003623 | 0.004003 | **0.905227** |
| bow_char_ngram_3_5_mmarco | 0.002852 | 0.003804 | **0.749698** |
| bow_char_ngram_3_5_stsb_multi_mt | 0.002826 | 0.003805 | **0.742618** |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.003627 | 0.004003 | **0.906058** |
| bow_maxabs_lr_char_ngram_3_5_mmarco | 0.002879 | 0.003804 | **0.756905** |
| bow_maxabs_lr_char_ngram_3_5_stsb_multi_mt | 0.002903 | 0.003805 | **0.762968** |
| cld3_OpenLID-v2 | 0.003470 | 0.004003 | **0.866804** |
| cld3_mmarco | 0.002765 | 0.003804 | **0.726974** |
| cld3_stsb_multi_mt | 0.002816 | 0.003805 | **0.739910** |
| fasttext_subword_OpenLID-v2 | 0.003672 | 0.004003 | **0.917451** |
| fasttext_subword_mmarco | 0.002918 | 0.003804 | **0.767195** |
| fasttext_subword_stsb_multi_mt | 0.002906 | 0.003805 | **0.763562** |
| fasttext_word_OpenLID-v2 | 0.003500 | 0.004003 | **0.874492** |
| fasttext_word_mmarco | 0.002619 | 0.003804 | **0.688397** |
| fasttext_word_stsb_multi_mt | 0.002854 | 0.003805 | **0.750095** |
| lid.176_OpenLID-v2 | 0.003332 | 0.004003 | **0.832488** |
| lid.176_mmarco | 0.002886 | 0.003804 | **0.758630** |
| lid.176_stsb_multi_mt | 0.002907 | 0.003805 | **0.763863** |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.003625 | 0.004003 | **0.905748** |
| tfidf_char_ngram_3_5_mmarco | 0.002850 | 0.003804 | **0.749184** |
| tfidf_char_ngram_3_5_stsb_multi_mt | 0.002828 | 0.003805 | **0.743288** |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.003635 | 0.004003 | **0.908121** |
| tfidf_lr_char_ngram_3_5_mmarco | 0.002890 | 0.003804 | **0.759601** |
| tfidf_lr_char_ngram_3_5_stsb_multi_mt | 0.002910 | 0.003805 | **0.764668** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_OpenLID-v2`

---

## Dataset: `tweet_sentiment_multilingual`

**Query languages:** `['ca', 'de', 'en', 'es', 'fr', 'it', 'nl', 'pt']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `8.973610` |
| S5_cross_level | `54.022224` |
| S1_morphological | `39.779899` |
| S2_lexical_diversity | `70.839381` |
| S3_structural | `83.050465` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 8.973610 | 8.973610 |
| S5_cross_level | 1.0 | 54.022224 | 54.022224 |
| S1_morphological | 1.0 | 39.779899 | 39.779899 |
| S2_lexical_diversity | 1.0 | 70.839381 | 70.839381 |
| S3_structural | 1.0 | 83.050465 | 83.050465 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 42.865832** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.060394` |
| S5_cross_level | `32.418494` |
| S1_morphological | `48.155949` |
| S2_lexical_diversity | `71.894556` |
| S3_structural | `91.637467` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.060394 | 12.060394 |
| S5_cross_level | 1.0 | 32.418494 | 32.418494 |
| S1_morphological | 1.0 | 48.155949 | 48.155949 |
| S2_lexical_diversity | 1.0 | 71.894556 | 71.894556 |
| S3_structural | 1.0 | 91.637467 | 91.637467 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 42.812124** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.710756` |
| S5_cross_level | `46.185305` |
| S1_morphological | `44.615416` |
| S2_lexical_diversity | `68.529015` |
| S3_structural | `84.719285` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.710756 | 14.710756 |
| S5_cross_level | 1.0 | 46.185305 | 46.185305 |
| S1_morphological | 1.0 | 44.615416 | 44.615416 |
| S2_lexical_diversity | 1.0 | 68.529015 | 68.529015 |
| S3_structural | 1.0 | 84.719285 | 84.719285 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 43.214865** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `13.832859` |
| S5_cross_level | `42.141153` |
| S1_morphological | `37.188721` |
| S2_lexical_diversity | `69.622856` |
| S3_structural | `67.029999` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 13.832859 | 13.832859 |
| S5_cross_level | 1.0 | 42.141153 | 42.141153 |
| S1_morphological | 1.0 | 37.188721 | 37.188721 |
| S2_lexical_diversity | 1.0 | 69.622856 | 69.622856 |
| S3_structural | 1.0 | 67.029999 | 67.029999 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 38.400637** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.996978` |
| S5_cross_level | `35.027057` |
| S1_morphological | `52.662055` |
| S2_lexical_diversity | `73.785487` |
| S3_structural | `97.789781` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.996978 | 12.996978 |
| S5_cross_level | 1.0 | 35.027057 | 35.027057 |
| S1_morphological | 1.0 | 52.662055 | 52.662055 |
| S2_lexical_diversity | 1.0 | 73.785487 | 73.785487 |
| S3_structural | 1.0 | 97.789781 | 97.789781 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 45.474932** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `201.135732` |
| S5_cross_level | `1232.202327` |
| S1_morphological | `317.809584` |
| S2_lexical_diversity | `826.479288` |
| S3_structural | `1241.288385` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 201.135732 | 201.135732 |
| S5_cross_level | 1.0 | 1232.202327 | 1232.202327 |
| S1_morphological | 1.0 | 317.809584 | 317.809584 |
| S2_lexical_diversity | 1.0 | 826.479288 | 826.479288 |
| S3_structural | 1.0 | 1241.288385 | 1241.288385 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 636.603533** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.802191` |
| S5_cross_level | `41.694033` |
| S1_morphological | `37.005155` |
| S2_lexical_diversity | `80.864478` |
| S3_structural | `93.302465` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.802191 | 12.802191 |
| S5_cross_level | 1.0 | 41.694033 | 41.694033 |
| S1_morphological | 1.0 | 37.005155 | 37.005155 |
| S2_lexical_diversity | 1.0 | 80.864478 | 80.864478 |
| S3_structural | 1.0 | 93.302465 | 93.302465 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 44.366289** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `13.285377` |
| S5_cross_level | `40.729411` |
| S1_morphological | `52.511513` |
| S2_lexical_diversity | `73.717010` |
| S3_structural | `91.198296` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__frac_romance', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__frac_agglutinative', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 13.285377 | 13.285377 |
| S5_cross_level | 1.0 | 40.729411 | 40.729411 |
| S1_morphological | 1.0 | 52.511513 | 52.511513 |
| S2_lexical_diversity | 1.0 | 73.717010 | 73.717010 |
| S3_structural | 1.0 | 91.198296 | 91.198296 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 45.338307** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `73.830163` |
| S5_cross_level | `407.895160` |
| S1_morphological | `143.701221` |
| S2_lexical_diversity | `314.278867` |
| S3_structural | `457.112253` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 73.830163 | 73.830163 |
| S5_cross_level | 1.0 | 407.895160 | 407.895160 |
| S1_morphological | 1.0 | 143.701221 | 143.701221 |
| S2_lexical_diversity | 1.0 | 314.278867 | 314.278867 |
| S3_structural | 1.0 | 457.112253 | 457.112253 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 232.920591** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.366523` |
| S5_cross_level | `43.181505` |
| S1_morphological | `57.974523` |
| S2_lexical_diversity | `93.564495` |
| S3_structural | `138.819816` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.366523 | 10.366523 |
| S5_cross_level | 1.0 | 43.181505 | 43.181505 |
| S1_morphological | 1.0 | 57.974523 | 57.974523 |
| S2_lexical_diversity | 1.0 | 93.564495 | 93.564495 |
| S3_structural | 1.0 | 138.819816 | 138.819816 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 57.376634** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `5.663293` |
| S5_cross_level | `44.245461` |
| S1_morphological | `34.441298` |
| S2_lexical_diversity | `60.968728` |
| S3_structural | `59.561655` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 5.663293 | 5.663293 |
| S5_cross_level | 1.0 | 44.245461 | 44.245461 |
| S1_morphological | 1.0 | 34.441298 | 34.441298 |
| S2_lexical_diversity | 1.0 | 60.968728 | 60.968728 |
| S3_structural | 1.0 | 59.561655 | 59.561655 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 34.166347** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `8.842955` |
| S5_cross_level | `51.658446` |
| S1_morphological | `36.708182` |
| S2_lexical_diversity | `42.191865` |
| S3_structural | `78.679300` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 8.842955 | 8.842955 |
| S5_cross_level | 1.0 | 51.658446 | 51.658446 |
| S1_morphological | 1.0 | 36.708182 | 36.708182 |
| S2_lexical_diversity | 1.0 | 42.191865 | 42.191865 |
| S3_structural | 1.0 | 78.679300 | 78.679300 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 36.435027** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.014909` |
| S5_cross_level | `52.697330` |
| S1_morphological | `48.736167` |
| S2_lexical_diversity | `73.035879` |
| S3_structural | `94.580501` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.014909 | 12.014909 |
| S5_cross_level | 1.0 | 52.697330 | 52.697330 |
| S1_morphological | 1.0 | 48.736167 | 48.736167 |
| S2_lexical_diversity | 1.0 | 73.035879 | 73.035879 |
| S3_structural | 1.0 | 94.580501 | 94.580501 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 46.932366** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `10.422991` |
| S5_cross_level | `51.382284` |
| S1_morphological | `47.275908` |
| S2_lexical_diversity | `69.430834` |
| S3_structural | `81.243813` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 10.422991 | 10.422991 |
| S5_cross_level | 1.0 | 51.382284 | 51.382284 |
| S1_morphological | 1.0 | 47.275908 | 47.275908 |
| S2_lexical_diversity | 1.0 | 69.430834 | 69.430834 |
| S3_structural | 1.0 | 81.243813 | 81.243813 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 43.351462** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.017890` |
| S5_cross_level | `43.434289` |
| S1_morphological | `40.653455` |
| S2_lexical_diversity | `65.686989` |
| S3_structural | `63.980240` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.017890 | 9.017890 |
| S5_cross_level | 1.0 | 43.434289 | 43.434289 |
| S1_morphological | 1.0 | 40.653455 | 40.653455 |
| S2_lexical_diversity | 1.0 | 65.686989 | 65.686989 |
| S3_structural | 1.0 | 63.980240 | 63.980240 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 37.246458** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.487589` |
| S5_cross_level | `45.299843` |
| S1_morphological | `32.317757` |
| S2_lexical_diversity | `69.153791` |
| S3_structural | `78.213137` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.487589 | 11.487589 |
| S5_cross_level | 1.0 | 45.299843 | 45.299843 |
| S1_morphological | 1.0 | 32.317757 | 32.317757 |
| S2_lexical_diversity | 1.0 | 69.153791 | 69.153791 |
| S3_structural | 1.0 | 78.213137 | 78.213137 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 39.510059** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.332255` |
| S5_cross_level | `37.782145` |
| S1_morphological | `32.971170` |
| S2_lexical_diversity | `67.579778` |
| S3_structural | `77.650156` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.332255 | 9.332255 |
| S5_cross_level | 1.0 | 37.782145 | 37.782145 |
| S1_morphological | 1.0 | 32.971170 | 32.971170 |
| S2_lexical_diversity | 1.0 | 67.579778 | 67.579778 |
| S3_structural | 1.0 | 77.650156 | 77.650156 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 37.660427** |

### §§ 4–5 · Similarity % (max_D = `636.603533`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | tweet_sentiment_multilingual | `34.166347` | 94.6% | ← yes |
| 2 | OpenLID-v2 | `36.435027` | 94.3% | ← yes |
| 3 | multilingual_cc_news | `37.246458` | 94.1% | ← yes |
| 4 | language-identification | `37.660427` | 94.1% |  |
| 5 | xlsum | `38.400637` | 94.0% |  |
| 6 | xnli | `39.510059` | 93.8% |  |
| 7 | massive | `42.812124` | 93.3% |  |
| 8 | multilingual_toxicity_dataset | `42.865832` | 93.3% |  |
| 9 | flores_plus | `43.214865` | 93.2% |  |
| 10 | europarl | `43.351462` | 93.2% |  |
| 11 | amazon_reviews_multi | `44.366289` | 93.0% |  |
| 12 | tydiqa | `45.338307` | 92.9% |  |
| 13 | mmarco | `45.474932` | 92.9% |  |
| 14 | stsb_multi_mt | `46.932366` | 92.6% |  |
| 15 | multi_eurlex | `57.376634` | 91.0% |  |
| 16 | exorde-social-media-december-2024-week1 | `232.920591` | 63.4% |  |
| 17 | wikipedia | `636.603533` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `tweet_sentiment_multilingual`** — inv_d = `0.029269`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_tweet_sentiment_multilingual | 0.996646 | 2 | 0.7500 | 0.021878 |
| tfidf_char_ngram_3_5_tweet_sentiment_multilingual | 0.995806 | 2 | 0.7500 | 0.021859 |
| fasttext_subword_tweet_sentiment_multilingual | 0.991340 | 2 | 0.7500 | 0.021761 |
| fasttext_word_tweet_sentiment_multilingual | 0.978316 | 2 | 0.7500 | 0.021475 |
| lid.176_tweet_sentiment_multilingual | 0.973852 | 2 | 0.7500 | 0.021377 |
| cld3_tweet_sentiment_multilingual | 0.945235 | 2 | 0.7500 | 0.020749 |
| bow_maxabs_lr_char_ngram_3_5_tweet_sentiment_multilingual | 0.993578 | 2 | 0.7500 | 0.021810 |
| tfidf_lr_char_ngram_3_5_tweet_sentiment_multilingual | 0.992464 | 2 | 0.7500 | 0.021786 |

**Neighbour: `OpenLID-v2`** — inv_d = `0.027446`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.980663 | 0 | 1.0000 | 0.026915 |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.981227 | 0 | 1.0000 | 0.026931 |
| fasttext_subword_OpenLID-v2 | 0.993905 | 0 | 1.0000 | 0.027279 |
| fasttext_word_OpenLID-v2 | 0.947366 | 0 | 1.0000 | 0.026002 |
| lid.176_OpenLID-v2 | 0.901862 | 0 | 1.0000 | 0.024753 |
| cld3_OpenLID-v2 | 0.939038 | 0 | 1.0000 | 0.025773 |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.981563 | 0 | 1.0000 | 0.026940 |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.983798 | 0 | 1.0000 | 0.027001 |

**Neighbour: `multilingual_cc_news`** — inv_d = `0.026848`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multilingual_cc_news | 0.975398 | 3 | 0.6250 | 0.016367 |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.976358 | 3 | 0.6250 | 0.016383 |
| fasttext_subword_multilingual_cc_news | 0.997083 | 3 | 0.6250 | 0.016731 |
| fasttext_word_multilingual_cc_news | 0.985130 | 3 | 0.6250 | 0.016531 |
| lid.176_multilingual_cc_news | 0.928836 | 3 | 0.6250 | 0.015586 |
| cld3_multilingual_cc_news | 0.955450 | 3 | 0.6250 | 0.016033 |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.975948 | 3 | 0.6250 | 0.016377 |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.979512 | 3 | 0.6250 | 0.016436 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.026915 | 0.027446 | **0.980663** |
| bow_char_ngram_3_5_multilingual_cc_news | 0.016367 | 0.026848 | **0.609624** |
| bow_char_ngram_3_5_tweet_sentiment_multilingual | 0.021878 | 0.029269 | **0.747485** |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.026940 | 0.027446 | **0.981563** |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.016377 | 0.026848 | **0.609967** |
| bow_maxabs_lr_char_ngram_3_5_tweet_sentiment_multilingual | 0.021810 | 0.029269 | **0.745183** |
| cld3_OpenLID-v2 | 0.025773 | 0.027446 | **0.939038** |
| cld3_multilingual_cc_news | 0.016033 | 0.026848 | **0.597156** |
| cld3_tweet_sentiment_multilingual | 0.020749 | 0.029269 | **0.708926** |
| fasttext_subword_OpenLID-v2 | 0.027279 | 0.027446 | **0.993905** |
| fasttext_subword_multilingual_cc_news | 0.016731 | 0.026848 | **0.623177** |
| fasttext_subword_tweet_sentiment_multilingual | 0.021761 | 0.029269 | **0.743505** |
| fasttext_word_OpenLID-v2 | 0.026002 | 0.027446 | **0.947366** |
| fasttext_word_multilingual_cc_news | 0.016531 | 0.026848 | **0.615706** |
| fasttext_word_tweet_sentiment_multilingual | 0.021475 | 0.029269 | **0.733737** |
| lid.176_OpenLID-v2 | 0.024753 | 0.027446 | **0.901862** |
| lid.176_multilingual_cc_news | 0.015586 | 0.026848 | **0.580522** |
| lid.176_tweet_sentiment_multilingual | 0.021377 | 0.029269 | **0.730389** |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.026931 | 0.027446 | **0.981227** |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.016383 | 0.026848 | **0.610224** |
| tfidf_char_ngram_3_5_tweet_sentiment_multilingual | 0.021859 | 0.029269 | **0.746854** |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.027001 | 0.027446 | **0.983798** |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.016436 | 0.026848 | **0.612195** |
| tfidf_lr_char_ngram_3_5_tweet_sentiment_multilingual | 0.021786 | 0.029269 | **0.744348** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_OpenLID-v2`

---

## Dataset: `tydiqa`

**Query languages:** `['en', 'fi', 'it', 'ja', 'ko', 'ru']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.206480` |
| S5_cross_level | `76.821620` |
| S1_morphological | `64.286787` |
| S2_lexical_diversity | `57.099161` |
| S3_structural | `100.599693` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.206480 | 14.206480 |
| S5_cross_level | 1.0 | 76.821620 | 76.821620 |
| S1_morphological | 1.0 | 64.286787 | 64.286787 |
| S2_lexical_diversity | 1.0 | 57.099161 | 57.099161 |
| S3_structural | 1.0 | 100.599693 | 100.599693 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 52.257192** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `2.685491` |
| S5_cross_level | `24.580007` |
| S1_morphological | `32.526744` |
| S2_lexical_diversity | `37.358487` |
| S3_structural | `72.862046` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 2.685491 | 2.685491 |
| S5_cross_level | 1.0 | 24.580007 | 24.580007 |
| S1_morphological | 1.0 | 32.526744 | 32.526744 |
| S2_lexical_diversity | 1.0 | 37.358487 | 37.358487 |
| S3_structural | 1.0 | 72.862046 | 72.862046 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 28.413894** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `15.603874` |
| S5_cross_level | `55.693486` |
| S1_morphological | `42.858595` |
| S2_lexical_diversity | `54.158649` |
| S3_structural | `75.846265` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 15.603874 | 15.603874 |
| S5_cross_level | 1.0 | 55.693486 | 55.693486 |
| S1_morphological | 1.0 | 42.858595 | 42.858595 |
| S2_lexical_diversity | 1.0 | 54.158649 | 54.158649 |
| S3_structural | 1.0 | 75.846265 | 75.846265 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 40.742498** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `19.458609` |
| S5_cross_level | `63.220164` |
| S1_morphological | `46.703163` |
| S2_lexical_diversity | `61.308791` |
| S3_structural | `80.489699` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 19.458609 | 19.458609 |
| S5_cross_level | 1.0 | 63.220164 | 63.220164 |
| S1_morphological | 1.0 | 46.703163 | 46.703163 |
| S2_lexical_diversity | 1.0 | 61.308791 | 61.308791 |
| S3_structural | 1.0 | 80.489699 | 80.489699 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 45.255561** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `3.391577` |
| S5_cross_level | `24.231333` |
| S1_morphological | `24.739702` |
| S2_lexical_diversity | `37.975573` |
| S3_structural | `71.266542` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 3.391577 | 3.391577 |
| S5_cross_level | 1.0 | 24.231333 | 24.231333 |
| S1_morphological | 1.0 | 24.739702 | 24.739702 |
| S2_lexical_diversity | 1.0 | 37.975573 | 37.975573 |
| S3_structural | 1.0 | 71.266542 | 71.266542 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 27.022357** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `206.149560` |
| S5_cross_level | `1243.514825` |
| S1_morphological | `330.715388` |
| S2_lexical_diversity | `833.686865` |
| S3_structural | `1258.532406` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 206.149560 | 206.149560 |
| S5_cross_level | 1.0 | 1243.514825 | 1243.514825 |
| S1_morphological | 1.0 | 330.715388 | 330.715388 |
| S2_lexical_diversity | 1.0 | 833.686865 | 833.686865 |
| S3_structural | 1.0 | 1258.532406 | 1258.532406 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 645.511605** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `17.021913` |
| S5_cross_level | `62.314232` |
| S1_morphological | `70.842792` |
| S2_lexical_diversity | `65.927527` |
| S3_structural | `110.709914` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 17.021913 | 17.021913 |
| S5_cross_level | 1.0 | 62.314232 | 62.314232 |
| S1_morphological | 1.0 | 70.842792 | 70.842792 |
| S2_lexical_diversity | 1.0 | 65.927527 | 65.927527 |
| S3_structural | 1.0 | 110.709914 | 110.709914 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 54.557632** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `1.452339` |
| S5_cross_level | `5.975152` |
| S1_morphological | `11.254938` |
| S2_lexical_diversity | `28.444830` |
| S3_structural | `46.751905` |
| cat (Hamming) | `0.176471` (3/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 1.452339 | 1.452339 |
| S5_cross_level | 1.0 | 5.975152 | 5.975152 |
| S1_morphological | 1.0 | 11.254938 | 11.254938 |
| S2_lexical_diversity | 1.0 | 28.444830 | 28.444830 |
| S3_structural | 1.0 | 46.751905 | 46.751905 |
| cat | 1.0 | 0.176471 | 0.176471 |
| **Total** | Σw = 6.0000 | | **D = 15.675939** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `79.364764` |
| S5_cross_level | `421.712492` |
| S1_morphological | `163.412452` |
| S2_lexical_diversity | `319.920445` |
| S3_structural | `478.024531` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 79.364764 | 79.364764 |
| S5_cross_level | 1.0 | 421.712492 | 421.712492 |
| S1_morphological | 1.0 | 163.412452 | 163.412452 |
| S2_lexical_diversity | 1.0 | 319.920445 | 319.920445 |
| S3_structural | 1.0 | 478.024531 | 478.024531 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 243.817545** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `20.382048` |
| S5_cross_level | `69.701943` |
| S1_morphological | `51.462667` |
| S2_lexical_diversity | `102.605765` |
| S3_structural | `161.087652` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 20.382048 | 20.382048 |
| S5_cross_level | 1.0 | 69.701943 | 69.701943 |
| S1_morphological | 1.0 | 51.462667 | 51.462667 |
| S2_lexical_diversity | 1.0 | 102.605765 | 102.605765 |
| S3_structural | 1.0 | 161.087652 | 161.087652 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 67.618444** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.501458` |
| S5_cross_level | `69.697852` |
| S1_morphological | `57.372767` |
| S2_lexical_diversity | `63.252880` |
| S3_structural | `92.692431` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.501458 | 14.501458 |
| S5_cross_level | 1.0 | 69.697852 | 69.697852 |
| S1_morphological | 1.0 | 57.372767 | 57.372767 |
| S2_lexical_diversity | 1.0 | 63.252880 | 63.252880 |
| S3_structural | 1.0 | 92.692431 | 92.692431 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 49.645055** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.397417` |
| S5_cross_level | `66.542538` |
| S1_morphological | `43.837377` |
| S2_lexical_diversity | `65.258324` |
| S3_structural | `85.151309` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.397417 | 12.397417 |
| S5_cross_level | 1.0 | 66.542538 | 66.542538 |
| S1_morphological | 1.0 | 43.837377 | 43.837377 |
| S2_lexical_diversity | 1.0 | 65.258324 | 65.258324 |
| S3_structural | 1.0 | 85.151309 | 85.151309 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 45.580180** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `7.347520` |
| S5_cross_level | `55.724171` |
| S1_morphological | `22.712045` |
| S2_lexical_diversity | `51.318820` |
| S3_structural | `81.624355` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 7.347520 | 7.347520 |
| S5_cross_level | 1.0 | 55.724171 | 55.724171 |
| S1_morphological | 1.0 | 22.712045 | 22.712045 |
| S2_lexical_diversity | 1.0 | 51.318820 | 51.318820 |
| S3_structural | 1.0 | 81.624355 | 81.624355 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 36.542721** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.250843` |
| S5_cross_level | `62.401546` |
| S1_morphological | `64.097227` |
| S2_lexical_diversity | `59.938101` |
| S3_structural | `93.874217` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cjk', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.250843 | 11.250843 |
| S5_cross_level | 1.0 | 62.401546 | 62.401546 |
| S1_morphological | 1.0 | 64.097227 | 64.097227 |
| S2_lexical_diversity | 1.0 | 59.938101 | 59.938101 |
| S3_structural | 1.0 | 93.874217 | 93.874217 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 48.681891** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `16.316824` |
| S5_cross_level | `71.615333` |
| S1_morphological | `58.043704` |
| S2_lexical_diversity | `61.817398` |
| S3_structural | `87.170248` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 16.316824 | 16.316824 |
| S5_cross_level | 1.0 | 71.615333 | 71.615333 |
| S1_morphological | 1.0 | 58.043704 | 58.043704 |
| S2_lexical_diversity | 1.0 | 61.817398 | 61.817398 |
| S3_structural | 1.0 | 87.170248 | 87.170248 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 49.239016** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.345976` |
| S5_cross_level | `56.538876` |
| S1_morphological | `48.121794` |
| S2_lexical_diversity | `56.161133` |
| S3_structural | `91.707894` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.345976 | 12.345976 |
| S5_cross_level | 1.0 | 56.538876 | 56.538876 |
| S1_morphological | 1.0 | 48.121794 | 48.121794 |
| S2_lexical_diversity | 1.0 | 56.161133 | 56.161133 |
| S3_structural | 1.0 | 91.707894 | 91.707894 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 44.224377** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `13.055471` |
| S5_cross_level | `56.594758` |
| S1_morphological | `64.153304` |
| S2_lexical_diversity | `49.289525` |
| S3_structural | `90.126021` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 13.055471 | 13.055471 |
| S5_cross_level | 1.0 | 56.594758 | 56.594758 |
| S1_morphological | 1.0 | 64.153304 | 64.153304 |
| S2_lexical_diversity | 1.0 | 49.289525 | 49.289525 |
| S3_structural | 1.0 | 90.126021 | 90.126021 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 45.614945** |

### §§ 4–5 · Similarity % (max_D = `645.511605`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | tydiqa | `15.675939` | 97.6% | ← yes |
| 2 | mmarco | `27.022357` | 95.8% | ← yes |
| 3 | massive | `28.413894` | 95.6% | ← yes |
| 4 | stsb_multi_mt | `36.542721` | 94.3% |  |
| 5 | flores_plus | `40.742498` | 93.7% |  |
| 6 | xnli | `44.224377` | 93.1% |  |
| 7 | xlsum | `45.255561` | 93.0% |  |
| 8 | OpenLID-v2 | `45.580180` | 92.9% |  |
| 9 | language-identification | `45.614945` | 92.9% |  |
| 10 | europarl | `48.681891` | 92.5% |  |
| 11 | multilingual_cc_news | `49.239016` | 92.4% |  |
| 12 | tweet_sentiment_multilingual | `49.645055` | 92.3% |  |
| 13 | multilingual_toxicity_dataset | `52.257192` | 91.9% |  |
| 14 | amazon_reviews_multi | `54.557632` | 91.5% |  |
| 15 | multi_eurlex | `67.618444` | 89.5% |  |
| 16 | exorde-social-media-december-2024-week1 | `243.817545` | 62.2% |  |
| 17 | wikipedia | `645.511605` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `tydiqa`** — inv_d = `0.063792`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_tydiqa | 0.998541 | 1 | 0.8333 | 0.053082 |
| tfidf_char_ngram_3_5_tydiqa | 0.998386 | 1 | 0.8333 | 0.053074 |
| fasttext_subword_tydiqa | 0.999769 | 1 | 0.8333 | 0.053148 |
| fasttext_word_tydiqa | 0.986141 | 1 | 0.8333 | 0.052423 |
| lid.176_tydiqa | 0.998998 | 1 | 0.8333 | 0.053107 |
| cld3_tydiqa | 0.968602 | 1 | 0.8333 | 0.051491 |
| bow_maxabs_lr_char_ngram_3_5_tydiqa | 0.996303 | 1 | 0.8333 | 0.052963 |
| tfidf_lr_char_ngram_3_5_tydiqa | 0.998230 | 1 | 0.8333 | 0.053066 |

**Neighbour: `mmarco`** — inv_d = `0.037006`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_mmarco | 0.974607 | 2 | 0.6667 | 0.024044 |
| tfidf_char_ngram_3_5_mmarco | 0.973939 | 2 | 0.6667 | 0.024028 |
| fasttext_subword_mmarco | 0.997353 | 2 | 0.6667 | 0.024606 |
| fasttext_word_mmarco | 0.894916 | 2 | 0.6667 | 0.022078 |
| lid.176_mmarco | 0.986219 | 2 | 0.6667 | 0.024331 |
| cld3_mmarco | 0.945066 | 2 | 0.6667 | 0.023316 |
| bow_maxabs_lr_char_ngram_3_5_mmarco | 0.983976 | 2 | 0.6667 | 0.024276 |
| tfidf_lr_char_ngram_3_5_mmarco | 0.987481 | 2 | 0.6667 | 0.024362 |

**Neighbour: `massive`** — inv_d = `0.035194`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_massive | 0.990937 | 0 | 1.0000 | 0.034875 |
| tfidf_char_ngram_3_5_massive | 0.991145 | 0 | 1.0000 | 0.034882 |
| fasttext_subword_massive | 0.997546 | 0 | 1.0000 | 0.035108 |
| fasttext_word_massive | 0.934868 | 0 | 1.0000 | 0.032902 |
| lid.176_massive | 0.979587 | 0 | 1.0000 | 0.034476 |
| cld3_massive | 0.958160 | 0 | 1.0000 | 0.033722 |
| bow_maxabs_lr_char_ngram_3_5_massive | 0.986331 | 0 | 1.0000 | 0.034713 |
| tfidf_lr_char_ngram_3_5_massive | 0.990836 | 0 | 1.0000 | 0.034872 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_massive | 0.034875 | 0.035194 | **0.990937** |
| bow_char_ngram_3_5_mmarco | 0.024044 | 0.037006 | **0.649738** |
| bow_char_ngram_3_5_tydiqa | 0.053082 | 0.063792 | **0.832118** |
| bow_maxabs_lr_char_ngram_3_5_massive | 0.034713 | 0.035194 | **0.986331** |
| bow_maxabs_lr_char_ngram_3_5_mmarco | 0.024276 | 0.037006 | **0.655984** |
| bow_maxabs_lr_char_ngram_3_5_tydiqa | 0.052963 | 0.063792 | **0.830253** |
| cld3_massive | 0.033722 | 0.035194 | **0.958160** |
| cld3_mmarco | 0.023316 | 0.037006 | **0.630044** |
| cld3_tydiqa | 0.051491 | 0.063792 | **0.807168** |
| fasttext_subword_massive | 0.035108 | 0.035194 | **0.997546** |
| fasttext_subword_mmarco | 0.024606 | 0.037006 | **0.664902** |
| fasttext_subword_tydiqa | 0.053148 | 0.063792 | **0.833141** |
| fasttext_word_massive | 0.032902 | 0.035194 | **0.934868** |
| fasttext_word_mmarco | 0.022078 | 0.037006 | **0.596611** |
| fasttext_word_tydiqa | 0.052423 | 0.063792 | **0.821784** |
| lid.176_massive | 0.034476 | 0.035194 | **0.979587** |
| lid.176_mmarco | 0.024331 | 0.037006 | **0.657479** |
| lid.176_tydiqa | 0.053107 | 0.063792 | **0.832498** |
| tfidf_char_ngram_3_5_massive | 0.034882 | 0.035194 | **0.991145** |
| tfidf_char_ngram_3_5_mmarco | 0.024028 | 0.037006 | **0.649293** |
| tfidf_char_ngram_3_5_tydiqa | 0.053074 | 0.063792 | **0.831988** |
| tfidf_lr_char_ngram_3_5_massive | 0.034872 | 0.035194 | **0.990836** |
| tfidf_lr_char_ngram_3_5_mmarco | 0.024362 | 0.037006 | **0.658321** |
| tfidf_lr_char_ngram_3_5_tydiqa | 0.053066 | 0.063792 | **0.831858** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_massive`

---

## Dataset: `wikipedia`

**Query languages:** `['ca', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'hr', 'it', 'ja', 'ko', 'lt', 'mk', 'nl', 'pl', 'pt', 'ro', 'ru', 'sl', 'sv', 'uk', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `164.938613` |
| S5_cross_level | `1143.292324` |
| S1_morphological | `307.542948` |
| S2_lexical_diversity | `747.922234` |
| S3_structural | `1328.127193` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 164.938613 | 164.938613 |
| S5_cross_level | 1.0 | 1143.292324 | 1143.292324 |
| S1_morphological | 1.0 | 307.542948 | 307.542948 |
| S2_lexical_diversity | 1.0 | 747.922234 | 747.922234 |
| S3_structural | 1.0 | 1328.127193 | 1328.127193 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 615.372513** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `170.548237` |
| S5_cross_level | `1178.608147` |
| S1_morphological | `329.148369` |
| S2_lexical_diversity | `774.080282` |
| S3_structural | `1374.438227` |
| cat (Hamming) | `0.176471` (3/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 170.548237 | 170.548237 |
| S5_cross_level | 1.0 | 1178.608147 | 1178.608147 |
| S1_morphological | 1.0 | 329.148369 | 329.148369 |
| S2_lexical_diversity | 1.0 | 774.080282 | 774.080282 |
| S3_structural | 1.0 | 1374.438227 | 1374.438227 |
| cat | 1.0 | 0.176471 | 0.176471 |
| **Total** | Σw = 6.0000 | | **D = 637.833289** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `167.704109` |
| S5_cross_level | `1177.248652` |
| S1_morphological | `330.236821` |
| S2_lexical_diversity | `771.553579` |
| S3_structural | `1374.004310` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 167.704109 | 167.704109 |
| S5_cross_level | 1.0 | 1177.248652 | 1177.248652 |
| S1_morphological | 1.0 | 330.236821 | 330.236821 |
| S2_lexical_diversity | 1.0 | 771.553579 | 771.553579 |
| S3_structural | 1.0 | 1374.004310 | 1374.004310 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 636.840265** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `167.035500` |
| S5_cross_level | `1167.834944` |
| S1_morphological | `325.269591` |
| S2_lexical_diversity | `770.012506` |
| S3_structural | `1365.638327` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 167.035500 | 167.035500 |
| S5_cross_level | 1.0 | 1167.834944 | 1167.834944 |
| S1_morphological | 1.0 | 325.269591 | 325.269591 |
| S2_lexical_diversity | 1.0 | 770.012506 | 770.012506 |
| S3_structural | 1.0 | 1365.638327 | 1365.638327 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 632.690635** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `171.024354` |
| S5_cross_level | `1180.488868` |
| S1_morphological | `334.553019` |
| S2_lexical_diversity | `777.516016` |
| S3_structural | `1378.323777` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 171.024354 | 171.024354 |
| S5_cross_level | 1.0 | 1180.488868 | 1180.488868 |
| S1_morphological | 1.0 | 334.553019 | 334.553019 |
| S2_lexical_diversity | 1.0 | 777.516016 | 777.516016 |
| S3_structural | 1.0 | 1378.323777 | 1378.323777 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 640.386300** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `45.117625` |
| S5_cross_level | `112.273488` |
| S1_morphological | `20.652004` |
| S2_lexical_diversity | `95.271312` |
| S3_structural | `128.424448` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 45.117625 | 45.117625 |
| S5_cross_level | 1.0 | 112.273488 | 112.273488 |
| S1_morphological | 1.0 | 20.652004 | 20.652004 |
| S2_lexical_diversity | 1.0 | 95.271312 | 95.271312 |
| S3_structural | 1.0 | 128.424448 | 128.424448 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 66.976087** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `169.085609` |
| S5_cross_level | `1176.043490` |
| S1_morphological | `324.575029` |
| S2_lexical_diversity | `766.570636` |
| S3_structural | `1355.849543` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 169.085609 | 169.085609 |
| S5_cross_level | 1.0 | 1176.043490 | 1176.043490 |
| S1_morphological | 1.0 | 324.575029 | 324.575029 |
| S2_lexical_diversity | 1.0 | 766.570636 | 766.570636 |
| S3_structural | 1.0 | 1355.849543 | 1355.849543 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 632.099149** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `170.727270` |
| S5_cross_level | `1179.710196` |
| S1_morphological | `341.616033` |
| S2_lexical_diversity | `775.469055` |
| S3_structural | `1376.854812` |
| cat (Hamming) | `0.470588` (8/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 170.727270 | 170.727270 |
| S5_cross_level | 1.0 | 1179.710196 | 1179.710196 |
| S1_morphological | 1.0 | 341.616033 | 341.616033 |
| S2_lexical_diversity | 1.0 | 775.469055 | 775.469055 |
| S3_structural | 1.0 | 1376.854812 | 1376.854812 |
| cat | 1.0 | 0.470588 | 0.470588 |
| **Total** | Σw = 6.0000 | | **D = 640.807993** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `94.944865` |
| S5_cross_level | `766.600486` |
| S1_morphological | `188.439981` |
| S2_lexical_diversity | `461.938288` |
| S3_structural | `903.553299` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 94.944865 | 94.944865 |
| S5_cross_level | 1.0 | 766.600486 | 766.600486 |
| S1_morphological | 1.0 | 188.439981 | 188.439981 |
| S2_lexical_diversity | 1.0 | 461.938288 | 461.938288 |
| S3_structural | 1.0 | 903.553299 | 903.553299 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 402.599095** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `166.713529` |
| S5_cross_level | `1173.626645` |
| S1_morphological | `320.346960` |
| S2_lexical_diversity | `765.058820` |
| S3_structural | `1354.640842` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 166.713529 | 166.713529 |
| S5_cross_level | 1.0 | 1173.626645 | 1173.626645 |
| S1_morphological | 1.0 | 320.346960 | 320.346960 |
| S2_lexical_diversity | 1.0 | 765.058820 | 765.058820 |
| S3_structural | 1.0 | 1354.640842 | 1354.640842 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 630.172309** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `167.688406` |
| S5_cross_level | `1180.551485` |
| S1_morphological | `330.358782` |
| S2_lexical_diversity | `769.746923` |
| S3_structural | `1364.478367` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 167.688406 | 167.688406 |
| S5_cross_level | 1.0 | 1180.551485 | 1180.551485 |
| S1_morphological | 1.0 | 330.358782 | 330.358782 |
| S2_lexical_diversity | 1.0 | 769.746923 | 769.746923 |
| S3_structural | 1.0 | 1364.478367 | 1364.478367 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 635.588308** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `165.566971` |
| S5_cross_level | `1170.586368` |
| S1_morphological | `325.633908` |
| S2_lexical_diversity | `763.752896` |
| S3_structural | `1359.690485` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 165.566971 | 165.566971 |
| S5_cross_level | 1.0 | 1170.586368 | 1170.586368 |
| S1_morphological | 1.0 | 325.633908 | 325.633908 |
| S2_lexical_diversity | 1.0 | 763.752896 | 763.752896 |
| S3_structural | 1.0 | 1359.690485 | 1359.690485 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 630.920791** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `170.625900` |
| S5_cross_level | `1181.037538` |
| S1_morphological | `337.215593` |
| S2_lexical_diversity | `780.944652` |
| S3_structural | `1382.925810` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 170.625900 | 170.625900 |
| S5_cross_level | 1.0 | 1181.037538 | 1181.037538 |
| S1_morphological | 1.0 | 337.215593 | 337.215593 |
| S2_lexical_diversity | 1.0 | 780.944652 | 780.944652 |
| S3_structural | 1.0 | 1382.925810 | 1382.925810 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 642.193543** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `169.139806` |
| S5_cross_level | `1180.836311` |
| S1_morphological | `327.790430` |
| S2_lexical_diversity | `777.731003` |
| S3_structural | `1378.878727` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 169.139806 | 169.139806 |
| S5_cross_level | 1.0 | 1180.836311 | 1180.836311 |
| S1_morphological | 1.0 | 327.790430 | 327.790430 |
| S2_lexical_diversity | 1.0 | 777.731003 | 777.731003 |
| S3_structural | 1.0 | 1378.878727 | 1378.878727 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 639.170556** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `166.317792` |
| S5_cross_level | `1161.114850` |
| S1_morphological | `321.921775` |
| S2_lexical_diversity | `766.195140` |
| S3_structural | `1354.824641` |
| cat (Hamming) | `0.117647` (2/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 166.317792 | 166.317792 |
| S5_cross_level | 1.0 | 1161.114850 | 1161.114850 |
| S1_morphological | 1.0 | 321.921775 | 321.921775 |
| S2_lexical_diversity | 1.0 | 766.195140 | 766.195140 |
| S3_structural | 1.0 | 1354.824641 | 1354.824641 |
| cat | 1.0 | 0.117647 | 0.117647 |
| **Total** | Σw = 6.0000 | | **D = 628.415307** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `169.213815` |
| S5_cross_level | `1175.570432` |
| S1_morphological | `329.386901` |
| S2_lexical_diversity | `775.676170` |
| S3_structural | `1372.921180` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 169.213815 | 169.213815 |
| S5_cross_level | 1.0 | 1175.570432 | 1175.570432 |
| S1_morphological | 1.0 | 329.386901 | 329.386901 |
| S2_lexical_diversity | 1.0 | 775.676170 | 775.676170 |
| S3_structural | 1.0 | 1372.921180 | 1372.921180 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 637.186907** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `167.981982` |
| S5_cross_level | `1172.205590` |
| S1_morphological | `319.681439` |
| S2_lexical_diversity | `765.404690` |
| S3_structural | `1350.366917` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 167.981982 | 167.981982 |
| S5_cross_level | 1.0 | 1172.205590 | 1172.205590 |
| S1_morphological | 1.0 | 319.681439 | 319.681439 |
| S2_lexical_diversity | 1.0 | 765.404690 | 765.404690 |
| S3_structural | 1.0 | 1350.366917 | 1350.366917 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 629.332260** |

### §§ 4–5 · Similarity % (max_D = `642.193543`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | wikipedia | `66.976087` | 89.6% | ← yes |
| 2 | exorde-social-media-december-2024-week1 | `402.599095` | 37.3% | ← yes |
| 3 | multilingual_toxicity_dataset | `615.372513` | 4.2% | ← yes |
| 4 | multilingual_cc_news | `628.415307` | 2.1% |  |
| 5 | language-identification | `629.332260` | 2.0% |  |
| 6 | multi_eurlex | `630.172309` | 1.9% |  |
| 7 | OpenLID-v2 | `630.920791` | 1.8% |  |
| 8 | amazon_reviews_multi | `632.099149` | 1.6% |  |
| 9 | xlsum | `632.690635` | 1.5% |  |
| 10 | tweet_sentiment_multilingual | `635.588308` | 1.0% |  |
| 11 | flores_plus | `636.840265` | 0.8% |  |
| 12 | xnli | `637.186907` | 0.8% |  |
| 13 | massive | `637.833289` | 0.7% |  |
| 14 | europarl | `639.170556` | 0.5% |  |
| 15 | mmarco | `640.386300` | 0.3% |  |
| 16 | tydiqa | `640.807993` | 0.2% |  |
| 17 | stsb_multi_mt | `642.193543` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `wikipedia`** — inv_d = `0.014931`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_wikipedia | 0.978142 | 0 | 1.0000 | 0.014604 |
| tfidf_char_ngram_3_5_wikipedia | 0.978001 | 0 | 1.0000 | 0.014602 |
| fasttext_subword_wikipedia | 0.996392 | 0 | 1.0000 | 0.014877 |
| fasttext_word_wikipedia | 0.959658 | 0 | 1.0000 | 0.014328 |
| lid.176_wikipedia | 0.939608 | 0 | 1.0000 | 0.014029 |
| cld3_wikipedia | 0.936570 | 0 | 1.0000 | 0.013984 |
| bow_maxabs_lr_char_ngram_3_5_wikipedia | 0.985320 | 0 | 1.0000 | 0.014712 |
| tfidf_lr_char_ngram_3_5_wikipedia | 0.985134 | 0 | 1.0000 | 0.014709 |

**Neighbour: `exorde-social-media-december-2024-week1`** — inv_d = `0.002484`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.901701 | 0 | 1.0000 | 0.002240 |
| tfidf_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.903643 | 0 | 1.0000 | 0.002245 |
| fasttext_subword_exorde-social-media-december-2024-week1 | 0.968330 | 0 | 1.0000 | 0.002405 |
| fasttext_word_exorde-social-media-december-2024-week1 | 0.895768 | 0 | 1.0000 | 0.002225 |
| lid.176_exorde-social-media-december-2024-week1 | 0.977396 | 0 | 1.0000 | 0.002428 |
| cld3_exorde-social-media-december-2024-week1 | 0.914822 | 0 | 1.0000 | 0.002272 |
| bow_maxabs_lr_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.913583 | 0 | 1.0000 | 0.002269 |
| tfidf_lr_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.922312 | 0 | 1.0000 | 0.002291 |

**Neighbour: `multilingual_toxicity_dataset`** — inv_d = `0.001625`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multilingual_toxicity_dataset | 0.955714 | 14 | 0.3913 | 0.000608 |
| tfidf_char_ngram_3_5_multilingual_toxicity_dataset | 0.956080 | 14 | 0.3913 | 0.000608 |
| fasttext_subword_multilingual_toxicity_dataset | 0.995558 | 14 | 0.3913 | 0.000633 |
| fasttext_word_multilingual_toxicity_dataset | 0.838982 | 14 | 0.3913 | 0.000533 |
| lid.176_multilingual_toxicity_dataset | 0.990585 | 14 | 0.3913 | 0.000630 |
| cld3_multilingual_toxicity_dataset | 0.979348 | 14 | 0.3913 | 0.000623 |
| bow_maxabs_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.970372 | 14 | 0.3913 | 0.000617 |
| tfidf_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.985689 | 14 | 0.3913 | 0.000627 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.002240 | 0.002484 | **0.901701** |
| bow_char_ngram_3_5_multilingual_toxicity_dataset | 0.000608 | 0.001625 | **0.373975** |
| bow_char_ngram_3_5_wikipedia | 0.014604 | 0.014931 | **0.978142** |
| bow_maxabs_lr_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.002269 | 0.002484 | **0.913583** |
| bow_maxabs_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.000617 | 0.001625 | **0.379711** |
| bow_maxabs_lr_char_ngram_3_5_wikipedia | 0.014712 | 0.014931 | **0.985320** |
| cld3_exorde-social-media-december-2024-week1 | 0.002272 | 0.002484 | **0.914822** |
| cld3_multilingual_toxicity_dataset | 0.000623 | 0.001625 | **0.383223** |
| cld3_wikipedia | 0.013984 | 0.014931 | **0.936570** |
| fasttext_subword_exorde-social-media-december-2024-week1 | 0.002405 | 0.002484 | **0.968330** |
| fasttext_subword_multilingual_toxicity_dataset | 0.000633 | 0.001625 | **0.389566** |
| fasttext_subword_wikipedia | 0.014877 | 0.014931 | **0.996392** |
| fasttext_word_exorde-social-media-december-2024-week1 | 0.002225 | 0.002484 | **0.895768** |
| fasttext_word_multilingual_toxicity_dataset | 0.000533 | 0.001625 | **0.328297** |
| fasttext_word_wikipedia | 0.014328 | 0.014931 | **0.959658** |
| lid.176_exorde-social-media-december-2024-week1 | 0.002428 | 0.002484 | **0.977396** |
| lid.176_multilingual_toxicity_dataset | 0.000630 | 0.001625 | **0.387620** |
| lid.176_wikipedia | 0.014029 | 0.014931 | **0.939608** |
| tfidf_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.002245 | 0.002484 | **0.903643** |
| tfidf_char_ngram_3_5_multilingual_toxicity_dataset | 0.000608 | 0.001625 | **0.374118** |
| tfidf_char_ngram_3_5_wikipedia | 0.014602 | 0.014931 | **0.978001** |
| tfidf_lr_char_ngram_3_5_exorde-social-media-december-2024-week1 | 0.002291 | 0.002484 | **0.922312** |
| tfidf_lr_char_ngram_3_5_multilingual_toxicity_dataset | 0.000627 | 0.001625 | **0.385704** |
| tfidf_lr_char_ngram_3_5_wikipedia | 0.014709 | 0.014931 | **0.985134** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_wikipedia`

---

## Dataset: `xlsum`

**Query languages:** `['en', 'es', 'fr', 'ja', 'ko', 'pt', 'ru', 'uk', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `8.517729` |
| S5_cross_level | `35.702615` |
| S1_morphological | `44.501227` |
| S2_lexical_diversity | `50.290328` |
| S3_structural | `78.299043` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 8.517729 | 8.517729 |
| S5_cross_level | 1.0 | 35.702615 | 35.702615 |
| S1_morphological | 1.0 | 44.501227 | 44.501227 |
| S2_lexical_diversity | 1.0 | 50.290328 | 50.290328 |
| S3_structural | 1.0 | 78.299043 | 78.299043 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 36.257706** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `20.186108` |
| S5_cross_level | `50.325387` |
| S1_morphological | `52.984085` |
| S2_lexical_diversity | `56.964538` |
| S3_structural | `85.621779` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 20.186108 | 20.186108 |
| S5_cross_level | 1.0 | 50.325387 | 50.325387 |
| S1_morphological | 1.0 | 52.984085 | 52.984085 |
| S2_lexical_diversity | 1.0 | 56.964538 | 56.964538 |
| S3_structural | 1.0 | 85.621779 | 85.621779 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 44.405806** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.019052` |
| S5_cross_level | `28.837607` |
| S1_morphological | `39.523759` |
| S2_lexical_diversity | `32.771537` |
| S3_structural | `57.529330` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.019052 | 9.019052 |
| S5_cross_level | 1.0 | 28.837607 | 28.837607 |
| S1_morphological | 1.0 | 39.523759 | 39.523759 |
| S2_lexical_diversity | 1.0 | 32.771537 | 32.771537 |
| S3_structural | 1.0 | 57.529330 | 57.529330 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 28.035116** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `1.268407` |
| S5_cross_level | `9.992063` |
| S1_morphological | `8.954592` |
| S2_lexical_diversity | `8.898519` |
| S3_structural | `11.044612` |
| cat (Hamming) | `0.000000` (0/17 flags differ) |

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 1.268407 | 1.268407 |
| S5_cross_level | 1.0 | 9.992063 | 9.992063 |
| S1_morphological | 1.0 | 8.954592 | 8.954592 |
| S2_lexical_diversity | 1.0 | 8.898519 | 8.898519 |
| S3_structural | 1.0 | 11.044612 | 11.044612 |
| cat | 1.0 | 0.000000 | 0.000000 |
| **Total** | Σw = 6.0000 | | **D = 6.693032** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `20.334683` |
| S5_cross_level | `52.006976` |
| S1_morphological | `52.512206` |
| S2_lexical_diversity | `58.558650` |
| S3_structural | `83.892393` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 20.334683 | 20.334683 |
| S5_cross_level | 1.0 | 52.006976 | 52.006976 |
| S1_morphological | 1.0 | 52.512206 | 52.512206 |
| S2_lexical_diversity | 1.0 | 58.558650 | 58.558650 |
| S3_structural | 1.0 | 83.892393 | 83.892393 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 44.609641** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `201.947627` |
| S5_cross_level | `1233.656411` |
| S1_morphological | `316.597604` |
| S2_lexical_diversity | `832.400844` |
| S3_structural | `1252.782280` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 201.947627 | 201.947627 |
| S5_cross_level | 1.0 | 1233.656411 | 1233.656411 |
| S1_morphological | 1.0 | 316.597604 | 316.597604 |
| S2_lexical_diversity | 1.0 | 832.400844 | 832.400844 |
| S3_structural | 1.0 | 1252.782280 | 1252.782280 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 639.622951** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `6.699565` |
| S5_cross_level | `15.557107` |
| S1_morphological | `38.998265` |
| S2_lexical_diversity | `38.045519` |
| S3_structural | `70.569108` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 6.699565 | 6.699565 |
| S5_cross_level | 1.0 | 15.557107 | 15.557107 |
| S1_morphological | 1.0 | 38.998265 | 38.998265 |
| S2_lexical_diversity | 1.0 | 38.045519 | 38.045519 |
| S3_structural | 1.0 | 70.569108 | 70.569108 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 28.380222** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `20.727547` |
| S5_cross_level | `60.905368` |
| S1_morphological | `50.953077` |
| S2_lexical_diversity | `61.024965` |
| S3_structural | `76.832283` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 20.727547 | 20.727547 |
| S5_cross_level | 1.0 | 60.905368 | 60.905368 |
| S1_morphological | 1.0 | 50.953077 | 50.953077 |
| S2_lexical_diversity | 1.0 | 61.024965 | 61.024965 |
| S3_structural | 1.0 | 76.832283 | 76.832283 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 45.142501** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `76.099911` |
| S5_cross_level | `408.484686` |
| S1_morphological | `143.630624` |
| S2_lexical_diversity | `316.853628` |
| S3_structural | `470.151707` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 76.099911 | 76.099911 |
| S5_cross_level | 1.0 | 408.484686 | 408.484686 |
| S1_morphological | 1.0 | 143.630624 | 143.630624 |
| S2_lexical_diversity | 1.0 | 316.853628 | 316.853628 |
| S3_structural | 1.0 | 470.151707 | 470.151707 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 235.928916** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `12.641066` |
| S5_cross_level | `24.024027` |
| S1_morphological | `52.316160` |
| S2_lexical_diversity | `65.331258` |
| S3_structural | `122.920131` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 12.641066 | 12.641066 |
| S5_cross_level | 1.0 | 24.024027 | 24.024027 |
| S1_morphological | 1.0 | 52.316160 | 52.316160 |
| S2_lexical_diversity | 1.0 | 65.331258 | 65.331258 |
| S3_structural | 1.0 | 122.920131 | 122.920131 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 46.313284** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `14.012106` |
| S5_cross_level | `26.865630` |
| S1_morphological | `51.039392` |
| S2_lexical_diversity | `44.705662` |
| S3_structural | `65.948934` |
| cat (Hamming) | `0.647059` (11/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 14.012106 | 14.012106 |
| S5_cross_level | 1.0 | 26.865630 | 26.865630 |
| S1_morphological | 1.0 | 51.039392 | 51.039392 |
| S2_lexical_diversity | 1.0 | 44.705662 | 44.705662 |
| S3_structural | 1.0 | 65.948934 | 65.948934 |
| cat | 1.0 | 0.647059 | 0.647059 |
| **Total** | Σw = 6.0000 | | **D = 33.869797** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `13.694195` |
| S5_cross_level | `39.922604` |
| S1_morphological | `40.381989` |
| S2_lexical_diversity | `75.043898` |
| S3_structural | `67.186979` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 13.694195 | 13.694195 |
| S5_cross_level | 1.0 | 39.922604 | 39.922604 |
| S1_morphological | 1.0 | 40.381989 | 40.381989 |
| S2_lexical_diversity | 1.0 | 75.043898 | 75.043898 |
| S3_structural | 1.0 | 67.186979 | 67.186979 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 39.459846** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `15.786623` |
| S5_cross_level | `33.534573` |
| S1_morphological | `44.672553` |
| S2_lexical_diversity | `42.701574` |
| S3_structural | `63.087042` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 15.786623 | 15.786623 |
| S5_cross_level | 1.0 | 33.534573 | 33.534573 |
| S1_morphological | 1.0 | 44.672553 | 44.672553 |
| S2_lexical_diversity | 1.0 | 42.701574 | 42.701574 |
| S3_structural | 1.0 | 63.087042 | 63.087042 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 33.355884** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.362152` |
| S5_cross_level | `28.813369` |
| S1_morphological | `57.072049` |
| S2_lexical_diversity | `43.580141` |
| S3_structural | `82.340550` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.362152 | 11.362152 |
| S5_cross_level | 1.0 | 28.813369 | 28.813369 |
| S1_morphological | 1.0 | 57.072049 | 57.072049 |
| S2_lexical_diversity | 1.0 | 43.580141 | 43.580141 |
| S3_structural | 1.0 | 82.340550 | 82.340550 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 37.312357** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `6.844585` |
| S5_cross_level | `21.020541` |
| S1_morphological | `24.659783` |
| S2_lexical_diversity | `17.288168` |
| S3_structural | `34.872685` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 6.844585 | 6.844585 |
| S5_cross_level | 1.0 | 21.020541 | 21.020541 |
| S1_morphological | 1.0 | 24.659783 | 24.659783 |
| S2_lexical_diversity | 1.0 | 17.288168 | 17.288168 |
| S3_structural | 1.0 | 34.872685 | 34.872685 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 17.506450** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `11.968428` |
| S5_cross_level | `24.996447` |
| S1_morphological | `34.172460` |
| S2_lexical_diversity | `39.159251` |
| S3_structural | `67.112451` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 11.968428 | 11.968428 |
| S5_cross_level | 1.0 | 24.996447 | 24.996447 |
| S1_morphological | 1.0 | 34.172460 | 34.172460 |
| S2_lexical_diversity | 1.0 | 39.159251 | 39.159251 |
| S3_structural | 1.0 | 67.112451 | 67.112451 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 29.626997** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `9.555974` |
| S5_cross_level | `12.522766` |
| S1_morphological | `34.490791` |
| S2_lexical_diversity | `30.001890` |
| S3_structural | `57.113588` |
| cat (Hamming) | `0.294118` (5/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 9.555974 | 9.555974 |
| S5_cross_level | 1.0 | 12.522766 | 12.522766 |
| S1_morphological | 1.0 | 34.490791 | 34.490791 |
| S2_lexical_diversity | 1.0 | 30.001890 | 30.001890 |
| S3_structural | 1.0 | 57.113588 | 57.113588 |
| cat | 1.0 | 0.294118 | 0.294118 |
| **Total** | Σw = 6.0000 | | **D = 23.996521** |

### §§ 4–5 · Similarity % (max_D = `639.622951`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | xlsum | `6.693032` | 99.0% | ← yes |
| 2 | multilingual_cc_news | `17.506450` | 97.3% | ← yes |
| 3 | language-identification | `23.996521` | 96.2% | ← yes |
| 4 | flores_plus | `28.035116` | 95.6% |  |
| 5 | amazon_reviews_multi | `28.380222` | 95.6% |  |
| 6 | xnli | `29.626997` | 95.4% |  |
| 7 | stsb_multi_mt | `33.355884` | 94.8% |  |
| 8 | tweet_sentiment_multilingual | `33.869797` | 94.7% |  |
| 9 | multilingual_toxicity_dataset | `36.257706` | 94.3% |  |
| 10 | europarl | `37.312357` | 94.2% |  |
| 11 | OpenLID-v2 | `39.459846` | 93.8% |  |
| 12 | massive | `44.405806` | 93.1% |  |
| 13 | mmarco | `44.609641` | 93.0% |  |
| 14 | tydiqa | `45.142501` | 92.9% |  |
| 15 | multi_eurlex | `46.313284` | 92.8% |  |
| 16 | exorde-social-media-december-2024-week1 | `235.928916` | 63.1% |  |
| 17 | wikipedia | `639.622951` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `xlsum`** — inv_d = `0.149409`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_xlsum | 0.981335 | 0 | 1.0000 | 0.146620 |
| tfidf_char_ngram_3_5_xlsum | 0.981388 | 0 | 1.0000 | 0.146628 |
| fasttext_subword_xlsum | 0.998764 | 0 | 1.0000 | 0.149224 |
| fasttext_word_xlsum | 0.974218 | 0 | 1.0000 | 0.145557 |
| lid.176_xlsum | 0.998587 | 0 | 1.0000 | 0.149198 |
| cld3_xlsum | 0.994289 | 0 | 1.0000 | 0.148556 |
| bow_maxabs_lr_char_ngram_3_5_xlsum | 0.979869 | 0 | 1.0000 | 0.146401 |
| tfidf_lr_char_ngram_3_5_xlsum | 0.981645 | 0 | 1.0000 | 0.146667 |

**Neighbour: `multilingual_cc_news`** — inv_d = `0.057122`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_multilingual_cc_news | 0.975398 | 2 | 0.7778 | 0.043335 |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.976358 | 2 | 0.7778 | 0.043378 |
| fasttext_subword_multilingual_cc_news | 0.997083 | 2 | 0.7778 | 0.044298 |
| fasttext_word_multilingual_cc_news | 0.985130 | 2 | 0.7778 | 0.043767 |
| lid.176_multilingual_cc_news | 0.928836 | 2 | 0.7778 | 0.041266 |
| cld3_multilingual_cc_news | 0.955450 | 2 | 0.7778 | 0.042449 |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.975948 | 2 | 0.7778 | 0.043359 |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.979512 | 2 | 0.7778 | 0.043518 |

**Neighbour: `language-identification`** — inv_d = `0.041673`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_language-identification | 0.997934 | 2 | 0.7778 | 0.032345 |
| tfidf_char_ngram_3_5_language-identification | 0.998033 | 2 | 0.7778 | 0.032348 |
| fasttext_subword_language-identification | 0.996164 | 2 | 0.7778 | 0.032288 |
| fasttext_word_language-identification | 0.870988 | 2 | 0.7778 | 0.028231 |
| lid.176_language-identification | 0.995624 | 2 | 0.7778 | 0.032270 |
| cld3_language-identification | 0.984446 | 2 | 0.7778 | 0.031908 |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.984950 | 2 | 0.7778 | 0.031924 |
| tfidf_lr_char_ngram_3_5_language-identification | 0.995288 | 2 | 0.7778 | 0.032259 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_language-identification | 0.032345 | 0.041673 | **0.776171** |
| bow_char_ngram_3_5_multilingual_cc_news | 0.043335 | 0.057122 | **0.758643** |
| bow_char_ngram_3_5_xlsum | 0.146620 | 0.149409 | **0.981335** |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.031924 | 0.041673 | **0.766072** |
| bow_maxabs_lr_char_ngram_3_5_multilingual_cc_news | 0.043359 | 0.057122 | **0.759071** |
| bow_maxabs_lr_char_ngram_3_5_xlsum | 0.146401 | 0.149409 | **0.979869** |
| cld3_language-identification | 0.031908 | 0.041673 | **0.765680** |
| cld3_multilingual_cc_news | 0.042449 | 0.057122 | **0.743128** |
| cld3_xlsum | 0.148556 | 0.149409 | **0.994289** |
| fasttext_subword_language-identification | 0.032288 | 0.041673 | **0.774794** |
| fasttext_subword_multilingual_cc_news | 0.044298 | 0.057122 | **0.775509** |
| fasttext_subword_xlsum | 0.149224 | 0.149409 | **0.998764** |
| fasttext_word_language-identification | 0.028231 | 0.041673 | **0.677435** |
| fasttext_word_multilingual_cc_news | 0.043767 | 0.057122 | **0.766212** |
| fasttext_word_xlsum | 0.145557 | 0.149409 | **0.974218** |
| lid.176_language-identification | 0.032270 | 0.041673 | **0.774374** |
| lid.176_multilingual_cc_news | 0.041266 | 0.057122 | **0.722428** |
| lid.176_xlsum | 0.149198 | 0.149409 | **0.998587** |
| tfidf_char_ngram_3_5_language-identification | 0.032348 | 0.041673 | **0.776248** |
| tfidf_char_ngram_3_5_multilingual_cc_news | 0.043378 | 0.057122 | **0.759390** |
| tfidf_char_ngram_3_5_xlsum | 0.146628 | 0.149409 | **0.981388** |
| tfidf_lr_char_ngram_3_5_language-identification | 0.032259 | 0.041673 | **0.774113** |
| tfidf_lr_char_ngram_3_5_multilingual_cc_news | 0.043518 | 0.057122 | **0.761843** |
| tfidf_lr_char_ngram_3_5_xlsum | 0.146667 | 0.149409 | **0.981645** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `fasttext_subword_xlsum`

---

## Dataset: `xnli`

**Query languages:** `['de', 'el', 'en', 'es', 'fr', 'ko', 'pt', 'ru', 'zh']`  
**Priority metric:** `f1_weighted` | k = 3

### § 0 · PCA Pipeline

| Stratum | PCs retained | Per-PC variance % | Cumulative % |
|---|---|---|---|
| S4_info_theoretic | 4 | [54.0, 25.7, 13.5, 5.4] | 98.58% |
| S5_cross_level | 9 | [44.5, 18.1, 11.7, 7.8, 4.7, 3.4, 2.7, 1.8, 1.4] | 96.12% |
| S1_morphological | 14 | [31.4, 13.6, 12.0, 8.1, 6.6, 4.8, 3.7, 3.5, 2.7, 2.1, 1.8, 1.7, 1.6, 1.4] | 95.02% |
| S2_lexical_diversity | 12 | [35.3, 16.7, 10.4, 7.5, 5.8, 5.2, 3.9, 3.3, 2.6, 1.8, 1.7, 1.3] | 95.49% |
| S3_structural | 13 | [28.9, 15.9, 13.7, 7.2, 6.7, 5.7, 4.5, 3.3, 2.7, 2.1, 1.9, 1.7, 1.1] | 95.46% |

**Stratum weights (w_s):** `{'S1_morphological': 1.0, 'S2_lexical_diversity': 1.0, 'S3_structural': 1.0, 'S4_info_theoretic': 1.0, 'S5_cross_level': 1.0, 'cat': 1.0}`

### §§ 1–3 · Per-Stratum Distances (all candidates)

#### Candidate: `multilingual_toxicity_dataset`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `54.540932` |
| S5_cross_level | `59.241644` |
| S1_morphological | `32.544259` |
| S2_lexical_diversity | `227.766863` |
| S3_structural | `75.314322` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 54.540932 | 54.540932 |
| S5_cross_level | 1.0 | 59.241644 | 59.241644 |
| S1_morphological | 1.0 | 32.544259 | 32.544259 |
| S2_lexical_diversity | 1.0 | 227.766863 | 227.766863 |
| S3_structural | 1.0 | 75.314322 | 75.314322 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 74.940552** |

#### Candidate: `massive`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `54.446960` |
| S5_cross_level | `33.147125` |
| S1_morphological | `40.021121` |
| S2_lexical_diversity | `233.029499` |
| S3_structural | `69.323157` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 54.446960 | 54.446960 |
| S5_cross_level | 1.0 | 33.147125 | 33.147125 |
| S1_morphological | 1.0 | 40.021121 | 40.021121 |
| S2_lexical_diversity | 1.0 | 233.029499 | 233.029499 |
| S3_structural | 1.0 | 69.323157 | 69.323157 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 71.700526** |

#### Candidate: `flores_plus`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `56.815243` |
| S5_cross_level | `53.496228` |
| S1_morphological | `30.120691` |
| S2_lexical_diversity | `232.439355` |
| S3_structural | `80.517962` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 56.815243 | 56.815243 |
| S5_cross_level | 1.0 | 53.496228 | 53.496228 |
| S1_morphological | 1.0 | 30.120691 | 30.120691 |
| S2_lexical_diversity | 1.0 | 232.439355 | 232.439355 |
| S3_structural | 1.0 | 80.517962 | 80.517962 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 75.633541** |

#### Candidate: `xlsum`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `56.982423` |
| S5_cross_level | `49.162572` |
| S1_morphological | `29.448080` |
| S2_lexical_diversity | `234.498822` |
| S3_structural | `75.575237` |
| cat (Hamming) | `0.176471` (3/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 56.982423 | 56.982423 |
| S5_cross_level | 1.0 | 49.162572 | 49.162572 |
| S1_morphological | 1.0 | 29.448080 | 29.448080 |
| S2_lexical_diversity | 1.0 | 234.498822 | 234.498822 |
| S3_structural | 1.0 | 75.575237 | 75.575237 |
| cat | 1.0 | 0.176471 | 0.176471 |
| **Total** | Σw = 6.0000 | | **D = 74.307267** |

#### Candidate: `mmarco`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `56.657933` |
| S5_cross_level | `35.514441` |
| S1_morphological | `47.058327` |
| S2_lexical_diversity | `233.820953` |
| S3_structural | `85.655759` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 56.657933 | 56.657933 |
| S5_cross_level | 1.0 | 35.514441 | 35.514441 |
| S1_morphological | 1.0 | 47.058327 | 47.058327 |
| S2_lexical_diversity | 1.0 | 233.820953 | 233.820953 |
| S3_structural | 1.0 | 85.655759 | 85.655759 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 76.510059** |

#### Candidate: `wikipedia`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `199.121296` |
| S5_cross_level | `1230.123499` |
| S1_morphological | `312.809742` |
| S2_lexical_diversity | `826.834942` |
| S3_structural | `1242.007056` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 199.121296 | 199.121296 |
| S5_cross_level | 1.0 | 1230.123499 | 1230.123499 |
| S1_morphological | 1.0 | 312.809742 | 312.809742 |
| S2_lexical_diversity | 1.0 | 826.834942 | 826.834942 |
| S3_structural | 1.0 | 1242.007056 | 1242.007056 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 635.188638** |

#### Candidate: `amazon_reviews_multi`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `57.971270` |
| S5_cross_level | `52.190552` |
| S1_morphological | `41.645236` |
| S2_lexical_diversity | `232.110392` |
| S3_structural | `87.498942` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__has_cyrillic', 'cat__n_languages', 'cat__has_greek']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 57.971270 | 57.971270 |
| S5_cross_level | 1.0 | 52.190552 | 52.190552 |
| S1_morphological | 1.0 | 41.645236 | 41.645236 |
| S2_lexical_diversity | 1.0 | 232.110392 | 232.110392 |
| S3_structural | 1.0 | 87.498942 | 87.498942 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 78.638026** |

#### Candidate: `tydiqa`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `55.800300` |
| S5_cross_level | `38.924926` |
| S1_morphological | `49.777637` |
| S2_lexical_diversity | `234.253591` |
| S3_structural | `85.970761` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 55.800300 | 55.800300 |
| S5_cross_level | 1.0 | 38.924926 | 38.924926 |
| S1_morphological | 1.0 | 49.777637 | 49.777637 |
| S2_lexical_diversity | 1.0 | 234.253591 | 234.253591 |
| S3_structural | 1.0 | 85.970761 | 85.970761 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 77.542771** |

#### Candidate: `exorde-social-media-december-2024-week1`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `81.919173` |
| S5_cross_level | `406.792358` |
| S1_morphological | `139.012967` |
| S2_lexical_diversity | `361.243530` |
| S3_structural | `460.287025` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 81.919173 | 81.919173 |
| S5_cross_level | 1.0 | 406.792358 | 406.792358 |
| S1_morphological | 1.0 | 139.012967 | 139.012967 |
| S2_lexical_diversity | 1.0 | 361.243530 | 361.243530 |
| S3_structural | 1.0 | 460.287025 | 460.287025 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 241.581725** |

#### Candidate: `multi_eurlex`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `54.207082` |
| S5_cross_level | `48.722351` |
| S1_morphological | `54.941378` |
| S2_lexical_diversity | `216.088142` |
| S3_structural | `152.785770` |
| cat (Hamming) | `0.529412` (9/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 54.207082 | 54.207082 |
| S5_cross_level | 1.0 | 48.722351 | 48.722351 |
| S1_morphological | 1.0 | 54.941378 | 54.941378 |
| S2_lexical_diversity | 1.0 | 216.088142 | 216.088142 |
| S3_structural | 1.0 | 152.785770 | 152.785770 |
| cat | 1.0 | 0.529412 | 0.529412 |
| **Total** | Σw = 6.0000 | | **D = 87.879023** |

#### Candidate: `tweet_sentiment_multilingual`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `53.451002` |
| S5_cross_level | `56.016983` |
| S1_morphological | `46.243624` |
| S2_lexical_diversity | `230.325722` |
| S3_structural | `90.378681` |
| cat (Hamming) | `0.705882` (12/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 53.451002 | 53.451002 |
| S5_cross_level | 1.0 | 56.016983 | 56.016983 |
| S1_morphological | 1.0 | 46.243624 | 46.243624 |
| S2_lexical_diversity | 1.0 | 230.325722 | 230.325722 |
| S3_structural | 1.0 | 90.378681 | 90.378681 |
| cat | 1.0 | 0.705882 | 0.705882 |
| **Total** | Σw = 6.0000 | | **D = 79.520316** |

#### Candidate: `OpenLID-v2`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `51.520053` |
| S5_cross_level | `59.096338` |
| S1_morphological | `26.519120` |
| S2_lexical_diversity | `168.377206` |
| S3_structural | `74.922022` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_isolating', 'cat__n_language_families', 'cat__n_tonal', 'cat__has_tonal', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 51.520053 | 51.520053 |
| S5_cross_level | 1.0 | 59.096338 | 59.096338 |
| S1_morphological | 1.0 | 26.519120 | 26.519120 |
| S2_lexical_diversity | 1.0 | 168.377206 | 168.377206 |
| S3_structural | 1.0 | 74.922022 | 74.922022 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 63.474418** |

#### Candidate: `stsb_multi_mt`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `57.761240` |
| S5_cross_level | `58.287106` |
| S1_morphological | `43.284720` |
| S2_lexical_diversity | `234.958710` |
| S3_structural | `89.392926` |
| cat (Hamming) | `0.411765` (7/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__has_greek', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 57.761240 | 57.761240 |
| S5_cross_level | 1.0 | 58.287106 | 58.287106 |
| S1_morphological | 1.0 | 43.284720 | 43.284720 |
| S2_lexical_diversity | 1.0 | 234.958710 | 234.958710 |
| S3_structural | 1.0 | 89.392926 | 89.392926 |
| cat | 1.0 | 0.411765 | 0.411765 |
| **Total** | Σw = 6.0000 | | **D = 80.682745** |

#### Candidate: `europarl`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `56.492753` |
| S5_cross_level | `57.815974` |
| S1_morphological | `45.119703` |
| S2_lexical_diversity | `235.039999` |
| S3_structural | `89.758521` |
| cat (Hamming) | `0.588235` (10/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_isolating', 'cat__n_language_families', 'cat__has_cjk', 'cat__n_tonal', 'cat__has_cyrillic', 'cat__has_tonal', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 56.492753 | 56.492753 |
| S5_cross_level | 1.0 | 57.815974 | 57.815974 |
| S1_morphological | 1.0 | 45.119703 | 45.119703 |
| S2_lexical_diversity | 1.0 | 235.039999 | 235.039999 |
| S3_structural | 1.0 | 89.758521 | 89.758521 |
| cat | 1.0 | 0.588235 | 0.588235 |
| **Total** | Σw = 6.0000 | | **D = 80.802531** |

#### Candidate: `multilingual_cc_news`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `54.968533` |
| S5_cross_level | `51.677779` |
| S1_morphological | `32.892957` |
| S2_lexical_diversity | `225.055645` |
| S3_structural | `77.842389` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_polysyllabic', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 54.968533 | 54.968533 |
| S5_cross_level | 1.0 | 51.677779 | 51.677779 |
| S1_morphological | 1.0 | 32.892957 | 32.892957 |
| S2_lexical_diversity | 1.0 | 225.055645 | 225.055645 |
| S3_structural | 1.0 | 77.842389 | 77.842389 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 73.778766** |

#### Candidate: `xnli`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `58.222248` |
| S5_cross_level | `52.790755` |
| S1_morphological | `16.977268` |
| S2_lexical_diversity | `229.214459` |
| S3_structural | `62.614827` |
| cat (Hamming) | `0.352941` (6/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_language_families', 'cat__n_languages', 'cat__n_agglutinative']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 58.222248 | 58.222248 |
| S5_cross_level | 1.0 | 52.790755 | 52.790755 |
| S1_morphological | 1.0 | 16.977268 | 16.977268 |
| S2_lexical_diversity | 1.0 | 229.214459 | 229.214459 |
| S3_structural | 1.0 | 62.614827 | 62.614827 |
| cat | 1.0 | 0.352941 | 0.352941 |
| **Total** | Σw = 6.0000 | | **D = 70.028750** |

#### Candidate: `language-identification`

| Stratum | d_s (Euclidean) |
|---|---|
| S4_info_theoretic | `53.751231` |
| S5_cross_level | `45.724020` |
| S1_morphological | `29.281319` |
| S2_lexical_diversity | `225.513921` |
| S3_structural | `62.189440` |
| cat (Hamming) | `0.235294` (4/17 flags differ) |

Differing categorical flags: `['cat__n_script_types', 'cat__n_polysyllabic', 'cat__has_hangul', 'cat__n_languages']`

**Weighted composite D:**

| Stratum | w_s | d_s | w_s × d_s |
|---|---|---|---|
| S4_info_theoretic | 1.0 | 53.751231 | 53.751231 |
| S5_cross_level | 1.0 | 45.724020 | 45.724020 |
| S1_morphological | 1.0 | 29.281319 | 29.281319 |
| S2_lexical_diversity | 1.0 | 225.513921 | 225.513921 |
| S3_structural | 1.0 | 62.189440 | 62.189440 |
| cat | 1.0 | 0.235294 | 0.235294 |
| **Total** | Σw = 6.0000 | | **D = 69.449204** |

### §§ 4–5 · Similarity % (max_D = `635.188638`)

sim% = (1 − D / max_D) × 100

| # | Dataset | D | sim% | In top-k? |
|---|---|---|---|---|
| 1 | OpenLID-v2 | `63.474418` | 90.0% | ← yes |
| 2 | language-identification | `69.449204` | 89.1% | ← yes |
| 3 | xnli | `70.028750` | 89.0% | ← yes |
| 4 | massive | `71.700526` | 88.7% |  |
| 5 | multilingual_cc_news | `73.778766` | 88.4% |  |
| 6 | xlsum | `74.307267` | 88.3% |  |
| 7 | multilingual_toxicity_dataset | `74.940552` | 88.2% |  |
| 8 | flores_plus | `75.633541` | 88.1% |  |
| 9 | mmarco | `76.510059` | 88.0% |  |
| 10 | tydiqa | `77.542771` | 87.8% |  |
| 11 | amazon_reviews_multi | `78.638026` | 87.6% |  |
| 12 | tweet_sentiment_multilingual | `79.520316` | 87.5% |  |
| 13 | stsb_multi_mt | `80.682745` | 87.3% |  |
| 14 | europarl | `80.802531` | 87.3% |  |
| 15 | multi_eurlex | `87.879023` | 86.2% |  |
| 16 | exorde-social-media-december-2024-week1 | `241.581725` | 62.0% |  |
| 17 | wikipedia | `635.188638` | 0.0% |  |

### §§ 6–7 · IDW Vote

score(m) = Σ(inv_d × metric_score × coverage_factor) / Σ(inv_d)

**Neighbour: `OpenLID-v2`** — inv_d = `0.015754`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.980663 | 1 | 0.8889 | 0.013733 |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.981227 | 1 | 0.8889 | 0.013741 |
| fasttext_subword_OpenLID-v2 | 0.993905 | 1 | 0.8889 | 0.013919 |
| fasttext_word_OpenLID-v2 | 0.947366 | 1 | 0.8889 | 0.013267 |
| lid.176_OpenLID-v2 | 0.901862 | 1 | 0.8889 | 0.012630 |
| cld3_OpenLID-v2 | 0.939038 | 1 | 0.8889 | 0.013150 |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.981563 | 1 | 0.8889 | 0.013746 |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.983798 | 1 | 0.8889 | 0.013777 |

**Neighbour: `language-identification`** — inv_d = `0.014399`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_language-identification | 0.997934 | 1 | 0.8889 | 0.012773 |
| tfidf_char_ngram_3_5_language-identification | 0.998033 | 1 | 0.8889 | 0.012774 |
| fasttext_subword_language-identification | 0.996164 | 1 | 0.8889 | 0.012750 |
| fasttext_word_language-identification | 0.870988 | 1 | 0.8889 | 0.011148 |
| lid.176_language-identification | 0.995624 | 1 | 0.8889 | 0.012743 |
| cld3_language-identification | 0.984446 | 1 | 0.8889 | 0.012600 |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.984950 | 1 | 0.8889 | 0.012606 |
| tfidf_lr_char_ngram_3_5_language-identification | 0.995288 | 1 | 0.8889 | 0.012739 |

**Neighbour: `xnli`** — inv_d = `0.014280`

| Model | metric score | gap_size | coverage_factor | contribution |
|---|---|---|---|---|
| bow_char_ngram_3_5_xnli | 0.995875 | 2 | 0.7778 | 0.011061 |
| tfidf_char_ngram_3_5_xnli | 0.995832 | 2 | 0.7778 | 0.011060 |
| fasttext_subword_xnli | 0.999558 | 2 | 0.7778 | 0.011102 |
| fasttext_word_xnli | 0.998835 | 2 | 0.7778 | 0.011094 |
| lid.176_xnli | 0.998968 | 2 | 0.7778 | 0.011095 |
| cld3_xnli | 0.989093 | 2 | 0.7778 | 0.010985 |
| bow_maxabs_lr_char_ngram_3_5_xnli | 0.999195 | 2 | 0.7778 | 0.011098 |
| tfidf_lr_char_ngram_3_5_xnli | 0.999401 | 2 | 0.7778 | 0.011100 |

**IDW aggregated scores (numerator / denominator → normalized):**

| Model | Σ numerator | Σ denominator | IDW score |
|---|---|---|---|
| bow_char_ngram_3_5_OpenLID-v2 | 0.013733 | 0.015754 | **0.871700** |
| bow_char_ngram_3_5_language-identification | 0.012773 | 0.014399 | **0.887052** |
| bow_char_ngram_3_5_xnli | 0.011061 | 0.014280 | **0.774569** |
| bow_maxabs_lr_char_ngram_3_5_OpenLID-v2 | 0.013746 | 0.015754 | **0.872500** |
| bow_maxabs_lr_char_ngram_3_5_language-identification | 0.012606 | 0.014399 | **0.875511** |
| bow_maxabs_lr_char_ngram_3_5_xnli | 0.011098 | 0.014280 | **0.777152** |
| cld3_OpenLID-v2 | 0.013150 | 0.015754 | **0.834700** |
| cld3_language-identification | 0.012600 | 0.014399 | **0.875063** |
| cld3_xnli | 0.010985 | 0.014280 | **0.769295** |
| fasttext_subword_OpenLID-v2 | 0.013919 | 0.015754 | **0.883471** |
| fasttext_subword_language-identification | 0.012750 | 0.014399 | **0.885479** |
| fasttext_subword_xnli | 0.011102 | 0.014280 | **0.777434** |
| fasttext_word_OpenLID-v2 | 0.013267 | 0.015754 | **0.842103** |
| fasttext_word_language-identification | 0.011148 | 0.014399 | **0.774212** |
| fasttext_word_xnli | 0.011094 | 0.014280 | **0.776872** |
| lid.176_OpenLID-v2 | 0.012630 | 0.015754 | **0.801655** |
| lid.176_language-identification | 0.012743 | 0.014399 | **0.884999** |
| lid.176_xnli | 0.011095 | 0.014280 | **0.776975** |
| tfidf_char_ngram_3_5_OpenLID-v2 | 0.013741 | 0.015754 | **0.872202** |
| tfidf_char_ngram_3_5_language-identification | 0.012774 | 0.014399 | **0.887140** |
| tfidf_char_ngram_3_5_xnli | 0.011060 | 0.014280 | **0.774536** |
| tfidf_lr_char_ngram_3_5_OpenLID-v2 | 0.013777 | 0.015754 | **0.874487** |
| tfidf_lr_char_ngram_3_5_language-identification | 0.012739 | 0.014399 | **0.884700** |
| tfidf_lr_char_ngram_3_5_xnli | 0.011100 | 0.014280 | **0.777312** |

### § 8 · Confidence

confidence = n_agreeing / k = 1 / 3 = **33.33%**

**→ Recommended model:** `tfidf_char_ngram_3_5_language-identification`

