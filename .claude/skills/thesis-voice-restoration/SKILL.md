---
name: thesis-voice-restoration
description: >-
  Load this skill when the task is to make thesis prose sound like Werner Hugo
  wrote it rather than an LLM — i.e. "does this read as AI-written?", "restore
  my voice", "humanise this chapter", "de-AI the abstract", "run the voice
  pass on CH3", or auditing a chapter for authorial-voice consistency before
  submission. It holds the author's measured voice fingerprint (derived from
  his 2024 Skripsie), the 2026-08-03 baseline audit scores for all six
  chapters plus front matter, the rewrite rules, the protected-elements list
  (structure and headings are NEVER changed), and the per-chapter workflow
  including the subagent-swarm audit pattern. It supersedes the generic
  /humanizer skill for anything inside the thesis estate: /humanizer's default
  advice (add personality, opinions, first person, short punchy sentences) is
  WRONG for an academic thesis and must not be applied here. Do NOT load this
  for: LaTeX conventions, department formatting or terminology canon (use
  thesis-writing-and-style), where a change may land or git discipline (use
  thesis-change-control), verifying that a number is correct
  (artifact-verification-playbook), or running an examination-panel content
  review (thesis-review-protocol). This skill changes HOW sentences read, never
  WHAT they claim.
---

# Thesis Voice Restoration

Making the MEng thesis read as though one human wrote it, without flattening
the analytical depth an MEng requires.

**Estate root:** `c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit`
**Backup of record (pre-restoration):**
`backups/pre_voice_restoration_2026-08-03/` — 6 chapters, 9 front-matter
files, `thesis.tex`. Restore from here if a pass goes wrong.
**Reference voice sample:** `Werner_Hugo_Skripsie.pdf` in
`D:\4th Final Year\Final Skripise hand in` (convert with `markitdown` before
reading — it is a scanned-layout PDF and the raw text is unusable).

---

## 0. Where things stand (updated 2026-08-03)

| File | Baseline | Now | State |
|---|---|---|---|
| `introduction_chapter.tex` (CH1) | 48 | **66** | Done, full coverage, proofread |
| `methodology_chapter.tex` (CH3) | 15 | **70** | Done, full coverage, proofread |
| `design_and_implementation.tex` (CH4) | 22 | **60** after sweep 1 | Sweep 2 applied, **not re-scored** |
| `scoping_review_chapter.tex` (CH2) | 28 | — | **Not started.** 1178 lines. `minor-changes-only` under change control — a voice pass qualifies, but do not restructure |
| `demonstration_and_evaluation.tex` (CH5) | 25 | **74** | Done 2026-08-10, full coverage, proofread. Now 1258 lines |
| `conclusion.tex` (CH6) | 18 | — | **Not started.** 247 lines, worst tell density of any chapter |
| `frontmatter/abstract.tex` | 10 | — | **Not started.** Do LAST, after the chapters, so it matches finished text |
| `frontmatter/acknowledgements.tex` | n/a | — | **Empty template stub — must be WRITTEN, not edited.** Every line commented out |

Body prose in CH1/CH3/CH4 verified clean of em dashes by
`scripts/check_dashes.py`; surviving literal em dashes in those files are all
inside `%` comments. Nothing has been committed; working branch is
`feature/api-dashboard-intergration`.

**Tooling (durable, in this skill):**
- `scripts/enum_paras.py` — paragraph inventory, touched vs untouched by exact
  text match. Run this BEFORE editing (workflow §6b step 2).
- `scripts/check_dashes.py` — the corrected dash sweep. Use instead of grep.
- `references/audit_prompt.md` — subagent voice-audit prompt.
- `references/proofread_prompt.md` — subagent proofread prompt.

---

## 1. The problem this skill solves

An external examiner reading the thesis straight through should perceive one
author. As audited on 2026-08-03, all six chapters had drifted the same
direction, away from the author's own register, in a way that reads as
machine-drafted. The drift is *consistent*, which is why it registers as a
single non-authorial voice rather than as patchiness.

**The single most diagnostic signal.** The author's Skripsie runs on
sentence-initial connectors: *Thus, Therefore, Hence, As a result, In
addition, Additionally, However, In contrast, Finally.* He reuses the same
handful relentlessly. In the MEng thesis: CH4 zero in 800 lines, CH5 zero in
1013 lines, CH3 one, CH2 three. That absence is more diagnostic than any
individual em dash. **Restoring these connectors is the highest-value single
edit in the whole pass.**

---

## 2. The author's voice fingerprint

Measured from the 2024 Skripsie. This is the target, not an aspiration.

**Person / stance.** Impersonal third person. No "we", no "I" in body prose.
In reflective sections he writes "the student". Work is described as done,
not narrated as being done.

**Sentence shape.** Plain subject-verb-object declaratives, 18–32 words.
Length varies but never dramatically. No one-line punchy fragments. No long
subordinate stacks. Paragraphs run 3–6 sentences and end on a fact, not a
flourish.

**Connectors.** See §1. Sentence-initial, comma-marked, repetitive by choice.
He does not cycle synonyms to avoid repeating "Therefore".

**Cross-references.** Explicit and constant: "Section 4.3 details these
redesigned processes", "detailed in Section 3.3.2 and Tables B.1–B.4". This
habit is already present in the MEng thesis and is *correct* — do not reduce it.

**Verdict sentences.** He closes an argument flatly: "Thus, the fourth
objective was met." The MEng equivalent is "Thus EQ1 was answered." Use
sparingly; the MEng chapters answer EQs and RQs, not numbered objectives.

**Hedging.** Modest and consistent: "has the potential to", "could help",
"would improve". Not over-qualified, not overclaimed.

**Vocabulary.** Plain working verbs: improve, reduce, ensure, identify,
address, analyse, document. Almost no abstract-noun inflation.

**Punctuation.** No em dashes. Commas and full stops do the work. Few
semicolons. No colons introducing dramatic reveals.

**Spelling.** South African / British: organisation, standardise, analyse,
labelled, minimising, artefact. (Already clean thesis-wide — zero American
forms found. Do not break this.)

**Human texture to PRESERVE — and the hard limit on it.** What reads as human
is *rhythm and construction*: uneven paragraph lengths, a repeated connector,
mild redundancy between a chapter conclusion and the final recap, a plain
sentence where a fancier one was available. Preserve those.

**Errors are NOT texture. Fix every one you find.** (User instruction,
2026-08-03, correcting an earlier version of this skill that said to leave
"the odd typo".) Typos, misspellings, subject-verb disagreement, article
slips, doubled words, broken parentheticals, comma splices and stray
punctuation are defects an examiner will mark. The submitted thesis must have
none. If you find one while doing a voice pass, fix it and report it
separately from the voice changes, so the user can see what was corrected
beyond style. Do not leave a known error in place on the grounds that it looks
authentic.

The distinction is: do not introduce a *uniform polish of register* the author
never had. Do make the text *correct*.

---

## 3. Calibration: the 65–75 target

**Agreed with the user, 2026-08-03.** An MEng thesis legitimately reads more
analytically than a fourth-year Skripsie. Chasing 90/100 against the Skripsie
would flatten arguments that deserve their complexity.

Target **65–75/100**: connectors and sentence rhythm restored, mechanical
tells removed, analytical depth kept.

**Defensible as-is — do NOT flag these:**
- "performance landscape" — a defined technical term in the framework, not
  filler. Reduce its use as a loose abstract noun; keep it where it names the
  1,785-record artefact.
- "paradigm" — the thesis's own domain term for TML vs DL. Not inflation.
- Heavy `Section~\ref{}` cross-referencing — both his habit and good practice.
- British spelling, absent Oxford commas — already matching.
- Technical enumerations that happen to have three items. Only rhetorical
  tricolon *stacking* is a tell.
- "robust", "significant" in their genuine statistical senses.

---

## 4. Protected elements — NEVER change these

**User instruction, 2026-08-03: the structure of the thesis stays as it is.
The focus is sentence rhythm and voice in the body text only.**

Do not touch:
1. **Headings and subheadings.** Wording, `\mysection`/`\mysubsection` macro
   choice, and **Title Case** all stay. Title Case is NOT on the target list,
   despite being a generic AI tell — it is this document's house style.
2. **Section order and section count.** No merging, splitting, resequencing.
3. **`\label{}` and `\ref{}` keys.** Every one, unchanged.
4. **Numbers, statistics, citations, `\cite{}` keys.** This skill has no
   authority over claims. If a rewrite would change what a sentence asserts,
   stop and leave the original.
5. **Tables, figures, equations, and their captions and environments.**
   (Caption prose may get a light connector/dash pass only if the user asks.)
6. **`\candidatetodo{}` review notes.** They are removed before submission by
   a separate process, not by this one.
7. **Chapter-opening roadmap paragraphs and closing summaries as structures.**
   Their prose may be rewritten; their presence and function may not be removed.

---

## 5. The target list — what a voice pass actually changes

Body prose only. In rough order of value:

1. **Restore sentence-initial connectors.** Aim for roughly one per 3–5
   sentences in argumentative passages, drawn from his set (Thus, Therefore,
   However, In addition, As a result, In contrast, Finally). Do not invent a
   wider set. Repetition is the point.
2. **Split long sentences.** Anything over ~35 words with stacked subordinate
   clauses becomes two or three declaratives. Target mean 18–32 words.
3. **Delete em dashes (`---`, `--`, `—`, `–`).** Replace with a full stop, a
   comma, a colon, or parentheses, in that order of preference. Restructure
   if none fits. Baseline count was ~130 thesis-wide; the target is zero in
   body prose.
4. **Unwind colon-led dramatic constructions.** "X is the real problem: Y"
   becomes two sentences or a "because" clause. Colons introducing genuine
   lists are fine.
5. **Remove negative parallelism.** "not X, but Y", "not merely X, it is Y",
   "it is not that A, it is that B" → a plain positive statement plus a
   contrast sentence.
6. **De-bold inline-header bullets.** `\item \textbf{Label.} text...` → plain
   prose sentences or unbolded enumerated items. This is the biggest visual
   tell after em dashes (~80 instances thesis-wide). Where a genuine
   definition list is warranted, keep the list but drop the bold run-in.
7. **Cut participial "-ing" tails** that add rhetorical depth rather than
   information: "…, highlighting the importance of…", "…, reflecting broader
   trends…". Convert to a new sentence with a connector.
8. **Break up 8–14 sentence paragraphs** into 3–6 sentence paragraphs at
   natural argument boundaries. Do not add or remove content to do it.
9. **Replace copula avoidance:** serves as / stands as / represents a /
   constitutes a / offers a → is / has.
10. **Drop significance inflation** where it is filler: pivotal, crucial,
    critical (non-technical), "key" as an adjective, underscores, highlights
    the importance of, testament.
11. **Remove self-conscious meta-commentary:** "deserves to be stated
    plainly", "should be read as", "One implication… deserves". State the
    thing.
12. **Remove italic mini-headers inside paragraphs** used as pseudo-bullets.
13. **Deflate generic upbeat closers.** "lays a reproducible, extensible
    foundation for…" → a plain statement of what the work provides.
14. **Delete flowery and inflated vocabulary.** See §5a. The author writes with
    plain working verbs and concrete nouns; every word on that list is a tell.

### 5a. Banned vocabulary — the flowery-language list

**User instruction, 2026-08-10.** These words do not appear in the author's
own writing and read as machine register. Remove them wherever they appear in
body prose, including captions if the user has asked for a caption pass.
Replace with the plain equivalent, or restructure the sentence.

| Banned | Plain replacement |
|---|---|
| delve into, dive into, explore (as "examine") | examine, study, look at |
| leverage, harness, utilise, employ (as "use") | use, apply |
| testament to, speaks to, a mark of | shows, indicates, is evidence that |
| showcase, spotlight, illuminate, shed light on | show, present, describe |
| navigate (a problem), grapple with, wrestle with | address, handle, deal with |
| underscore, highlight (as emphasis), emphasise heavily | show, state plainly |
| pivotal, crucial, vital, paramount, indispensable | important, needed, or cut |
| critical (non-technical), key (as adjective) | main, primary, or cut |
| robust (non-statistical), powerful, compelling | reliable, strong, or cut |
| seamless, effortless, elegant, intuitive (as praise) | cut |
| landscape, realm, arena, sphere, tapestry, ecosystem | field, area, or the actual noun |
| journey, roadmap (as metaphor), lens through which | cut or name the thing |
| foster, cultivate, unlock, unleash, empower, enable (as puffery) | allow, support, make possible |
| rich, nuanced, multifaceted, holistic, comprehensive (as filler) | cut |
| profound, remarkable, striking, notable (as praise) | cut, or give the number |
| ever-evolving, rapidly changing, in today's world | cut |
| serves to, aims to, seeks to (before a verb) | the verb itself |
| it is worth noting that, importantly, notably | cut and state the fact |
| a wide array of, a plethora of, a myriad of | many, or the count |
| meticulous, careful consideration, deep understanding | cut |
| bridge the gap, pave the way, at the forefront, cornerstone | say what the work does |
| transformative, revolutionary, game-changing, cutting-edge | cut |

**Exceptions that stay** (already in §3, restated because this list would
otherwise catch them): "performance landscape" as the defined technical term
naming the 1,785-record artefact; "paradigm" for TML vs DL; "robust" and
"significant" in genuine statistical senses; "comprehensive" where it
describes an actual exhaustive sweep and the sweep is documented.

Grep for the list after each sweep:
```bash
grep -nEi "delve|leverag|harness|testament|showcase|spotlight|illuminat|shed light|\
grapple|underscore|pivotal|crucial|vital|paramount|indispensable|seamless|\
elegant|realm|arena|tapestry|ecosystem|foster|cultivat|unlock|unleash|empower|\
multifaceted|holistic|profound|remarkable|ever-evolving|plethora|myriad|\
meticulous|pave the way|forefront|cornerstone|transformative|cutting-edge|\
worth noting|bridge the gap" chapters/<file>.tex
```

---

## 6. Workflow

### 6a. Audit a chapter (read-only)

Dispatch one Sonnet subagent per chapter with the audit prompt in
`references/audit_prompt.md`. Chapters are independent, so run the swarm in
parallel in a single message. Each returns: a 0–100 voice score, a quantified
tell table with line numbers, rhythm metrics, structural conformance, and
ranked worst offenders.

Only spawn subagents when the user asks for a swarm or when auditing three or
more chapters at once. For a single section, audit inline.

### 6b. Rewrite a chapter

1. **Confirm the backup exists** for the file you are about to change. If
   `backups/pre_voice_restoration_*/` does not contain it, make one first.
2. **Enumerate every body paragraph in the chapter before editing any of it,**
   and keep the list. Then work the list start to finish, marking each
   paragraph touched-or-deliberately-skipped with a reason. Do NOT work only
   from the audit's "worst offenders" list — that is a sample, not an
   inventory. Coverage beats depth: a chapter where the worst ten paragraphs
   are perfect and thirty are untouched still scores near its baseline,
   because the score averages the whole chapter. This was the CH1 and CH3
   failure mode (see the pass logs in §8).
3. Work **section by section**, not whole-file in one edit. Long chapters
   (CH2 at 1178 lines, CH5 at 1013) must be done in passes.
3. Rewrite in place with `Edit`, one paragraph or contiguous block at a time.
   Never `Write` a whole chapter file — it destroys the diff and risks
   silently dropping content.
4. After each block, verify: same number of paragraphs, same claims, same
   `\ref`/`\cite` keys, same numbers.
5. **Self-check before moving on:** grep the edited region for `---`, `\item
   \textbf`, "not only", "rather than", " serves as ", " represents a ".
6. At chapter end, run the whole-file greps in §7 and report residual counts.

### 6c. Order of work

Agreed with the user, 2026-08-03:
- **Pass 1 (now):** CH1 → CH2 → CH3 → CH4.
- **Pass 2 (later):** CH5, CH6.
- **Pass 3 (later):** acknowledgements (must be WRITTEN — the file is an empty
  template stub, every line commented out), abstract.

The abstract is deliberately last despite being highest-visibility, because
it should be rewritten to match the finished chapters, not the other way round.

---

### 6d. Proofread pass (mandatory before a chapter is called done)

A voice pass is not finished until the chapter is also *correct*. No spellcheck
binary is installed on this machine (`aspell`, `hunspell`, `ispell` all absent,
verified 2026-08-03), and `language_tool_python` is not in `thesis_final`. Use
a Sonnet subagent per chapter with the proofread prompt in
`references/proofread_prompt.md`, and cross-check against the IDE's own
diagnostics, which surface in tool results after each edit.

Classify every hit into one of three buckets and act accordingly:
- **Fix silently:** unambiguous typos, doubled words, missing/duplicated
  articles, subject-verb disagreement, broken parentheticals, comma splices,
  stray or stacked punctuation.
- **Fix and report:** anything where the correction changes emphasis or could
  touch meaning.
- **Do NOT touch:** proper nouns and technical identifiers the checker does not
  know (`fastText`, `spaCy`, `Peffers`, `PsyMatrix`, `TyDiQA`, `MMARCO`,
  `SuperPCA`), and British/SA spellings (`characterisation`, `operationalise`,
  `analyse`). The IDE's spellchecker flags both categories constantly; they are
  false positives every time.

### 6e. Chapter-specific notes for the remaining work

**CH2 (`scoping_review_chapter.tex`, 1178 lines, baseline 28).** Freeze status is
`minor-changes-only` (user rule, 2026-07-12): typos, refs and wording only. A
voice pass qualifies; re-scoping, re-running the protocol, or restructuring
does not. The baseline audit found voice drift that *worsens* through the
chapter: the early methodology prose is closest to the author, Scoping Review A's
synthesis is worse, and Scoping Review B (from "Step 5: Collate, Summarise, and
Report Results" onward) is the most machine-dense stretch in the whole thesis,
with 50--70 word sentences chaining three to five participial clauses. Budget
the most effort at the END of the chapter, not the start. Expect long
literature-summary paragraphs of 6--9 sentences; split them.

**CH5 (`demonstration_and_evaluation.tex`, 1013 lines, baseline 25).** 42 em
dashes, the most of any chapter. Register shifts: the early evaluation-design
section is plainest, the middle (Paradigm Decision / Performance Gap / Failure
Mode analysis) is essayistic argument-building where nearly all the em dashes,
bold-lead sentences and "rather than X, Y" parallelisms cluster, and the late
walkthrough returns to procedural prose. 16 `\textbf{X.}` paragraph run-ins —
protected, leave them. Watch the numbers closely: this chapter carries the
headline results (99.18% range capture, 0.0073 regret, 2/17 strict top-1) and
the confidence-signal claim ceiling. Rule 7 applies hardest here.

**CH6 (`conclusion.tex`, 247 lines, baseline 18).** Worst tell density in the
thesis: 29 em dashes and 21 `\item \textbf{Label.}` bullets in 247 lines. The
closing sentence is a near-verbatim match for the anti-profile's own
"generic upbeat closer" example ("lays a reproducible, extensible foundation
for..."). Short chapter, high yield. Note its section shape (Summary of the
Research / Answers to Research Questions / Theoretical + Practical
Contributions / Limitations / Future Work / Closing Remarks) deliberately
differs from the Skripsie's closing chapter — that is structure, protected, do
not "restore" the Skripsie shape.

**Abstract.** 13 lines, highest visibility per word, em-dash-led opening
definition. Do it AFTER the chapters so it matches finished text.

**Acknowledgements.** Not a voice pass. The file is an untouched template stub
with every line commented out, including a placeholder "Thank you to Leanne".
It must be written from scratch, in first person, naming supervisor and family.
This is the one page where a human voice is unmistakable, and it is currently
blank. Ask the user for the content; do not invent names or sentiments.

## 7. Verification greps

Run from the thesis root after each chapter.

**Dashes — use the script, NOT grep.** `grep -- "---" f | grep -v candidatetodo`
is wrong twice over (see the CH4 pass log in §8):
```bash
python <skill>/scripts/check_dashes.py chapters/<file>.tex
```
Note that bare `--` is the CORRECT LaTeX en dash for ranges and paired compounds
(`3--5-gram`, `sentence--sentence`, `17--18`). Never "fix" those.

**Connector density — must go UP.** Paragraphs are single long lines, so a
line-anchored `grep -c` undercounts badly. Count occurrences, not lines:
```bash
OLD=backups/pre_voice_restoration_2026-08-03/chapters/<file>.tex
NEW=chapters/<file>.tex
for f in $OLD $NEW; do grep -v "^\s*%" $f \
  | grep -oE "(^|\. )(Thus|Therefore|However|In addition|As a result|In contrast|Finally|Additionally|Hence|Otherwise)," \
  | wc -l; done
```

**Structural integrity — every count must be IDENTICAL before and after:**
```bash
for pat in "cite{" "ref{" "label{" "textbf{" "item " "mysection{" "mysubsection{" \
           "begin{equation}" "begin{algorithm" "begin{table}" "begin{figure}" \
           "textit{" "emph{" "candidatetodo{"; do
  o=$(grep -o "$pat" $OLD|wc -l); n=$(grep -o "$pat" $NEW|wc -l)
  [ "$o" != "$n" ] && echo "!! $pat $o -> $n"
done
```
Any mismatch must be explained, not waved through. Diff the contents to confirm
it is a deliberate change:
`diff <(grep -oE "textit\{[^}]*\}" $OLD|sort) <(grep -oE "textit\{[^}]*\}" $NEW|sort)`

**Other tells (grep is fine here):**
```bash
grep -nE "not only|not merely" chapters/<file>.tex
grep -nE "serves as|stands as|represents a|constitutes a|offers a" chapters/<file>.tex
grep -n "item \\\\textbf" chapters/<file>.tex   # protected — count only, do not edit
grep -oEi "\b([a-z]{3,})\s+\1\b" chapters/<file>.tex   # doubled words
```

---

## 8. Baseline audit — 2026-08-03

Six Sonnet agents, one per chapter, scored against the Skripsie fingerprint.
Re-score after each pass and record the delta here.

| File | Baseline | Post-pass | Headline finding |
|---|---|---|---|
| `frontmatter/abstract.tex` | 10 | — | Em-dash-led opening definition; first sentence an examiner reads |
| `chapters/methodology_chapter.tex` | 15 | **70** (2026-08-03, full coverage) | 14 inline-header bold lists; 8–12 sentence paragraphs; mean 35–40 words |
| `chapters/conclusion.tex` | 18 | — | 29 em dashes, 21 bold bullets, "lays a foundation" closer |
| `chapters/design_and_implementation.tex` | 22 | **60** after sweep 1 (2026-08-03); sweep 2 applied, not re-scored | Zero connectors in 800 lines; mean 35–45 words |
| `chapters/demonstration_and_evaluation.tex` | 25 | **74** (2026-08-10, full coverage) | 42 em dashes; essayistic "not X, it is Y" argumentation |
| `chapters/scoping_review_chapter.tex` | 28 | — | 70-word sentences with stacked participial tails; drift worsens late |
| `chapters/introduction_chapter.tex` | 48 | **66** (2026-08-03, full coverage) | Partially hand-edited already; AI drafts visible in `%` comments |
| `frontmatter/acknowledgements.tex` | n/a | — | **Empty template stub. Nothing written.** |

Thesis-wide baseline: ~130 em dashes, ~80 bold inline-header bullets, mean
sentence length 28–45 words against an 18–32 target.

**Already clean, do not break:** British/SA spelling (zero American forms),
Oxford commas mostly absent, `Section~\ref` cross-referencing dense and
idiomatic.

### CH1 pass log (2026-08-03) — lessons for the remaining chapters

Independent Sonnet re-audit scored the pass **48 → 64**, then five residual
tells were fixed (not independently re-scored). Integrity verified: 36 cites,
14 refs, 11 labels, 57 `\textbf`, 44 `\item`, 9 `\mysection`, 4 `\subsection`
all identical before and after. Connectors 1 → 8. Live em dashes 7 → 0 (the
two survivors are inside a `%` comment and a `\candidatetodo`, both protected).

Four things that generalise:

1. **One pass is not enough.** The first sweep hit the obvious offenders and
   left ~30 of 40 paragraphs untouched, landing at 64. Budget a second sweep
   over the paragraphs the first one skipped, not just the flagged ones.
2. **Watch for precision loss when simplifying vocabulary.** The pass dropped
   "ad-hoc" and "empirical" as qualifiers while plainifying a sentence. That is
   a real loss, not a style win. Simplify inflated words; keep load-bearing
   modifiers. The re-audit's "overcorrection check" caught this — always ask
   for it.
3. **Formal statements are off limits.** The MRQ, SRQ 1–4, EQ 1–3 and the five
   Objectives are restated verbatim in Ch6 and the front matter. Rewriting one
   silently desynchronises the thesis. Leave them, even when they are the
   longest sentences in the chapter.
4. **`\textbf{Chapter~N — Title}` inline labels are body prose, not headings.**
   Their em dashes are in scope (changed to colons). `\mysection` arguments are
   not. Keep that line clear.

### CH3 pass log (2026-08-03) — the coverage lesson

Sweep 1 scored **15 → 35** and the re-audit's verdict was blunt: roughly half the
chapter was byte-identical to the baseline. The touched half landed at 60–70; the
untouched half still scored 15, and a chapter score averages both. Sweep 2 then
covered the ten paragraph groups the auditor named. Final: connectors 2 → 16,
live em dashes 0, all 61 cites / 106 refs / 37 labels / 7 equations / 4
algorithms / the 105–68–37 paradigm table intact.

**The lesson that generalises: coverage beats depth.** Rewriting the worst
passages beautifully still yields a mediocre chapter score, because the
untouched paragraphs drag the average down. Enumerate every body paragraph in
the chapter FIRST, then work the list, rather than chasing the audit's "worst
offenders" list alone. Ask the re-audit explicitly which regions were left
byte-identical — that question surfaced the problem here.

Two genuine defects found and fixed as a side effect (both flagged to the user,
neither a voice issue):
- Four stacked colons doing semicolon work in the scope paragraph
  ("...short text: code-switching...: discrimination...: data scarcity...").
- A comma splice in the evaluation-methodology paragraph ("...depends on the
  deployment scenario, the knowledge base records a full suite...").

One overcorrection caught by the re-audit and reverted: "This distinction is not
incidental bookkeeping" was flattened to "This distinction matters", losing the
pre-emptive rhetorical work. Replaced with "This distinction has consequences for
how the results should be read." Negative parallelism sometimes carries meaning;
check what the construction is doing before deleting it.

### Full-coverage sweep (2026-08-03) — the tooling that made it work

Both chapters reached target only after a **paragraph inventory** was built and
worked start to finish: CH1 48 → 66 (23/30 paragraphs touched), CH3 15 → 35 →
**70** (62/83 touched). The enumerator lives at
`scratchpad/enum_paras.py`; it lists every body paragraph and marks each
touched-or-untouched by **exact text match against the backup** (do NOT use
`diff` line numbers — paragraph splits shift them and every line reads as
"changed").

**Known blind spot in the enumerator:** it skips lines starting with `\item`,
so prose *inside* list items is invisible to it. CH1's entire Scope section
(six Inclusions items, three Exclusions items) was missed for exactly this
reason and only surfaced because the re-audit was asked to list byte-identical
paragraphs. Always ask the re-audit for that list; never trust the script alone.

Paragraphs correctly left untouched are: formal MRQ/SRQ/EQ/Objective statements
(restated verbatim elsewhere in the thesis), equation lead-ins, short
cross-reference sentences, and the chapter-opening roadmap (which already
matches the author's habit). Record the reason for each skip.

Four regressions the re-audits caught, all now fixed — this is why the
re-audit's "overcorrection check" is not optional:
- **Content loss (the serious one).** Deleting what looked like a redundant
  participial tail removed a real clause: "…establishes the methodology
  foundation, *translating the scoping review evidence into a defined solution
  design*." Restored as its own sentence. **Never delete a trailing clause
  without checking whether it carries content the sentence does not.**
- **Terminology loss.** "high-velocity TML / high-robustness DL" was flattened
  to "fast / more robust", dropping the velocity-versus-robustness contrast the
  thesis uses throughout. Restored as "the computational velocity of the TML
  paradigm and the robustness of the DL paradigm".
- **Tense mismatch introduced by a split:** "generates … This involved …" →
  "This involves".
- **A revert that went too far.** "This distinction is not incidental
  bookkeeping**:**" — the tell was the *colon*, not the negation. A plain
  `X is not Y.` predicate is ordinary English, not the "not only… but also"
  parallelism on the target list. Original predicate restored, colon gone.

### CH4 pass log (2026-08-03) — two verification holes worth keeping

22 → **60** after sweep 1; sweep 2 then covered the regions the re-audit named
(Package Design, Model Training, the Phase 4 tail, and `\item` prose in the
ingestion pipeline and four-way split). Substantial untouched paragraphs went
from ~31 to 7. Connectors 0 → 14. Integrity clean: 18 cites, 80 refs, 45 labels,
91 items, 25 `\candidatetodo` notes, all tables/figures/equations/algorithms
byte-identical, and every checked number preserved.

**Hole 1: the em-dash grep silently skipped a whole class of lines.** The
standard sweep pipes through `grep -v candidatetodo` to ignore review notes.
But body prose often *follows* a `\candidatetodo{...}` on the same source line,
so that filter discards the prose too. A live em dash at L293 survived two
verification passes because of it. **Correct method: strip `\candidatetodo{...}`
bodies with a brace-matching parse, then search what remains.** A working
implementation is in the CH4 sweep (see `scratchpad/`); never use the
line-level `grep -v`.

**Hole 2: literal em dash characters (U+2014) are invisible to a `---` grep.**
CH4 held 7 of them, all inside bold run-in labels (`\textbf{S4 — Information-
Theoretic:}`). Always check both forms:
`python -c "import io;print(io.open(P,encoding='utf-8').read().count('—'))"`.
A non-ASCII character inventory is a cheap way to catch this and any genuine
mojibake at the same time. (Terminal `?` renderings are usually just cp1252
display limits, not file corruption — verify by decoding, not by eye.)

Label fix pattern: `\textbf{S4 — Information-Theoretic:}` →
`\textbf{S4 Information-Theoretic:}`. Do NOT substitute a colon, since these
labels already end in one and `S4: Information-Theoretic:` reads badly.

Two genuine defects found and fixed as a side effect: a comma splice in the
chapter-opening roadmap ("structured as follows, Section~..."), and a missing
`\textbf{}` wrapper leaving "Logistic Regression Two pipelines are trained:"
running together while its sibling subsection had one. Also changed
"well-calibrated recommendations" → "reliable recommendations": the phrase was
about retrieval quality, not the confidence signal, but it is safer nowhere
near rule 7.

### CH5 pass log (2026-08-10) — the "stale baseline" lesson

25 → **74** in three sweeps (two audit agents on halves, my own edits, then a
re-audit + proofread agent pair). Integrity clean: all `\cite`/`\ref`/`\label`/
`\textbf`/`\item`/`\mysection`/`\mysubsection`/table/`\textit`/`\emph`/
`\candidatetodo` counts identical, and every numeric token byte-identical in the
same order. Connectors 18 → 36. Live body-prose em dashes 0 (the four remaining
`---` are table "not applicable" cells; the 11 literal U+2014 are all in `%`
comments). New backup at `backups/pre_voice_ch5_2026-08-10/`.

Three things that generalise:

1. **Re-measure the baseline before trusting §0.** CH5 had been substantially
   reworked between 2026-08-03 and 2026-08-10 (1013 → 1229 lines, connectors
   1 → 18, 42 em dashes → 4 table cells). The recorded baseline of 25 and the
   "42 em dashes" note in §6e were both stale. Run the dash script and the
   connector count against the *current* file before planning a pass, and take a
   fresh backup rather than diffing against the 2026-08-03 one.
2. **This chapter's dominant tell was paragraph length, not sentence length.**
   Mean sentence length was already inside 18–32 words. The damage was in
   8–17-sentence blocks (the LLM comparison, the stratum-weight findings, the
   Chapter Summary) and in one-line punchy fragments used as dramatic beats
   ("They are.", "Refitting is essential.", "No scenario supports the earlier
   claim."). The fingerprint forbids those fragments; fold each into the
   sentence that explains it, rather than deleting it.
3. **Both audit agents scored their half at 58 and both were right about
   *where*.** Splitting one long chapter across two Sonnet auditors by line
   range, each asked for an exhaustive paragraph inventory plus an explicit
   "which ranges are already CLEAN" list, gave better coverage than a single
   whole-chapter audit did on CH1/CH3.

Two pre-existing defects found and reported, NOT fixed by this pass because they
are content, not voice:
- `demonstration_and_evaluation.tex:466` — "The best neural candidate is within
  0.39 percentage points of the best TML candidate on all 17 datasets"
  contradicts `tab:paradigm_regret` immediately below it, where the gap reaches
  0.0556 on Exorde. The 0.39 pp figure appears to belong to the four TML-win
  datasets, not all 17. Present in the backup; needs the author's decision.
- `tab:k_ablation` column header still reads `\textbf{Policy}` after the tracked
  "policy → selection strategy" rename recorded at L200. Table header, protected
  by §4.5, so reported rather than edited.

One overcorrection caught by the re-audit and reverted: "faces a genuinely
different selection problem" had been flattened to "faces a different selection
problem". The intensifier was load-bearing.

**Subagents wrote files again.** The read-only re-audit agent left
`new_textit.txt` and `old_textit.txt` in the thesis root (scratch from its own
integrity diff). Harmless, deleted. `git status` after every thesis subagent
call, as the standing rule says.

### Proofread results (2026-08-03)

Run after the CH1 and CH3 voice passes, per §6d. Mechanical scans (doubled
words, spaced punctuation, stacked punctuation, article slips) returned clean
on both chapters. Two real errors surfaced, **both pre-existing in the backup,
neither introduced by the voice pass**, both now fixed:

- `introduction_chapter.tex:40` — comma splitting subject from verb: "within a
  single sequence, produces sparse cues" → comma removed.
- `methodology_chapter.tex:478` — "carries **four** limitations" above a list of
  **five** bullets → corrected to "five". Verified by counting the `\item`s
  (Knowledge-base scale, Representation circularity, Scope of the similarity
  hypothesis, Language and register scope, Evaluation scope).

Also fixed during the CH3 voice pass: "item-profile similarity (examplified by,
dataset fingerprint proximity in this study)" — a misspelling inside a broken
parenthetical. Under the corrected §2 policy this is a plain defect fix, not a
judgement call.

Two false alarms worth remembering: the IDE flags every British spelling and
every technical proper noun, and a "DL not defined" report is wrong because the
acronym is declared in `frontmatter/defined_acronyms.tex:24`. Check the
front-matter acronym file before accepting any undefined-acronym finding.

**Worked example of the target register:**
`drafts/voice_demo_ch4_benchmark_results.tex` — CH4 §Cross-Benchmark Results
and Chapter Summary rewritten in the author's voice, numbers and refs
unchanged. Read this before starting any pass.

---

## 9. Relationship to `/humanizer`

`/humanizer` is the generic Wikipedia-derived AI-tells guide. Its *pattern
catalogue* (§§1–33) is a useful checklist and this skill's §5 is derived from
it.

**But its default voice advice is actively wrong here.** /humanizer's
"PERSONALITY AND SOUL" section tells you to add opinions, first person,
humour, tangents, and short punchy sentences. Applying that to a Stellenbosch
MEng thesis would be worse than the current AI register. /humanizer itself
says so: *"For encyclopedic, technical, legal, or reference text, neutral and
plain is the correct human voice; don't inject opinions or first person."*

So: use /humanizer's tell list, ignore its voice prescription, and take the
voice from §2 of this skill instead.

Also inherit /humanizer's false-positive discipline (§DETECTION GUIDANCE):
formal vocabulary, perfect grammar, and isolated transition words are not
tells. Look for **clusters**.

---

## 10. Provenance

- Voice fingerprint derived 2026-08-03 from `Werner_Hugo_Skripsie.pdf`
  (2024 undergraduate final-year report, Stellenbosch Industrial Engineering),
  converted via `markitdown`.
- Baseline audit 2026-08-03: six parallel Sonnet subagents, one per chapter
  plus front matter.
- Calibration target (65–75) and the protected-structure rule are direct user
  decisions from that session, not inferences.
- Backup taken 2026-08-03 before any edit.
