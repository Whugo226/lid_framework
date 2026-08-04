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

**Human texture to PRESERVE.** Occasional article slips, the odd typo, mild
redundancy between a chapter conclusion and the final recap. A 200-page
document with zero such texture is itself a tell. Do not sand these off, and
do not introduce a uniform polish the author never had.

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
2. Work **section by section**, not whole-file in one edit. Long chapters
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

## 7. Verification greps

Run from the thesis root after each chapter:

```bash
# em dashes in body prose
grep -n -- "---" chapters/<file>.tex | grep -v candidatetodo
# bold inline-header bullets
grep -n "item \\\\textbf" chapters/<file>.tex
# negative parallelism
grep -nE "not only|not merely|rather than" chapters/<file>.tex
# copula avoidance
grep -nE "serves as|stands as|represents a|constitutes a|offers a" chapters/<file>.tex
# connector density (should be NON-ZERO and rising)
grep -cE "^(Thus|Therefore|However|In addition|As a result|In contrast|Finally)," chapters/<file>.tex
```

The connector count is the one that must go **up**. Everything else goes down.

---

## 8. Baseline audit — 2026-08-03

Six Sonnet agents, one per chapter, scored against the Skripsie fingerprint.
Re-score after each pass and record the delta here.

| File | Baseline | Post-pass | Headline finding |
|---|---|---|---|
| `frontmatter/abstract.tex` | 10 | — | Em-dash-led opening definition; first sentence an examiner reads |
| `chapters/methodology_chapter.tex` | 15 | — | 14 inline-header bold lists; 8–12 sentence paragraphs; mean 35–40 words |
| `chapters/conclusion.tex` | 18 | — | 29 em dashes, 21 bold bullets, "lays a foundation" closer |
| `chapters/design_and_implementation.tex` | 22 | — | Zero connectors in 800 lines; mean 35–45 words |
| `chapters/demonstration_and_evaluation.tex` | 25 | — | 42 em dashes; essayistic "not X, it is Y" argumentation |
| `chapters/scoping_review_chapter.tex` | 28 | — | 70-word sentences with stacked participial tails; drift worsens late |
| `chapters/introduction_chapter.tex` | 48 | **64** (2026-08-03) | Partially hand-edited already; AI drafts visible in `%` comments |
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
