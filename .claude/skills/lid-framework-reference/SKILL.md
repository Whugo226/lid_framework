---
name: lid-framework-reference
description: Domain knowledge pack for the thesis's LID model-recommendation framework. Load this whenever you must reason about, write about, review, or defend the framework itself — the DeepProfiler → FeatureStratifier → FingerprintBuilder → MKBStore → SimilarityEngine pipeline, the S1–S6 strata and their feature counts, the composite-distance / IDW / consensus-confidence math, the 17-corpus/24-language data design, the model roster, or the headline validation numbers (99.18% mean range capture, 0.0073 mean regret, 2/17 strict top-1, confidence signal untested — figures regenerated 2026-07-31). Do NOT load it for: how to run/verify artifacts (use artifact-verification-playbook), tracing where a claim lives in the thesis text (use thesis-claims-archaeology), running the dashboard demo (use dashboard-demo-runbook), or writing-style/LaTeX questions (use thesis-writing-and-style). Paths, env, and git conventions live in thesis-estate-and-env.
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

> ⚠️ **REGENERATED 2026-07-31 — the whole of this section was rewritten.** The
> evaluation was re-run after the coverage-guard correction (2026-07-17) and the
> reporting-measures rework (2026-07-21). **`validation_report.json` (2026-05-14)
> is no longer the source of record for Ch5** and neither is
> `analysis\validation_statistics.py`, which reads it. Both still exist and both
> still print the OLD numbers (3/17, 0.0078, 2/2-vs-1/15) — running them will
> mislead you.

**Primary artifact is now `analysis\reporting_measures_2026-07-21.json`**
(generator `analysis\reporting_measures.py`), which reports three evaluation
conditions plus every baseline policy. `random_baseline_mc_results.json` is
unchanged and still current.

The headline metric changed too: Ch5 now **leads with range capture** (how much
of the achievable performance range the recommendation captures) and demotes
strict exact-match to a strictness check.

Condition A (evaluation splits, full MKB) is the headline condition:

| Figure | Value | Provenance |
|---|---|---|
| **Mean range capture** (headline) | **99.18%** (worst case 96.89%) | [artifact-verified 2026-07-31] `reporting_measures_2026-07-21.json` |
| **Mean regret Δ_f1** | **0.0073** (median 0.0029, max 0.0259) | [artifact-verified 2026-07-31] same |
| Strict top-1 accuracy | **2/17 = 11.8%** (was 3/17 before the coverage fix) | [artifact-verified 2026-07-31] same |
| Rank of ground truth | mean 6.4, median 5, max 23; top-3 6/17, top-10 14/17 | [artifact-verified 2026-07-31] same |
| Random-policy mean regret | **0.3830** (MC mean, 10⁵ trials, seed 42; analytic 0.3832) | [artifact-verified 2026-07-12] `random_baseline_mc_results.json` — unchanged |
| Blind constant pick (mean of 103 policies) | **0.3902** | [artifact-verified 2026-07-31] `reporting_measures_2026-07-21.json` |
| Best constant policy (ORACLE, hindsight) | **0.0127** mean / 0.0627 max / 98.61% range capture | [artifact-verified 2026-07-31] same |
| Constant XLM-V Base (zero-shot) | 0.0175 mean / 98.02% range capture | [artifact-verified 2026-07-31] same |
| Constant `lid.176` (zero-shot) | 0.0207 mean / 97.76% | [artifact-verified 2026-07-31] same |
| Constant CLD3 (zero-shot) | 0.0305 mean / 96.58% | [artifact-verified 2026-07-31] same |
| **LLM baseline — NOW RUN** | `gpt-oss-120b` via Groq, 3 draws × 17, 51 calls: mean gap **0.0823**, max 0.4182, 90.2% range capture, exact-match 9.8%, self-consistency 0.569 | [artifact-verified 2026-07-31] `reporting_measures_2026-07-21.json` → `llm_baseline`; raw `llm_baseline_gptoss.json` |
| Paired framework-vs-policy (sign tests, condition A) | vs CLD3 17-0, p≈0; vs XLM-V 9-1-7, **p = 0.0029**; vs `lid.176` 8-9, p = 0.0478; vs best constant 6-3-8, **p = 0.0645 (n.s.)**; vs LLM 14-2-1, **p = 0.000107** | [artifact-verified 2026-07-31] same → `paired_framework_vs_policy` |
| Condition B (reserved validation splits) | 1/17 exact, regret 0.0079, range capture 99.11% | [artifact-verified 2026-07-31] same |
| Condition C (leave-one-corpus-out refit) | **0/17 exact, regret 0.0160, range capture 98.21%** — the generalisation bound | [artifact-verified 2026-07-31] same |
| MKB scale | 17 datasets, 1,785 performance records, 105 variants/query | [artifact-verified 2026-07-31] loaded `mkb.pkl` |
| In-domain vs cross-domain landscape | in-domain mean 0.939–0.995 (SD 0.008–0.060); cross-domain 0.551–0.604 | [artifact-verified 2026-07-31] ran `analysis\benchmark_landscape.py` |
| Distance concentration | relative contrast 1.55 mean, CV 0.25 over 272 pairs; per-stratum RC 1.46–3.95 | [artifact-verified 2026-07-31] `analysis\distance_contrast_2026-07-31.json` |
| spaCy vs stanza throughput | 1.5 s / 5,570 tok/s vs 29.2 s / 289 tok/s; 8,427 vs 8,426 tokens | [artifact-verified 2026-07-31] `analysis\bench_results.json` — now confirmed |
| Lingualyzer ground truth | Dutch 314/351 (89.5%), 37 disagreements: adverb 12, demonstrative 6, passive 6, interrogative 6, unknown-word 2, other 5 | [artifact-verified 2026-07-31] `tests\data\lingualyzer_human_comparison.csv`. English 351/351 still [unverified] — no artifact with a correctness column located |
| End-to-end profiling | 69.1 s for 5 languages × 100 segments, 2,726 features | [artifact-verified 2026-07-31] `analysis\r13_timing.json` |

**STALE-FIGURE WARNING.** Figures that must NOT be reintroduced:
1. **The confidence-signal result is RETRACTED.** "2/2 vs 1/15, p = 0.022" was
   itself superseded — it "did not survive the coverage-guard correction"
   (Ch5 §Confidence). Under corrected coverage inventories **13 of 17
   evaluations receive non-zero confidence and 4 receive zero**, and Ch5 now
   states the signal is **untested on this sample**, with two configurations
   underpowered to have shown an effect at any outcome. Do not write "promising
   rather than established" — that is now itself an overclaim. See §8 rule 1.
2. "Confidence 2/3 vs 1/14, p = 0.063" — stale two generations back.
3. Old headline numbers **3/17 / 17.6% / mean gap 0.0078 / max 0.0489 (Tweet
   Sentiment)** are superseded by 2/17 / 0.0073 / max 0.0259. The Tweet
   Sentiment worst case in particular no longer holds.
4. `validation_report.json` contains `confidence_calibration_r:
   0.7434, p: 0.0006` — **do not cite this Pearson r**. Ch5 explicitly
   retracts it: with most confidence values at 0.00, "any reported r value
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
   confidence", never a probability. **As of 2026-07-21 the ceiling dropped
   again: the signal is UNTESTED on this sample.** The earlier favourable
   association did not survive the coverage-guard correction; Ch5 now says no
   scenario provides evidence the signal is informative, and two were
   underpowered to provide it at any outcome. Write "untested on this sample"
   or "requires a materially larger held-out set" — do NOT write "promising
   rather than established", which is now itself an overclaim.
2. Validation protocol = **held-out sample validation** on disjoint per-corpus
   row splits — never "leave-one-out validation across the MKB". (LOO exists
   only as the stratum-weight correlation analysis and the `evaluate_loo()`
   diagnostic method — do not present either as the Ch5 protocol.)
3. **2,726 core features / 327 families** — never 3,066 (a stale count may
   linger in old code docstrings).
4. **Three trained families, six configurations, three zero-shot** — never
   "five model families".
5. Headline framing the thesis now uses: **range capture leads (99.18% mean,
   96.89% worst case)**; mean regret **0.0073** vs random 0.3830 vs blind
   constant pick 0.3902 vs best constant 0.0127 vs LLM 0.0823; strict
   exact-match **2/17** is demoted to a strictness check, not the headline.
   Note the honest limit: the framework's advantage over the *hindsight-chosen*
   best constant policy is **not statistically significant (p = 0.0645)** —
   the significant wins are over CLD3, XLM-V (p = 0.0029) and the LLM
   (p = 0.000107). Never claim it beats the best constant policy significantly.
6. The external examiner is believed to be an IR expert: the framework IS a
   retrieval system (k-NN over fingerprints). Be ready for precision@k / MRR
   framing (MRR = 0.203 is already computed), "why not learned ranking /
   embedding retrieval", concentration-of-measure, and TF-IDF-vs-linguistic-
   features challenges — the Tessari/Beyer/Aggarwal + stratified-PCA chain in
   §7 is the prepared answer.

## Provenance and maintenance

Date-stamps are mixed. **§6 headline results and §8 rules 1 and 5 were
regenerated 2026-07-31** against the post-coverage-fix artifacts. Everything
else (§1–§5, §7 — pipeline map, strata, math, data design, literature) still
carries its **2026-07-12** verification and was not re-checked in that pass;
those facts are structural and unlikely to have moved, but treat the date
difference as real. Volatile items: headline numbers change if the evaluation is
re-run; stratum counts change if the MKB is refit; the types-per-lemma /
Honoré / dead-pattern cleanups (§2) were still pending as of 2026-07-31.

One-line re-verification commands (run from
`C:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit`):

```powershell
# Stratum table (expect: Core features: 2726  families: 327  PCs: 63)
C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\stratum_audit.py

# CURRENT headline stats — read the artifact, do NOT run validation_statistics.py
# (expect condition A: range capture 99.18 / regret 0.007287 / top1 2/17; LLM 0.0823)
Get-Content analysis\reporting_measures_2026-07-21.json

# ⚠️ SUPERSEDED: validation_statistics.py reads validation_report.json (2026-05-14)
# and still prints the pre-coverage-fix numbers (3/17, 0.0078, 2/2 vs 1/15).
# Useful only for the random/chance context figures — never for the headline.

# Random baseline (expect mc_mean_gap.mean ≈ 0.3830, analytic 0.3832) — still current
Get-Content random_baseline_mc_results.json

# MKB counts (expect 17 datasets / 1785 records / 332-dim fingerprints)
C:\Users\User\miniconda3\envs\thesis_final\python.exe -c "import sys; sys.path.insert(0,'src'); from lid_toolkit.recommender.mkb_store import MKBStore; m=MKBStore.load('mkb.pkl'); print(len(m.datasets), sum(len(m.get_entry(n).performances) for n in m.datasets), len(m.get_entry(m.datasets[0]).fingerprint))"
```

If this file and a freshly loaded artifact disagree, the artifact wins —
update this file.
