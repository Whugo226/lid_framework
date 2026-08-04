---
name: thesis-index
description: >-
  Router and one-page map for the LID-recommendation MEng thesis skill library
  (Werner Hugo, Stellenbosch, submission 2026-09-01). Load this FIRST in any
  fresh session that opens on this project — it maps the four-root estate and
  routes a task ("revise a chapter", "verify a number", "run a review",
  "regenerate a table", "prep the viva", "what's next before submission") to
  the exact sibling skill(s) to load, and gives the cold-start loading order.
  It is a dispatcher, not a knowledge base: it holds no framework facts,
  numbers, or procedures of its own — every real answer lives in a sibling.
  Smaller (Sonnet-class) models especially should load this before acting.
metadata:
  type: reference
---

# Thesis Skill Library — Index & Router

You are (re)entering work on an MEng thesis project with **zero conversation
memory**. This skill orients you and points you at the right sibling skill.
It contains no load-bearing facts of its own — do not answer thesis questions
from this file; load the sibling it names and answer from there.

**Project in one line:** "An Interactive Framework for Language Identification
Model Recommendation" — a Design-Science MEng thesis (Werner Hugo, Stellenbosch
University, supervisor Prof Mandla Gwetu). Submission **2026-09-01**; progress
report due **2026-07-31**; external examiner believed to be an
information-retrieval expert; target grade ≥75%.

**Golden rules that override any local guess (all siblings restate these):**
- Every number in prose must trace to a saved artifact. Never "eyeball" a figure.
- Never write "calibrated confidence" — the signal is a *consensus* measure.
- New material lands in `drafts/` first, never straight into `chapters/`.
- The estate is READ-ONLY except where a task explicitly authorises a write,
  and never via mutating git commands unless the user asks.
- Resolve canonical chapters from `thesis.tex`'s `\input` list — the
  `chapters/` folder contains 9 stale `.text` decoys.

---

## The estate (four roots, one Windows machine, verified 2026-07-12)

| Root | Path | What |
|---|---|---|
| Toolkit repo (git; skills live here) | `c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit` | package `src/`, `analysis/`, artifacts (`mkb.pkl`, `validation_report.json`, `profiles/`), `.claude/skills/`, `project_context/SESSION_FACTS_LEDGER.md` |
| Thesis LaTeX | `c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit` | `thesis.tex`, `chapters/`, `drafts/`, `appendices/`, `frontmatter/`, `thesis_feedback/`, `thesis_checklist/` |
| Experiments | `c:\Users\User\OneDrive\Masters\LID_experiments` | training/benchmarking scripts, split dirs `01a/01b/02/03`, `benchmark_metadata.json` |
| Research notes | `C:\Users\User\OneDrive\Masters\Thesis\deep-research` | reference-only Node/TS deep-research clone |

Full path/env/build detail → **thesis-estate-and-env**.
Session-learned facts, corrected claims, verified numbers →
`project_context/SESSION_FACTS_LEDGER.md` (a file, not a skill; the
archaeology/framework skills supersede it where they disagree).

---

## Task router — match your task, load the named skill(s)

| Your task | Load | Then also |
|---|---|---|
| Find a file / set up env / run a script or the build | **thesis-estate-and-env** | — |
| Understand how the framework works (pipeline, strata, math, results) | **lid-framework-reference** | — |
| Verify / trace a specific number to its artifact | **artifact-verification-playbook** | — |
| Check whether a claim was already corrected before touching it | **thesis-claims-archaeology** | — |
| Edit / add / reword / update ANYTHING (prose, table, number, code) | **thesis-change-control** (gate) | the how-to sibling it routes you to |
| Write / restyle LaTeX prose, tables, captions, front matter | **thesis-writing-and-style** | thesis-change-control |
| "Does this read as AI-written?" / restore my voice / humanise a chapter | **thesis-voice-restoration** | thesis-change-control |
| Decide if a NEW empirical claim is strong enough / examiner-safe | **evidence-standards** | — |
| Review / examine / mock-defend a chapter or the whole thesis | **thesis-review-protocol** | thesis-claims-archaeology (mandatory before re-review) |
| Prep for the oral defense (Q&A, examiner simulation) | **examiner-defense-pack** | dashboard-demo-runbook (for the live demo) |
| Run / demo the Streamlit dashboard | **dashboard-demo-runbook** | — |
| "What's next / what's left before submission?" / progress report / LLM baseline | **thesis-completion-campaign** | the gate-specific siblings it names |

If two rows apply, load both. If a task changes files, **thesis-change-control
is always in the set** — it is the gate every write passes through.

---

## Cold-start loading orders (common sessions)

- **"Continue the thesis / what's next":** thesis-index → thesis-completion-campaign
  → thesis-estate-and-env (as needed for commands). The campaign is the WHAT/WHEN;
  it routes you to the HOW siblings per gate.
- **"Revise chapter X":** thesis-index → thesis-claims-archaeology (don't reopen
  settled battles) → thesis-change-control → thesis-writing-and-style
  (+ lid-framework-reference if the edit touches framework facts/numbers).
- **"Review / re-review the thesis":** thesis-index → thesis-claims-archaeology
  → thesis-review-protocol (+ artifact-verification-playbook to check numbers).
- **"Prep the viva":** thesis-index → examiner-defense-pack → lid-framework-reference
  → dashboard-demo-runbook.
- **"Verify this number":** thesis-index → artifact-verification-playbook
  (+ thesis-claims-archaeology if you also need where it's stated in the .tex).
- **"Make it not sound AI-written":** thesis-index → thesis-voice-restoration
  → thesis-change-control. Do NOT load the generic /humanizer skill for thesis
  text; thesis-voice-restoration supersedes it and explains why.

---

## Skill inventory (13 incl. this router)

| Skill | One line |
|---|---|
| thesis-index | This router + estate map + loading orders. |
| thesis-estate-and-env | Where everything is; env, run commands, LaTeX build. |
| lid-framework-reference | How the framework works: pipeline, strata, math, results. |
| artifact-verification-playbook | Read-only recipes to trace any number to an artifact. |
| thesis-claims-archaeology | Settled battles: every corrected claim + re-check greps. |
| thesis-change-control | The gate for HOW any change may land. |
| thesis-writing-and-style | LaTeX house style + department checklist compliance. |
| thesis-voice-restoration | Author's voice fingerprint + de-AI rewrite pass (body prose only). |
| evidence-standards | What counts as examiner-safe proof for a new claim. |
| thesis-review-protocol | Grounded examination-panel review (read-only). |
| examiner-defense-pack | IR-tuned viva Q&A with concede/defend markings. |
| dashboard-demo-runbook | Launch + demo the Streamlit dashboard for the defense. |
| thesis-completion-campaign | Gated plan from 2026-07-12 to submission 2026-09-01. |

---

## When NOT to use this skill

Once you know which sibling you need (or you are already mid-task inside one),
you do not need the router. It is for orientation and dispatch only. Do not
cite it as a source for any fact — it deliberately holds none.

## Provenance and maintenance

- Estate map, dates, and the 11 siblings verified against disk 2026-07-12.
- Re-list the library: `ls "<toolkit repo>\.claude\skills"` — expect 13 dirs,
  each with a `SKILL.md`.
- If a sibling is renamed/added/removed, update the router table and the
  inventory here in the same change (this is the one file that must know the
  full roster). Keep it factless otherwise.
