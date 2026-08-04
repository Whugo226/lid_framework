# Thesis Skill Library — Overview

A purpose-built skill library for the MEng thesis *"An Interactive Framework for
Language Identification Model Recommendation"* (Werner Hugo, Stellenbosch,
submission 2026-09-01). Each skill owns a narrow slice and cross-references its
siblings, so they compose without overlap. Every skill's own description states
what **not** to use it for and points to the correct sibling.

Located in: `.claude/skills/`

---

## Router / start-here

- **thesis-index** — The dispatcher. A one-page map of the four-root estate that
  routes a task ("revise a chapter", "verify a number", "prep the viva") to the
  right sibling skill and gives cold-start loading order. Holds no facts of its
  own. **Load this first in a fresh session.**

## Knowledge & reference

- **lid-framework-reference** — Domain knowledge pack for the framework itself:
  the DeepProfiler → FeatureStratifier → FingerprintBuilder → MKBStore →
  SimilarityEngine pipeline, S1–S6 strata, the distance / IDW /
  consensus-confidence math, the 17-corpus / 24-language design, and headline
  numbers. Load when reasoning about, writing about, or defending the framework.

- **thesis-estate-and-env** — The "where is everything and how do I run it"
  runbook: locating the repo / LaTeX / experiments, which chapter files are
  canonical, running Python / analysis scripts / dashboard in the `thesis_final`
  conda env, building the PDF, and finding artifacts (mkb.pkl,
  validation_report.json, profiles/, split dirs, benchmark_metadata.json).

## Writing & change management

- **thesis-change-control** — The gatekeeper. Decides *how* a change may land:
  drafts-first workflow, which changes need a saved artifact, which tables must
  be regenerated, examiner-safe language, and git discipline (feature branch,
  commit only when asked, no amend / force-push). **Load before editing
  anything.**

- **thesis-writing-and-style** — LaTeX house style: department formatting
  checklist, `\mysection` / boxed-tabular conventions, the terminology canon
  (framework vs toolkit, corpus vs dataset, Meta-Knowledge Base, strata S1–S6).
  Load when producing or changing `.tex` prose, tables, captions, or front matter.

- **thesis-voice-restoration** — Makes prose read as the author wrote it rather
  than an LLM. Holds the voice fingerprint measured from his 2024 Skripsie, the
  2026-08-03 baseline audit of all six chapters, the rewrite target list, and
  the protected-elements rule (headings and structure are frozen; body prose
  only). Supersedes the generic `/humanizer` skill inside the thesis estate.
  Load for "does this sound AI-written?", "restore my voice", or a de-AI pass.

- **evidence-standards** — Governs evidence *quality*: what counts as
  examiner-safe proof, which statistical methods are actually implemented in
  `analysis/*.py`, the six rules for admitting a result, and the hard claim
  ceiling on the confidence signal (never "calibrated"). Load **before** writing
  an evidential sentence, not after.

## Verification & review

- **artifact-verification-playbook** — Read-only recipes to trace any numeric
  claim to a saved artifact and re-derive it by running a command ("measure,
  don't eyeball"). For numbers like 2,726 features / 327 families / 63 PCs / 17
  datasets / 99.18% range capture / 0.0073 mean regret / 2/17 strict top-1.
  ⚠️ Validation figures were regenerated **2026-07-31** after the coverage-guard
  correction: `validation_report.json` and `validation_statistics.py` are
  superseded; the source of record is
  `analysis/reporting_measures_2026-07-21.json`, and the confidence-signal
  result is **retracted** (see thesis-claims-archaeology A-13).

- **thesis-claims-archaeology** — The settled-battles register: every claim
  found wrong and corrected (leave-one-out wording, feature counts, model-family
  counts, calibration language, EQ answers, review-era statistics), so you never
  re-fight a settled battle or resurrect a stale wrong version. Load before
  editing / reverting / quoting chapters, or when a number "looks familiar."

- **thesis-review-protocol** — Read-only four-voice examination panel (Chair +
  Methodology + Mathematics + Empirical) behind a VERIFIED /
  PLAUSIBLE-UNVERIFIED / PRESENTATION-ONLY verification gate. Load to review,
  examine, critique, or "mock-defend" the thesis or a chapter. Produces a
  critique; never edits thesis files.

## Defense & planning

- **examiner-defense-pack** — Oral-defense prep: Q&A crib and examiner
  simulation, tuned for an information-retrieval-expert examiner (IR-framed
  challenges like learned ranking, cosine vs Euclidean, TF-IDF, precision@k /
  MRR), each with a grounded strong answer, artifact evidence, honest
  concession, and a LOAD-BEARING / CONCEDE-GRACEFULLY marking.

- **dashboard-demo-runbook** — Runbook for launching and demonstrating the
  Streamlit explainer dashboard (`src/lid_toolkit/explainer/dashboard.py`):
  panel inventory, exact launch command, prerequisites, known failure modes with
  fixes, and a suggested oral-defense walkthrough.

- **thesis-completion-campaign** — The decision-gated plan from now to submission
  (2026-09-01): what's left, running the LLM baseline, the progress-report
  deadline (2026-07-31), adopting stratification drafts, closing consistency
  items, and the final re-review. The *what & when* — siblings are the *how*.

---

## The overall design

`thesis-index` routes; the middle skills each own one concern (framework facts,
environment, writing rules, evidence quality, verification, review, defense,
demo, planning); and every description explicitly says what *not* to use it for,
pointing to the correct sibling — so they compose without overlap.

### Typical loading order for common tasks

| Task | Load |
|------|------|
| Fresh session / "where do I start" | `thesis-index` |
| Edit a chapter | `thesis-change-control` → `thesis-writing-and-style` (+ `evidence-standards` if claims) |
| "Does this sound AI-written?" / voice pass | `thesis-voice-restoration` → `thesis-change-control` |
| Verify a number | `artifact-verification-playbook` |
| "Where does this number come from?" | `thesis-claims-archaeology` → `artifact-verification-playbook` |
| Review / mock-defend a chapter | `thesis-review-protocol` (after `thesis-claims-archaeology`) |
| Prep the viva | `examiner-defense-pack` |
| Run the live demo | `dashboard-demo-runbook` |
| "What's left before submission?" | `thesis-completion-campaign` |
| Find files / run things | `thesis-estate-and-env` |
