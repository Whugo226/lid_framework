# Thesis ↔ Toolkit Claim-Verification Prompt

Reusable workflow for checking that the claims in a thesis chapter are true to what the
`lid_toolkit` framework and `LID_experiments` actually do. Run it **one chapter at a time**:
paste everything under `--- PROMPT ---` into Claude Code and set `{PATH_TO_CHAPTER.tex}`.

Suggested order (highest technical-claim density first):
1. `chapters/toolkit_architecture.tex`
2. `chapters/design_and_implementation.tex`
3. `chapters/experimental_design_and_methodology.tex`
4. `chapters/demonstration_and_evaluation.tex`
5. `chapters/methodology_chapter.tex`

--- PROMPT ---

ROLE
You are a technical fact-checker and code auditor verifying an MEng thesis against the
software it describes. For every checkable claim in the given thesis chapter, determine
whether the actual codebase and experiment artifacts confirm it, contradict it, or cannot
settle it — and cite file:line evidence for each verdict. You are adversarial toward the
PROSE, not the code: assume the thesis may be wrong or stale, and treat the code + generated
artifacts as the source of truth.

EMPHASIS FOR THIS RUN: FULL CLAIM COVERAGE — IN BOTH DIRECTIONS.
(A) FORWARD (thesis → code): extract and render a verdict on EVERY checkable claim in the
    chapter, including soft architectural / data-flow claims — not just headline numbers.
    Do not skip a claim because it "seems obviously true"; trace it.
(B) REVERSE (code → thesis): also inventory what the toolkit ACTUALLY contains and flag
    anything academically significant that the chapter FAILS to mention (see Step 6). The
    author's stated fear is silent omissions — methods, formulas, or stack choices that are
    present and important in the code but absent from the thesis.

OVERARCHING CONSTRAINT — IT IS A MASTER'S THESIS, NOT A TECHNICAL MANUAL.
Never recommend adding content that turns the thesis into implementation documentation. Every
"missing" item must pass the ACADEMIC-SIGNIFICANCE FILTER before you suggest including it:
  INCLUDE (thesis-worthy) if it is any of:
    - a methodological choice a reader needs to reproduce or judge the work
      (the distance metric, the weighting scheme, the feature families, key formulas,
       the model/algorithm used, dataset provenance and splits, evaluation protocol);
    - a design decision with a rationale/trade-off that affects results or validity;
    - a named external tool/library that materially shapes the method (e.g. spaCy for
      linguistic parsing, fastText as a baseline) — named once at the right altitude,
      not version-pinned dependency lists.
  EXCLUDE (leave in the code, keep out of the thesis) if it is:
    - routine engineering (file I/O, caching, CLI plumbing, logging, error handling);
    - library minutiae, exact versions, function signatures, class hierarchies;
    - anything whose absence does not affect reproducibility, validity, or the contribution.
  When in doubt, recommend a ONE-SENTENCE mention at method altitude, not a subsection.
  For every reverse-pass suggestion, state WHERE it belongs (which chapter/section) and at
  what altitude (a sentence, a formula, a table row) — never "add a section on X".

SOURCES OF TRUTH (in priority order)
1. Runtime behavior — values obtained by actually executing the code / reading the real
   generated artifacts (mkb.pkl, validation_report.json, eval_profiles/, profiles/).
2. Source code — src/lid_toolkit/**.py, especially:
     logic/profiler*.py           (linguistic meta-feature extraction; feature count/dims)
     recommender/fingerprint_builder.py, mkb_similarity.py, feature_stratifier.py,
     recommender.py, typology_lookup.py  (distance metric, weighting, voting, MKB)
     facade.py, cli.py            (public API surface / workflow)
   NOTE: multiple profiler_*.py variants exist (profiler.py, profiler_legacy.py,
   profiler_spacy*.py, profiler_knowledge_base.py). Determine which is ACTUALLY imported/used
   at runtime (trace imports from facade.py / cli.py / __init__.py) before trusting any single
   file. Legacy / experimental variants are NOT ground truth.
3. Experiment artifacts — LID_experiments/model_training/, model_benchmarking_evaluation/,
   model_benchmarking_knowledge/, datasets/, and *.log / *.json / *.csv results.
4. Config — config.yaml, pyproject.toml, environment.yml.
Prose in comments/READMEs/docstrings is NOT ground truth; it can be as stale as the thesis.

INPUT
- Thesis chapter file: {C:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/chapters/design_and_implementation.tex}
- Toolkit root:   c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit
- Experiments:    c:/Users/User/OneDrive/Masters/LID_experiments

STEP 1 — EXTRACT CLAIMS
Read the chapter and extract every CHECKABLE claim into a numbered list. A checkable claim
is any statement that could be true or false about the built system, e.g.:
  - Quantities / dimensions ("extracts 2726-dimensional linguistic meta-features")
  - Named methods / metrics ("weighted composite Euclidean distance", "similarity voting")
  - Architecture / data flow ("the Profiler feeds the Fingerprint Builder which...")
  - Algorithms / formulas (the exact distance or weighting equation)
  - Datasets / counts ("17 datasets", "N languages", train/test splits)
  - Results / metrics (accuracy, F1, coverage numbers)
  - Component names and their responsibilities
Ignore un-checkable claims (motivation, related-work framing, opinions). For each claim
record: (a) the exact quote, (b) chapter location, (c) what artifact would prove/disprove it.

STEP 2 — TRACE EACH CLAIM
For each claim, go find the ground truth. Prefer to MEASURE over READ:
  - Dimension/count claims: actually load the artifact or run the code and count.
      e.g. load mkb.pkl and report the real fingerprint vector length; count the feature
      names the profiler emits for a sample text; count entries in the dataset dir.
  - Metric/algorithm claims: read the actual function computing it and quote the formula/code.
    Name the true metric (Euclidean? weighted? cosine? composite?).
  - Results claims: open the real results json/csv/log and compare numbers.
Record evidence as file:line quotes and/or the command you ran + its output.

STEP 3 — VERDICT PER CLAIM
  ✅ VERIFIED      — code/artifact matches the thesis claim exactly.
  ⚠️ IMPRECISE     — directionally right but wrong number/term/detail (give the correct value).
  ❌ CONTRADICTED  — code/artifact says something different (give what it actually is).
  ❓ UNVERIFIABLE  — cannot be settled from available code/artifacts (say what's missing).
For ⚠️/❌ provide EXACT corrected wording the author can paste into the thesis.

STEP 4 — OUTPUT: TRACEABILITY MATRIX
Markdown table, most-severe first (❌, then ⚠️, then ❓, then ✅):

| # | Thesis claim (quote) | Verdict | Ground truth (file:line / measured value) | Suggested thesis wording |

Then a "Corrections summary" listing only the ❌/⚠️ rows as ready-to-apply edits.
Also report coverage: total checkable claims found vs. verdicted.

STEP 6 — REVERSE / OMISSION PASS (code → thesis)
Independently of the chapter's claims, inventory what the toolkit ACTUALLY contains, then
compare against what the chapter mentions and surface academically significant GAPS. Cover:
  - TECHNICAL STACK actually used: read pyproject.toml / environment.yml / imports to find the
    real methodological dependencies (e.g. spaCy, fastText, scikit-learn, UMAP, Streamlit) and
    which ones SHAPE THE METHOD vs. which are plumbing. Report only the method-shaping ones.
  - KEY FORMULAS / ALGORITHMS present in code (the distance metric and its weighting, any
    normalisation/standardisation, the voting/aggregation rule, feature-extraction math). For
    each, give the actual formula from the code and whether the chapter states it.
  - COMPONENTS / DATA FLOW that exist but are undescribed (a real pipeline stage, a
    knowledge base, a stratifier, a typology lookup) — anything a reader needs to understand
    the method.
  - EVALUATION / DATA facts present in artifacts (real dataset count, languages, splits,
    metrics computed) that the chapter omits.
For each gap, RUN IT THROUGH THE ACADEMIC-SIGNIFICANCE FILTER above. Output:
  | Present in code (file:line) | Academically significant? | Currently in thesis? | Recommendation (where + altitude) |
Only rows where "significant = yes AND in thesis = no" are actionable — list those first and,
for each, draft the ONE- OR TWO-SENTENCE thesis wording (or the formula) to add, at the right
altitude. Explicitly mark items you deliberately EXCLUDED as implementation detail, so the
author sees you considered and rejected them (this is the guard against over-teching the thesis).

STEP 5 — BUG / DEFECT PASS (secondary)
While tracing, note genuine defects in the code you had to read (not style nits): logic
errors, wrong formulas, silent except-swallows, off-by-one in feature construction, metric
computed differently than intended, dead/duplicate profiler variants that risk being imported
by mistake, mismatches between config.yaml and code. Report separately:
  | Severity | File:line | Defect | Why it matters | Fix |
Only report defects you can point at in code — no speculation.

RULES
- Never assert a number you did not measure or read directly. If you infer, mark ❓ and say so.
- When code and thesis disagree, the code wins; correct the thesis, not the code (unless it's
  an actual bug → Step 5).
- Resolve which profiler/recommender variant is live before judging any claim about them.
- Keep quotes exact. Cite file:line for everything.

CALIBRATION EXAMPLES (verify these two first as a warm-up)
1. "The Profiler extracts 2726-dimensional linguistic meta-features."
   → Load the real fingerprint / inspect the profiler output and report the TRUE dimension.
2. "The framework uses a weighted composite Euclidean distance."
   → Read the recommender/mkb_similarity distance function and state the TRUE metric + weighting.

--- END PROMPT ---
