# Subagent audit prompt template

Dispatch one Sonnet subagent per chapter, all in parallel in a single message.
Substitute `<CHAPTER_PATH>`, `<CHAPTER_LABEL>`, and `<N_WORST>` (8 for short
chapters, 10–12 for CH2/CH4/CH5).

Add the `## Internal drift` block only for chapters over ~800 lines.
Add the `## Section-by-section heat map` block only when the user intends to
rewrite that chapter next.

---

You are auditing ONE chapter of an MEng thesis for authorial-voice consistency
and AI-writing tells. This is a READ-ONLY task: do not edit any file.

STEP 1. Read the voice fingerprint in section 2 of:
`c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit\.claude\skills\thesis-voice-restoration\SKILL.md`
It describes the author's genuine human voice, taken from his 2024
undergraduate Skripsie. Also read section 3 (defensible items you must NOT
flag) and section 4 (protected elements — headings, structure, labels,
numbers, citations are all out of scope and must not be criticised).

STEP 2. Read this chapter IN FULL (in chunks if long):
`<CHAPTER_PATH>`
(chapter label: `<CHAPTER_LABEL>`)

STEP 3. Produce a report with exactly these sections:

## <CHAPTER_LABEL> — voice verdict
One paragraph. How close is this chapter's BODY PROSE to the Skripsie voice?
Give a similarity score 0-100 where 100 = indistinguishable from the Skripsie
author and 0 = obviously LLM-drafted. Score prose rhythm and register only.
Do not let heading style, section structure, or content quality affect the score.

## Quantified tells
A table with counts for the whole chapter. Rows: em/en dashes used as
punctuation (excluding those inside `\candidatetodo`); participial "-ing"
tails; copula avoidance verbs (serves as / stands as / represents a /
constitutes a / offers a); significance-inflation words used as filler
(pivotal / crucial / critical / key / underscore / highlight / testament);
AI vocabulary hits (list the actual words found); rhetorical rule-of-three
stacking (NOT ordinary technical enumerations); negative parallelisms
("not only...but also", "not merely X, it is Y", "not X, but Y");
colon-led dramatic sentences; inline-header bold bullets
(`\item \textbf{Label.}`); italic mini-headers used as pseudo-bullets inside
paragraphs; self-conscious meta-commentary ("deserves to be stated",
"should be read as"); paragraphs longer than 6 sentences; generic upbeat
closers; **every hit from the banned flowery-vocabulary list in SKILL.md §5a**
(name each banned word found, with count and line numbers). For each, give the
count and up to 2 verbatim examples WITH the line number.

Do NOT include rows for Title Case headings, Oxford commas, American
spellings, or section structure. Headings and structure are frozen by user
instruction, and spelling/commas were already verified clean.

## Connector density
Count sentence-initial, comma-marked instances of the author's connector set:
Thus, Therefore, Hence, As a result, In addition, Additionally, However,
In contrast, Finally. Report the raw count and the count per 100 lines of
prose. This is the chapter's single most diagnostic number. State what the
chapter uses INSTEAD (ordinals, colons, unmarked juxtaposition, "Consequently",
etc.).

## Rhythm metrics
Do real word counts on at least three representative paragraphs — do not
estimate. Report mean sentence length and range per paragraph, then a chapter
estimate. State whether paragraph lengths are uniform or varied. The Skripsie
baseline is 18-32 word sentences, 3-6 sentence paragraphs, visibly varied.

## Worst offenders
The `<N_WORST>` single worst BODY-PROSE passages in this chapter, most damaging
first. For each: line number, the verbatim LaTeX text, which tell(s) it
triggers, and a one-line rewrite in the Skripsie voice. The rewrite must
preserve every number, claim, `\ref` key and `\cite` key in the original.

Be strict and concrete. Cite line numbers for everything. Do not soften
findings. Do not comment on content correctness, claim validity, LaTeX
validity, citations, headings, or section structure — body-prose voice only.
