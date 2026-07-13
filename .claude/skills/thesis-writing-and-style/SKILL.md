---
name: thesis-writing-and-style
description: >-
  Load this skill whenever writing, editing, or reviewing LaTeX text for the
  MEng thesis "An Interactive Framework for Language Identification Model
  Recommendation" (Stellenbosch University, Werner Hugo, submission
  2026-09-01) — i.e., any task that produces or changes .tex prose, tables,
  figures, captions, front matter, or appendices, or that checks the thesis
  against the 2026 department formatting checklist. It encodes: the mandatory
  and recommended department requirements, the house LaTeX conventions
  (\mysection, boxed tabulars, appendix pattern, \candidatetodo, bibliography
  setup), the terminology canon (framework vs toolkit, corpus vs dataset,
  Meta-Knowledge Base, strata S1–S6), and a dated current-state audit. Do NOT
  load it for: deciding WHERE new material lands or git workflow (use
  thesis-change-control), verifying numeric claims behind prose (use
  thesis-claims-archaeology / artifact-verification-playbook), running the
  review panel (thesis-review-protocol), prioritising submission work
  (thesis-completion-campaign), or environment/build troubleshooting
  (thesis-estate-and-env).
---

# Thesis Writing and Style — Stellenbosch MEng, 2026

How thesis text and LaTeX must be written in this project. Everything below
was verified against the actual files on 2026-07-12 unless marked otherwise.

**Thesis root:** `c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit`
**Canonical chapter set** = the `\input` list in `thesis.tex` (lines 63–72):
`chapters/introduction_chapter.tex`, `chapters/scoping_review_chapter.tex`,
`chapters/methodology_chapter.tex`, `chapters/design_and_implementation.tex`,
`chapters/demonstration_and_evaluation.tex`, `chapters/conclusion.tex`, plus
`appendices/appendices.tex` → `appendices/an_appendix.tex`.
⚠️ The `chapters/` dir also contains stale `.text` near-duplicates. NEVER
edit a `.text` file; always resolve scope from `thesis.tex` first.

**Calibration rule (user-stated):** this is a Master's thesis, NOT a journal
submission or technical manual. Do not over-polish or over-flag style.
**Examiner-safety rule:** never write "calibrated confidence" — the
confidence score is a *consensus signal*; calibration evidence is directional
only (p = 0.022). The thesis's own Ch3/Ch5 disclaimers are the ceiling.

## 1. Department requirements — 2026 checklist

Source: `c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\thesis_checklist\2026 Thesis Checklist_grammarlayout.pdf`
(read in full 2026-07-12). "Status" = state of the thesis as measured
2026-07-12 (PDF built 2026-07-11, 183 pages total).

### Mandatory items

| # | Requirement | Status 2026-07-12 |
|---|---|---|
| M1 | Soft copy submitted as Adobe PDF | ✅ pdflatex build produces `thesis.pdf` |
| M2 | Page i, top third: Title | Via `\TitlePage` (class macro, `frontmatter/title_page.tex`) — visually confirm in PDF |
| M3 | Page i: author full names + surname below title | `thesis.tex:27` `\author{Werner Hugo}{Werner Hugo}` |
| M4 | Page i, middle: exact formula "Thesis presented in partial fulfilment of the requirements for the degree of Master of Engineering (Industrial Engineering/ Engineering Management) in the Faculty of Engineering at Stellenbosch University" | Driven by `\degree{MEng (Industrial Engineering)}{Master of Engineering (Industrial Engineering)}` + `\faculty{Faculty of Engineering}` (`thesis.tex:29–30`) — visually confirm rendered wording |
| M5 | Page i, bottom centred: Supervisor name + graduation month/year (e.g. March 2027) | `\supervisor[c]{Prof.\ Mandla Gwetu}` (`thesis.tex:31`). ⚠️ No `\setdate{month}{year}` call found — class defaults to COMPILE date (`stb-thesis.cls:481` `\STB@year=\number\year`). Set explicitly before submission (planned graduation December 2026). |
| M6 | Page ii upper half: DECLARATION with exact wording; date only, no signature | Rendered by `\DeclarationPage` (`stb-thesis.cls:521`); wording lives in the class (`\ThesisDeclare`). ⚠️ `frontmatter/declaration.tex:1` has stale `\DeclarationDate{10 May 2024}` — update at submission. Verify rendered wording letter-for-letter against the checklist PDF. |
| M7 | Page ii lower half: "Copyright ©2027 Stellenbosch University All rights reserved" (graduation-ceremony year) | Printed by class from `\STB@year` (`stb-thesis.cls:539`) = compile year unless `\setdate` is called. Confirm required year (Dec 2026 grad → likely ©2026; checklist example uses ©2027 for March 2027) with supervisor, then set via `\setdate`. |
| M8 | Page iii: English abstract ≤500 words, heading "Abstract" | ✅ 322 words, heading `\chapter*{Abstract}`, starts roman iii (`thesis.toc`) |
| M9 | Page iv: Afrikaans abstract ≤500 words, heading "Opsomming" OR "Uittreksel", quality-checked Afrikaans | ✅ 275 words, heading "Uittreksel" (`frontmatter/abstract.tex:16`). Note: falls on roman v (Abstract spans iii–iv). ⚠️ Afrikaans quality check still needed (checklist: "check the quality of the Afrikaans carefully"). |
| M10 | ToC: all entries with page numbers; appendices with titles listed | ✅ `thesis.toc` lists Appendices A–D with titles and pages |
| M11 | List of figures / List of tables with page numbers | ✅ present (`thesis.tex:52–55`) |
| M12 | Consistent heading capitalisation | Enforced via `\MFUnocap`/`\Addlcwords` (`thesis.tex:5–13`) + titlecaps — spot-check per chapter |
| M13 | No page number on title page | Class handles; roman numbering starts after dedication (`thesis.tex:42`) |
| M14 | Declaration on page i or ii | Acknowledgements = i (`thesis.toc`), Declaration follows → ii. ✅ (order differs from checklist's optional-pages suggestion: Ack/Dedication currently precede Declaration/Abstract — both optional, allowed) |
| M15 | Introduction starts on page 1 | ✅ `thesis.toc`: Chapter 1 Introduction = page 1 |
| M16 | Captions: "Table x:" ABOVE tables; "Fig x:" BELOW figures | ✅ audited 2026-07-12: all 20 table envs caption-above, all 20 figures caption-below (see §3) |
| M17 | Margins single-sided 2 cm left/right, 2 cm top/bottom | ❌ NON-COMPLIANT: `imports.tex:2` = `left=3cm,right=2cm,top=2.5cm,bottom=2.5cm`. Decision needed (report, don't silently change — a margin change reflows the whole document). |

### Recommended items

| # | Recommendation | Status 2026-07-12 |
|---|---|---|
| R1 | Headings before Introduction unnumbered | ✅ front matter uses `\chapter*` |
| R2 | Introduction = Chapter 1; numbering 1, 1.1, … | ✅ |
| R3 | First appendix = Appendix A; numbering A.1 | ✅ Appendices A–D |
| R4 | No section with only one sub-section | Not audited — check during final pass |
| R5 | ≤1 paragraph before the first subheading | Not audited — check during final pass |
| R6 | Appendix pages continue body numbering or A.1… | ✅ continue body numbering (App. A = p. 133) |
| R7 | Equation numbers | Present where used |
| R8 | Chapter-based caption numbers (Fig 2.1, Table 4.1) | ✅ default class behaviour |
| R9 | Graphs: no chart title (caption explains) | Not audited per-figure |
| R10 | One reference style, consistent (IEEE = order of use) | ✅ natbib numeric + IEEEtranN (see §2) |
| R11 | Hard space between number and unit (`10~ms`) | Apply in new text; not retro-audited |
| R12 | Physical-quantity symbols in italics | Standard math mode — apply in new text |
| R13 | Figure text ≥10 pt | Check regenerated figures |
| R14 | Core < 150 pages (MEng R) | ✅ core Ch1–Ch6 = pages 1–119 (References at 120); total PDF 183 pp |
| R15 | Professional language editing + proof of editing | ❗ Not yet arranged (2026-07-12). Budget lead time before 2026-09-01. |

## 2. House LaTeX conventions (all verified in the files)

| Convention | Definition / evidence | Usage rule |
|---|---|---|
| `\mysection{X}{Y}` / `\mysubsection{X}{Y}` / `\mysubsubsection{X}{Y}` | Defined `imports.tex:444–451 / :436–443 / :428–435`. Arg 1 = short (ToC/header) title, arg 2 = displayed title; both usually identical. 133 uses across chapters. | ALWAYS use these instead of `\section`/`\subsection` in chapters — they manage running-header marks. |
| `\mychapter{short}{title}{subtitle}` | `imports.tex:452–458` | Chapter openings in chapters use it (subtitle line under rule). |
| Boxed tabular | `\begin{tabular}{|l|c|c|}` style with `\hline` after EVERY row; 16 boxed tabulars in chapters. Helper `\mytable` (centering + `\small` + arraystretch 1.2) at `imports.tex:289–294`. | Match this style for any new table; do not introduce booktabs-style open tables in chapters. |
| `[H]` floats | 39 `\begin{table}[H]`/`\begin{figure}[H]` in chapters ([H] provided via `float` loaded by `algorithm`, `imports.tex:348`) | Default float spec is `[H]` — place floats exactly where written. |
| Wide tables | `\begin{small}` wrapper (14 uses, e.g. `appendices/an_appendix.tex:53`) | Wrap wide tables in `\begin{small}…\end{small}`, keep boxed style. |
| `longtable` | Loaded `imports.tex:285` (+`ltcaption` :286, `multicol` :126). 8 standalone longtables. Caption goes in the longtable header (first rows) → above, checklist-compliant. | Use for multi-page tables; pdflatex needs ~3 passes to converge widths (log: "Table widths have changed"). |
| Appendix chapter pattern | `appendices/an_appendix.tex:1–2`: `\chapter{Title}{}` (note trailing empty group) then `\makeatletter\@mkboth{}{Appendix}\makeatother`, then `\label{appen:...}` | Copy this three-line pattern verbatim for every new appendix chapter. Labels use the `appen:` prefix. |
| `\candidatetodo{...}` | Defined `thesis.tex:21`: `\newcommand{\candidatetodo}[1]{\todo[color=candidatecolor]{Candidate: #1}}` (todonotes margin note, blue). Sibling `\revtodo` (green, reviewer) at `thesis.tex:20`. | Semantics: an OPEN author TODO. Count must be ZERO at submission. Add one whenever you leave known-incomplete text; never delete one without doing (or consciously waiving) the task. |
| Bibliography | `imports.tex:398–399`: `\usepackage[square,numbers,compress,sort]{natbib}` + `\bibliographystyle{IEEEtranN}`; `thesis.tex:77–80`: `\chapter*{References}` + `\renewcommand{\bibsection}{}` + `\bibliography{references}` → `references.bib` in thesis root | Numeric [n] citations via `\cite{...}` (IEEE-style, natbib-compatible). Keep one style; keys follow the existing zotero-style pattern (`beyerWhenNearestNeighbor1999`). |
| Captions | `caption` package `[margin=\the\parindent,small,bf,rm]` (`imports.tex:16`) → bold "Table 4.1:" label | Just `\caption{...}` + `\label{...}`; placement per §1 M16. |
| Cross-refs | `hyperref` (linktocpage) + `cleveref` loaded (`imports.tex:370, :579`); dominant idiom in chapters is `Section~\ref{...}` / `Table~\ref{...}` / `Chapter~\ref{...}` | Follow the `Word~\ref{}` idiom. Label prefixes in use: `chap:`, `sec:`, `subsec:`, `fig:`, `tab:`, `appen:`. |
| Acronyms | `acro` package; definitions in `frontmatter/defined_acronyms.tex` (e.g. MKB at :342–345). `\ac{...}` used in Ch3/Ch4 (8 each); other chapters often write expanded forms literally. | For a new acronym: declare it in `defined_acronyms.tex`, then `\ac{KEY}` at first use per chapter (`\acresetall` runs between chapters, `thesis.tex`). |
| Class & front matter | `stb-thesis` class, option `masters-t` (`thesis.tex:1`). Title page = `\TitlePage`; declaration = `\DeclarationDate{...}` + `\DeclarationPage` (`frontmatter/declaration.tex`). | Do not hand-build title/declaration pages; set the class macros. |
| Draft-edit macros | `\reviewer{}`, `\candidate{}` colour macros (`thesis.tex:18–19`) | Working-draft markup only; must not survive to submission. |

## 3. Current-state audit — dated observations (2026-07-12)

For thesis-completion-campaign to act on. PDF measured: `thesis.pdf` built
2026-07-11, 183 pages.

1. **Abstract word counts** (from `frontmatter/abstract.tex`, LaTeX commands
   stripped): English Abstract = **322 words**, Uittreksel = **275 words**.
   Both within the 500-word mandatory limit, with headroom for the pending
   EQ3 additions.
2. **Caption placement**: audited ALL chapters + appendix programmatically —
   20/20 table environments have the caption above the tabular, 20/20 figure
   environments have the caption below `\includegraphics`, 0 violations.
   8 standalone longtables carry captions in their headers (above). COMPLIANT.
3. **Live `\candidatetodo` count = 5** (plus 2 commented-out). Count robustly
   with `grep -rnE '\candidatetodo' chapters/*.tex | grep -vE '^[^:]*:[0-9]+:[[:space:]]*%'`
   — the naive `^[^%]*\candidatetodo` form under-counts because it breaks on
   lines containing an escaped `\%` (e.g. demonstration:117's "95\%"). Live:
   - `chapters/scoping_review_chapter.tex:108` — verify Scoping Review A
     search string against original database exports ("LID" repeated twice).
   - `chapters/methodology_chapter.tex:209` — double-check Beyer & Aggarwal
     papers (concentration-of-measure citations).
   - `chapters/demonstration_and_evaluation.tex:117` — add LLM-baseline row
     to `tab:baseline_comparison` + validation-split confirmatory subsection.
   - `chapters/conclusion.tex:55` — same two EQ3 pending items (LLM baseline,
     validation-split results).
   - `chapters/conclusion.tex:114` — remove "LLM comparator outstanding"
     clause once the LLM baseline is run.
   - (commented, not live — leave or delete: `methodology_chapter.tex:142`
     justify-k=3 note; `methodology_chapter.tex:170` model-vs-instance
     redundancy consolidation.)
4. **Margins non-compliant** (M17): `imports.tex:2` sets 3/2/2.5/2.5 cm vs
   mandatory 2 cm all round. Changing this reflows everything — decide once,
   late, then re-check page counts and float placement.
5. **Title-page date / copyright year not pinned**: no `\setdate` call →
   both default to compile date. Set before submission (M5, M7).
6. **Stale declaration date**: `frontmatter/declaration.tex:1` =
   `\DeclarationDate{10 May 2024}`.
7. **Student number**: `thesis.tex:28` `\Studentnumber{2516726}` (7 digits)
   vs actual student number 25167626 (8 digits) — verify and fix if the
   macro is rendered anywhere.
8. **Core page count** = 119 pages (Ch1 p.1 → References p.120) — under the
   recommended 150.
9. **Professional editing** (R15) not yet arranged; proof of editing is a
   checklist item.

## 4. Terminology canon (majority current usage, counted 2026-07-12)

Counts are case-insensitive whole-word matches across the six compiled
chapter .tex files.

| Concept | Canonical form | Evidence / rule |
|---|---|---|
| The artifact | **framework** (156 uses; also in the thesis title) | "toolkit" (11 uses, Ch1/Ch2 + abstract) is reserved for the concrete Python package (`lid_toolkit`) as an implementation of the framework. Never interchange within a paragraph. |
| Extracted characteristics | **meta-feature** (hyphenated; 46 uses; zero "metafeature"/"meta feature") | Plain "feature" is fine for the 2,726 raw columns once context is set; "meta-feature" when contrasting with the LID models' own input features. |
| Source text collections vs experiment units | **corpus/corpora** for source collections ("17 multilingual benchmark corpora"); **dataset** for partitioned experiment units ("17 held-out evaluation datasets", "dataset fingerprint") | Both live (corpora 133, datasets 209) — the distinction is deliberate; preserve it. |
| Knowledge store | **Meta-Knowledge Base (MKB)** — title case | Matches the acro definition (`frontmatter/defined_acronyms.tex:342–345`) and majority usage (19 title-case vs 11 lowercase). ⚠️ Known inconsistency: Ch1 (`introduction_chapter.tex`) mostly uses lowercase "meta-knowledge base" — harmonise toward title case during the final pass. |
| Strata | **"five continuous strata (S1–S5) and one categorical stratum (S6)"** (`conclusion.tex:34`, `design_and_implementation.tex:18`) | Names: S1 Morphological Richness · S2 Lexical Diversity · S3 Structural/Syntactic · S4 Information-Theoretic · S5 Cross-Level Cohesion · S6 Categorical Typological Block. Abstract's "six … feature strata" is the count of all six. Use "S<n>" codes after first spelled-out mention. |
| Confidence output | **consensus(-based) confidence score/signal** | NEVER "calibrated confidence" (examiner-safety rule; see header). |
| Validation protocol | **held-out sample validation** (per-corpus row splits, disjoint) | NEVER "leave-one-out validation" — settled battle CC-1; the only legitimate "leave-one-out" is the stratum-weight correlation analysis at `design_and_implementation.tex:331`. |
| Model families | **three trained families (six configurations) + three off-the-shelf zero-shot** | Never "five model families" (settled battle CC-4). |
| Feature count | **2,726 core features (327 of Lingualyzer's 351 base measures)** | Never 3,066 (settled battle CC-5). |

## 5. Locator discipline

Every finding, fix instruction, or edit report MUST cite:
**chapter + section label + file:line**, e.g.
`Ch4 §Feature Stratification (subsec ref) — chapters/design_and_implementation.tex:226`.
Absolute paths when the reader may be a fresh session. Reviews are read-only
(finding + fix + locator, no edits) — see thesis-change-control for where
new material lands (`drafts/`, never directly `chapters/`).

## 6. When NOT to use this skill

- Choosing where new content lands, branch/commit workflow, or the stale
  `.text` file hazard in depth → **thesis-change-control**.
- Verifying or re-deriving any NUMBER before it enters prose →
  **thesis-claims-archaeology** and **artifact-verification-playbook**.
- Running or re-running the examination-panel review → **thesis-review-protocol**.
- What evidence a claim needs before it is written at all → **evidence-standards**.
- Prioritising the submission to-do list (this skill's §3 feeds it) →
  **thesis-completion-campaign**.
- Python/conda/MiKTeX environment issues, compile loops → **thesis-estate-and-env**.
- Framework/architecture facts (module names, stratum contents, results) →
  **lid-framework-reference**.

## Provenance and maintenance

All facts date-stamped **2026-07-12**; measured against `thesis.pdf` built
2026-07-11 and the .tex sources at that date. Volatile items: word counts,
candidatetodo count, page counts, margin setting, terminology counts.

Re-verification one-liners (Git Bash, from the thesis root
`c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit`):

- Abstract word counts: strip LaTeX from prose lines of
  `frontmatter/abstract.tex` and count words per half (Abstract vs
  Uittreksel); expected 2026-07-12: 322 / 275. (Any script works; do NOT use
  a bash heredoc for inline Python here — backslashes get mangled on this
  machine. Write a temp .py file and run it.)
- Live TODOs: `grep -rn '^[^%]*\\candidatetodo' chapters/*.tex | wc -l` — was 6.
- Caption placement: for each `table` env, `\caption` index < `\begin{tabular`
  index; for each `figure` env, `\caption` after `\includegraphics` — was
  20/20 and 20/20 clean (script pattern: temp .py, regex over env bodies).
- Margins: `sed -n '2p' imports.tex` — currently `left=3cm,right=2cm,top=2.5cm,bottom=2.5cm`.
- Core pages: `grep 'chapter}{References' thesis.toc` (References page − 1 =
  core end; was 119).
- Terminology: `grep -rioc '\bframework\b' chapters/*.tex` etc. (framework 156,
  toolkit 11, meta-feature 46, datasets 209, corpus/corpora 133,
  Meta-Knowledge Base 19 title / 11 lower).
- Settled-claims stay dead:
  `grep -rniE "leave-one-out|3,?066|five model families|calibrated confidence|2/3 vs 1/14|p ?= ?0\.063" . --include="*.tex"`
  — expect only the legitimate uses listed in §4.
- Checklist source of truth: re-read
  `thesis_checklist/2026 Thesis Checklist_grammarlayout.pdf` if the department
  reissues it.
