---
name: thesis-completion-campaign
description: >
  The executable, decision-gated campaign plan carrying the MEng thesis from
  2026-07-12 to submission on 2026-09-01. Load this skill when the user asks
  "what's next", "what's left before submission", wants to run the LLM
  baseline, draft the progress report (hard deadline 2026-07-31), adopt the
  stratification drafts, close the open code/prose consistency items, run the
  final re-review or checklist sweep, or plan the remaining weeks. Do NOT load
  this for the mechanics of HOW to edit thesis files (use thesis-change-control),
  how to review (thesis-review-protocol), style/checklist detail
  (thesis-writing-and-style), framework facts (lid-framework-reference), or
  environment setup (thesis-estate-and-env) — this skill is the WHAT and WHEN;
  siblings are the HOW.
---

# Thesis Completion Campaign — 2026-07-12 → 2026-09-01

Imperative runbook for a zero-context session. Every gate has entry criteria,
copy-pasteable commands, expected observations, and branch-on-failure
instructions. Success at every gate is **measurable** — never judged by eye.

**Definitions used throughout**
- *Gate* — a numbered milestone; do not start gate N+1's thesis edits before
  gate N's exit check passes (Gate 0 runs in parallel with everything).
- *Change control* — ALL edits to thesis `.tex`, toolkit code, or appendices
  go through the **thesis-change-control** skill (drafts-first, reviews
  read-only, machine-generated tables regenerated never hand-edited).
- *MKB* — Meta-Knowledge Base, the 17-dataset fitted artifact `mkb.pkl`.
- *EQ3* — experimental question 3: framework vs random / constant / LLM
  selection baselines.

## Key facts (verified 2026-07-12 unless tagged)

| Fact | Value |
|---|---|
| Submission deadline | **2026-09-01** (2025 report anticipated hand-in 28 Aug 2026) |
| Progress report due | **2026-07-31** (HARD) |
| Thesis root | `c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit` |
| Toolkit repo root | `c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit` |
| Python | `C:\Users\User\miniconda3\envs\thesis_final\python.exe` (miniconda3, NOT anaconda3) |
| LaTeX | MiKTeX 25.3 `pdflatex` on PATH; build = pdflatex → bibtex → pdflatex ×2 |
| Canonical chapters | resolve from `thesis.tex` `\input` list — stale `.text` near-duplicates exist in `chapters/` |
| Headline numbers | **Updated 2026-07-31.** Mean range capture **99.18%** (min 96.89%) now leads; mean gap **0.0073**; strict top-1 **2/17** (demoted to a strictness check); random Monte-Carlo **0.3830**; blind constant pick **0.3902**; best constant policy **0.0127**; zero-shot XLM-V **0.0175**; LLM `gpt-oss-120b` **0.0823**. Source: `analysis\reporting_measures_2026-07-21.json` — **not** `validation_statistics.py`, which is superseded. |
| Confidence signal | **Retracted 2026-07-21.** The 2/2-vs-1/15, p=0.022 result did not survive the coverage-guard correction; Ch5 reports the signal as **untested on this sample** (13 non-zero / 4 zero). Do not write "promising rather than established" — it is now an overclaim. NEVER write "calibrated confidence". |

## Campaign map

| Gate | Deliverable | Deadline / week |
|---|---|---|
| 0 | Progress report draft → signed → submitted | **2026-07-31 hard**; draft W1 |
| 1 | LLM baseline run + Ch5/Ch6 integration | W1 |
| 2 | Code/prose consistency closes + ablation decision memo | W2 |
| 3 | Stratification drafts adopted; clean compile | W2–W3 |
| 4 | Re-review pass; `\candidatetodo` → 0 | W4 |
| 5 | Department checklist compliance sweep | W5 |
| 6 | Language edit + final PDF + submission package | W5–W7 |

---

## GATE 0 — Progress report (HARD DEADLINE 2026-07-31)

**Entry criteria:** none — start immediately; runs in parallel with Gates 1–3.

**Template** (read it before drafting):
`c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\thesis_checklist\WHugo_progress_report_signedMG25Jul2025.pdf`
Verified structure (2 pages, LaTeX-produced):
- Header: date (left), "Project supervisor: Prof Mandla Gwetu" (right); title; "Werner Hugo (25167626)"
- §1 Planned Graduation Date: December 2026
- §2 Subjects Completed to Date — module table (Professional communication 871 / Research Methodology (REM) / MEng Research Ind Eng — all N/A; Introduction to Automotive Information Engineering using IT — 87.42)
- §3 Thesis Progress (literature %, experiments, preliminary findings)
- §4 Identified Obstacles
- §5 Deviations from Previous Progress Report
- "Anticipated Thesis Hand-in Date: 28 August 2026"
- Signature line: supervisor (signed 25 July 2025) + student

**⚠️ CRITICAL — the pivot declaration.** The 2025 report is titled
*"Language Identification for Domain-Specific Short Texts in Automotive
Customer Warranty Claims"*. The project has pivoted to
*"An Interactive Framework for Language Identification Model Recommendation"*
(the live `\title` in `thesis.tex`). §5 Deviations MUST declare, explicitly:
1. **Topic change** — from warranty-claims LID to the LID model-recommendation
   framework.
2. **Industry-data dependency dropped** — the 2025 report's §4 said secure
   access to the industry partner's proprietary warranty data was established;
   the 2026 report must state that arm was abandoned and the work now uses 17
   public multilingual benchmark corpora.
3. **Methodology change** — CRISP-DM → Design Science Research (DSR).

**Steps**
1. Draft as LaTeX (matches the 2025 look) at
   `c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\drafts\progress_report_2026.tex`
   — new material lands in `drafts/`, never elsewhere. A possible source
   template exists at `c:\Users\User\OneDrive\Masters\Thesis\Progress Report\University_of_Birmingham_Final_Year_Progress_Report_template\`
   (unverified that it produced the 2025 PDF — check before reusing).
2. §3 content: full draft exists post-panel-review (verdict: "Major revisions
   — documentation-level, not experimental"); 17-corpus MKB built; validation
   complete (headline numbers table above); remaining work = documentation
   closes + EQ3 additions. Use only numbers from the Key-facts table or the
   compiled thesis. §1: December 2026. Anticipated hand-in: 28 August 2026.
3. Compile standalone (`pdflatex` in `drafts/`), hand to the **user** to
   review, convert, and route for signatures. The agent never signs or submits.

**Exit check:** user confirms signed report submitted, dated ≤ 2026-07-31.
**If the user has not signed by 2026-07-28 → escalate**: raise it at the top
of every session reply until done. This gate cannot slip.

---

## GATE 1 — LLM baseline run ✅ **CLOSED (verified 2026-07-31)**

> **This gate is complete. Do not re-run it.** The arm was executed with
> `gpt-oss-120b` (open-weights, served via Groq), temperature 0.7, 3 repeats ×
> 17 datasets = 51 API calls. Results: mean gap **0.0823**, median 0.0560, max
> 0.4182, range capture 90.2%, exact-match 9.8%, self-consistency 0.569; paired
> against the framework 14-2-1, one-sided **p = 0.000107** — the strongest
> significant comparison in the thesis. Raw artifact `llm_baseline_gptoss.json`
> (repo root); summarised in `analysis\reporting_measures_2026-07-21.json` under
> `llm_baseline`. Ch5 carries the full treatment (tiered baseline table + a
> dedicated LLM section); Ch6's EQ3 answer includes it.
>
> ⚠️ `llm_baseline_MIXED_do_not_use.json` also sits in the repo root — the
> filename is the instruction. `llm_baseline_results_llama33_partial.json` is an
> abandoned partial run. Neither is the artifact of record.
>
> The historical entry criteria and procedure are kept below for provenance only.

**Entry criteria (historical):** `analysis/llm_baseline.py` exists;
`validation_report.json` exists at repo root (2026-05-14 build); eval dir
`c:\Users\User\OneDrive\Masters\LID_experiments\datasets\02_evaluation_15_cleaned`
exists.

**What the script does** (verified by full read, 2026-07-12): simulates a
practitioner asking an LLM which LID model to deploy. Per evaluation dataset
(17 total) it sends one API call. Fairness protocol — GIVEN: the candidate
inventory (6 trained configurations × 17 training corpora with one-line
register descriptions + 3 zero-shot detectors) and a profile computed from the
evaluation split only (ISO language list from parquet filenames, char-length
median/IQR, N seeded sample texts truncated to 200 chars, seed 42). WITHHELD:
all benchmark numbers, the query corpus's identity, the fingerprints/MKB.
Structured output (`json_schema`) forces `top_choice`, `ranked_top3`,
`reasoning`. Scoring: `gap = ground_truth_score − chosen_score` (f1_weighted
on the eval split), exactly the framework's metric.

**Exact usage** (defaults verified from argparse):
```
python analysis/llm_baseline.py [--report validation_report.json]
                                [--eval-dir <02_evaluation_15_cleaned>]
                                [--n-samples 10] [--model claude-opus-4-8]
                                [--dry-run]
```
Requires `ANTHROPIC_API_KEY` (or an `ant auth login` profile) and internet —
run LOCALLY, not on the HPC. Uses the current API correctly
(`claude-opus-4-8` is a valid live model id; adaptive thinking; json_schema
output; cached system prompt; refusals are skipped per-dataset, not fatal).

**Output:** written to `<report dir>\llm_baseline_results.json` — with the
default report path that is the **repo root**. JSON contains: `model`,
`n_datasets`, `n_scored`, `exact_matches`, `mean_gap`, `max_gap`,
`median_gap`, and `per_dataset` entries (`dataset`, `llm_choice`,
`llm_ranked_top3`, `llm_reasoning`, `valid_candidate`, `ground_truth_model`,
`ground_truth_score`, `resolved_key`, `chosen_score`, `gap`, `exact_match`).

**Step 1 — preflight** (repo root, thesis_final env):
```powershell
& C:\Users\User\miniconda3\envs\thesis_final\python.exe -c "import anthropic"
```
Expected as of 2026-07-12: **ModuleNotFoundError** (verified — not installed).
→ `& C:\Users\User\miniconda3\envs\thesis_final\python.exe -m pip install anthropic`
Then confirm the key: `$env:ANTHROPIC_API_KEY` non-empty (ask the user for it;
never invent or commit one).

**Step 2 — dry run** (no API calls, no cost):
```powershell
& C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\llm_baseline.py --dry-run
```
Expected: 17 blocks of `===== <dataset> =====` each showing the corpus
profile prompt (languages line, char-length line, ~10 truncated sample docs),
then `[dry run] no API calls made`. Verify: language lists look like ISO
codes; samples are real text; no tracebacks.
- If a `FileNotFoundError` on parquet → eval-dir moved; pass `--eval-dir` explicitly.
- If a dataset name KeyError → `validation_report.json` schema drifted; open
  it and check `per_dataset[*].dataset` exists before touching the script.

**Step 3 — real run** (~17 Opus calls; minutes; a few USD at most):
```powershell
& C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\llm_baseline.py
```
Expected: one line per dataset `"{dataset} -> {choice} gap=0.xxxx"`, then
`exact k/17  mean gap 0.xxxx  max gap 0.xxxx` and
`saved -> ...\llm_baseline_results.json`.
- If any line prints `request refused — skipping` → note it; `n_scored` < 17
  must be reported in the thesis text.
- If `gap=n/a` / `"error": "choice not resolvable"` → the LLM named a
  candidate that doesn't map to a benchmark key; record it as unresolvable
  (that IS a result — the baseline failed to nominate a scoreable model), do
  not silently rerun.
- If `valid_candidate: false` in the JSON → the schema constrained field
  names, not values; the LLM invented an ID. Same treatment: report it.

**Step 4 — integration (change-controlled edits, via thesis-change-control):**
1. **Ch5**: add one row to Table `tab:baseline_comparison`
   (`chapters/demonstration_and_evaluation.tex`, table at ~line 119–130) with
   the LLM baseline's mean and max gap, + one discussion sentence. This
   resolves item (1) of the `\candidatetodo` at
   `demonstration_and_evaluation.tex:117`.
2. **Ch6**: extend the EQ3 answer at `chapters/conclusion.tex:55` with the LLM
   result, resolving item (1) of its `\candidatetodo`.
3. Framing rule: report the result factually either way. If the LLM baseline
   beats or nears the framework, that is a finding to discuss, not hide —
   examiner-safe language only.
4. ⚠️ Both candidatetodos also list a **second** pending item — the
   confirmatory run on reserved validation splits (`model_benchmarking_validation`
   on the HPC + `validate_recommendations_validation.py`). That is a separate
   user decision, NOT covered by this gate. Present it as a decision memo:
   run it (needs HPC time) or reframe/remove the promise. Do not delete the
   todo until the user decides.

**Exit check:** `llm_baseline_results.json` exists at repo root with
`n_datasets: 17`; Ch5 table row + Ch6 sentence landed; recompile passes
(Gate 3 build procedure).

---

## GATE 2 — Close the open code/prose consistency items

**Entry criteria:** none (independent of Gate 1). All three code items live in
`src\lid_toolkit\recommender\feature_stratifier.py`. Ground truth: in the
fitted artifact and in the code's pattern lists, all 25 types-per-lemma
feature families are **S1** (patterns `"word types per lemma"`,
`"types per lemma"` at lines 107–108 sit in the S1 list) — and S1 is the
better construct fit (inflected types per lemma ≈ paradigm size ≈
morphological richness).

**Item A — types-per-lemma S2→S1 (prose + docstring).**
- `chapters/design_and_implementation.tex:226` — the S2 bullet in "The Five
  Continuous Strata" ends "...and word-types-per-lemma measures." Delete that
  clause from S2 and add it to the S1 bullet.
- `feature_stratifier.py` module docstring: S2 description (line ~21) lists
  "word-types-per-lemma measures" — move to the S1 description (line ~17).
- Also merge these prose edits with Gate 3's bridging-table adoption (same
  change set — the draft's header comment notes the dependency).

**Item B — Honoré.** Docstring line ~20 claims "Honoré's statistic" in S2. No
Honoré feature exists in the 2,726-feature core; the `"honoré"` pattern
(line ~116) never fires. Remove the docstring claim AND the dead pattern.

**Item C — dead entropy patterns.** `"word entropy"`, `"letter entropy"`
(lines ~120–121, S2 list) can never match — S4's `"entropy"` pattern (line
~66) is checked first (first-match-wins, priority order S4→S5→S1→S2→S3).
Delete both lines so code and prose don't look contradictory to an examiner.

**Invariant check — MANDATORY after the code edits** (proves the refactor
changed zero assignments; repo root):
```powershell
& C:\Users\User\miniconda3\envs\thesis_final\python.exe -c @"
import pickle
from lid_toolkit.recommender.feature_stratifier import _assign_stratum
mkb = pickle.load(open('mkb.pkl','rb'))
f2s = mkb.stratifier._feature_to_stratum
bad = [(n,s,_assign_stratum(n)) for n,s in f2s.items() if _assign_stratum(n)!=s]
print(f'checked {len(f2s)} pooled features, mismatches: {len(bad)}')
print(bad[:5])
"@
```
Expected: `checked 2926 pooled features, mismatches: 0`. Then:
```powershell
& C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\stratum_audit.py
```
Expected verification totals: **2,726 / 327 / 63**.
- If mismatches > 0 → you deleted a live pattern, not a dead one. Revert the
  code edit and diff against the pattern lists quoted above.
- If `mkb.pkl` fails to unpickle → you are not at the repo root or not in
  thesis_final (see thesis-estate-and-env).

**Item D — ablation deferral: DECISION MEMO (do not decide unilaterally).**
Note first: the stratification-ablation deferral is **already stated live** as a
Ch3 limitation at `chapters/methodology_chapter.tex:405` — so the thesis does
NOT silently drop it. The more specific commented sentence at
`chapters/methodology_chapter.tex:215` ("% An ablation study comparing
stratified and global PCA ... is deferred to future work...") is an *optional*
elaboration. Present both branches to the user:
- **Branch 1 (cheap, honest):** uncomment/reinstate the sentence as a stated
  limitation (consider echoing in Ch6 limitations). External evidence already
  cited in that section: SuperPCA (Jiang), Segmented-PCA (Fu), Shi
  personalized-PCA. ~30 min.
- **Branch 2 (~1 day):** run the stratified-vs-global-PCA ablation — swap a
  global PCA into the existing validation loop; the loop pattern lives in
  `analysis/ablation_k.py`. Then report in Ch5 and replace the deferral
  sentence with the result.
Either branch lands via change control. Record the decision date in the memo.

**Exit check:** invariant check passes (0 mismatches, 2,726/327/63); Ch4 S1/S2
bullets match the docstring match the code; ablation memo answered by user.

---

## GATE 3 — Adopt the stratification drafts

**Entry criteria:** Gate 2 items A–C ready to land (they ship in the same
change set). Both drafts compile clean standalone (verified during authoring)
and are `\input` NOWHERE yet (verified 2026-07-12).

**Steps**
1. Move `drafts\stratum_audit_appendix.tex` → `appendices\stratum_audit_appendix.tex`.
   Defines `appen:stratum_audit`, `tab:stratum_audit_summary`,
   `tab:stratum_audit_s1..s5`, `tab:stratum_audit_s6`. Content between
   AUTO-GENERATED markers is machine output of `analysis/stratum_audit.py` —
   if the MKB ever changes, **regenerate, never hand-edit**.
2. Append to `appendices\appendices.tex` (currently one line,
   `\input{appendices/an_appendix}`):
   `\input{appendices/stratum_audit_appendix}`
3. Merge `drafts\stratum_bridging_table.tex` (bridging prose + Table
   `tab:stratum_lingualyzer_mapping`) into Ch4 §Feature Stratification —
   `chapters/design_and_implementation.tex`, section starts line 204
   (`\mysection{Phase 2: ...}`, label `sec:feature_stratification`); the
   natural insertion point is around the "Five Continuous Strata" subsection
   (line 218). All three labels it references resolve: 
   `subsec:feature_extraction_technique` (methodology_chapter.tex:194),
   `subsec:pca_technique` (methodology ~line 206), `appen:stratum_audit`
   (step 1). Land Gate 2's S1/S2 bullet edits in this same change.
4. Recompile — full cycle, **3+ pdflatex passes** (longtable needs them):
```powershell
cd "c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit"
pdflatex -interaction=nonstopmode thesis.tex
bibtex thesis
pdflatex -interaction=nonstopmode thesis.tex
pdflatex -interaction=nonstopmode thesis.tex
```
5. Measurable checks on the FINAL pass's log:
```bash
grep -c "Table widths have changed" thesis.log        # expect: 0
grep -E "Warning.*(undefined|multiply.defined)" thesis.log   # expect: no output
grep "There were undefined references" thesis.log      # expect: no output
```

**Branches**
- "Table widths have changed" > 0 → run one more pdflatex pass and re-grep;
  longtables converge in ~3 passes.
- Undefined reference naming `appen:stratum_audit` → step 2's `\input` line
  missing or the file wasn't moved.
- Undefined citation → new prose cites a key absent from `references.bib`;
  add via citation workflow (thesis-writing-and-style), never invent a key.
- Duplicate-label error → the file was left in `drafts/` AND copied to
  `appendices/`; a stray `\input` of the drafts copy exists. `thesis.tex`'s
  `\input` list is canonical — check it.

**Exit check:** all three greps clean; PDF contains the appendix (it appears
in ToC/LoT) and the bridging table renders inside Ch4.

---

## GATE 4 — Re-review

**Entry criteria:** Gates 1–3 landed and compiling clean.

1. Invoke **thesis-review-protocol** in **re-review mode** against the prior
   panel findings (artifact "Thesis Review Panel — Full Review Report", early
   July 2026 — retrieve via the Artifact list/WebFetch; original counts
   3 Critical / 11 Major / 14 Minor / 5 Nitpick, verdict "Major revisions —
   documentation-level, not experimental"). Re-review verifies fixes and does
   NOT re-open settled items. Reviews are read-only; findings come with fix +
   locator; edits then route through thesis-change-control.
2. **`\candidatetodo` sweep to zero.** Count command (thesis root) — the
   `grep -v` filter excludes commented-out lines and is robust to escaped `\%`
   inside a todo line (which breaks the naive `^[^%]*` form):
```bash
grep -rnE '\\candidatetodo' chapters/*.tex | grep -vE '^[^:]*:[0-9]+:[[:space:]]*%'
```
   As of 2026-07-13: **5 live** (conclusion 2 — :55, :114; demonstration 1 —
   :117; methodology 1 — :209 "Double check beyer and aggarwal papers";
   scoping_review 1 — :108) **+ 2 commented** (methodology :142, :170 — not
   live, leave or delete). **thesis-writing-and-style §3 owns the enumerated
   list** — read it there, don't re-count here. Target before submission:
   live count = 0. Each todo is resolved (do the check / land the edit) or
   explicitly waived by the user — never silently deleted.
3. **Settled-claims regression grep** (wrong old claims must stay dead):
```bash
grep -rniE "leave-one-out|3,?066|five model families|calibrated confidence" chapters/ frontmatter/ appendices/
```
   Expected: exactly one legitimate hit —
   `design_and_implementation.tex:331` "leave-one-out dataset pairs" (a
   stratum-weight correlation analysis, not the validation protocol). ANY
   other hit means a corrected claim was resurrected (stale `.text` files and
   git history contain the wrong versions) → fix via change control.
4. Cross-chapter consistency re-check: EQ2/EQ3 mapping in Ch1 (~
   `introduction_chapter.tex:220`), headline numbers identical across
   abstract / Ch5 / Ch6 (use the Key-facts table as ground truth), and the
   new LLM-baseline number appears consistently wherever EQ3 is answered.

**Exit check:** re-review verdict ≤ minor; candidatetodo count 0; regression
grep shows only the one legitimate hit.

---

## GATE 5 — Department checklist compliance sweep

**Entry criteria:** Gate 4 exit. Execute via **thesis-writing-and-style**
(it owns the per-item mechanics and live measurements); this gate is the
occurrence and the pass/fail list. Mandatory items (from
`thesis_checklist\2026 Thesis Checklist_grammarlayout.pdf`):

- [ ] English Abstract ≤ 500 words (p. iii); Afrikaans "Opsomming"/"Uittreksel" ≤ 500 words (p. iv, quality-checked)
- [ ] Captions: "Table x:" ABOVE tables, "Fig x:" BELOW figures — every float
- [ ] Title page: title in top third; author; "MEng (Industrial Engineering)" formula; supervisor; graduation month/year; NO page number on title page
- [ ] Declaration exact wording p. ii (no signature, date only); "Copyright ©… Stellenbosch University" lower half p. ii — confirm the year against the checklist PDF (planned graduation December 2026)
- [ ] Page numbering: roman front matter; Introduction starts on arabic page 1
- [ ] ToC / LoF / LoT complete with page numbers; appendices listed
- [ ] Margins 2 cm all round; consistent heading capitalisation
- [ ] Recommended: no single sub-sections; ≤ 1 paragraph before first subheading; appendix A.1 numbering; chapter-based caption numbers; hard space number–unit; core < 150 pages

**⚠️ Known discrepancy to resolve here (found 2026-07-12):** `thesis.tex:28`
sets `\newcommand{\Studentnumber}{2516726}` — 7 digits. The student number
everywhere else (progress report, ledger) is **25167626** (8 digits). Verify
where `\Studentnumber` is rendered and correct it via change control.

**Exit check:** every mandatory box ticked with a command-or-page-number
verification recorded (thesis-writing-and-style defines the measurement for
each); word counts of both abstracts recorded ≤ 500.

---

## GATE 6 — Final: language edit, final build, submission package

**Entry criteria:** Gate 5 exit. ⚠️ **Book the language editor by Week 4** —
professional editing is department-recommended WITH PROOF, and turnaround is
typically 1–2 weeks; booking late is the biggest schedule risk after Gate 0.

1. **Language edit.** Send the compiled PDF + source to a professional editor;
   obtain the editing certificate/proof for the submission package.
   Incorporate edits via change control (editors change prose, not numbers —
   re-run the Gate 4 regression grep after incorporating).
2. **Final PDF build.** Clean build from scratch: delete `thesis.aux`,
   `thesis.bbl`, `thesis.toc`, `thesis.lof`, `thesis.lot`, then the full
   Gate 3 build cycle (pdflatex, bibtex, pdflatex ×2, +1 if the longtable
   grep is nonzero). All three Gate 3 log greps must be clean.
3. **Submission package:** final PDF soft copy; language-editing proof;
   whatever the department portal requires (user confirms the list with the
   department — the agent cannot see the portal). Target hand-in
   **2026-08-28** (as anticipated in the progress report), hard limit
   **2026-09-01**.

**Exit check:** user confirms submission receipt. Campaign over; switch to
**examiner-defense-pack** for oral-defense prep (external examiner is
believed to be an information-retrieval expert).

---

## Week-by-week schedule (7 weeks)

| Week | Dates | Do | Gate |
|---|---|---|---|
| W1 | Jul 13–19 | Gate 1 end-to-end (install → dry-run → run → integrate). Draft Gate 0 report; hand to user. | 0-draft, 1 |
| W2 | Jul 20–26 | Gate 2 items A–C + invariant check; ablation decision memo to user; Gate 3 adoption + clean compile. User routes Gate 0 for supervisor signature (2025 signature was Jul 25 — same window). | 2, 3, 0-sign |
| W3 | Jul 27–Aug 2 | **Progress report SUBMITTED by Jul 31 (hard).** If ablation Branch 2 chosen, run it now. Buffer for Gate 2/3 spillover. | **0 done** |
| W4 | Aug 3–9 | Gate 4 re-review + fix findings; candidatetodo → 0. **Book language editor.** | 4 |
| W5 | Aug 10–16 | Gate 5 checklist sweep; manuscript to language editor. | 5, 6-start |
| W6 | Aug 17–23 | Incorporate language edits; re-run regression grep; final clean build. | 6 |
| W7 | Aug 24–31 | Final checks, submission package, submit ~Aug 28 (buffer to Sep 1). | 6 done |

Slack rule: Gates 1–3 have ~1 week of combined float (W3 buffer). Gate 0 has
none. If any gate slips past its week, cut scope in this order: ablation
Branch 2 → confirmatory validation-split run → recommended (non-mandatory)
checklist items. Never cut: Gate 0, the candidatetodo sweep, the mandatory
checklist items, the language-edit proof.

## When NOT to use this skill

- Editing mechanics, draft/adopt workflow, commit discipline → **thesis-change-control**
- Running or interpreting a review → **thesis-review-protocol**
- Style, captions, abstract word counts, citation hygiene → **thesis-writing-and-style**
- What the framework/numbers mean → **lid-framework-reference**; claim provenance → **thesis-claims-archaeology**
- Verifying artifacts (mkb.pkl, reports) → **artifact-verification-playbook**
- Environment/paths/build quirks → **thesis-estate-and-env**
- Defense preparation after submission → **examiner-defense-pack**

## Provenance and maintenance

All facts date-stamped **2026-07-12** unless noted. Volatile facts and
one-line re-verification commands:

- LLM baseline not yet run: `ls c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit\llm_baseline_results.json` (absent = not run). Script defaults: re-read the docstring of `analysis\llm_baseline.py`.
- `anthropic` not installed in thesis_final: `& C:\Users\User\miniconda3\envs\thesis_final\python.exe -c "import anthropic"` (errored 2026-07-12).
- Drafts unadopted: `grep -rn "stratum_audit_appendix\|stratum_lingualyzer_mapping" "c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\thesis.tex" "...\appendices\appendices.tex" "...\chapters\design_and_implementation.tex"` — no hits = still unadopted.
- Open code items: `grep -n "honoré\|word entropy\|letter entropy" src\lid_toolkit\recommender\feature_stratifier.py` — hits = Gate 2 not done.
- candidatetodo live count (5 as of 2026-07-13): `grep -rnE '\candidatetodo' "c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\chapters\"*.tex | grep -vE '^[^:]*:[0-9]+:[[:space:]]*%'`
- Stratum totals: `python analysis\stratum_audit.py` → 2,726 / 327 / 63.
- Progress-report template + department checklist: files in `Thesis Template Legit\thesis_checklist\` (both verified present 2026-07-12).
- Student-number discrepancy: `grep -n "Studentnumber" "c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\thesis.tex"` (showed `2516726` on 2026-07-12).
- If this skill and an on-disk artifact disagree, the artifact wins.
