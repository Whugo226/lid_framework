---
name: artifact-verification-playbook
description: Tested, read-only recipes to trace any numeric claim in the LID-toolkit MEng thesis to a saved artifact and re-derive it by running a command ("measure, don't eyeball"). Load this skill whenever you need to verify a thesis number (2,726 features / 327 families / 63 PCs / 17 datasets / 1,785 benchmark records / 17.6% accuracy / 0.0078 mean regret / p = 0.022 confidence split), inspect mkb.pkl or validation_report.json, count benchmark_metadata.json records, or answer "where does this number come from?". Do NOT load it for locating which .tex file/line states a claim (use thesis-claims-archaeology), for what counts as sufficient evidence for a NEW claim (use evidence-standards), for running the Streamlit dashboard (use dashboard-demo-runbook), or for conceptual explanations of the framework (use lid-framework-reference).
---

# Artifact Verification Playbook

Every recipe here was executed read-only on 2026-07-12 against the live estate;
expected outputs shown are actual outputs. Rule of the house (convention #4 in
the session-facts ledger): **no numeric claim enters prose without a saved
artifact behind it** — and if prose, notes, or memory disagree with the
artifact, **the artifact wins**.

## Ground rules

| Rule | Detail |
|---|---|
| Measure, don't eyeball | Run the command; never quote a number from memory or an old chat/ledger. |
| Read-only | These recipes never mutate the estate. When a script has a file output, redirect it to a temp dir unless regeneration is the goal. |
| Python | `C:\Users\User\miniconda3\envs\thesis_final\python.exe` (miniconda3, NOT anaconda3). |
| Working dir | Always run from the toolkit repo root: `c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit`. `mkb.pkl` only unpickles from there (module paths). |
| Current artifact | `mkb.pkl` (repo root, 2026-07-03). Backups `mkb_old_apr28/may5/may14.pkl`, `mkb_backup_with_librispeech_2026-07-03.pkl` are NOT current. |
| Examiner safety | Never write "calibrated confidence". The confidence value is a consensus signal (fraction of k=3 neighbours agreeing); the thesis's own ceiling is "promising support ... rather than established calibration" (`demonstration_and_evaluation.tex:327`). |

Jargon: **MKB** = Meta-Knowledge Base, the pickled `MKBStore` holding one
fingerprint + benchmark performances per historical dataset. **Stratum** =
one of five linguistically coherent feature groups (S1–S5) that get
independent PCA, plus S6 = categorical typology flags (never PCA'd).
**Regret / Δ_f1** = ground-truth best model's f1_weighted minus the
recommended model's.

---

## Recipe 1 — Summarise mkb.pkl (`scripts/mkb_summary.py`)

API trap: `mkb.datasets` is a **list of names**, not a dict — use
`mkb.get_entry(name)`. `mkb.stratifier` is the fitted `FeatureStratifier`;
`entry.fingerprint` is an `OrderedDict[str, float]` whose `cat__*` keys are
the S6 flags.

```powershell
cd c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit
C:\Users\User\miniconda3\envs\thesis_final\python.exe .claude\skills\artifact-verification-playbook\scripts\mkb_summary.py
```

Expected output (verified 2026-07-12, abridged):

```
Datasets (17):
  exorde-social-media-december-2024-week1        24 langs  105 model variants
  ... (17 rows, every one 105 model variants) ...
stratifier.stratum_summary():
                      n_raw_features  n_pcs  var_explained_pct
S4_info_theoretic                 20      5               97.4
S5_cross_level                   260     11               95.2
S1_morphological                 813     16               96.1
S2_lexical_diversity             433     15               95.6
S3_structural                   1200     16               95.4
total core features: 2726   total_pcs: 63
Fingerprint of 'exorde-...': 332 dims = 315 continuous + 17 cat__
  continuous key pattern: <stratum>_PC<nn>_<stat>, stats: {'mean': 63, 'std': 63, 'min': 63, 'max': 63, 'het': 63}
  S6 categorical flags (17): cat__n_languages, cat__n_tonal, cat__has_tonal,
    cat__n_script_types, cat__has_cjk/_cyrillic/_greek/_hangul/_latin,
    cat__n_agglutinative, cat__frac_agglutinative, cat__n_isolating,
    cat__n_polysyllabic, cat__n_language_families, cat__frac_germanic/_romance/_slavic
Sample performance record: metrics = accuracy, f1_macro, f1_weighted,
  inference_time_ms_per_sample, inference_time_total_s, n_samples,
  precision_macro/weighted, recall_macro/weighted, throughput_samples_per_sec
```

Key structural facts this proves: 17 datasets x 105 variants = **1,785
performance records inside the MKB** (reconciles with Recipe 4); fingerprint =
63 PCs x 5 stats + 17 flags = **332 dims**; stratum internals live at
`stratifier._fits[stratum].feature_names` (post-validity-filter core) and
`stratifier._feature_to_stratum` (pooled pre-filter union, 2,926 incl. the 200
conditional paragraph-level variants that the filter drops).

---

## Recipe 2 — Re-derive the stratum numbers (2,726 / 327 / 63)

`analysis/stratum_audit.py` loads `mkb.pkl` and regenerates the appendix
LaTeX enumeration. Its default `--out` overwrites
`analysis/stratum_audit_tables.tex` (that file is machine-generated by design
— convention #3: regenerate, never hand-edit). **To verify only, redirect
`--out` to a temp file:**

```powershell
cd c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit
C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\stratum_audit.py --out $env:TEMP\stratum_audit_check.tex
```

Expected console output (verified 2026-07-12):

```
Core features: 2726   families: 327   PCs: 63
  S1 Morphological Richness     108 families   813 features  16 PCs
  S2 Lexical Diversity           51 families   433 features  15 PCs
  S3 Structural/Syntactic       151 families  1200 features  16 PCs
  S4 Information-Theoretic        4 families    20 features   5 PCs
  S5 Cross-Level Cohesion        13 families   260 features  11 PCs
```

"Family" = a Lingualyzer base measure with its level–statistic suffix
stripped (e.g. "Word length (Par SD)" → family "Word length"). 327 families
independently reconfirms the thesis's "327 of 351 Lingualyzer base measures".

---

## Recipe 3 — Inspect validation_report.json

`validation_report.json` (repo root, generated 2026-05-14 by
`validate_recommendations.py`) is the artifact behind every Ch5 headline
metric. Actual top-level structure (verified 2026-07-12):

| Key | Type | Value / meaning |
|---|---|---|
| `timestamp` | str | `2026-05-14T11:48:53` |
| `priority_metric` | str | `f1_weighted` |
| `recommendation_accuracy` | float | **0.1765** (the thesis's 17.6%) |
| `n_correct` / `n_total` | int | **3 / 17** |
| `performance_delta` | dict | mean **0.007803**, std 0.012496, min 0.0, max **0.048862**, median 0.002165 |
| `confidence_calibration_r` / `_p` | float | 0.7434 / 0.0006 — Pearson r of confidence vs correctness. **Not what the thesis reports** (see below). |
| `per_dataset` | list(17) | per-query records: `dataset, recommended_model, confidence, idw_scores` (all 105 variants), `is_correct, ground_truth_model, ground_truth_score, recommended_score, performance_delta, all_benchmark_scores, top3_neighbours` |

Derived statistics (baselines, MRR, confidence split, Wilson CIs) do NOT live
in the JSON — they are computed from it by `analysis/validation_statistics.py`:

```powershell
cd c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit
C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\validation_statistics.py
```

Expected output (verified 2026-07-12):

```
n = 17, priority = f1_weighted, reported accuracy = 0.1765, mean gap = 0.007803
[1] chance exact-match = 0.95%   random-policy mean gap = 0.3832
[2] constant policies evaluated: 103; best five:
    mean 0.0127 ... fasttext_subword_exorde-social-media-december-2024-week1
    mean 0.0175 ... xlm_v_base_language_id
    policies beating framework mean gap (0.007803): 0
[3] top-1 3/17, top-3 3/17, top-5 3/17, MRR 0.203
[4] non-zero conf: 2/2 correct;  zero conf: 1/15
    hypergeometric one-sided p = 0.0221
    Wilson 95% CI accuracy 3/17: [6.2%, 41.0%]
[5] corpus re-identification: top-1 12/17, top-3 14/17
```

⚠️ **Stale-figure trap:** older notes carry "2/3 vs 1/14, p = 0.063" for the
confidence split. The live artifact and the compiled thesis both say
**2/2 vs 1/15, exact p = 0.022** (`demonstration_and_evaluation.tex:101-102,
:327, :337`). Do not reintroduce the stale figures. Also do not swap in the
JSON's Pearson p = 0.0006 for the thesis's exact-test p = 0.022 — different
tests; the thesis deliberately reports the conservative one.

Random baseline detail: mean gap 0.3832 is the analytic expectation; the
thesis's Monte-Carlo figure 0.3830 (10^5 policies, seed 42) lives in
`random_baseline_mc_results.json` (repo root, from `analysis/random_baseline_mc.py`).

---

## Recipe 4 — Count the benchmark records (1,785)

```powershell
$root = "c:\Users\User\OneDrive\Masters\LID_experiments\model_benchmarking_knowledge"
$all = Get-ChildItem -Path $root -Recurse -Filter benchmark_metadata.json
"total on disk: $($all.Count)"
"excluding librispeech_asr: $(($all | Where-Object { $_.FullName -notmatch 'librispeech' }).Count)"
```

Expected (verified 2026-07-12): `total on disk: 1888`,
`excluding librispeech_asr: 1785`.

Reconciliation — the 103-record difference is entirely the excluded
`librispeech_asr` dataset (its profile is parked as
`profiles\librispeech_asr.pkl.excluded`, so `build_from_filesystem` never
fingerprints it and its performance rows are orphaned). Cross-checks that all
agree on **1,785**: filesystem count above; MKB contents (17 datasets x 105
variants, Recipe 1); thesis claim at `design_and_implementation.tex:756`
("1{,}785 measured dataset--model records"). Per-family layout:
cld3 17 + fasttext 612 + fasttext_off_the_shelf 17 + logistic_regression 612 +
naive_bayes 612 + xlm_v_base 18 = 1,888 on disk.

---

## Recipe 5 — Worked example: trace "2,726" end-to-end

1. **Claim in prose.** `chapters\design_and_implementation.tex:17` ("extracts
   a 2,726-dimensional linguistic meta-feature vector per detected language")
   and `:220` ("assigns each of the 2,726 raw features to exactly one of five
   strata"); also `conclusion.tex:33` and `:66`. Locate live occurrences with:
   ```powershell
   Select-String -Path "c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\chapters\*.tex" -Pattern "2,?726"
   ```
2. **Artifact.** `mkb.pkl` → fitted `FeatureStratifier` → per-stratum
   `feature_names` lists (post-validity-filter core).
3. **Reproducing command.** Recipe 2 (`stratum_audit.py`) prints
   `Core features: 2726`; Recipe 1 (`mkb_summary.py`) prints
   `total core features: 2726` independently. Both were run 2026-07-12 and
   agree with the prose. Chain closed.

Same pattern for a validation metric, e.g. mean regret **0.0078**:
`demonstration_and_evaluation.tex:95` / `:130` / `:205` →
`validation_report.json["performance_delta"]["mean"] = 0.007803` →
re-derivable via `analysis\validation_statistics.py` (Recipe 3).

---

## Recipe 6 — Pointer recipes (inspected 2026-07-12; describe, don't re-run)

| Artifact / flow | What it is |
|---|---|
| `MKBStore.build_from_filesystem` (`src\lid_toolkit\recommender\mkb_store.py:292`) | Full MKB rebuild: loads every `profiles\*.pkl` (features x languages DataFrame) via `add_raw_profile`, rglobs `benchmark_metadata.json` under a benchmark dir (skipping `mlruns`/`__pycache__`), stores each file's `metrics` dict keyed by dataset (`meta["dataset"]`) and variant (parent dir name), then `finalise()` pools all language columns, fits the stratified PCA (variance_threshold 0.95, max 20 PCs/stratum, StandardScaler per stratum, PCA random_state 42) and computes all fingerprints. `save()` pickles the whole store. **Rebuilding is a hours-scale, estate-mutating operation — never do it as part of verification.** |
| `analysis\bench_results.json` | spaCy-vs-stanza pipeline timing on 5 languages (en, nl, de, es, fi): per-language seconds, tokens, tok/s, component list. The headline "spaCy 5,570 vs stanza 289 tokens/s" is the **aggregate** sum(tokens)/sum(seconds): 8427/1.51 s and 8426/29.20 s (verified arithmetic). Generated by `analysis\benchmark_stanza_vs_spacy.py`. |
| `analysis\walkthrough_results.json` | Ch5 practitioner-walkthrough outputs from `analysis\walkthrough_demo.py`: WiLI-2018 sample (600 texts, outside the MKB), 24 detected languages, profile time 107.8 s, and three captured queries — q1 f1_weighted priority (recommends `fasttext_subword_exorde-...`, confidence 0.3333), q2 latency priority (`fasttext_word_multi_eurlex`), q3 coverage guard with required langs incl. lt/ko/mk. Each query stores recommended_model, confidence, top-3 neighbours with similarity %, top-3 IDW scores, and the full explanation text (per-stratum distance breakdown). |
| `analysis\r13_timing.json` | DeepProfiler end-to-end timing (from `analysis\time_deepprofiler_e2e.py`): init 0.23 s, profile 69.1 s for 500 segments / 5 languages / 2,726 features. |
| `random_baseline_mc_results.json` (repo root) | Monte-Carlo random baseline (seed 42, 10^5 trials, pool 105): mc mean gap 0.3830 [0.2524, 0.5135], analytic 0.38325, best single random policy 0.1314, P(≥3 exact matches) = 0.0005. Backs `demonstration_and_evaluation.tex:117` and Table `tab:baseline_comparison`. |

---

## When NOT to use this skill

- **Finding where a claim is stated** in the thesis, or hunting stale/wrong
  claim variants across drafts → `thesis-claims-archaeology`.
- **Deciding what evidence a new claim needs** (tests, disclaimers, phrasing
  ceilings) → `evidence-standards`.
- **Running or demoing the Streamlit dashboard** → `dashboard-demo-runbook`.
- **Understanding the framework conceptually** (strata semantics, IDW voting,
  coverage guard) → `lid-framework-reference`.
- Anything that would **mutate** the estate (rebuilding the MKB, regenerating
  reports in place, editing chapters) → that is change-control work
  (`thesis-change-control`), not verification.

## Provenance and maintenance

All facts and outputs above verified live on **2026-07-12** against
`mkb.pkl` (2026-07-03), `validation_report.json` (2026-05-14), and the
compiled thesis chapters. One-line re-verification:

- Stratum numbers: `C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\stratum_audit.py --out $env:TEMP\sa.tex` → `2726 / 327 / 63`.
- MKB summary: Recipe 1 command → 17 datasets, 332-dim fingerprints, 105 variants each.
- Validation stats: `...python.exe analysis\validation_statistics.py` → accuracy 3/17, mean gap 0.007803, MRR 0.203, conf split 2/2 vs 1/15 (p = 0.0221), Wilson [6.2%, 41.0%].
- Record count: Recipe 4 one-liner → 1888 / 1785.
- Volatile: if `mkb.pkl`'s mtime changes, or a `validation_report.json` newer
  than 2026-05-14 appears (a confirmatory run on the reserved validation
  splits is a live TODO at `demonstration_and_evaluation.tex:117`), re-run
  every recipe before quoting any number here.
