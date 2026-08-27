# Subagent proofread prompt template

One Sonnet agent per chapter. Substitute `<CHAPTER_PATH>` and `<CHAPTER_LABEL>`.
Run after the voice pass, before calling a chapter done.

---

You are proofreading one chapter of an MEng thesis for OUTRIGHT ERRORS.
READ-ONLY: do not edit any file. Report only; the caller applies fixes.

Read this file IN FULL (in chunks if long): `<CHAPTER_PATH>`
(chapter label: `<CHAPTER_LABEL>`)

Report every genuine error, in line order, as a table:
`line | the exact wrong text | the correction | category`

Categories to hunt:
1. Misspellings and typos in ordinary English words.
2. Doubled words ("the the", "is is", "and and") — these survive editing passes
   and are easy to miss when reading for sense.
3. Missing, duplicated or wrong articles ("a exception", "an unique",
   "the the framework").
4. Subject-verb disagreement, especially where a long subordinate clause
   separates subject from verb.
5. Broken or unclosed parentheticals, and parentheses/brackets whose contents
   no longer parse as a phrase.
6. Comma splices (two independent clauses joined by only a comma).
7. Stray, stacked or wrong punctuation: multiple colons doing semicolon work,
   a full stop inside a clause, a missing full stop at paragraph end, doubled
   commas, space before punctuation.
8. Wrong word ("effect"/"affect", "its"/"it's", "compliment"/"complement",
   "principle"/"principal", "discrete"/"discreet").
9. Number/unit agreement in prose ("17 dataset", "three model family").
10. Sentences that are ungrammatical or incomplete as written, regardless of
    cause.

DO NOT report any of the following. They are false positives here:
- British / South African spellings: characterisation, operationalise, analyse,
  organised, labelled, minimising, artefact, programme, standardised. The thesis
  uses these deliberately and consistently.
- Proper nouns and technical identifiers: fastText, FastText, spaCy, scikit-learn,
  Peffers, PsyMatrix, TextBrew, AutoNLP, AutoML, SuperPCA, Segmented-PCA, CLD3,
  XLM-V, OpenLID, TyDiQA, MMARCO, FLORES+, Europarl, Exorde, Lingualyzer,
  Garouani, Srinivasan, Dolicki, Spanakis, Tessari, Aggarwal, Beyer, Jiang, Fu,
  Xia, Chang, Aamodt, Blachnik, Leake, Dudani, Corrales, Joulin, Conneau, Liang.
- LaTeX macros, `\cite`/`\ref`/`\label` keys, maths mode, table and algorithm
  bodies, and anything inside a `%` comment or a `\candidatetodo{}`.
- Style preferences: sentence length, Oxford commas, Title Case headings,
  passive voice, word choice. This is a correctness pass, not a style pass.

If a hit is ambiguous (it might be deliberate, or fixing it might change
meaning), still report it but mark it `AMBIGUOUS` in the category column and say
in one line what the risk is.

End with a count: total errors found, broken down by category. If you find none,
say so explicitly rather than inventing marginal hits.
