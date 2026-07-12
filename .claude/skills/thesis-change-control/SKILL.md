---
name: thesis-change-control
description: >-
  Load this BEFORE you change anything in the thesis estate — editing a chapter,
  adding prose or a table, touching a number, regenerating a machine-made table,
  or modifying toolkit/analysis code. It is the gatekeeper that decides HOW a
  change may land: where new material goes (drafts/ first, never chapters/),
  which changes need a saved artifact behind them, which tables must be
  regenerated instead of hand-edited, what language is examiner-safe, and the
  git discipline (feature branch, commit only when asked, no amend/force-push).
  Read it whenever the request is "edit/add/fix/reword/update" anything under the
  four estate roots, or before a commit or pre-merge check. Do NOT load it for
  pure investigation with no write (use thesis-estate-and-env to find files, or
  thesis-review-protocol to run a read-only review). It states the change RULES;
  for the deep how-to of a task it gates, defer to the sibling it names
  (artifact-verification-playbook, thesis-writing-and-style, thesis-review-protocol,
  thesis-claims-archaeology, evidence-standards).
---

# Thesis Change Control

The rulebook for mutating anything in Werner Hugo's MEng thesis estate
(submission **2026-09-01**). Every rule here was paid for by a past incident.
This skill is a **gate**, not a task guide: it tells you whether and how a change
may land. For the mechanics of the gated task, defer to the named sibling skill.

**Jargon, defined once:**
- **Estate** — the four repo roots on this one machine (paths below).
- **MKB** — Model Knowledge Base; the fitted `mkb.pkl` artifact + its store.
- **Artifact** (evidence sense) — a saved file/output on disk that a number was
  read from (pickle, JSON, generated `.tex`, script stdout). Not the claude.ai
  "Artifact" web page — context disambiguates.
- **Generated table** — a `.tex` table emitted by a script, wrapped in
  `AUTO-GENERATED` markers.
- **Live vs stale** — a chapter file is *live* only if `thesis.tex` `\input`s it;
  everything else (esp. `.text` files) is *stale* and must never be edited.

## The four estate roots (absolute, date-stamped 2026-07-12)

| Root | Path | Git? |
|---|---|---|
| Toolkit (primary; skills live here) | `c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit` | yes |
| Thesis (LaTeX) | `c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit` | check locally |
| Experiments | `c:\Users\User\OneDrive\Masters\LID_experiments` | — |
| Research notes | `C:\Users\User\OneDrive\Masters\Thesis\deep-research` | — |

Python for any toolkit/analysis code: `C:\Users\User\miniconda3\envs\thesis_final\python.exe`
(miniconda3, **not** anaconda3). Run toolkit code from the toolkit repo root.

---

## The seven non-negotiables (rule → why → the incident that bought it)

### 1. Reviews are read-only
**Rule:** A review produces findings as *fix + locator* (what to change, and the
exact `file:line`), never as edits to thesis files.
**Why:** If a review both measures and mutates, you can no longer tell what the
review actually found versus what it silently changed.
**Incident:** Earlier sessions mixed reviewing and editing; it became impossible
to reconstruct what a given review had assessed. The panel protocol (v2.0.0) was
made strictly read-only in response. Run reviews via **thesis-review-protocol**.

### 2. New material lands in `drafts/` first — never straight into `chapters/`
**Rule:** Draft new chapter prose, tables, or appendices in
`Thesis Template Legit\drafts\`. Promote into a live chapter (`\input` it, or
paste the reviewed block) only after it compiles clean standalone and its
consistency edits are ready to land with it.
**Why:** The chapters directory is littered with near-duplicate dead files, and
one of them still carried a `\label` the compiled thesis once referenced —
editing the wrong file wastes a session and can resurrect a stale cross-ref.
**Incident (verified 2026-07-12):** `chapters/` holds **9 stale `.text`
near-duplicates** — `experimental_design_and_methodology.text`,
`experimental_design_and_methodology1.text`, `introduction_chapter.text`,
`methodology.text`, `natural_lang_proc.text`, `scoping_review_chapter.text`,
`scoping_review_old.text`, `toolkit_architecture.text`,
`verification_and_validation.text` — sitting beside the 6 live `.tex` chapters.
**Always resolve the live set from `thesis.tex`'s `\input` list first.** As of
2026-07-12 the live chapters are exactly: `introduction_chapter`,
`scoping_review_chapter`, `methodology_chapter`, `design_and_implementation`,
`demonstration_and_evaluation`, `conclusion`. Current drafts staged but not yet
`\input` anywhere: `drafts/stratum_bridging_table.tex`,
`drafts/stratum_audit_appendix.tex`.

### 3. Machine-generated tables are regenerated, never hand-edited
**Rule:** If a `.tex` table sits between `AUTO-GENERATED` markers, do not touch
the numbers by hand. Change the source data or the script, then **rerun the
script**. Never hand-patch a generated table to match prose.
**Why:** A hand-edit silently diverges from its source; the next regeneration
overwrites it, and in the meantime the thesis carries an unbacked number.
**Incident / precedent (verified 2026-07-12):** the pipeline
`analysis/stratum_audit.py` → `analysis/stratum_audit_tables.tex` → embedded in
`drafts/stratum_audit_appendix.tex` between markers at lines **46–47**
(`% ── BEGIN AUTO-GENERATED (analysis/stratum_audit.py) ──` /
`% ── AUTO-GENERATED by analysis/stratum_audit.py — do not edit by hand ──`) and
**337** (`% ── END AUTO-GENERATED ──`). If the MKB changes, rerun:
```
cd c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit
C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis/stratum_audit.py
```
Expect the verification totals **2,726 / 327 / 63** (core features / families / PCs).

### 4. No numeric claim enters prose without a saved artifact behind it
**Rule:** Before a number lands in a chapter, name the artifact or command it
came from, and confirm it matches. If ledger and artifact disagree, **the
artifact wins.**
**Why:** Untraced numbers propagate through drafts and become impossible to
audit.
**Incident:** the feature count `3,066` survived multiple drafts purely because
nobody traced it; the correction to the true **2,726 core features** required
actually loading the fitted stratifier. (A stale `3,066` may still lurk in a
`src/` docstring — grep `3,?066` before trusting any feature count.) For the
mechanics of loading `mkb.pkl` and re-deriving a number, use
**artifact-verification-playbook**; the depth of what counts as adequate
evidence lives in **evidence-standards**.

### 5. Verification before criticism
**Rule:** Never flag something as a flaw until you have opened the artifact that
would prove it. Enumerate before you accuse.
**Why:** The obvious-looking weakness is often an artifact of not having looked.
**Incident:** the S3 "Structural/Syntactic" stratum is defined as a catch-all
(empty-string, last-match pattern), which *looked* like a design weakness — a
stratum defined by what it is not. A full enumeration of all 151 S3 families
proved every one is genuinely structural/syntactic (PoS distributions, ratios,
positions, lengths, counts, punctuation). The criticism would have been wrong.

### 6. Calibration clause — this is a Master's thesis
**Rule:** Hold changes to Master's-thesis standard, **not** journal-submission or
technical-manual standard. Do not over-engineer prose, over-flag docstring/style
nits, or demand rigor the deliverable does not require.
**Why:** Effort spent polishing beyond the bar is effort stolen from a 7-week
runway to submission.
**Incident:** earlier sessions over-flagged docstring and style issues until the
user set this rule explicitly (2026-07-12).

### 7. Examiner-safe language — the thesis's own disclaimers are the ceiling
**Rule:** Never write "**calibrated confidence**" for the recommender's
confidence signal. It is a **consensus confidence signal**. Any claim about it
may go no further than the thesis's own Ch3/Ch5 disclaimers.
**Why:** "Calibrated" asserts probabilistic calibration the evidence does not
support; an examiner will catch the overclaim.
**Incident / evidence ceiling:** calibration evidence is **directional only** —
2/3 vs 1/14 correct, exact one-sided **p = 0.063**, described in-thesis as
"suggestive rather than established." Safe existing phrasings to mirror:
`methodology_chapter.tex:256` "not a calibrated probability";
`demonstration_and_evaluation.tex:327` "rather than established calibration".
For fuller wording guidance use **thesis-writing-and-style**.

---

## Chapter freeze status (as of 2026-07-12)

| Chapter (live `.tex`) | Status | What you may change |
|---|---|---|
| introduction_chapter | open | anything, per the rules above |
| scoping_review_chapter (Ch2) | **minor-changes-only** | typos, refs, wording ONLY — protocol already executed; do NOT re-scope, re-run, or restructure |
| methodology_chapter (Ch3) | open | anything; note live `\candidatetodo`s remain |
| design_and_implementation (Ch4) | open | anything |
| demonstration_and_evaluation (Ch5) | open | anything |
| conclusion (Ch6) | open | anything |

**No chapter is fully frozen.** Ch2's minor-only status is a **user rule stated
2026-07-12** — treat any structural or experimental change to Ch2 as out of
bounds without explicit new instruction.

---

## Git discipline

- **Current working branch:** `feature/api-dashboard-intergration` — the typo
  "intergration" is in the **real branch name**; do not "correct" it.
- **Main branch:** `main`. Never commit thesis/toolkit work directly to `main`;
  branch first (feature branch) if you are on it.
- **Commit ONLY when the user asks.** Do not commit or push on your own
  initiative, even after a clean change.
- **No history rewriting:** no `git commit --amend`, no `git push --force` /
  `--force-with-lease`, no rebasing published branches — unless the user
  explicitly requests it.
- Prefer a **new commit** over amending an existing one.
- Toolkit repo is the git primary; verify the thesis repo's own VCS state
  locally before assuming it is versioned.

---

## Change classification — pick the class, pass its gate

Every change is one (or a cascade) of four classes. Cascade upward: a code
change that moves a number also triggers the number-bearing and, if it feeds a
generated table, the generated-content gates.

| Class | You are… | Gate it MUST pass before landing | Owning sibling for the how-to |
|---|---|---|---|
| **Prose-only** | rewording, grammar, restructuring text with no number and no generated block | New material → `drafts/` first (rule 2). Respect freeze status (Ch2 minor-only). Examiner-safe language (rule 7). Master's-thesis calibration (rule 6). | thesis-writing-and-style |
| **Number-bearing** | inserting/altering any numeric claim | Named saved artifact behind it and it matches; artifact wins over ledger (rule 4). | artifact-verification-playbook, evidence-standards |
| **Generated-content** | changing a machine-made table/figure | Do NOT hand-edit; change source/script and rerun; `AUTO-GENERATED` markers intact; verification totals reprinted (rule 3). | — (script is self-documenting; see rule 3) |
| **Code** | editing `src/` or `analysis/` | Feature branch; runs/imports from repo root under `thesis_final`; commit only when asked; no amend/force-push. If it changes a number or a generated table, ALSO pass those gates. | thesis-estate-and-env |

Reviewing (measuring, not changing) is not on this table on purpose — it never
lands a change (rule 1). Run it through **thesis-review-protocol**.

---

## Pre-merge / pre-commit checklist

Run top-to-bottom before asking the user to approve a commit or a merge.

| # | Check | How to confirm | Gate/rule |
|---|---|---|---|
| 1 | Editing a **live** file, not a stale `.text` | Target appears in `thesis.tex` `\input` list | 2 |
| 2 | New material staged in `drafts/`, not pasted raw into a chapter | `git status` / file location | 2 |
| 3 | Ch2 untouched beyond minor wording | diff scoping_review_chapter | freeze |
| 4 | Every new/changed number traces to a saved artifact | name the artifact per number; artifact wins | 4 |
| 5 | No generated table hand-edited | `AUTO-GENERATED` markers intact; script rerun if data changed | 3 |
| 6 | Generated totals still 2,726 / 327 / 63 (if MKB touched) | `python analysis/stratum_audit.py` | 3 |
| 7 | No forbidden phrase reintroduced | grep (command below) → only known-legit hits | 7, and thesis-claims-archaeology |
| 8 | Language at Master's-thesis level, not over-polished | judgment | 6 |
| 9 | On a feature branch, not `main` | `git rev-parse --abbrev-ref HEAD` | git |
| 10 | Commit only because the **user asked**; no amend/force-push | recall the request | git |
| 11 | Changed toolkit/analysis code still imports & runs from repo root | run it under `thesis_final` | Code gate |

**Forbidden-phrase / regression sweep (check 7):**
```
grep -rniE "leave-one-out|3,?066|five model families|calibrated confidence" "c:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit" --include="*.tex"
```
Expect only the known-legitimate survivors (a stratum-weight Pearson analysis's
"leave-one-out dataset pairs"; disclaimer uses of "calibrat*"). Any *new* hit is
a settled battle being re-lost — see **thesis-claims-archaeology** for the full
CC-1…CC-8 list before reverting.

---

## When NOT to use this skill

- **Pure investigation / navigation with no write** — finding a file, reading a
  chapter, resolving a path or env question → **thesis-estate-and-env**.
- **Running a review** (read-only measurement, no edit) → **thesis-review-protocol**.
- **Deciding a claim's truth or re-deriving a number** → **artifact-verification-playbook**
  (mechanics) / **evidence-standards** (what counts) / **thesis-claims-archaeology**
  (settled-battle history).
- **Actually writing polished prose or matching house LaTeX style** →
  **thesis-writing-and-style**. This skill only gates *whether/how* that prose
  may land; it is not the style guide.

Use this skill the moment a task turns from "look" to "change."

---

## Provenance and maintenance (facts date-stamped 2026-07-12)

Volatile facts to re-verify if this skill feels stale:

- **Live chapter set** (may change as drafts get promoted):
  `grep -n '\\input{chapters' "c:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/thesis.tex"`
- **Stale `.text` count** (currently 9): `ls "c:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters/"*.text`
- **AUTO-GENERATED markers present** (currently lines 46–47, 337):
  `grep -n AUTO-GENERATED "c:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/drafts/stratum_audit_appendix.tex"`
- **Generated totals** (currently 2,726 / 327 / 63):
  `C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis/stratum_audit.py` (from toolkit repo root)
- **Current branch** (currently `feature/api-dashboard-intergration`, typo real):
  `git rev-parse --abbrev-ref HEAD`
- **Ch2 freeze** and **commit-only-when-asked** are user rules from 2026-07-12;
  re-confirm with the user if the runway or scope has shifted.
- Source of record for the incidents behind rules 1–7: the session-facts ledger
  `project_context/SESSION_FACTS_LEDGER.md` §4 (and §1 for CC-1…CC-8). The ledger
  is a snapshot; where this skill and an artifact disagree, **the artifact wins**.
