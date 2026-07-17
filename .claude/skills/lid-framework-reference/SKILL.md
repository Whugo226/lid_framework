---
name: lid-framework-reference
description: Domain knowledge pack for the thesis's LID model-recommendation framework. Load this whenever you must reason about, write about, review, or defend the framework itself — the DeepProfiler → FeatureStratifier → FingerprintBuilder → MKBStore → SimilarityEngine pipeline, the S1–S6 strata and their feature counts, the composite-distance / IDW / consensus-confidence math, the 17-corpus/24-language data design, the model roster, or the headline validation numbers (17.6% top-1, 0.0078 mean regret, 2/2 vs 1/15 confidence split). Do NOT load it for: how to run/verify artifacts (use artifact-verification-playbook), tracing where a claim lives in the thesis text (use thesis-claims-archaeology), running the dashboard demo (use dashboard-demo-runbook), or writing-style/LaTeX questions (use thesis-writing-and-style). Paths, env, and git conventions live in thesis-estate-and-env.
---

# LID Framework Reference

The thesis ("An Interactive Framework for Language Identification Model
Recommendation", Werner Hugo, MEng Industrial Engineering, Stellenbosch)
builds a case-based-reasoning recommender: profile an unlabelled multilingual
corpus into a linguistic "fingerprint", retrieve the k most similar historical
corpora from a Meta-Knowledge Base (MKB), and recommend the LID model that
performed best on those neighbours. This skill is the ground-truth reference
for how that framework actually works and which numbers are real.

All facts below were re-verified against code and artifacts on **2026-07-12**
unless tagged otherwise. Tags: **[artifact-verified 2026-07-12]** = re-run /
re-loaded this date; **[thesis-verified 2026-07-12]** = read in the live
compiled .tex this date; **[unverified, from review session]** = carried from
the early-July 2026 review session, not re-checked.

Jargon, defined once:
| Term | Meaning |
|---|---|
| LID | Language identification (classify the language of a text) |
| MKB | Meta-Knowledge Base — pickled store (`mkb.pkl`) of 17 dataset fingerprints + 1,785 model-performance records |
| Fingerprint | Fixed-length 332-dim vector describing one dataset (315 continuous PCA stats + 17 categorical flags) |
| Stratum | One of six semantically coherent feature groups (S1–S5 continuous, S6 categorical) |
| Base-measure family | One Lingualyzer measure (e.g. "Word entropy"); expands into up to 9 level×statistic variant features |
| Core features | The fixed 2,726-feature schema after the validity filter |
| TML | Traditional machine learning (Naive Bayes / Logistic Regression pipelines, vs neural FastText / transformers) |
| Regret / Δ_f1 | Ground-truth best model's f1_weighted minus the recommended model's f1_weighted on the same evaluation split |
| Consensus confidence C | Fraction of k neighbours whose own best model equals the recommendation — a consensus measure, NOT a probability |
| Lingualyzer | Linders & Louwerse (2023) multilingual text-analysis instrument; its 351 base measures are the feature inventory the DeepProfiler implements |

## When NOT to use this skill

- You need to run/rebuild an artifact or re-verify a number end-to-end →
  `artifact-verification-playbook`.
- You need to know where in the thesis a claim is stated or whether an old
  wrong claim resurfaced → `thesis-claims-archaeology`.
- You are launching the Streamlit dashboard or the WiLI walkthrough →
  `dashboard-demo-runbook`.
- You need LaTeX house style, chapter conventions, or prose voice →
  `thesis-writing-and-style`.
- You need paths/conda env/git facts only → `thesis-estate-and-env`.

## 1. Pipeline component map [artifact-verified 2026-07-12]

All modules under `C:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit\src\lid_toolkit\`.

| Component | Module | Class / key API | Role |
|---|---|---|---|
| DeepProfiler | `logic\profiler_knowledge_base.py` | `DeepProfiler.get_multilingual_profile(text_series)` → DataFrame (features × languages) | Implements Lingualyzer's measures: spaCy annotation, wordfreq Zipf scores, compressed-fastText semantic vectors, fastText `lid.176.bin` routes each text to the right per-language spaCy model |
| FeatureStratifier | `recommender\feature_stratifier.py` | `fit(df)`, `transform(vec)` → {stratum: PC array}; `_STRATUM_PATTERNS` | Assigns every feature to one stratum (first-match-wins substring patterns), StandardScaler + PCA per stratum |
| FingerprintBuilder | `recommender\fingerprint_builder.py` | `build(df)` → `OrderedDict[str, float]`; `stratum_slice()`, `to_array()` | Per language: project into PC spaces; per PC: mean/std/min/max/het across languages; append `cat__*` S6 flags |
| Typology lookup (S6) | `recommender\typology_lookup.py` | `dataset_typology_flags(iso_codes)` → 17 `cat__*` flags; `TYPOLOGY` catalogue of exactly 24 languages | WALS/Ethnologue/Glottolog-sourced categorical properties |
| MKBStore | `recommender\mkb_store.py` | `MKBStore.load("mkb.pkl")`; `.datasets` (LIST of names), `.get_entry(name)`, `.stratifier`, `.builder`, `.finalise()`, `build_from_filesystem()` | Persists raw profiles, fitted stratifier, fingerprints, and `performances[variant][metric]` records |
| SimilarityEngine | `recommender\mkb_similarity.py` | `query(fp, priority_metric, k, user_iso_codes)` → `Recommendation`; `trace_query()` returns full math trace; `learn_weights()` | Weighted multi-stratum distance, k-NN (default k=3), coverage guard, IDW vote, consensus confidence, explanation text |
| Recommender (facade) | `recommender\recommender.py` | `Recommender.from_store("mkb.pkl")`, `.recommend(text_series)`, `.recommend_from_profile(df)`, `.evaluate_loo()`, `Recommender.build_mkb(...)` | End-to-end API used by the dashboard and validation scripts |

Query-time flow: raw texts → `DeepProfiler.get_multilingual_profile` →
`FingerprintBuilder.build` (uses the MKB's fitted stratifier) →
`SimilarityEngine.query` → `Recommendation(recommended_model, confidence,
neighbours, all_model_scores, explanation, uncoverable_languages)`.

API traps (all confirmed by running):
- `mkb.datasets` is a **list of names** — use `mkb.get_entry(name)`, never dict-index.
- `entry.fingerprint` is an OrderedDict whose `cat__*` keys are the S6 flags.
- Stratifier internals: `_fits[stratum].feature_names` = core post-filter
  names; `_feature_to_stratum` = pooled pre-filter union.
- Run everything from the repo root with
  `C:\Users\User\miniconda3\envs\thesis_final\python.exe` (miniconda3, not anaconda3), or imports/unpickling fail.

## 2. The feature space and strata S1–S5 [artifact-verified 2026-07-12]

Origin: the DeepProfiler implements **327 of Lingualyzer's 351 base
measures**. Each family expands over a variant grid: (Sentence|Paragraph) ×
(Avg, SD, Min, Max) + Document = up to 9 variants (burstiness is undefined at
sentence level → 5; some families have 8, 4, or 1). Pooled union = 2,926
assigned features; the fit-time validity filter drops exactly the 200
conditional paragraph-level variants (S1 −104, S2 −8, S3 −88) → the fixed
**2,726-feature core** every fingerprint is built from.

Per-stratum table, extracted from the fitted stratifier inside the deployed
`mkb.pkl` (re-verified by running `analysis\stratum_audit.py`, which prints
totals 2,726 / 327 / 63):

| Stratum | Construct | Lingualyzer 3×2×3 bridge | Families | Core feats | PCs | Var. |
|---|---|---|---|---|---|---|
| S1 Morphological Richness | Inflectional morphology: person, number, definiteness, tense, voice, word–lemma Levenshtein, types-per-lemma | unit = morphological | 108 | 813 | 16 | 96.1% |
| S2 Lexical Diversity | TTR, MATTR, hapax legomena, Zipf frequency scores, per-PoS type counts | unit = lexical | 51 | 433 | 15 | 95.6% |
| S3 Structural / Syntactic (catch-all) | PoS distributions/ratios, positions, lengths, counts, punctuation | unit = syntagmatic | 151 | 1,200 | 16 | 95.4% |
| S4 Information-Theoretic | Word/letter entropy, Zipf steepness & goodness-of-fit | complexity type | 4 | 20 | 5 | 97.4% |
| S5 Cross-Level Cohesion | Cross-level overlap, cosine distance, Levenshtein (Par–Doc, Sent–Doc, Par–Par adj, Sent–Par, Sent–Sent adj) | distributional type | 13 | 260 | 11 | 95.2% |
| **Total** | | | **327** | **2,726** | **63** | |

Defense narrative (from the bridging-table work): the five strata are a
**coarsening of Lingualyzer's published 3×2×3 taxonomy** (S1/S2/S3 ≈ the
linguistic-unit dimension; S4 ≈ complexity type; S5 ≈ distributional type).
Five, not eighteen, because sparse cells (S4 has only 20 features) cannot
support stable PCA, and coarser partitions reunite heterogeneous covariance
structures. Canonical prose: `Thesis Template Legit\drafts\stratum_bridging_table.tex`
(table `tab:stratum_lingualyzer_mapping`) and `drafts\stratum_audit_appendix.tex`
(`appen:stratum_audit`) — check whether they are `\input` into `thesis.tex` yet
before citing them as "in the thesis".

Assignment mechanics (in `feature_stratifier.py::_STRATUM_PATTERNS`):
- **First-match-wins** case-insensitive substring patterns on lowercased
  feature names, checked in priority order **S4 → S5 → S1 → S2 → S3**.
- **S3 is the catch-all** (its pattern list is the empty string, matching
  everything unclaimed). This looked like a design weakness; a full
  enumeration audit proved all 151 S3 families genuinely structural/syntactic.
  Verify-before-criticise.
- PCA config: `variance_threshold=0.95`, `max_components=20`, StandardScaler
  per stratum, constant columns dropped at fit, `PCA(random_state=42)`.

Known quirks — state these, never paper over them:
| Quirk | Fact | Status |
|---|---|---|
| Zipf split | Zipf *frequency* measures (frequent/infrequent word) land in S2; Zipf *steepness/goodness-of-fit* land in S4 (its patterns fire first). Defensible: lexical sophistication vs distribution shape — but must be stated explicitly. | By design; examiner-visible |
| Types-per-lemma | All 25 types-per-lemma features are in **S1** in the fitted artifact (patterns at S1 list end), and S1 is the better construct fit (paradigm size ≈ morphological richness). But the module docstring and the Ch4 S2 bullet (~`design_and_implementation.tex:226`) still say S2. | ❌ prose+docstring fix pending (2026-07-12) |
| Honoré | Docstring mentions "Honoré's statistic" in S2; no Honoré feature exists in the 2,726 core — the `honoré` pattern never fires. | ❌ docstring fix pending |
| Dead patterns | `word entropy` / `letter entropy` in the S2 pattern list (`feature_stratifier.py:120-121`) are dead — S4's `entropy` always matches first. | ❌ deletion pending |

## 3. Stratum S6 — categorical typological block [artifact-verified 2026-07-12]

Exactly **17 flags** from `typology_lookup.dataset_typology_flags()`, prefixed
`cat__`, **never PCA'd**, appended raw to the fingerprint:

`n_languages, n_tonal, has_tonal, n_script_types, has_cjk, has_cyrillic,
has_greek, has_hangul, has_latin, n_agglutinative, frac_agglutinative,
n_isolating, n_polysyllabic, n_language_families, frac_germanic,
frac_romance, frac_slavic`

(5 script-presence binaries; has_tonal; 5 counts incl. n_languages /
n_script_types / n_language_families; 3 family fractions; frac_agglutinative;
n_polysyllabic.)

S6 distance = normalised **Hamming-style** distance: the fraction of flags
whose values **differ by more than 0.5** (`mkb_similarity.py:420`; also stated
at `design_and_implementation.tex:240`). Rationale: script presence, tonality,
and family composition are discrete properties with no continuous gradient.

## 4. The math [thesis-verified 2026-07-12; matches code]

Fingerprint structure: for each stratum's PCs, five statistics across the
dataset's languages — mean, std, min, max, het (ddof=1 heterogeneity) →
63 PCs × 5 = **315 continuous dims + 17 categorical = 332 dims** (confirmed by
loading `mkb.pkl`).

**Composite distance** (`design_and_implementation.tex:326`, Eq.
`eq:composite_distance`; implemented in `SimilarityEngine._weighted_distance`):

```
D(q,h) = [ Σ_{s∈Sc} w_s · ||q_s − h_s||₂  +  w_cat · d_Hamming(q_cat, h_cat) ]
         / [ Σ_{s∈Sc∪{cat}} w_s ]
```

Per-stratum **Euclidean** distance on each stratum's 5-stat PC slice, plus the
weighted S6 Hamming term, normalised by the weight sum. All six weights
default to 1.0 (`_DEFAULT_STRATUM_WEIGHTS`); `learn_weights()` can derive
data-driven weights via Pearson correlation over leave-one-out dataset pairs —
NOTE: this is the one legitimate "leave-one-out" in the project (a
stratum-weight analysis, `design_and_implementation.tex:331`), NOT the
validation protocol, which is held-out per-corpus row splits.

**Similarity %** (display only): `sim%(h_i) = 100 × (1 − D(q,h_i)/max_j D(q,h_j))`.

**IDW vote** (Eq. `eq:idw_vote`, `design_and_implementation.tex:363`;
`_idw_vote`):

```
IDW(m) = Σ_{i=1..k} [1/(D(q,h_i)+ε)] · perf(m,h_i) · cov(m,q)
         / Σ_{i=1..k} [1/(D(q,h_i)+ε)]
```

ε = 1e-9. `cov(m,q)` is the language-coverage factor: 1.0 if model m's
known languages cover the user's ISO set, else `1 − gap/n_user_langs` — the
**soft penalty is the default and is what Eq. eq:idw_vote and the Ch5
walkthrough describe** (a gapped model can still win the vote; the guard then
warns). [artifact-verified 2026-07-16] An earlier version of this file (and
the `_idw_vote` docstring) claimed unconditional hard-filtering — that was
never implemented and is not in the thesis math. Since 2026-07-16 an
**opt-in** `strict_coverage=True` parameter (on `query`, `trace_query`, and
the `Recommender` facade methods) provides hard-filtering for operational
deployments: models with an *effective* gap (gap minus languages no candidate
covers at all) get factor 0 whenever a fully-covering candidate exists in the
top-k. Default remains False = thesis behaviour.

Model "known languages" resolution (2026-07-16 fix,
`recommender\model_language_coverage.py`): explicit `_training_languages` in
the performance record (never populated in the deployed MKB) → published
zero-shot inventories (lid.176: 176 langs, CLD3: 103 base codes, XLM-V
language-id: 102 FLEURS langs; `nb` credited via the `no` macrolanguage,
`iw`→`he`, `fil`/`tl` aliased) → training-corpus iso_codes inferred from the
variant-name suffix (trained configs only). Before this fix, zero-shot models
were wrongly credited with only the benchmark corpus's languages, so
wide-coverage queries (e.g. 64 company languages) falsely reported lid.176 as
gapped. The facade methods also accept a `user_iso_codes` override so a
deployment can declare languages beyond what the profiler detects.

Census-detected coverage (2026-07-16, opt-in `use_detected_coverage=True` on
the `Recommender` facade): `_profile_user_mode` attaches
`df.attrs["detected_languages"]` and `["detected_language_counts"]`. The
coverage basis comes from the lid.176 census, split two ways — **coverage**
(which languages are present) counts only HIGH-confidence detections
(prob ≥ 0.50, as a fraction of the full census, ≥1% support), which drops
lid.176 low-confidence mislabels (e.g. German→`als`/Alemannic); **per-language
profiling sampling stays at conf 0.0** so the fingerprint reflects data as-is.
Default (`use_detected_coverage=False`) uses the profiled columns — so the WiLI
walkthrough and validation are unchanged. Prose: Ch4
`design_and_implementation.tex` coverage-guard subsection
(`subsec:coverage_guard_confidence`). Caveat: the profiler *uses* lid.176, so
lid.176 covers whatever it detects — a high-confidence idiosyncratic code can
collapse a multi-model choice to lid.176 sole survivor; inspect
`detected_language_counts` when it matters.

Denominator is the **global** Σ inv-distance (per-model
normalisation would cancel proximity for single-neighbour models).
Lower-is-better metrics (`inference_time_*`) are inverted before voting.

**Consensus confidence** (Eq. `eq:consensus_index`,
`methodology_chapter.tex:252`; also `eq:confidence` in Ch4):

```
C = (1/k) Σ_{i=1..k} 1[m_i = m*]
```

where m_i is neighbour i's own best model. The thesis's own ceiling for any
claim about C — quote it, never exceed it (`methodology_chapter.tex:256`):

> "This metric is a *consensus measure*, not a calibrated probability of
> correctness: it quantifies the consistency of the retrieved neighbourhood
> rather than the probability that m* is optimal for the query."

and Ch5 (`demonstration_and_evaluation.tex:242`) reads the empirical split as
"**promising rather than established**". NEVER write "calibrated confidence".

`trace_query()` / `recommend_from_profile_traced()` return a math-trace dict
with every intermediate (per-stratum d, Hamming, composite D, max_D, IDW
numerators/denominator, confidence breakdown) — use it for any manual
verification or defense walkthrough.

## 5. Data design and model roster [artifact-verified 2026-07-12]

**17 corpora** in the deployed MKB (from `mkb.pkl`):
OpenLID-v2, amazon_reviews_multi, europarl,
exorde-social-media-december-2024-week1, flores_plus,
language-identification, massive, mmarco, multi_eurlex, multilingual_cc_news,
multilingual_toxicity_dataset, stsb_multi_mt, tweet_sentiment_multilingual,
tydiqa, wikipedia, xlsum, xnli. (librispeech_asr was excluded —
`profiles\librispeech_asr.pkl.excluded`; backup `mkb_backup_with_librispeech_2026-07-03.pkl`.)

**24 in-scope languages** (from `typology_lookup.TYPOLOGY` and confirmed as
the union of MKB iso_codes): ca da de el en es fi fr hr it ja ko lt mk nb nl
pl pt ro ru sl sv uk zh — 6 Germanic, 6 Romance, 6 Slavic, plus lt, el, zh,
ja, ko, fi.

**Four-way per-corpus row split** (seed 42, per-row random routing at
ingestion; `design_and_implementation.tex:583-590`; dirs verified on disk
under `c:\Users\User\OneDrive\Masters\LID_experiments\datasets\`):
| Split | Dir | Use |
|---|---|---|
| 50% | `01a_knowledge_train_50` | Train the six candidate configs per corpus |
| 20% | `01b_knowledge_benchmark_20` | Cross-benchmark → MKB performance records; also profiled for MKB fingerprints |
| 15% | `02_evaluation_15` | Held-out "unknown user dataset" queries + evaluation-side cross-benchmark ground truth (Ch5) |
| 15% | `03_validation_15` | Final untouched confirmatory split |

Never describe validation as leave-one-out over the MKB (settled battle CC-1);
it is held-out sample validation on disjoint row splits. The 80/20 inside
01a is only within-pool training mechanics.

**Model roster** — 3 trained families × 2 configs = **6 trained
configurations**, plus **3 zero-shot** off-the-shelf models
(`design_and_implementation.tex:651-689`):
| Family | Configs |
|---|---|
| Multinomial Naive Bayes (TML) | `bow_char_ngram_3_5`, `tfidf_char_ngram_3_5` (char n-grams 3–5) |
| Logistic Regression (TML) | `bow_maxabs_lr_char_ngram_3_5`, `tfidf_lr_char_ngram_3_5` |
| FastText (neural) | `fasttext_word` (word unigrams), `fasttext_subword` (minn=2, maxn=4, word bigrams) |
| Zero-shot | CLD3 (`gcld3`), fastText `lid.176`, XLM-V Base (`juliensimon/xlm-v-base-language-id`) |

Never write "five model families were trained" (settled battle CC-4).
Trained variant names carry their training-corpus suffix
(e.g. `fasttext_subword_europarl`); zero-shot appear per-dataset
(`cld3_europarl`) or bare (`xlm_v_base_language_id`). The deployed MKB holds
**1,785 performance records** across 137 unique variant names; the validation
candidate pool per query was **105** variants (103 common to all 17 datasets
for constant policies).

## 6. Headline results — corrected figures with provenance

Primary artifacts (repo root): `validation_report.json` (timestamp
2026-05-14, priority `f1_weighted`, k=3), `random_baseline_mc_results.json`,
and `analysis\validation_statistics.py` (recomputes baselines/stats from the
report; re-run it rather than trusting prose).

| Figure | Value | Provenance |
|---|---|---|
| Strict top-1 accuracy | **17.6%** (3/17: OpenLID-v2, FLORES+, Wikipedia) | [artifact-verified 2026-07-12] `validation_report.json` |
| Wilson 95% CI on accuracy | [6.2%, 41.0%] | [artifact-verified 2026-07-12] ran `validation_statistics.py` |
| Mean regret Δ_f1 | **0.0078** (median 0.0022, max 0.0489 = Tweet Sentiment) | [artifact-verified 2026-07-12] `validation_report.json` |
| Random-policy mean regret | **0.3830** (MC mean, 10⁵ trials, seed 42; analytic expectation 0.3832) | [artifact-verified 2026-07-12] `random_baseline_mc_results.json` |
| Best constant policy | **0.0127** mean / 0.0627 max (`fasttext_subword` Exorde-trained); 0 of 103 constant policies beat the framework | [artifact-verified 2026-07-12] ran `validation_statistics.py` |
| Constant XLM-V Base (zero-shot) | 0.0175 mean / 0.0633 max | [artifact-verified 2026-07-12] same |
| Chance exact-match | 0.95% (1/105); framework ≈ 18× chance | [artifact-verified 2026-07-12] same |
| Confidence split | **2/2 correct at non-zero confidence (0.67, 0.33) vs 1/15 at zero confidence**; exact hypergeometric one-sided **p = 0.0221** | [artifact-verified 2026-07-12] ran `validation_statistics.py`; matches Ch5 §Confidence (`demonstration_and_evaluation.tex:242`) |
| MRR of ground truth in IDW ranking | 0.203 (top-1 = top-3 = top-5 = 3/17) | [artifact-verified 2026-07-12] same |
| Corpus re-identification | top-1 12/17 (70.6%), top-3 14/17 (82.4%) | [artifact-verified 2026-07-12] same |
| Shortlist quality | top-3 contains a candidate within 0.5pp of optimum in 12/17; mean best-of-shortlist gap 0.0047 | [thesis-verified 2026-07-12] Ch5:250; recomputable from report |
| MKB scale | 17 datasets, 1,785 performance records in `mkb.pkl` | [artifact-verified 2026-07-12] loaded `mkb.pkl` (filesystem `model_benchmarking_knowledge` now holds 1,888 metadata files — a superset incl. excluded corpora) |
| spaCy vs stanza throughput | 5,570 vs 289 tokens/s | [unverified, from review session] `analysis\bench_results.json` exists — check before citing |
| Lingualyzer ground truth | English 351/351 (100%); Dutch 314/351 (89.5%), 37 disagreements in adverb/demonstrative/passive families | [unverified, from review session] `project_context\lingualyzer_ground*_*.xlsx` |

**STALE-FIGURE WARNING.** Two figures circulated in earlier session notes and
must not be reintroduced:
1. "Confidence 2/3 vs 1/14, p = 0.063" is **stale** (an earlier report
   version). The current artifact and the compiled Ch5 both say **2/2 vs
   1/15, p = 0.022**.
2. `validation_report.json` itself contains `confidence_calibration_r:
   0.7434, p: 0.0006` — **do not cite this Pearson r**. Ch5 explicitly
   retracts it: with 15 of 17 confidence values = 0.00, "any reported r value
   would be dominated by the two non-zero observations" — the hypergeometric
   exact test is the thesis's chosen statistic.
Old report versions (`validation_report_old_apr28/apr30/may2/may14.json`) and
MKB backups sit in the repo root; only `validation_report.json` and `mkb.pkl`
are current.

## 7. The dataset-similarity hypothesis and its literature [thesis-verified 2026-07-12]

Core assumption (named in `methodology_chapter.tex:200`): the **dataset
similarity hypothesis** — datasets similar in linguistic meta-feature profile
tend to share optimal model performance rankings, so a model best on retrieved
neighbours generalises to a similar query dataset. Cite exactly as the thesis
does (BibTeX keys from `methodology_chapter.tex`):

| Claim supported | Work | Cite key | What it showed (per thesis §3) |
|---|---|---|---|
| Corpus-level stats predict held-out performance | Xia et al. 2020 | `xiaPredictingPerformanceNatural2020` | Across 9 NLP tasks, vocabulary size / TTR / sentence length / word overlap let regressors predict unseen-setting scores; beat expert humans on the MT prediction task |
| Rankings transfer across languages | Srinivasan et al. 2021 | `srinivasanPredictingPerformanceMultilingual2021` | Typological features + vocabulary overlap recover pairwise performance orderings with 92–99% accuracy, incl. languages absent from training |
| Fine-grained features beat collapsed distances | Dolicki & Spanakis 2021 | `dolickiAnalysingImpactLinguistic2021` | Per-feature-type linguistic features outperform aggregated syntactic distance by 2–4× for cross-lingual transfer prediction |
| Decomposed (stratified) drift beats holistic | Chang et al. 2023 | `changCharacterizingMeasuringLinguistic2023` | Splitting dataset drift into vocabulary/structural/semantic components predicts OOD performance better than holistic metrics |
| Stratified > global PCA (mechanism) | Jiang et al. 2018 (SuperPCA) | `jiangSuperPCASuperpixelwisePCA2018` | Per-region PCA gives higher first-to-second eigenvalue ratio and better downstream accuracy than global PCA on hyperspectral data |
| Stratified > global PCA (independent confirmation) | Fu et al. 2022 (Segmented-PCA) | `fuFusionPCASegmentedPCA2022` | PCA within correlated subgroups beats global PCA; unified projection misses local diversity |
| Global PCA misrepresents heterogeneous groups | Shi 2024 | `shiPersonalizedPCADecoupling2024` | Single global PCA privileges high-variance groups in heterogeneous covariance settings |
| Euclidean over cosine in PCA space | Tessari et al. 2025 | `tessariSurpassingCosineSimilarity2025` | Cosine similarity loses geometric interpretability in high-dim orthogonalised spaces; also cited for concentration-of-measure alongside `beyerWhenNearestNeighbor1999`, `aggarwalSurprisingBehaviorDistance2001` (⚠ live `\candidatetodo` at `methodology_chapter.tex:209`: "Double check beyer and aggarwal papers") |
| PCA properties / Euclidean validity | Abdi & Williams 2010 | `abdiPrincipalComponentAnalysis2010` | Factor scores = projections on principal axes; Euclidean distance reflects PCA's MSE objective |
| CBR retrieve + IDW precedent | Aamodt & Plaza 1994; Dudani 1976; Corrales 2020 | `aamodtCaseBasedReasoningFoundational1994`, `dudaniDistanceWeightedKNearestNeighborRule1976`, `corralesCasebasedReasoningSystem2020` | k-NN case retrieval and distance-weighted voting are established instance-based-learning machinery |

Do not invent details beyond these summaries — they are paraphrases of the
thesis's own sentences (methodology_chapter.tex:196–226), which is the ceiling.

Related open item: the stratified-vs-global PCA **ablation is deferred**. This
is **already stated live** as a Ch3 limitation at `methodology_chapter.tex:405`
(so the thesis does not silently drop it); a more specific deferral sentence is
additionally commented out at `methodology_chapter.tex:215`. Optionally reinstate
:215 as elaboration, or run the ablation — but never claim the ablation exists.

## 8. Examiner-safe language rules (hard constraints)

1. Confidence C is a **consensus measure/signal/index** — never "calibrated
   confidence", never a probability. Empirical support is "promising rather
   than established" (2/2 vs 1/15, p = 0.022, fragile at n=2).
2. Validation protocol = **held-out sample validation** on disjoint per-corpus
   row splits — never "leave-one-out validation across the MKB". (LOO exists
   only as the stratum-weight correlation analysis and the `evaluate_loo()`
   diagnostic method — do not present either as the Ch5 protocol.)
3. **2,726 core features / 327 families** — never 3,066 (a stale count may
   linger in old code docstrings).
4. **Three trained families, six configurations, three zero-shot** — never
   "five model families".
5. Headline framing the thesis itself uses: strict accuracy is the *stringent*
   metric (18× chance); **mean regret 0.0078 vs random 0.3830 vs best constant
   0.0127** is the primary validity criterion; worst case 0.0489 is traced to
   a named aggregation failure mode (generalist neighbour outvoting a
   correctly retrieved specialist).
6. The external examiner is believed to be an IR expert: the framework IS a
   retrieval system (k-NN over fingerprints). Be ready for precision@k / MRR
   framing (MRR = 0.203 is already computed), "why not learned ranking /
   embedding retrieval", concentration-of-measure, and TF-IDF-vs-linguistic-
   features challenges — the Tessari/Beyer/Aggarwal + stratified-PCA chain in
   §7 is the prepared answer.

## Provenance and maintenance

Date-stamp: all [artifact-verified] and [thesis-verified] tags refer to
**2026-07-12**. Volatile items: headline numbers change if `mkb.pkl` or
`validation_report.json` are regenerated; stratum counts change if the MKB is
refit; the types-per-lemma/Honoré/dead-pattern cleanups (§2) and the
stratification drafts' `\input` adoption were still pending on this date.

One-line re-verification commands (run from
`C:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit`):

```powershell
# Stratum table (expect: Core features: 2726  families: 327  PCs: 63)
C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\stratum_audit.py

# Headline stats (expect: 17.6%/0.0078; best constant 0.0127; 2/2 vs 1/15 p=0.0221; MRR 0.203; re-id 12/17)
C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\validation_statistics.py

# Random baseline (expect mc_mean_gap.mean ≈ 0.3830, analytic 0.3832, framework 0.0078)
Get-Content random_baseline_mc_results.json

# MKB counts (expect 17 datasets / 1785 records / 332-dim fingerprints)
C:\Users\User\miniconda3\envs\thesis_final\python.exe -c "import sys; sys.path.insert(0,'src'); from lid_toolkit.recommender.mkb_store import MKBStore; m=MKBStore.load('mkb.pkl'); print(len(m.datasets), sum(len(m.get_entry(n).performances) for n in m.datasets), len(m.get_entry(m.datasets[0]).fingerprint))"
```

If this file and a freshly loaded artifact disagree, the artifact wins —
update this file.
