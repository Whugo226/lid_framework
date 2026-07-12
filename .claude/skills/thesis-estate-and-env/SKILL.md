---
name: thesis-estate-and-env
description: >
  The "where is everything and how do I run it" runbook for Werner Hugo's MEng
  LID-recommendation thesis estate (four roots on one Windows machine). Load
  this FIRST in any session that needs to: locate the toolkit repo, thesis
  LaTeX folder, LID_experiments, or deep-research notes; resolve which chapter
  files are canonical (thesis.tex \input list vs the stale .text duplicates);
  run toolkit Python, analysis/ scripts, or the Streamlit dashboard in the
  thesis_final conda env; build the thesis PDF with pdflatex/latexmk; or find
  artifacts (mkb.pkl + backups, validation_report.json, profiles/, split dirs,
  benchmark_metadata.json). Do NOT load for: what the numbers mean or how the
  framework works (use lid-framework-reference), verifying a numeric claim
  against an artifact (artifact-verification-playbook), editing rules and
  drafts-first workflow (thesis-change-control), or a full dashboard demo
  script (dashboard-demo-runbook).
---

# Thesis Estate and Environment Runbook

All paths verified by listing/running on **2026-07-12**. This machine is
Windows 10, PowerShell 5.1 (no `&&` operator — chain with `;` or
`if ($?) { ... }`). Git Bash is also available.

## 1. The four-root estate map

Four roots, one machine, all under OneDrive (beware sync lag on freshly
written files).

| Root | Absolute path | What lives there |
|---|---|---|
| **Toolkit repo** (git, primary; skills live here) | `C:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit` | The `lid_toolkit` Python package, fitted MKB artifacts, analysis scripts, validation reports, session ledger, `.claude\skills\` |
| **Experiments** (git) | `C:\Users\User\OneDrive\Masters\LID_experiments` | Dataset splits, model training runs, cross-benchmark result trees (`benchmark_metadata.json` files) |
| **Thesis** (git) | `C:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit` | Stellenbosch `stb-thesis` LaTeX project: `thesis.tex`, chapters, drafts, feedback, checklist, compiled `thesis.pdf` |
| **Research notes** (git) | `C:\Users\User\OneDrive\Masters\Thesis\deep-research` | A Node/TypeScript "Open Deep Research" agent clone (src/*.ts, `report.md` output). Reference material only — not part of the thesis build |

### Key subpaths per root

**Toolkit repo** (`...\Python\toolkit_dev\lid_toolkit`):
- `src\lid_toolkit\` — the package (`recommender\`, `explainer\`, `models\`, `data\`, `logic\`, `cli.py`, `facade.py`)
- `analysis\` — one-off analysis/ablation scripts + their output JSONs and generated LaTeX
- `profiles\` — 17 fitted dataset-profile `.pkl` files (+ 1 `.excluded`)
- `project_context\` — includes `SESSION_FACTS_LEDGER.md` (session knowledge snapshot; the skill library supersedes it)
- `mkb.pkl` (repo root) — current fitted Model Knowledge Base; dated backups alongside (see §5)
- `.claude\skills\` — this skill library

**LID_experiments** (`...\Masters\LID_experiments`):
- `datasets\` — the four-way per-corpus row splits (see §5) + ingest/cleaning/split-generator scripts
- `model_benchmarking_knowledge\` — cross-benchmark on the 01b splits (source of MKB performance records)
- `model_benchmarking_evaluation\` — cross-benchmark on the 02 splits
- `model_benchmarking_validation\` — configs + HPC submit scripts for the 03 splits (`README.md`, `config_cross_benchmark_validation.yaml`; no result trees here as of 2026-07-12)
- `model_training\`, `model_training_results\`, `off_the_shelf_models\`
- Directories suffixed `_old`, `_old_copy`, `_safety` are superseded snapshots — do not read numbers from them.

**Thesis** (`...\Thesis\Thesis Template Legit`):
- `thesis.tex` — the build entry point and the ONLY authority on canonical scope (§2)
- `chapters\` — live `.tex` chapters AND stale `.text` duplicates (trap — §2)
- `drafts\` — staging area for new material (never write new sections straight into `chapters\`; see thesis-change-control)
- `appendices\`, `frontmatter\`, `figures\`
- `thesis_feedback\` — supervisor feedback (`thesis_feedback.md`, `chapter_3_feedback_updated.md`, `Chapter_3_feedback.md`, `thesis_structure_template.md`)
- `thesis_checklist\` — `2026 Thesis Checklist_grammarlayout.pdf` (department submission checklist) and `WHugo_progress_report_signedMG25Jul2025.pdf` (template for the progress report due 2026-07-31)
- `references.bib` — the live bibliography (`thesis.tex` says `\bibliography{references}`). `my-library.bib` (8.9 MB) is a raw library export, NOT the compiled bib.

**deep-research** (`...\Thesis\deep-research`): `src\` (TypeScript agent), `report.md`. No thesis artifacts live here.

## 2. Canonical-scope resolution (do this before touching any chapter)

**Never trust a chapter file to be live.** The only authority is the `\input`
list in `thesis.tex`. Verified 2026-07-12, the canonical body is:

| Chapter | Live file (in `chapters\`) |
|---|---|
| Ch1 Introduction | `introduction_chapter.tex` |
| Ch2 Scoping review | `scoping_review_chapter.tex` |
| Ch3 Methodology | `methodology_chapter.tex` |
| Ch4 Design & implementation | `design_and_implementation.tex` |
| Ch5 Demonstration & evaluation | `demonstration_and_evaluation.tex` |
| Ch6 Conclusion | `conclusion.tex` |
| Appendices | `appendices\appendices.tex` → `\input{appendices/an_appendix}` |
| Front matter | `frontmatter\` (title_page, dedication, acknowledgements, declaration, abstract, nomenclature, defined_acronyms, definitions) |

Re-derive at any time:

```powershell
Select-String -Path "C:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\thesis.tex" -Pattern '\\input'
```

### The stale `.text` duplicate trap

`chapters\` contains **9 stale files with extension `.text`** (not `.tex` —
they never compile, but they are near-duplicates of live chapters and have
burned sessions that edited a dead file). Enumerated 2026-07-12:

- `experimental_design_and_methodology.text`
- `experimental_design_and_methodology1.text`
- `introduction_chapter.text`
- `methodology.text`
- `natural_lang_proc.text`
- `scoping_review_chapter.text`
- `scoping_review_old.text`
- `toolkit_architecture.text`
- `verification_and_validation.text`

Rules: (a) never edit a `.text` file; (b) never grep-and-fix across
`chapters\` without excluding `*.text` — stale files still contain retired
labels (e.g. `chap:experimental_design`) and retired claims, and matches in
them are NOT bugs; (c) when checking whether a wrong claim is "fixed", filter
to `--include="*.tex"`.

### Other scope dirs

- `drafts\` — new material staged here first (as of 2026-07-12:
  `stratum_bridging_table.tex`, `stratum_audit_appendix.tex` — both compile
  clean standalone, neither yet `\input` into the thesis). Adoption rules:
  see thesis-change-control.
- `appendices\an_appendix.tex` is the single live appendix file.
- `thesis_feedback\` and `thesis_checklist\` are read-only reference inputs.

## 3. Python environment and running things

**Env:** conda env `thesis_final` under **miniconda3, NOT anaconda3** (the
anaconda3 path does not exist — verified 2026-07-12).

```powershell
# The interpreter (Python 3.10.19, verified):
C:\Users\User\miniconda3\envs\thesis_final\python.exe --version
```

`lid_toolkit` is importable from anywhere in this env (it resolves to the
repo's `src\lid_toolkit\` — src-layout install), **but always run from the
repo root anyway**: `mkb.pkl`, `profiles\`, and analysis outputs are
addressed by relative path.

```powershell
Set-Location "C:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit"

# Sanity check (verified 2026-07-12 — prints "lid_toolkit OK"):
C:\Users\User\miniconda3\envs\thesis_final\python.exe -c "import lid_toolkit; print('lid_toolkit OK')"

# Load the current MKB (verified: MKBStore, 17 datasets):
C:\Users\User\miniconda3\envs\thesis_final\python.exe -c "import pickle; m = pickle.load(open('mkb.pkl','rb')); print(type(m).__name__, len(m.datasets))"

# Run an analysis script (example — regenerates stratum audit tables):
C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\stratum_audit.py
```

MKB API gotcha (one line here; details in artifact-verification-playbook):
`mkb.datasets` is a **list of names** — use `mkb.get_entry(name)`, not dict
indexing.

### Streamlit dashboard

File verified to exist:
`C:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit\src\lid_toolkit\explainer\dashboard.py`
(streamlit 1.58.0 is installed in the env). Launch from the repo root:

```powershell
Set-Location "C:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit"
C:\Users\User\miniconda3\envs\thesis_final\python.exe -m streamlit run src\lid_toolkit\explainer\dashboard.py
```

(Equivalent to `streamlit run src/lid_toolkit/explainer/dashboard.py` with the
env activated.) It blocks the terminal and opens a browser tab — run in a
background shell if you need to keep working. For the demo walkthrough
itself, use dashboard-demo-runbook.

### Git context (toolkit repo)

Branch `feature/api-dashboard-intergration` — **the typo "intergration" is in
the real branch name**; do not "fix" it. Main branch: `main`.

## 4. LaTeX build

Toolchain verified 2026-07-12: **MiKTeX 25.3** — `pdflatex` is MiKTeX-pdfTeX
4.21; `latexmk` 4.86a; `bibtex` (MiKTeX-BibTeX 4.1) is the bibliography
engine actually used (per `thesis.blg`), not biber.

Build from the thesis root. `.latexmkrc` already configures
`pdflatex -synctex=1 -interaction=nonstopmode -file-line-error`:

```powershell
Set-Location "C:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit"
latexmk -pdf thesis.tex
```

Manual equivalent (when latexmk misbehaves):

```powershell
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error thesis.tex
bibtex thesis
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error thesis.tex
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error thesis.tex
```

(Command form verified against `.latexmkrc` and existing build artifacts; a
full build was not re-run on 2026-07-12 to avoid touching aux files.)

- **Multi-pass is mandatory:** `longtable` needs ~3 passes to converge column
  widths. Convergence check — this must produce NO matches:
  `Select-String -Path thesis.log -Pattern "Table widths have changed"`.
  If it matches, run pdflatex again.
- **Outputs land in the thesis root itself** (no build subdir): `thesis.pdf`,
  `thesis.aux`, `thesis.bbl`, `thesis.log`, `thesis.toc`, `thesis.lof`,
  `thesis.lot`, `thesis.out`, `thesis.synctex.gz`.
- `longtable` and `multicol` are loaded via `imports.tex` (ledger: lines
  ~285 / ~126) — do not re-`\usepackage` them in drafts.
- `poppler`/`pdftoppm` is NOT installed (ledger-verified 2026-07-12): no
  per-page PDF-to-image rendering; whole-file PDF reading works.
- House style (boxed tabulars, `\mysection{X}{X}`, `[H]` floats, etc.):
  see thesis-writing-and-style.

## 5. Artifact inventory (verified 2026-07-12)

### MKB pickles (toolkit repo root)

| File | Size (bytes) | mtime | Status |
|---|---|---|---|
| `mkb.pkl` | 8,526,902 | 2026-07-03 | **CURRENT** — loads as `MKBStore`, 17 datasets |
| `mkb_backup_with_librispeech_2026-07-03.pkl` | 8,708,125 | May 14 | backup (18-dataset variant incl. librispeech) |
| `mkb_old_may14.pkl` | 8,545,857 | May 5 | superseded |
| `mkb_old_may5.pkl` | 8,037,652 | Apr 28 | superseded |
| `mkb_old_apr28.pkl` | 8,037,652 | Apr 28 | superseded |

Naming convention: `mkb_old_<date>` = the mkb that was replaced around that
date. Only ever load `mkb.pkl` for live numbers.

### Validation reports (toolkit repo root)

- `validation_report.json` (228,096 B, May 14) + `validation_report.md` —
  current. `validation_report_old_apr28/apr30/may2/may14.*` are superseded.
- `validate_recommendations.py` (generator) and
  `validate_recommendations_validation.py` (Jul 10 variant for the 03
  validation splits).

### profiles\ (toolkit repo)

17 active fitted dataset profiles + 1 excluded (18 files): `OpenLID-v2`,
`amazon_reviews_multi`, `europarl`,
`exorde-social-media-december-2024-week1`, `flores_plus`,
`language-identification`, `massive`, `mmarco`, `multi_eurlex`,
`multilingual_cc_news`, `multilingual_toxicity_dataset`, `stsb_multi_mt`,
`tweet_sentiment_multilingual`, `tydiqa`, `wikipedia`, `xlsum`, `xnli`
(each `.pkl`), plus `librispeech_asr.pkl.excluded` (deliberately excluded —
the `.excluded` suffix keeps it out of loads). The 17 active profiles match
the 17 MKB datasets. `profiles_old_*` dirs are superseded snapshots.

### analysis\ outputs (toolkit repo)

- `analysis\stratum_audit.py` → `analysis\stratum_audit_tables.tex`
  (machine-generated LaTeX — regenerate, never hand-edit)
- `analysis\walkthrough_results.json` (dashboard walkthrough data, Jul 10)
- `analysis\bench_results.json` (stanza-vs-spaCy timing),
  `analysis\r13_timing.json`
- `random_baseline_mc_results.json` sits in the **repo root**, not analysis\
- Scripts present, no saved output found as of 2026-07-12:
  `llm_baseline.py` (decision = RUN, still pending), `ablation_k.py`,
  `corpus_eda.py`, `random_baseline_mc.py`, `validation_statistics.py`,
  `benchmark_landscape.py`, `benchmark_stanza_vs_spacy.py`,
  `time_deepprofiler_e2e.py`, `walkthrough_demo.py`

### LID_experiments split dirs

`C:\Users\User\OneDrive\Masters\LID_experiments\datasets\` — four-way
per-corpus row split (seed 42), each with a `_cleaned` variant:

| Dir | Role |
|---|---|
| `01a_knowledge_train_50` | 50% — training pool |
| `01b_knowledge_benchmark_20` | 20% — cross-benchmark → MKB performance records |
| `02_evaluation_15` | 15% — evaluation |
| `03_validation_15` | 15% — held-out validation |

### benchmark_metadata.json layout

Path pattern (example verified 2026-07-12):

```
model_benchmarking_evaluation\<model>\<dataset>\<model>_<dataset>\benchmark_metadata.json
e.g. C:\Users\User\OneDrive\Masters\LID_experiments\model_benchmarking_evaluation\cld3\europarl\cld3_europarl\benchmark_metadata.json
```

Model dirs: `cld3`, `fasttext`, `fasttext_off_the_shelf`,
`logistic_regression`, `naive_bayes`, `xlm_v_base`. Same tree shape under
`model_benchmarking_knowledge\`. Verified schema:

```json
{
  "dataset": "europarl",
  "model": "cld3",
  "metrics": {
    "accuracy": 0.988439, "f1_macro": 0.538071, "f1_weighted": 0.993367,
    "precision_macro": ..., "precision_weighted": ..., "recall_macro": ...,
    "recall_weighted": ..., "inference_time_total_s": ...,
    "inference_time_ms_per_sample": ..., "throughput_samples_per_sec": ...,
    "n_samples": 389748
  }
}
```

## 6. When NOT to use this skill

- Interpreting framework numbers/design (strata, regret, baselines) →
  **lid-framework-reference**
- Tracing a thesis claim to its artifact → **thesis-claims-archaeology** /
  **artifact-verification-playbook**
- Editing workflow, drafts-first rules, review read-only rules →
  **thesis-change-control**
- Running the demo narrative on the dashboard → **dashboard-demo-runbook**
- LaTeX house style / prose conventions → **thesis-writing-and-style**

## Provenance and maintenance

All facts above verified 2026-07-12 by this authoring session (listings, file
reads, and read-only runs), except: `poppler` absence, `imports.tex` line
numbers, and the ~3-pass longtable behaviour, which are from the session
ledger (`project_context\SESSION_FACTS_LEDGER.md`, itself dated ✅ 2026-07-12);
and the full pdflatex build, which was not re-run (command form taken from
`.latexmkrc`). Volatile facts and one-line re-verification commands:

- Four roots still exist: `ls` each path in §1.
- Canonical chapters: `Select-String thesis.tex -Pattern '\\input'` (§2).
- Stale `.text` census: `Get-ChildItem "...\Thesis Template Legit\chapters\*.text"` — 9 files on 2026-07-12.
- Env: `C:\Users\User\miniconda3\envs\thesis_final\python.exe --version` → Python 3.10.19.
- Package + MKB: the two one-liners in §3 → "lid_toolkit OK" / "MKBStore 17".
- Dashboard file: `Test-Path "...\lid_toolkit\src\lid_toolkit\explainer\dashboard.py"` → True; streamlit 1.58.0.
- LaTeX: `pdflatex --version` → MiKTeX-pdfTeX 4.21 (MiKTeX 25.3); `latexmk --version` → 4.86a.
- Artifacts: `ls ...\lid_toolkit\mkb*.pkl` (5 files), `ls ...\lid_toolkit\profiles` (18 entries), the example `benchmark_metadata.json` path in §5.
- Git branch (typo is real): `git -C "...\lid_toolkit" branch --show-current` → `feature/api-dashboard-intergration`.
