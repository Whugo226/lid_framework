# Session-Facts Ledger — Fable → Opus distillation raw material

**Written:** 2026-07-12, by the Fable 5 session that ran the stratification audit
and drafted the bridging/appendix tables.
**Purpose:** Persist knowledge learned across working sessions that exists nowhere
else on disk, so the skill-library distillation run (and any future session) can
draw from a file instead of conversational memory. Primary consumers:
`thesis-claims-archaeology`, `thesis-change-control`, `lid-framework-reference`,
`artifact-verification-playbook`, `examiner-defense-pack`.
**Trust model:** Facts marked ✅ were verified against artifacts on 2026-07-12 in
this session. Facts marked 📋 come from the examination-panel review session
(early July 2026), verified there but not re-verified today. Facts marked ❓ need
checking. Re-verify anything volatile before embedding in a skill.

---

## 1. Settled battles — corrected claims (do NOT reintroduce the wrong version)

Old drafts and stale files still contain the wrong versions. Any session touching
front/back matter or reverting from git history risks resurrecting them.

| # | Wrong (old) | Right (current) | Status 2026-07-12 |
|---|---|---|---|
| CC-1 | "Leave-one-out validation across the 17-dataset MKB" | Held-out sample validation: per-corpus row-splits, evaluation splits disjoint from all training/benchmarking/MKB data | ✅ FIXED — zero live matches in compiled .tex (abstract, intro, conclusion clean). One legitimate remaining use: `design_and_implementation.tex:331` "leave-one-out dataset pairs" describes a stratum-weight Pearson-correlation analysis, NOT the validation protocol. ❓ Verify that analysis exists in code. |
| CC-3 | Two-pool dataset-level design; 80/20 as primary partition | Four-way per-corpus row split 50/20/15/15 (dirs `01a_knowledge_train_50` / `01b_knowledge_benchmark_20` / `02_evaluation_15` / `03_validation_15`), seed 42; MKB perf records come from cross-benchmark on 01b splits; 80/20 is within-pool training mechanics | ✅ FIXED — Ch4 §Data Partitioning (`design_and_implementation.tex:574+`) now describes the four-way split with figure `fig:data_partitioning`. |
| CC-4 | "Five model families were trained" | Three trained families (MNB, Logistic Regression, FastText; six configurations) + three off-the-shelf zero-shot (CLD3, fastText lid.176, XLM-V Base) | ✅ FIXED — no "five model families" matches in .tex. |
| CC-5 | 3,066 features | 2,726 core features (327 of Lingualyzer's 351 base measures) | ✅ FIXED in .tex (no matches). ❓ A stale "3,066" may survive in a code docstring — grep `3,?066` in `src/`. |
| CC-6 | "Calibrated confidence score" | Consensus confidence signal; calibration evidence is directional only (2/3 vs 1/14 correct, exact one-sided p = 0.063, "suggestive rather than established") | ✅ FIXED — all remaining "calibrat*" uses are disclaimers or diagnostic descriptions (`methodology_chapter.tex:256` "not a calibrated probability"; `demonstration_and_evaluation.tex:327` "rather than established calibration"). Minor loose wording: `design_and_implementation.tex:566` "well-calibrated recommendations" (about length regimes, not the signal). |
| CC-7 | Broken refs: `fig:corpus_eda`, `tab:corpus_summary`, `chap:experimental_design` | Corpus EDA now exists | ✅ MOSTLY FIXED — `tab:corpus_summary` defined at `design_and_implementation.tex:532`, `fig:corpus_eda` at `:563` and resolves in thesis.aux. `chap:experimental_design` refs survive only in a commented line (`methodology_chapter.tex:79`) and stale `.text` files. |
| — | Types-per-lemma in S2 (Ch4 S2 bullet + `feature_stratifier.py` docstring) | All 25 types-per-lemma features are in **S1** in the fitted artifact; S1 is also the better construct fit (inflected types per lemma ≈ paradigm size ≈ morphological richness) | ❌ OPEN — fix Ch4 "Five Continuous Strata" S2 bullet (~`design_and_implementation.tex:226`) and the module docstring. Noted in `drafts/stratum_bridging_table.tex` header comment. |
| — | Docstring: "Honoré's statistic" in S2 | No Honoré feature exists in the 2,726 core set; the `honoré` pattern never fires | ❌ OPEN — remove from `feature_stratifier.py` docstring. |
| — | S2 pattern list contains `word entropy`, `letter entropy` | Dead patterns — S4's `entropy` pattern always matches first (priority order) | ❌ OPEN — delete the two dead patterns (`feature_stratifier.py:120-121`) so code and prose don't look contradictory to an examiner reading both. |
| CC-2 | Ch6 answers EQ3 with usability/practitioner utility (an earlier draft's EQ3) | Actual EQ3 = comparison vs random / LLM baselines; answer lives in Ch5 §Baseline Comparison (0.0078 vs 0.3832 vs 0.0127) | ❓ UNVERIFIED TODAY — was Critical in the review; conclusion has since been edited (other fixes landed). Re-check Ch6 §Answers to Research Questions and `introduction_chapter.tex:222` EQ2/EQ3 parenthetical swap. |
| CC-8 | Code-switching motivates the thesis in Ch1, then is silently dropped | (finding truncated in available transcript) | ❓ Status and full details unknown — re-derive from Ch1 motivation vs. scope sections, or from the full panel report. |

**Review-panel meta:** Chair's verdict was "Major revisions — documentation-level,
not experimental"; counts 3 Critical / 11 Major / 14 Minor / 5 Nitpick. Findings
beyond CC-8 are NOT in this ledger (the transcript was truncated). The full report
was published as a Claude Artifact titled "Thesis Review Panel — Full Review
Report" (favicon-stable HTML, early July 2026) from a previous session — retrieve
via the Artifact list/WebFetch if needed. Several findings have since been fixed
(see table); a re-review pass should use the panel prompt's `re-review` mode
rather than re-opening settled items.

---

## 2. Verified numbers (✅ extracted from `mkb.pkl` fitted stratifier, 2026-07-12)

| Stratum | Families | Core feats | PCs | Var % |
|---|---|---|---|---|
| S1 Morphological Richness | 108 | 813 | 16 | 96.1 |
| S2 Lexical Diversity | 51 | 433 | 15 | 95.6 |
| S3 Structural/Syntactic (catch-all) | 151 | 1,200 | 16 | 95.4 |
| S4 Information-Theoretic | 4 | 20 | 5 | 97.4 |
| S5 Cross-Level Cohesion | 13 | 260 | 11 | 95.2 |
| **Total** | **327** | **2,726** | **63** | — |

- Assigned pooled union = 2,926; the validity filter drops exactly the 200
  conditional paragraph-level variants (S1 −104, S2 −8, S3 −88) → 2,726 core.
- 327 families independently reconfirms the thesis's "327 of 351 Lingualyzer
  base measures" claim.
- Variant grid: (Sent|Par) × (Avg, SD, Min, Max) + Doc = 9; burstiness is
  undefined at sentence level → 5; some measures have 4, 8, or 1 variants.
- Assignment: first-match-wins substring patterns on lowercased feature names,
  priority order **S4, S5, S1, S2, S3**; S3 is the catch-all (empty-string
  pattern). Full audit: all 151 S3 families are genuinely structural/syntactic
  (PoS distributions, PoS ratios, positions, lengths, counts, punctuation).
- S6 categorical block: exactly 17 flags from
  `src/lid_toolkit/recommender/typology_lookup.py::dataset_typology_flags`
  (5 script-presence binaries, has_tonal, 5 counts incl. n_languages/
  n_script_types/n_language_families, frac_germanic/romance/slavic/
  agglutinative). Never PCA'd; Hamming-style distance, differ-by->0.5 rule.
- PCA config: variance_threshold 0.95, max_components 20, StandardScaler per
  stratum, constant columns dropped at fit, PCA random_state=42.
- Zipf split (examiner-visible quirk): Zipf *frequency*-based measures
  (frequent/infrequent word) are S2; Zipf *steepness/goodness-of-fit* are S4.
  Defensible (lexical sophistication vs distribution shape) but must be stated.

✅ Headline results — CORRECTED 2026-07-12 (later session): re-verified by
running `analysis/validation_statistics.py` against the live
`validation_report.json` and reading the current Ch5 baseline table:
top-1 accuracy 3/17 (17.6%), Wilson 95% CI [6.2%, 41.0%]; mean regret
0.0078; random baseline mean regret **0.3830** (Monte-Carlo 10⁵ trials,
seed 42 — NOT 0.3832 as the review session recorded); best constant policy
0.0127 (fasttext_subword, Exorde-trained); constant XLM-V Base zero-shot
0.0175; confidence split **2/2 vs 1/15, exact one-sided hypergeometric
p = 0.0221** (the review-era "2/3 vs 1/14, p = 0.063" is STALE — do not
reuse it); MRR of ground-truth model in IDW ranking 0.203; corpus
re-identification 12/17 and 14/17; constant-policy sweep = 103 policies.
⚠️ The p = 0.0221 correction does NOT relax the claim ceiling: still a
consensus signal, never "calibrated"; nominally significant but fragile at
n = 17. 📋 Still review-era: 1,785 `benchmark_metadata.json` records;
17 datasets in the MKB; spaCy 5,570 vs stanza 289 tokens/s; Lingualyzer
ground truth: English 351/351 (100%), Dutch 314/351 (89.5%, 37 disagreements
concentrated in adverb/demonstrative/passive families — `tab:groundtruth_dutch_disagreements`).

---

## 3. Environment quirks (✅ all confirmed by running, 2026-07-12)

- Python: `C:\Users\User\miniconda3\envs\thesis_final\python.exe` — it is
  **miniconda3, NOT anaconda3** (anaconda3 path does not exist).
- `lid_toolkit` imports and `mkb.pkl` unpickles when run from the repo root.
- `MKBStore` API: `mkb.datasets` is a **list of names** — use
  `mkb.get_entry(name)`, not dict indexing. `mkb.stratifier` holds the fitted
  `FeatureStratifier`; `entry.fingerprint` is a dict whose `cat__*` keys are
  the S6 flags; stratifier internals: `_fits[stratum].feature_names` (core,
  post-filter), `_feature_to_stratum` (pooled union, pre-filter).
- MKB backups in repo root: `mkb_old_apr28/may5/may14.pkl`,
  `mkb_backup_with_librispeech_2026-07-03.pkl`. `mkb.pkl` is current.
- LaTeX: MiKTeX 25.3 `pdflatex` on PATH. `longtable` needs ~3 passes to
  converge column widths (check log for "Table widths have changed").
  `poppler/pdftoppm` NOT installed (no per-page PDF rendering; whole-file
  PDF reading works). `longtable` + `multicol` loaded via `imports.tex`
  (:285, :126).
- Thesis house LaTeX style: boxed `tabular{|l|c|c|}` with `\hline` after every
  row; `[H]` floats; `\begin{small}` for wide tables; `\mysection{X}{X}` /
  `\mysubsection{X}{X}` two-argument macros; appendix chapters use
  `\chapter{Title}{}` + `\makeatletter\@mkboth{}{Appendix}\makeatother`;
  `\candidatetodo{...}` marks open author TODOs (several still live in Ch3).
- Git: repo branch `feature/api-dashboard-intergration` (sic — typo is in the
  real branch name); main branch `main`.
- Supervisor feedback exists on disk: `Thesis Template Legit/thesis_feedback/`
  (e.g., `chapter_3_feedback_updated.md`) — Phase 1 discovery must read it.

---

## 4. Conventions and their incident stories (change-control raw material)

1. **Reviews are read-only.** The panel review protocol (v2.0.0) never edits
   thesis files; findings come with fix + locator instead. Incident: earlier
   sessions mixing review and edit made it impossible to tell what the review
   had measured.
2. **New material lands in `drafts/`, never directly in `chapters/`.**
   Incident: the chapters dir contains ~9 stale `.text` near-duplicates
   (e.g., `scoping_review_chapter.text`, `toolkit_architecture.text`) that
   have burned time via edits to dead files and still hold a label the
   compiled thesis once referenced. Canonical scope = resolve `thesis.tex`
   `\input` list first, always.
3. **Machine-generated tables are regenerated, never hand-edited.** Precedent:
   `analysis/stratum_audit.py` → `analysis/stratum_audit_tables.tex` →
   embedded in `drafts/stratum_audit_appendix.tex` between AUTO-GENERATED
   markers. If the MKB changes, rerun the script.
4. **No numeric claim enters prose without a saved artifact behind it.**
   Incident: the 3,066-vs-2,726 feature count survived multiple drafts
   because it was never traced; the fix required loading the artifact.
5. **Verification before criticism.** Incident: the S3 catch-all looked like a
   design weakness (negative definition) but a full enumeration proved it
   coherent — the criticism would have been wrong. Check the artifact first.
6. **Calibration clause for all reviewing/writing:** this is a Master's
   thesis, NOT a journal submission or a technical manual (user-stated rule;
   earlier sessions over-flagged docstring/style issues until corrected).
7. **Examiner-safety for generated text:** never write "calibrated
   confidence"; the thesis's own Ch3/Ch5 disclaimers are the ceiling for any
   claim about the confidence signal.

---

## 5. Open items & deferred experiments (decision memos needed)

| Item | State 2026-07-12 |
|---|---|
| Stratified-vs-global PCA ablation | Deferred; the deferral sentence is **commented out** at `methodology_chapter.tex:215` — either reinstate as limitation or run (~1 day: swap global PCA into the existing validation loop, pattern in `analysis/ablation_k.py`). External evidence already cited: SuperPCA (Jiang), Segmented-PCA (Fu), Shi personalized-PCA. |
| LLM recommendation baseline (EQ3 arm) | `analysis/llm_baseline.py` EXISTS ❓ — check whether it has been run and has saved results before assuming the arm is missing; CC-2's "not run" status may be stale. |
| Corpus EDA | ✅ Landed — `tab:corpus_summary` + `fig:corpus_eda` now in Ch4. |
| k-sensitivity ablation | `analysis/ablation_k.py` exists; review credited a real neighbourhood-size ablation in Ch5. |
| Types-per-lemma / Honoré / dead-pattern cleanups | ❌ Open, see §1. Small code+prose commit. |
| Adoption of stratification drafts | `drafts/stratum_bridging_table.tex` (→ Ch4 §Feature Stratification) and `drafts/stratum_audit_appendix.tex` (→ `appendices/`) compile clean standalone; NOT yet `\input` anywhere; consistency edits in §1 must land with them. |
| `candidatetodo` sweep | Several live TODOs in Ch3 (e.g., "Double check beyer and aggarwal papers", `methodology_chapter.tex:209`). Enumerate before submission. |

---

## 6. Session deliverables index (2026-07-12)

- `analysis/stratum_audit.py` — regenerates the full feature-to-stratum
  enumeration LaTeX from `mkb.pkl` (`--mkb`, `--out` args; prints verification
  totals 2,726/327/63).
- `analysis/stratum_audit_tables.tex` — generated output (summary table + 5
  longtables).
- `Thesis Template Legit/drafts/stratum_bridging_table.tex` — bridging prose +
  Table `tab:stratum_lingualyzer_mapping` (S1–S6 ↔ constructs ↔ Lingualyzer
  3×2×3 taxonomy ↔ counts/PCs). References `subsec:feature_extraction_technique`
  (Ch3 taxonomy ¶), `subsec:pca_technique`, `appen:stratum_audit`.
- `Thesis Template Legit/drafts/stratum_audit_appendix.tex` — full appendix
  chapter: labels `appen:stratum_audit`, `tab:stratum_audit_summary`,
  `tab:stratum_audit_s1..s5`, `tab:stratum_audit_s6`.
- Key defense narrative distilled: the five strata are a **coarsening of
  Lingualyzer's published 3×2×3 taxonomy** (S1/S2/S3 ≈ unit dimension:
  morphological/lexical/syntagmatic; S4 ≈ complexity type; S5 ≈ distributional
  type), each an established construct; five not eighteen because sparse cells
  (S4 = 20 features) cannot support stable PCA and coarser partitions reunite
  heterogeneous covariance structures.

## 7. Phase-1 answers & institutional facts (user-provided 2026-07-12)

- **Submission deadline: 1 September 2026** (~7 weeks from ledger date; the
  2025 progress report anticipated hand-in 28 Aug 2026 — consistent).
- **Progress report due 31 July 2026.** Template = previous report at
  `Thesis Template Legit/thesis_checklist/WHugo_progress_report_signedMG25Jul2025.pdf`
  (sections: Planned Graduation Date; Subjects Completed; Thesis Progress;
  Identified Obstacles; Deviations from Previous Report; Anticipated Hand-in
  Date; supervisor+student signatures). ⚠️ The 2025 report is titled
  "Language Identification for Domain-Specific Short Texts in Automotive
  Customer Warranty Claims" — the project has since pivoted to the LID
  model-recommendation framework; the 2026 report's Deviations section MUST
  declare this pivot (topic + industry-data dependency dropped + CRISP-DM →
  DSR).
- **Supervisor:** Prof Mandla Gwetu. **Student:** Werner Hugo (25167626).
  Planned graduation: December 2026.
- **External examiner:** believed to be an information-retrieval expert
  (nothing else known). Defense prep should anticipate IR-framed questions:
  the framework IS a retrieval system (k-NN over fingerprints) — expect "why
  not learned ranking / embedding retrieval", precision@k / MRR framing,
  concentration-of-measure, TF-IDF-vs-linguistic-features challenges.
- **Chapter freeze status:** none frozen; Ch2 (scoping review) minor changes
  only (already-executed protocol); all others open.
- **LLM baseline: decision = RUN** (still on the to-do list; script ready,
  never executed).
- **Ambition bar: ≥75%** (distinction level at Stellenbosch).
- **Department checklist** (mandatory items, from
  `thesis_checklist/2026 Thesis Checklist_grammarlayout.pdf`): PDF soft copy;
  title-page format (title top third; author; MEng (Industrial Engineering/
  Engineering Management) formula; supervisor names + graduation month/year,
  e.g. March 2027); Declaration exact wording on p. ii (no signature, date
  only); "Copyright ©2027 Stellenbosch University" lower half p. ii; English
  Abstract ≤500 words (p. iii); Afrikaans "Opsomming"/"Uittreksel" ≤500 words
  (p. iv, quality-checked); ToC/LoF/LoT complete with page numbers +
  appendices listed; consistent heading capitalisation; no page number on
  title page; Introduction starts on page 1; captions "Table x:" ABOVE
  tables, "Fig x:" BELOW figures; margins 2 cm all round. Recommended: no
  single sub-sections; ≤1 paragraph before first subheading; appendices A.1
  numbering; chapter-based caption numbers; consistent reference style; hard
  space number–unit; core < 150 pages; professional language editing with
  proof.

## 8. Provenance and maintenance

- Re-verify stratum numbers: `python analysis/stratum_audit.py` (repo root,
  thesis_final env) — expect 2,726 / 327 / 63.
- Re-verify settled claims stay dead:
  `grep -rniE "leave-one-out|3,?066|five model families|calibrated confidence" "Thesis Template Legit" --include="*.tex"`
  — expect only the legitimate uses listed in §1.
- Re-verify env: `ls C:\Users\User\miniconda3\envs\thesis_final` and
  `pdflatex --version`.
- This ledger is a snapshot, not a living doc: the skill library supersedes it
  once built. If ledger and artifact disagree, the artifact wins.
