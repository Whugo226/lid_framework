---
name: thesis-claims-archaeology
description: >-
  The settled-battles register for the LID-framework MEng thesis (Werner Hugo,
  Stellenbosch, submission 2026-09-01). Load this BEFORE editing, reverting, or
  quoting from any thesis chapter, front/back matter, old draft, git history,
  or the toolkit's recommender code — it lists every claim that was found wrong
  and corrected (leave-one-out wording, feature counts, model-family counts,
  calibration language, EQ answers, review-era statistics), so you never
  re-fight a settled battle or resurrect a wrong version from a stale file.
  Also load it when a number or claim you are about to write "looks familiar
  from an old report". Do NOT use it for: landing new edits (use
  thesis-change-control), running a fresh review pass (use
  thesis-review-protocol), sourcing framework facts like stratum counts (use
  lid-framework-reference), or deciding what evidence a new claim needs (use
  evidence-standards).
---

# Thesis Claims Archaeology — the settled battles

Every entry below is a claim that was once wrong in the thesis or code, was
corrected, and MUST NOT come back. Old drafts, stale `.text` files in
`chapters/`, git history, presentation materials, and the early-July review
report all still contain wrong versions. **All statuses below were re-verified
against the live files on 2026-07-12** (not copied from the ledger).

Vocabulary used once, here:
- **Live .tex** = the chapter files actually `\input` by
  `C:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\thesis.tex`
  (introduction_chapter, scoping_review_chapter, methodology_chapter,
  design_and_implementation, demonstration_and_evaluation, conclusion, plus
  frontmatter/ and appendices/). Nothing else is canonical.
- **MKB** = Meta-Knowledge Base (17 dataset fingerprints + performance records,
  `mkb.pkl` in the toolkit repo root).
- **Ledger** = `project_context\SESSION_FACTS_LEDGER.md` in the toolkit repo
  (snapshot 2026-07-12; this skill supersedes its §1).

Paths below:
- `THESIS` = `C:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit`
- `REPO` = `c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit`

Run the grep commands in Git Bash (the Bash tool). Statuses: ✅ SETTLED (fix
landed, verified live), ❌ OPEN (wrong version still present — fix pending),
⚠️ RESIDUAL (settled, but a minor loose end remains).

---

## How to use this register

1. Before touching a chapter or recommender-code file, scan the table below
   for entries whose "where the fix lives" is in that file.
2. Before quoting ANY statistic from an old report, artifact, or the ledger,
   check entry A-10 (figure drift) and re-verify against
   `REPO\validation_report.json` / `analysis/validation_statistics.py`.
3. After any edit session, run the consolidated watch-list grep (bottom).
4. Never "fix" an OPEN item by trusting this file's description alone — open
   the target lines first (line numbers drift; anchors given are stable text).

## Quick-reference table

| # | Wrong (never reintroduce) | Right (current) | Status 2026-07-12 |
|---|---|---|---|
| A-1 | "Leave-one-out validation" as the evaluation protocol | Held-out sample validation (per-corpus row splits, disjoint from all training/benchmarking/MKB data) | ✅ SETTLED (one legitimate "leave-one-out dataset pairs" use survives — see A-1) |
| A-2 | Two-pool dataset-level design; 80/20 as the primary partition | Four-way per-corpus row split 50/20/15/15, seed 42 | ✅ SETTLED |
| A-3 | "Five model families were trained" | 3 trained families (MNB, LR, FastText; 6 configurations) + 3 off-the-shelf zero-shot (CLD3, fastText lid.176, XLM-V Base) | ✅ SETTLED |
| A-4 | 3,066 features | 2,726 core features (327 of Lingualyzer's 351 base measures) | ✅ SETTLED (incl. code docstrings) |
| A-5 | "Calibrated confidence score" | Consensus confidence signal; calibration promising/directional only | ✅ SETTLED / ⚠️ one benign "well-calibrated recommendations" phrase |
| A-6 | Broken refs `fig:corpus_eda`, `tab:corpus_summary`, `chap:experimental_design` | Both labels exist and resolve; `chap:experimental_design` refs only in comments + stale files | ✅ SETTLED |
| A-7 | Types-per-lemma features listed under S2 | All 25 types-per-lemma features are in S1 in the fitted artifact (better construct fit too) | ❌ OPEN (Ch4 bullet + docstring) |
| A-8 | "Honoré's statistic" in S2 docstring; dead `honoré` pattern | No Honoré feature exists in the 2,726 core set | ❌ OPEN (docstring + dead pattern) |
| A-9 | `word entropy` / `letter entropy` patterns in S2 code list | Dead patterns — S4's `entropy` always matches first | ❌ OPEN (code only; prose is correct) |
| A-10 | Review-era stats: "2/3 vs 1/14, p = 0.063"; random baseline "0.3832" quoted as the MC figure | 2/2 vs 1/15, exact one-sided hypergeometric p = 0.0221; MC random baseline 0.3830 (analytic expectation 0.3832 — two estimators) | ✅ SETTLED in .tex / ⚠️ Ch5-vs-Ch6 0.3830/0.3832 inconsistency |
| A-11 (CC-2) | Ch6 answers EQ3 with usability/practitioner utility (an earlier draft's EQ3) | EQ3 = comparison vs random / constant / LLM baselines; answered in Ch6 with 0.0078 vs 0.3832 vs 0.0127 | ✅ SETTLED / ⚠️ LLM-baseline arm still outstanding (flagged in-text) |
| A-12 (CC-8) | Code-switching motivates Ch1 then is silently dropped | Ch1 explicitly scopes it out; Ch3 lists it as out of scope; Ch6 lists it as future work | ✅ SETTLED |
| **A-13** | **Everything in A-10, plus 3/17 · 17.6% · 0.0078 · max 0.0489 · "promising rather than established"** | **The 2026-07-17 coverage fix and 2026-07-21 reporting rework superseded the whole evaluation. See A-13.** | ⚠️ **SUPERSEDES A-10 (added 2026-07-31)** |

---

## A-1 — Leave-one-out → held-out validation

- **Wrong:** "Leave-one-out validation across the 17-dataset MKB."
- **Right:** Held-out sample validation: each corpus is row-split at ingestion;
  the 17 evaluation splits are disjoint from all data used in model training,
  benchmarking, and MKB construction. The protocol establishes *within-corpus
  generalisation* (Ch6 Limitations says so explicitly — do not overclaim).
- **Why wrong:** LOO would mean removing whole datasets from the MKB and
  querying with them; that is not what was run. The distinction is exactly the
  kind an examiner probes.
- **Fix lives:** abstract (`THESIS\frontmatter\abstract.tex`, "17 held-out
  evaluation datasets — genuine partitions... disjoint from all data"),
  Ch5 §Chapter Summary ("held-out sample protocol"), Ch6 Limitations
  §Within-corpus generalisation.
- **The ONE legitimate surviving use:** `chapters\design_and_implementation.tex`
  §Weighted Composite Distance (near line 331): "Pearson correlations between
  per-stratum distances and performance gaps across all **leave-one-out dataset
  pairs**" — this describes the OPTIONAL stratum-weight-learning capability,
  NOT the validation protocol. **Verified 2026-07-12: the code exists and
  matches the prose** — `REPO\src\lid_toolkit\recommender\mkb_similarity.py`,
  `SimilarityEngine.learn_weights()` (def at line 284): iterates all ordered
  MKB entry pairs (i ≠ j), collects per-stratum distances and |best-F1| gaps,
  derives normalised Pearson-correlation weights. Also surfaced as
  `Recommender.learn_weights()` (`recommender.py:167`). It is a *capability*,
  not an executed analysis — the prose says "can be derived", and Ch6
  Limitations item "Equal stratum weighting default" correctly notes the
  current MKB is too small for reliable estimates. Do not delete this mention
  and do not promote it to a result.
- **Contamination vectors:** `chapters\verification_and_validation.text` (3
  hits), `chapters\toolkit_architecture.text` (1 hit),
  `REPO\latex\presentation.tex` + `REPO\latex\generate_presentation*.py`
  ("Leave-One-Out Validation" slides — regenerate before any reuse).
- **Re-check:**
  ```bash
  grep -rniE "leave.one.out" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/frontmatter" --include="*.tex"
  # Expect exactly ONE hit: design_and_implementation.tex "leave-one-out dataset pairs"
  ```

## A-2 — Two-pool design → 50/20/15/15 four-way split

- **Wrong:** two-pool dataset-level design with 80/20 as the primary partition.
- **Right:** every corpus is row-split at ingestion into
  `01a_knowledge_train_50` / `01b_knowledge_benchmark_20` / `02_evaluation_15`
  / `03_validation_15` (seed 42). MKB performance records come from
  cross-benchmarking on the 01b splits. The stratified 80/20 exists only
  *inside* the 50% training split as model-training mechanics.
- **Why wrong:** the old framing implied evaluation data could leak from the
  same pool used to build the MKB; the four-way split is the leakage defence.
- **Fix lives:** Ch4 §Data Partitioning — `\label{sec:data_partitioning}` at
  `design_and_implementation.tex:575`, `fig:data_partitioning` at `:620`;
  80/20 correctly framed at `:611` ("internal stratified 80/20") and `:627`
  ("Within the 50% knowledge-training split..."). Verified live 2026-07-12.
- **Re-check:**
  ```bash
  grep -niE "two.pool|80/20" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters/"*.tex
  # Expect: NO "two-pool"; 80/20 only inside §Data Partitioning as within-pool mechanics
  ```

## A-3 — Five model families → 3 trained + 3 zero-shot

- **Wrong:** "Five model families were trained."
- **Right:** three trained families — Multinomial Naive Bayes, Logistic
  Regression, FastText — in six configurations, benchmarked alongside three
  off-the-shelf zero-shot models: CLD3, fastText `lid.176`, XLM-V Base.
- **Why wrong:** conflated trained candidates with zero-shot comparators;
  contradicted the training scripts (only three `train_*_core.py` families).
- **Fix lives:** `introduction_chapter.tex` DSR step 3 (near :220) and
  Chapter-4 outline (near :248): "three model families (six configurations)...
  alongside three off-the-shelf zero-shot models". Zero wrong-version matches
  in any .tex (verified 2026-07-12).
- **Re-check:**
  ```bash
  grep -rniE "five model famil|5 model famil" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit" --include="*.tex"
  # Expect: no matches
  ```

## A-4 — 3,066 → 2,726 features

- **Wrong:** 3,066 features.
- **Right:** 2,726 core features from 327 of Lingualyzer's 351 base measures.
  (Pooled pre-filter union is 2,926; the validity filter drops exactly the 200
  conditional paragraph-level variants. Full breakdown: lid-framework-reference.)
- **Why wrong:** 3,066 was never traced to an artifact; loading the fitted
  `mkb.pkl` stratifier gives 2,726. This incident created the "no numeric
  claim without a saved artifact" rule (see evidence-standards).
- **Fix lives:** all .tex (zero `3,?066` matches) AND `src/` — the ledger's
  feared stale docstring is **already fixed**: `feature_stratifier.py`
  module docstring now opens with "a fixed 2,726-feature core schema per
  language; up to ~2,926 in the pooled union". Verified 2026-07-12.
- **Contamination vector:** `chapters\toolkit_architecture.text` (1 hit of
  3,066).
- **Re-check:**
  ```bash
  grep -rniE "3,?066" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit" --include="*.tex" "c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit/src"
  # Expect: no matches
  ```

## A-5 — "Calibrated confidence" → consensus confidence signal

- **Wrong:** "calibrated confidence score."
- **Right:** the confidence value is a *consensus* index C = fraction of the k
  neighbours whose own best model matches the recommendation (Eq.
  `eq:consensus_index`). Calibration evidence is "promising rather than
  established" (current figures in A-10). **Examiner-safety rule: never write
  "calibrated confidence" in any generated text, ever.** The thesis's own
  disclaimers are the ceiling.
- **Why wrong:** "calibrated" claims P(correct | score) alignment, which two
  non-zero-confidence observations cannot establish.
- **Fix lives:** `methodology_chapter.tex:256` ("a *consensus measure*, not a
  calibrated probability of correctness"); `demonstration_and_evaluation.tex`
  §Confidence Calibration (near :242, "promising rather than established") and
  §Discussion (near :327, "promising support ... rather than established
  calibration"). Section titles "Confidence Calibration" name the *analysis
  topic* and are fine. All verified live 2026-07-12.
- **⚠️ Residual (benign, unfixed):** `design_and_implementation.tex:566`
  "well-calibrated recommendations" — about length-regime coverage of the MKB,
  not the confidence signal. Harmless but a cheap word-swap ("reliable") if
  ever editing that paragraph.
- **⚠️ Code residual (❌ OPEN, examiner-visible if the dashboard is demoed):** a
  stale docstring in `REPO\src\lid_toolkit\recommender\mkb_similarity.py`
  (~line 24) still says "calibrated signal". Prose is correct; the code lags.
  Never quote it; fix it with the A-7/A-8/A-9 docstring cleanups (same file
  family). Re-check: `grep -niE "calibrat" src/lid_toolkit/recommender/mkb_similarity.py`.
- **Re-check:**
  ```bash
  grep -rniE "calibrated confidence" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit" --include="*.tex"
  # Expect: no matches. (Bare "calibrat*" hits are disclaimers/titles — inspect, don't delete.)
  ```

## A-6 — Broken refs: fig:corpus_eda / tab:corpus_summary / chap:experimental_design

- **Wrong:** the review found `\ref`s to labels that did not exist.
- **Right / current:** Corpus EDA landed in Ch4 §Corpus Characteristics.
  Verified 2026-07-12: `tab:corpus_summary` defined
  `design_and_implementation.tex:532`, `fig:corpus_eda` at `:563`, both
  referenced in the same subsection (near :527) and both resolve in
  `THESIS\thesis.aux` (Table 4.6 p. 86; Figure 4.2 p. 87).
  `chap:experimental_design` is defined ONLY in the stale
  `experimental_design_and_methodology1.text:2`; live refs to it survive only
  in a commented line (`methodology_chapter.tex` ~:79) and stale `.text`
  files — no live broken refs.
- **Why it matters:** a git-history revert of Ch4 or an accidental `\input` of
  a `.text` file re-breaks this instantly.
- **Re-check:**
  ```bash
  grep -n "corpus_eda\|corpus_summary" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/thesis.aux"
  grep -rn "chap:experimental_design" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters" --include="*.tex" | grep -v "^\s*%"
  # First: both \newlabel lines present. Second: only commented occurrences.
  ```

## A-7 — Types-per-lemma listed under S2 (❌ OPEN)

- **Wrong (still live):** Ch4 "Five Continuous Strata" S2 bullet
  (`design_and_implementation.tex:226`) ends "...and word-types-per-lemma
  measures"; `feature_stratifier.py` module docstring (lines ~19–21) lists
  "word-types-per-lemma measures" under S2.
- **Right:** all 25 types-per-lemma features land in **S1** in the fitted
  artifact — the code's S1 pattern list contains `"word types per lemma"` and
  `"types per lemma"` (`feature_stratifier.py:107–108`), and S1 is checked
  before S2. S1 is also the better construct fit: inflected types per lemma ≈
  paradigm size ≈ morphological richness.
- **Why wrong:** docstring and prose were written from the intended design,
  not the fitted artifact; the audit of `mkb.pkl` exposed the mismatch.
- **Fix (pending):** delete the phrase from the Ch4 S2 bullet, add
  "word-types-per-lemma" to the S1 bullet (`design_and_implementation.tex:225`)
  if desired, and correct the docstring. A header comment in
  `THESIS\drafts\stratum_bridging_table.tex` records this dependency — the
  bridging table must land WITH these consistency edits (see
  thesis-change-control). Verified still wrong 2026-07-12.
- **Re-check:**
  ```bash
  grep -n "types.per.lemma" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters/design_and_implementation.tex" "c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit/src/lid_toolkit/recommender/feature_stratifier.py"
  # OPEN while the S2 bullet (:226) and docstring S2 entry still say it; SETTLED when only S1 mentions remain
  ```

## A-8 — Honoré's statistic (❌ OPEN, dead pattern)

- **Wrong (still live):** `feature_stratifier.py` docstring lists "Honoré's
  statistic" under S2 (line ~20) and the S2 pattern list contains `"honoré"`
  (line ~117).
- **Right:** no Honoré feature exists anywhere in the 2,726 core set; the
  pattern never fires. Remove both (docstring phrase + dead pattern).
- **Why it matters:** an examiner reading code against prose sees the code
  "claiming" a feature the thesis never mentions. Note removal is
  behaviour-neutral (pattern matches nothing), but re-run
  `analysis/stratum_audit.py` after touching the pattern lists to prove
  2,726/327/63 unchanged.
- **Contamination vector:** `toolkit_architecture.text:161` carries the same
  wrong S2 bullet (Honoré + types-per-lemma).
- **Re-check:**
  ```bash
  grep -niE "honor" "c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit/src/lid_toolkit/recommender/feature_stratifier.py"
  # OPEN while any hit remains; SETTLED at zero hits
  ```

## A-9 — Dead `word entropy` / `letter entropy` S2 patterns (❌ OPEN)

- **Wrong (still live):** `feature_stratifier.py` S2 pattern list contains
  `"word entropy"` and `"letter entropy"` (lines ~120–121).
- **Right:** they are dead — S4's `"entropy"` pattern (line ~66) is checked
  first (priority order S4, S5, S1, S2, S3; first-match-wins), so every
  entropy feature is S4. The Ch4 prose is already correct and even explains
  this routing (`design_and_implementation.tex:220, :223`) — only the code
  cleanup is pending, so code and prose don't look contradictory side-by-side.
- **Fix (pending):** delete the two lines; behaviour-neutral; re-run
  `analysis/stratum_audit.py` to confirm totals unchanged.
- **Re-check:**
  ```bash
  grep -n "word entropy\|letter entropy" "c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit/src/lid_toolkit/recommender/feature_stratifier.py"
  # OPEN while hits remain in the S2 list; SETTLED at zero
  ```

## A-10 — Review-era figure drift: confidence stats & random baseline

**The rule this entry exists to enforce: any number sourced from the
early-July review report, the ledger, or memory of either MUST be re-verified
against `REPO\validation_report.json` (via `analysis/validation_statistics.py`)
before reuse.** The evaluation was re-run after the review; the review-era
numbers are themselves now archaeology.

- **Wrong (review-era, stale):** confidence split "2/3 vs 1/14 correct,
  p = 0.063"; random-baseline mean regret quoted as a single figure 0.3832.
- **Right (verified by running `analysis/validation_statistics.py` AND
  `analysis/random_baseline_mc.py` on 2026-07-12):**
  - Confidence: **2/2** non-zero-confidence correct vs **1/15** zero-confidence,
    exact one-sided hypergeometric **p = 0.0221** (thesis rounds to 0.022);
    Wilson 95% CI for 2/2 = [34.2%, 100%]. Framing ceiling: "nominally
    significant but resting on only two non-zero-confidence evaluations;
    promising rather than established."
  - Random baseline — **two legitimate estimators coexist**:
    **0.3832** = exact analytic expectation of the per-draw gap
    (`validation_statistics.py` section [1]); **0.3830** = Monte-Carlo
    per-trial mean (`random_baseline_mc.py`, 10^5 trials, seed 42, which also
    prints the analytic 0.3832 as its cross-check). Know which one you are
    quoting.
  - Other stable headline figures (same run): accuracy 3/17 = 17.6% (Wilson CI
    [6.2%, 41.0%]), mean gap 0.0078, best constant policy 0.0127 (max 0.0627),
    XLM-V constant 0.0175, corpus re-identification 12/17 top-1.
- **Fix lives:** old figures fully purged from live .tex (verified — the only
  `0.063`/`1/14`/`2/3` hits estate-wide are in unrelated cached papers).
  Current figures live at `demonstration_and_evaluation.tex` §Confidence
  Calibration (:242), §Discussion (:327), §Chapter Summary (:337), baseline
  table (:127–130), and `conclusion.tex` EQ2 answer (:53).
- **⚠️ Residual cross-chapter inconsistency (open, minor):** Ch5's baseline
  table (:127) quotes **0.3830** labelled "Monte-Carlo, 10^5 trials"; Ch6's
  EQ3 answer (:55) quotes **0.3832** unlabelled. Both numbers are real, but an
  examiner may flag the mismatch — either harmonise on the MC figure or label
  Ch6's as the analytic expectation.
- **Re-check:**
  ```bash
  grep -rniE "0\.063|1/14|p = 0\.06" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters" --include="*.tex"   # expect none
  cd "c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit" && C:/Users/User/miniconda3/envs/thesis_final/python.exe analysis/validation_statistics.py
  # expect: 2/2 vs 1/15, p = 0.0221, mean gap 0.007803, random 0.3832 (analytic)
  ```

## A-13 — The whole evaluation was re-run; A-10's "current" figures are now archaeology too

**Added 2026-07-31. Read this before quoting ANY validation number.**

A-10 exists to enforce "re-verify before reuse." It then named a set of figures
as current. Those figures are now themselves stale — which is the entry's own
lesson applied to itself.

Two changes did it:
1. **Coverage-guard correction (2026-07-17)**, artifact
   `analysis\coverage_fix_validation_impact_2026-07-17.json` — corrected the
   zero-shot language inventories, which changed which recommendations are
   counted correct.
2. **Reporting-measures rework (2026-07-21)**, artifact
   `analysis\reporting_measures_2026-07-21.json` — Ch5 re-led on *range capture*
   rather than strict exact-match, and added two further evaluation conditions.

| Was "current" per A-10 | Is now (condition A) |
|---|---|
| accuracy 3/17 = 17.6%, Wilson [6.2%, 41.0%] | **2/17 = 11.8%**, demoted to a strictness check |
| mean gap 0.0078 | **0.007287** |
| max gap 0.0489 (Tweet Sentiment) | **0.0259** — the Tweet Sentiment worst case no longer holds |
| — | **mean range capture 99.18%, min 96.89%** ← the new headline |
| confidence 2/2 vs 1/15, p = 0.0221 | **retracted — signal reported as untested**; split is now 13 non-zero / 4 zero |
| best constant 0.0127 | 0.012727 — unchanged ✅ |
| random MC 0.3830 / analytic 0.3832 | unchanged ✅ |
| LLM arm "not yet executed" | **executed** — `gpt-oss-120b`, mean gap 0.0823, p = 0.000107 |

**New facts with no A-10 equivalent:** blind constant pick 0.3902; condition B
(reserved validation splits) 1/17, 0.0079, 99.11%; condition C
(leave-one-corpus-out refit) 0/17, 0.0160, 98.21%; paired sign tests, of which
the load-bearing one is that the framework does **not** significantly beat the
hindsight-chosen best constant policy (p = 0.0645).

**Do not run `analysis\validation_statistics.py` for headline figures.** It reads
the 2026-05-14 `validation_report.json` and faithfully prints the old numbers.

**Re-check:**
```bash
cd "c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit"
cat analysis/reporting_measures_2026-07-21.json   # condition A = headline
```
If a newer `reporting_measures_*.json` exists, it wins over this entry.

## A-11 (CC-2) — Ch6's EQ3 answer answered the wrong question

- **Wrong:** Ch6 answered EQ3 with usability/practitioner-utility content —
  the EQ3 of an *earlier draft* (visible in the commented-out question block
  in `introduction_chapter.tex:113–117`; the old EQs survive there as
  comments — a contamination vector if ever uncommented).
- **Right / current (verified 2026-07-12): SETTLED.**
  - Ch1 EQ3 (`introduction_chapter.tex:109`): "How does the framework compare
    with alternative model selection strategies, such as random model
    selection or LLM-based recommendation?"
  - Ch6 EQ3 answer (`conclusion.tex:55`) now answers exactly that: 0.0078 vs
    random 0.3832 (~49×) vs best constant 0.0127 (~1.6×) vs XLM-V 0.0175,
    citing Ch5 §Baseline Comparison.
  - The `introduction_chapter.tex:222` EQ2/EQ3 parenthetical swap is **fixed**:
    EQ2 ↔ near-optimal-vs-ground-truth, EQ3 ↔ alternative strategies. Correct.
  - Usability now appears only where it belongs: Ch6 Limitations item
    "Baseline breadth and usability evidence" (:114) explicitly says no formal
    practitioner study was done.
- **⚠️ Residual (tracked in-text, not silent):** the LLM-recommendation arm of
  EQ3 is still outstanding — `\candidatetodo` at `conclusion.tex:55` and the
  limitation clause at `:114` both flag it; `analysis/llm_baseline.py` exists
  but per the ledger has not been run (decision = RUN; see
  thesis-completion-campaign). Do not remove those flags without landing the
  result. Also carries the 0.3832/0.3830 nit from A-10.
- **Re-check:**
  ```bash
  grep -n "EQ 3" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters/conclusion.tex" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters/introduction_chapter.tex"
  # Ch6 EQ3 must talk baselines, not usability; Ch1:109 wording must mention random + LLM
  ```

## A-12 (CC-8) — Code-switching: motivation vs scope

- **Wrong (review finding):** Ch1 used code-switching to motivate the thesis,
  then no later chapter addressed or scoped it — a silent drop.
- **Right / current (re-derived 2026-07-12): SETTLED — coherent thread:**
  - Ch1 motivation still cites code-mixing as a difficulty driver (:40, :48),
    but now closes the loop at `introduction_chapter.tex:51`: "Code-switching
    and code-mixing are cited here as evidence of the breadth and difficulty
    of the short-text LID challenge; handling them is a distinct token-level
    sequence-labelling task and lies outside the scope of this thesis
    (Section \ref{sec:scope})..." — and `\label{sec:scope}` exists (:172).
  - Ch3 `methodology_chapter.tex:408`: code-switching, similar-language
    discrimination, and low-resource settings declared out of scope.
  - Ch6 `conclusion.tex:138`: code-switching support listed as future work.
  - Ch2 retains its legitimate literature coverage (themes, datasets) — that
    is survey content, not a scope claim.
- **Why it matters:** the classic examiner trap "you motivated with X and
  never handled X" is now answered in the text itself; do not delete the :51
  scope sentence when editing Ch1's problem statement.
- **Re-check:**
  ```bash
  grep -niE "code.switch|code.mix" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters/introduction_chapter.tex" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters/methodology_chapter.tex" "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters/conclusion.tex"
  # Expect: Ch1 scope-out sentence present; Ch3 out-of-scope item; Ch6 future-work item
  ```

---

## Watch-list — run after any edit or revert session

Consolidated re-check (Git Bash, one command; ~5 s):

```bash
grep -rniE "leave.one.out|3,?066|five model famil|calibrated confidence|two.pool|0\.063\b|1/14" \
  "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters" \
  "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/frontmatter" \
  "C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/appendices" \
  --include="*.tex" \
  "c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit/src"
```

**Expected clean result (2026-07-12): exactly ONE hit** — the legitimate
"leave-one-out dataset pairs" in `design_and_implementation.tex` (A-1). Any
other hit is a resurrection; treat it as a defect and trace how it got back in.
(Plus, until A-7/A-8/A-9 land: the `feature_stratifier.py` docstring/pattern
hits for honoré/entropy if you extend the pattern.)

### Contamination vectors — where wrong versions still live

1. **Stale `.text` files in `THESIS\chapters\`** (9 files, NOT compiled —
   `thesis.tex` inputs only `.tex`). Never edit, never `\input`, never copy
   from without running the watch-list grep on the pasted text:
   - `experimental_design_and_methodology.text`
   - `experimental_design_and_methodology1.text` (defines the dead
     `chap:experimental_design` label)
   - `introduction_chapter.text` (pre-scope-fix Ch1)
   - `methodology.text`
   - `natural_lang_proc.text`
   - `scoping_review_chapter.text`, `scoping_review_old.text`
   - `toolkit_architecture.text` (carries: 1× leave-one-out, 1× 3,066, the
     wrong Honoré/types-per-lemma S2 bullet)
   - `verification_and_validation.text` (carries: 3× leave-one-out)
2. **Git history**: any `git checkout <old>` / revert of a chapter or of
   `feature_stratifier.py` can resurrect every settled entry at once. After
   ANY revert, run the watch-list grep before doing anything else.
3. **Old MKB pickles** (`REPO\mkb_old_*.pkl`, `mkb_backup_*.pkl`) and old
   validation reports (`REPO\validation_report_old_*.json/.md`): numbers from
   these are historical; only `mkb.pkl` and `validation_report.json` are live.
4. **Presentation/briefing materials** (`REPO\latex\presentation.tex`,
   `generate_presentation*.py`): still say "Leave-One-Out Validation";
   regenerate before reuse in the defense (see examiner-defense-pack).
5. **The review report and the ledger themselves** (see A-10): review-era
   statistics are stale; ledger §1 statuses are as of 2026-07-12 and drift.
6. **Commented-out old EQs** in `introduction_chapter.tex:113–117` — never
   uncomment.

### The full panel report

The complete examination-panel review exists only as a Claude Artifact:
**"Thesis Review Panel — Full Review Report"** (early July 2026; chair's
verdict "Major revisions — documentation-level, not experimental"; 3 Critical
/ 11 Major / 14 Minor / 5 Nitpick). Findings beyond CC-8/A-12 are NOT in the
ledger or this skill — retrieve the artifact via `Artifact action:"list"` +
WebFetch if a finding's full wording is needed. **Any next review pass must be
run in re-review mode via thesis-review-protocol** — do not re-open the
settled items above, and re-verify any statistic the report quotes (A-10).

## When NOT to use this skill

- Landing an edit or new material into the thesis → thesis-change-control
  (drafts/ staging, regeneration rules, read-only-review convention).
- Running or re-running a review pass → thesis-review-protocol.
- Looking up correct framework facts (stratum tables, S6 flags, PCA config,
  headline results) → lid-framework-reference.
- Deciding what evidence a NEW claim needs → evidence-standards.
- Verifying artifacts (mkb.pkl loading, script reruns) → artifact-verification-playbook.
- Anything about the dashboard, environment setup, or defense prep → the
  respective sibling skills (dashboard-demo-runbook, thesis-estate-and-env,
  examiner-defense-pack).

## Provenance and maintenance

All statuses re-verified **2026-07-12** by direct greps of the live .tex and
`src/`, plus fresh runs of `analysis/validation_statistics.py` and
`analysis/random_baseline_mc.py` (thesis_final env, repo root). Volatile
facts and their one-line re-checks:

- Settled-claims still dead → watch-list grep above (expect 1 legitimate hit).
- A-7/A-8/A-9 open/closed → the three per-entry greps (feature_stratifier.py
  + design_and_implementation.tex).
- Current validation figures → `C:/Users/User/miniconda3/envs/thesis_final/python.exe analysis/validation_statistics.py`
  from `REPO` (expect: 2/2 vs 1/15, p = 0.0221, mean gap 0.007803, analytic
  random 0.3832; MC script prints 0.3830).
- Labels resolve → grep `thesis.aux` for `corpus_eda|corpus_summary` after
  each full compile (3 pdflatex passes; see thesis-estate-and-env).
- Line numbers cited here (e.g., :226, :331, :566) were accurate 2026-07-12
  and WILL drift — anchor on the quoted text, not the number.
