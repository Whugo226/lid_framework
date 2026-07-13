---
name: examiner-defense-pack
description: >-
  Load this when preparing the user (Werner Hugo, MEng, viva after 2026-09-01
  submission) for the ORAL DEFENSE: drafting or rehearsing answers to
  anticipated examiner questions, building a Q&A crib, simulating an examiner,
  or deciding what to concede vs defend. The external examiner is believed to
  be an INFORMATION-RETRIEVAL expert and the framework IS a retrieval system
  (k-NN over dataset fingerprints), so IR-framed challenges (learned ranking,
  cosine vs Euclidean, TF-IDF, precision@k/MRR) are covered explicitly, each
  with a grounded strong answer, artifact evidence, honest concession, and a
  LOAD-BEARING / CONCEDE-GRACEFULLY marking. Do NOT use it to write or edit
  thesis chapters (thesis-writing-and-style + evidence-standards), to run a
  chapter review (thesis-review-protocol), to trace a number to its artifact
  (artifact-verification-playbook), or to drive the live dashboard demo
  (dashboard-demo-runbook) — this skill is defense argumentation only.
---

# Examiner Defense Pack — anticipated questions with grounded answers

Context: MEng thesis "An Interactive Framework for Language Identification
Model Recommendation" (Werner Hugo, 25167626, supervisor Prof Mandla Gwetu,
Stellenbosch). Submission 2026-09-01; target grade ≥75%. External examiner:
believed information-retrieval (IR) expert — nothing else known. The framework
is instance-based meta-learning: k-NN retrieval (k=3) over stratified-PCA
"fingerprints" of dataset linguistic meta-features, with inverse-distance-
weighted (IDW) voting. An IR expert will recognise it as a retrieval system
and probe it with IR vocabulary. That is an opportunity, not a threat: the
thesis has real answers.

Jargon used once: **MKB** = Meta-Knowledge Base (the 17-dataset case base).
**Regret** / **Δf1** = ground-truth best model's weighted F1 minus the
recommended model's weighted F1 on the same evaluation split (lower better).
**Consensus index / confidence score C** = fraction of the k retrieved
neighbours whose own best model coincides with the recommendation.
**TML** = traditional machine learning (char n-gram MNB / Logistic Regression).

## Ground rules (non-negotiable)

1. **Never bluff past a real gap.** Every answer below is marked
   **LOAD-BEARING** (the thesis's contribution depends on it — defend it) or
   **CONCEDE-GRACEFULLY** (a real limitation the thesis already owns — concede
   it first, on your own terms, then scope it).
2. **Never say "calibrated confidence."** The signal is a consensus index;
   the thesis's own ceiling is "promising rather than established"
   (`demonstration_and_evaluation.tex:242`). See Q11.
3. **Every number quoted in defense must have been re-verified against
   artifacts within one week of the viva.** Commands in
   "Pre-viva re-verification" below. If a number cannot be re-verified, do
   not quote it.
4. Concede-gracefully items should be volunteered *before* the examiner
   raises them when the answer naturally touches the area — it converts a
   weakness into evidence of rigour.

## Canonical figures (all ✅ verified 2026-07-12 against thesis .tex AND by running `analysis/validation_statistics.py`)

| Figure | Value | Thesis locator |
|---|---|---|
| Strict top-1 accuracy | 17.6% (3/17); Wilson 95% CI [6.2%, 41.0%] | `demonstration_and_evaluation.tex:91,201` |
| Mean / median / max regret | 0.0078 / 0.0022 / 0.0489 | `:95,205,201` |
| Random baseline mean regret | 0.3830 (Monte-Carlo 10⁵ policies, seeded) / 0.3832 (analytic) | `:117,127` |
| Best constant policy | 0.0127 (fasttext_subword, Exorde-trained); max 0.0627 | `:128` |
| Constant XLM-V Base (zero-shot) | 0.0175; max 0.0633 | `:129` |
| Chance of exact top-1 match | 0.95% (1 of 105 variants); 17.6% ≈ 18× chance | `:112` |
| P(3 exact matches by chance) | 5.0×10⁻⁴; 0 of 100,000 random policies ≤ framework's 0.0078 | `:117` |
| Confidence split | non-zero conf 2/2 correct vs zero-conf 1/15; exact one-sided hypergeometric **p = 0.0221** | `:242`; conclusion `:39,53` |
| Corpus re-identification | top-1 12/17 (70.6%); top-3 14/17 (82.4%) | `:104-105,138` |
| k=1 ablation | exact 8/17 (47.1%) but mean regret 0.0784, max 0.8766 | `:228` (tab:k_ablation) |
| Top-3 shortlist | candidate within 0.5pp of optimum in 12/17; mean best-of-shortlist gap 0.0047, worst 0.0173 | `:250` |
| **MRR** (mean reciprocal rank of ground-truth model in engine ranking) | **0.203** (analysis script output; NOT reported in thesis text) | `analysis/validation_statistics.py` [3] |
| Features / families / PCs | 2,726 core / 327 families / 63 PCs; per-stratum 813/433/1,200/20/260 feats, 16/15/16/5/11 PCs, ≥95.2% variance | `analysis/stratum_audit.py`; drafts tables |
| spaCy vs stanza throughput | 5,570 vs 289 tokens/s (~19×), identical ~8,400-token input, i7-1065G7 CPU | `design_and_implementation.tex:83-98` |
| Lingualyzer ground truth | English 351/351 (100%); Dutch 314/351 (89.5%), 37 disagreements | `design_and_implementation.tex:158-198` |
| Short-text regime | 120-char truncation at word boundaries (40 for CJK); floors 30/10 chars | `design_and_implementation.tex:465` |
| Scope | 17 corpora, 24 spaCy-supported languages, 3 trained families (6 configs) + 3 zero-shot | conclusion `:24-26,84` |

⚠️ STALE FIGURE ALERT: the session-facts ledger records the confidence split as
"2/3 vs 1/14, p = 0.063" — that is review-era and WRONG for the current thesis.
The compiled thesis and the script both give **2/2 vs 1/15, p = 0.0221**. Use
0.0221. (Unverified-today ledger figure: 1,785 `benchmark_metadata.json`
records — re-verify before quoting.)

All thesis locators are under
`c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\chapters\`.
Repo paths are under
`c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit\`.

---

# Part A — IR-angle questions

## Q1. "This is a retrieval system. Why hand-crafted k-NN instead of a learned ranking function or learned embedding retrieval?" — LOAD-BEARING

**Strong answer.** Learned approaches need meta-level training instances, and
each instance here costs a full benchmarking programme: a corpus only becomes
usable training data after every candidate model has been trained and
evaluated on it under controlled conditions (`methodology_chapter.tex:172`).
The supply is bounded by experimental scope, not by how many corpora exist —
17 cases cannot train a reliable ranker or encoder. Instance-based retrieval
computes similarity at query time with no fitting step, remains valid at case
bases as small as k=1, and every newly benchmarked dataset is immediately
retrievable without retraining (CBR Retain stage, `methodology_chapter.tex:148`).
It is also not merely a stopgap: Garouani et al. (2023) benchmarked k-NN
against model-based meta-learners (Random Forest, XGBoost) across 400
real-world datasets and the k-NN approach won all 20 held-out accuracy cases
(`methodology_chapter.tex:172`). Finally, interpretability is a stated design
requirement (#3, `methodology_chapter.tex:113`): retrieved neighbours and
per-stratum distance contributions are inspectable via `trace_query()`
(`design_and_implementation.tex:410`), whereas a learned embedding space
discards loading-based audit — the explicit reason the thesis diverges from
PsyMatrix, the closest prior system, which uses a variational autoencoder
(`methodology_chapter.tex:177`).

**Evidence.** §3 "Design Decision Evaluation" (`methodology_chapter.tex:165-183`),
Garouani citation, PsyMatrix contrast, k-ablation table.

**Concession.** At MKB scales of 50–100+ datasets, learned ranking/weighting
becomes viable and is planned: `learn_weights()` exists in the artifact
(`design_and_implementation.tex:331`, Pearson correlations over leave-one-out
dataset pairs) but is documented as unreliable at n=17 (conclusion limitation 6).

## Q2. "Why Euclidean distance in PCA space rather than cosine similarity, the IR default?" — LOAD-BEARING

**Strong answer.** Cosine was the initial candidate and was rejected on three
grounds (`methodology_chapter.tex:219-222`): (1) cosine's advantage over
Euclidean in raw feature spaces is invariance to scale heterogeneity, and
per-stratum PCA with StandardScaler already normalises within-stratum variance
— the motivation for cosine disappears (Abdi & Williams 2010); (2) PCA factor
scores are projections onto principal axes, so Euclidean distance in that
space directly measures separation along each axis of variation and matches
PCA's own MSE objective; (3) Tessari et al. (2025): in high-dimensional
orthogonalised spaces, angular relationships become statistically degenerate,
so cosine estimates are unreliable regardless of the true relationship.
Concentration of measure (Beyer 1999; Aggarwal 2001) is handled *upstream*:
distances are computed in the compressed 63-dimensional space (5–16 PCs per
stratum), not the raw 2,726-dimensional one (`methodology_chapter.tex:209`).

**Evidence.** `subsec:similarity_technique`; conclusion theoretical
contribution 2 ("chosen over global cosine similarity on geometric grounds").

**Concession.** No empirical cosine-vs-Euclidean head-to-head on this MKB;
the argument is geometric and literature-based. If pressed: the ablation that
*was* run (k=1 vs k=3) targeted the aggregation stage, judged the bigger risk.

⚠️ Pre-viva to-do: live `\candidatetodo{Double check beyer and aggarwal
papers}` at `methodology_chapter.tex:209` — verify those two citations say
what the sentence claims before the viva.

## Q3. "Why 2,726 hand-engineered linguistic features instead of TF-IDF or character-n-gram corpus representations?" — LOAD-BEARING

**Strong answer.** TF-IDF representations are language-specific: cross-corpus
similarity would require shared-vocabulary assumptions that do not hold across
typologically diverse languages (`methodology_chapter.tex:175`). General
document statistics miss the morphological and syntactic dimensions most
predictive of LID performance differences across language families. The
granularity choice is externally evidenced: Dolicki & Spanakis (2021) found
fine-grained linguistic features (word order, morphological feature
distributions) outperform aggregated syntactic distance measures by 2–4× in
predicting cross-lingual transfer (`methodology_chapter.tex:200`). The dataset
similarity hypothesis is further supported by Xia et al. 2020 (corpus
statistics predict held-out NLP performance better than human experts on MT),
Srinivasan et al. 2021 (92–99% pairwise performance-ordering recovery from
typological features), and Chang et al. 2023 (decomposed drift beats holistic
metrics — retroactively validating stratification). And interpretability
again: each fingerprint dimension has a linguistic name a practitioner can
audit; a char-n-gram profile does not.

**Concession.** No within-thesis empirical comparison of linguistic
fingerprints vs an n-gram-profile retrieval baseline; the evidence is
external. Scoped honestly by the "scope of the similarity hypothesis"
limitation (`methodology_chapter.tex:407`): the literature supports
performance *prediction*, the thesis needed and tested best-model *identity*
preservation — that is exactly what the held-out evaluation measures.

## Q4. "How is this different from AutoML / meta-learning hyperparameter optimisation?" — LOAD-BEARING

**Strong answer.** Two categorical differences (`methodology_chapter.tex:97,106`).
First, AutoML optimises hyperparameters *within* a fixed architecture; the
performance differences documented in Scoping Review A are *architectural*
incompatibilities between model families and dataset regimes (char n-gram vs
subword-neural vs transformer), which HPO cannot cross. Second, AutoML's inner
loop needs labelled data on the target task; the framework's practitioner
scenario is an **unlabelled** corpus with no language annotations
(`methodology_chapter.tex:23`) — supervised search is impossible without
incurring precisely the labelling cost the framework avoids. The framework
selects among existing candidates at query time, label-free, in seconds.

**Evidence.** `subsec:design_requirements`; ruled-out alternatives also
include best-on-average selection — empirically beaten (0.0078 vs 0.0127).

**Concession.** The two are complementary, not rivals: nothing prevents
running HPO *after* the framework has picked the family. The thesis fixes
hyperparameters from literature consensus (char 3–5 n-grams,
`demonstration_and_evaluation.tex:48`) and does not claim they are per-dataset
optimal.

## Q5. "You evaluate a ranking system. Where are precision@k, MRR, nDCG? Why top-1 accuracy plus 'regret'?" — LOAD-BEARING (with a graceful edge)

**Strong answer.** The task is *selection*, not ranked-list consumption: the
practitioner deploys exactly one model, so the operative loss is the
performance cost of that deployment — regret, the standard criterion in the
algorithm-selection literature (conclusion, theoretical contribution 3).
Binary-relevance rank metrics presuppose a meaningful relevance cut; here
"relevance" is graded and near-tied — most candidates score F1 > 0.95, and in
the k=1 ablation three of nine "misses" matched the ground-truth score to four
decimal places (`demonstration_and_evaluation.tex:234`). Exact-match metrics
therefore *under-report* quality; regret is effectively the graded-relevance
evaluation with true gain = actual F1. The thesis argues this explicitly and
contributes it as a position: strict top-1 accuracy is misleading for
similarity-based recommenders in high-accuracy regimes. IR-style diagnostics
*are* present where they measure the right thing: corpus re-identification is
precision@1/@3 of the retrieval layer itself (12/17, 14/17), and the shortlist
analysis is a graded success@3 (candidate within 0.5pp of optimum in 12/17).

**If asked point-blank for MRR:** it has been computed — **0.203**
(`analysis/validation_statistics.py`, section [3]; not in the thesis text).
Give it, then immediately explain why reciprocal rank of the exact-best model
mis-scores near-ties, and pivot to mean regret 0.0078.

**Concession.** MRR/P@k are not reported in the thesis; a fair point for a
revision note. The defense is that they were considered and are less
informative here, not that they were overlooked — and you can produce the
number on request, which demonstrates command of the evaluation.

---

# Part B — Framework and methodology questions

## Q6. "Your five strata look ad hoc. Justify the partition." — LOAD-BEARING

**Strong answer.** The strata are a principled *coarsening of Lingualyzer's
published 3×2×3 measure taxonomy* (Linders et al. 2023;
`methodology_chapter.tex:196`): S1/S2/S3 refine its linguistic-unit dimension
(morphological / lexical / syntagmatic), S4 collects the
information-theoretic operationalisations of its complexity type, S5 is its
distributional type. Each stratum operationalises an established construct
(morphological richness, lexical diversity, syntactic surface structure,
information-theoretic complexity, inter-segment cohesion). Five rather than
eighteen cells because sparse cells cannot support stable PCA — S4 already has
only 20 features — while a coarser partition would reunite heterogeneous
covariance structures, recreating the dominance problem stratification
prevents. Assignment is deterministic (first-match-wins keyword patterns,
priority S4→S5→S1→S2→S3), hence fully reproducible and fully audited: the
complete 327-family enumeration is machine-generated from the fitted artifact
(`analysis/stratum_audit.py` → verified totals 2,726/327/63), and the S3
catch-all was audited in full — all 151 families are genuinely
structural/syntactic; nothing falls through
(`drafts/stratum_audit_appendix.tex`, "Audit of the S3 Catch-All").

**Quirk to state proactively if strata come up:** Zipf *frequency*-based
measures (frequent/infrequent word) sit in S2 (lexical sophistication); Zipf
*steepness/goodness-of-fit* sit in S4 (distribution shape). Defensible, but
say it before the examiner finds it.

**⚠️ Status gap (must fix before viva):** the bridging table and audit
appendix live in `Thesis Template Legit\drafts\stratum_bridging_table.tex` and
`drafts\stratum_audit_appendix.tex` and are **not yet `\input`** into the
thesis. Adopting them requires the consistency edits in "Known traps" below.
If they have not landed by the viva, this answer must be given verbally
without citing the appendix.

## Q7. "Did you ablate stratified vs global PCA? How do you know stratification helps?" — CONCEDE-GRACEFULLY

**Concede first.** No — that ablation was not run, and the thesis says so:
the limitations section states that stratum-weight refinement and a
stratification ablation are "deferred … rather than attempted on an
under-powered case base" (`methodology_chapter.tex:405`). With 17 cases the
ablation could not be concluded reliably in either direction.

**Then defend the design on external evidence** (`methodology_chapter.tex:213`):
the structural mechanism (heterogeneous within-group covariance defeats a
single global projection; Shi et al. 2024) is confirmed empirically in domains
with the same structure — SuperPCA (Jiang et al. 2018: per-region PCA yields
higher first-to-second eigenvalue ratios and beats global PCA on three public
hyperspectral datasets) and Segmented-PCA (Fu et al. 2022). What *was*
validated end-to-end: the stratified fingerprints are stable (re-identification
12/17 top-1) and carry actionable signal (beats every constant policy).

**Options open as of 2026-07-12:** the ~1-day ablation (swap global PCA into
the validation loop; pattern in `analysis/ablation_k.py`) is still on the
open-items list, and the explicit deferral sentence is *commented out* at
`methodology_chapter.tex:215` — either run the ablation or reinstate the
sentence before submission. Do not claim in the viva that the deferral is
stated in §3.5.2 unless that comment has been reinstated; the live anchor is
the limitations bullet (`:405`).

## Q8. "The same features build the knowledge base and characterise queries. Isn't that circular?" — CONCEDE-GRACEFULLY

**Concede first.** Yes — the thesis names this "representation circularity"
(`methodology_chapter.tex:406`): any systematic bias in feature extraction is
inherited on both sides of the comparison, and the held-out evaluation tests
recommendation quality *under*, but cannot fully isolate, the shared
representation.

**Then scope it.** The circularity is symmetric: a systematic extraction bias
shifts query and case fingerprints identically, so the *between-corpus*
comparisons that retrieval relies on are preserved — the same argument the
thesis makes for annotation-convention bias in the Dutch ground-truth analysis
(`design_and_implementation.tex:200`). Crucially, the evaluation criterion is
external to the representation: recommendations are scored against measured
model performance (ground-truth F1 of every candidate on the held-out split),
not against anything derived from the features. A circular representation
that carried no real signal would not beat 100,000 random policies or every
constant policy.

## Q9. "n = 17. How can any statistical claim survive that?" — LOAD-BEARING (as scoped)

**Strong answer.** By scoping the claims to what n=17 supports and using
small-sample-honest statistics throughout: Wilson intervals on every
proportion (top-1: [6.2%, 41.0%]; non-zero-confidence 2/2: [34.2%, 100%]),
an exact one-sided hypergeometric test for the confidence split (p = 0.0221,
explicitly called "fragile"), and an explicit *refusal* to compute a Pearson
correlation on a degenerate confidence distribution
(`demonstration_and_evaluation.tex:242`). The headline comparative claims are
not sample estimates at all: "beats every constant policy" is a complete
enumeration of all 103 constant policies from the benchmark matrix, and the
random baseline is a 10⁵-policy seeded Monte-Carlo in which zero policies
reached the framework's mean regret (P(3 exact matches by chance) =
5.0×10⁻⁴). And 17 is the *meta-level* n; each case rests on a full
cross-benchmark of 105 model variants (the underlying record count is in
`benchmark_metadata.json` — re-verify before quoting a figure). The evaluation
claims within-corpus generalisation only, stated in limitations
(`methodology_chapter.tex:409`; conclusion limitation 2).

**Concession.** Confirmatory power is limited; the reserved 15% validation
splits exist for a frozen-protocol re-run (outstanding as of 2026-07-12 —
`\candidatetodo` at `demonstration_and_evaluation.tex:117`). If run by viva
time, cite it; if not, name it as designed-but-pending.

## Q10. "17.6% top-1 accuracy. Isn't your system simply wrong 82% of the time?" — LOAD-BEARING

**Strong answer.** No — that reading treats a graded problem as binary. The
deployed-model cost is regret: mean 0.0078 (0.78 F1 points from optimal),
median 0.0022, worst case bounded at 0.0489 across all 17 evaluations — never
catastrophic. Against that: random selection costs 0.3830 (~49× worse), the
best constant policy 0.0127 (framework 1.6× better), the strongest zero-shot
default 0.0175. Exact-match is also 18× the 0.95% chance level. The k-ablation
proves the low top-1 is a *chosen* trade, not a defect: k=1 gets 47.1%
exact-match but with mean regret 0.0784 and worst case 0.8766 — an 87.7-point
collapse when retrieval misses. k=3 IDW sacrifices exact-match for a tenfold
mean-regret and eighteenfold worst-case reduction
(`demonstration_and_evaluation.tex:234`) — bounding worst-case harm is the
right priority for a deployment recommender. The thesis elevates this to a
contribution: regret, not strict accuracy, is the valid criterion for
meta-recommenders in high-accuracy regimes (conclusion contribution 3).

**Concession.** In 6 of 8 paradigm misses the engine over-recommends the
generalist XLM-V Base where a trained specialist wins
(`demonstration_and_evaluation.tex:142`); the failure analysis attributes
this to OpenLID-v2's centrally located fingerprint dominating sparse
neighbourhoods — expected to dilute as the MKB grows.

## Q11. "Is your confidence score calibrated?" — LOAD-BEARING on honesty; the signal itself is conceded

**Strong answer.** No, and the thesis never claims it is. C is a *consensus
index* — the fraction of the k neighbours whose own best model matches the
recommendation (Eq. `eq:consensus_index`, `methodology_chapter.tex:252`) — and
is explicitly "a consensus measure, not a calibrated probability of
correctness" (`:256`). Empirically the pattern is supportive: both non-zero-
confidence recommendations were correct (2/2) vs 1/15 at zero confidence;
exact one-sided p = 0.0221 — nominally significant but resting on two
observations, so "promising rather than established"
(`demonstration_and_evaluation.tex:242`). 15/17 zero-confidence outcomes are
themselves diagnostic of MKB sparsity: with 17 fingerprints, neighbours beyond
the re-identified source corpus usually carry different best models. Practical
use is honest too: at zero confidence, treat the output as a shortlist — the
top-3 contains a near-optimal candidate (≤0.5pp) in 12/17 cases.

**Never say:** "calibrated confidence", "the confidence is validated". The
in-thesis disclaimers are the ceiling. (One cosmetic trap: the phrase
"well-calibrated recommendations" at `design_and_implementation.tex:566` is
about length-regime coverage, not the signal — know it exists in case the
examiner quotes it; consider rewording before submission.)

## Q12. "Chapter 1 uses code-switching to motivate the problem — then you never handle it." — CONCEDE-GRACEFULLY

**Answer.** The live text already draws the line: code-switching is "cited
here as evidence of the breadth and difficulty of the short-text LID
challenge; handling them is a distinct token-level sequence-labelling task and
lies outside the scope of this thesis" (`introduction_chapter.tex:51`), with
the scope narrowing argued at `methodology_chapter.tex:16` and code-switching
named first among future-work extensions (conclusion `:138`). The task
formulation differs categorically: this thesis does document-level,
single-label selection; code-switching needs multi-label/token-level
reformulation plus a code-mixed benchmark that does not exist for this
language set (fuller argument exists in a commented paragraph at
`methodology_chapter.tex:20` — usable verbally). Nuance to have ready: the
dataset-selection *noise* criterion lists code-mixing as a noise property
(`methodology_chapter.tex:305`) — i.e., code-mixed noise is represented in the
data profiles even though the *task* stays single-label. That is consistent,
but say it precisely.

## Q13. "Why spaCy and not stanza — Lingualyzer itself uses stanza?" — LOAD-BEARING on the decision

**Strong answer.** The initial implementation *was* stanza-backed (matching
Lingualyzer). An empirical like-for-like timing test — identical 100
Europarl segments per language across 5 typologically varied languages,
~8,400 tokens, near-identical tokenisation (8,427 vs 8,426), single-process
CPU, warm-up excluded — measured stanza at 289 tokens/s vs spaCy at 5,570
(~19× faster; `design_and_implementation.tex:81-98`, `tab:spacy_vs_stanza`).
At that throughput stanza is impractical for the framework's interactive use
(full 24-language profile <6 min on CPU with spaCy, `:110`). The measure
definitions were ground-truth-verified on the stanza backend first (same
conventions as Lingualyzer) and then re-used by the spaCy production
pipelines. The cost is owned: the 24-language constraint follows from
official spaCy model availability (conclusion limitation 4).

**Concession.** Annotation *accuracy* was not compared head-to-head (spaCy sm
pipelines, NER disabled, vs stanza's fuller stack) — the decision is
throughput + coverage; annotation-convention dependence is mitigated by the
fixed-pipeline-per-language design (Q14).

## Q14. "Your Dutch ground-truth agreement is only 89.5%. What does that say about your features?" — LOAD-BEARING core argument

**Strong answer.** The pattern is diagnostic, not damning
(`design_and_implementation.tex:158-200`). English: 351/351 exact — the
measure *arithmetic* is correct. All 37 Dutch disagreements involve measures
depending on token-level annotations, concentrated in families where the Dutch
pipeline tagged none of the annotator-marked constructions (adverbs 12,
demonstratives 6, passive voice 6, interrogatives 6, unknown-word position 2,
singleton ratio/length 5; `tab:groundtruth_dutch_disagreements`). So the
divergence is annotation-*convention* difference, not implementation error —
and it would apply to any backend. The mitigation is architectural: every
corpus is profiled by the same fixed pipeline per language, so a systematic
tagging convention shifts all fingerprints identically and preserves the
between-corpus comparisons retrieval depends on. The verification even
corroborates the schema design: 4 of the 24 excluded measures are among the
Dutch disagreements.

**Concession.** The bias-cancellation argument holds *within* a language;
across languages, annotation-dependent features inherit per-language model
quality differences, so cross-language comparability is weaker for those
features. That is part of why the framework is scoped to 24 mature-tooling
languages.

## Q15. "What can you actually claim beyond 24 languages, 17 corpora, and 120-character texts?" — CONCEDE-GRACEFULLY

**Answer.** Very little — deliberately, and the thesis says so at every
level. The evaluation establishes **within-corpus generalisation** (fresh
disjoint samples of known corpora), not novel-corpus generalisation
(`methodology_chapter.tex:409`; conclusion limitation 2). The short-text
regime is enforced by construction: 120-char word-boundary truncation (40 for
CJK), floors 30/10 (`design_and_implementation.tex:465`) — so no claim extends
to long-form text. Language scope is bounded by spaCy model availability;
low-resource exclusion is named "a significant limitation and the primary
direction for future extension" (`methodology_chapter.tex:318`). What *is*
claimed to generalise is the architecture: retrieval needs no retraining to
grow (Retain stage), coverage gains are largest exactly when the base is
small (Leake & Wilson citation, `methodology_chapter.tex:148`), and the
reserved validation splits + frozen protocol exist for confirmatory extension.
Scoping this tightly is DSR discipline, not evasion: one scenario treated
exhaustively rather than five treated shallowly (`methodology_chapter.tex:16`).

---

# Part C — Known traps (examiner reads code AND prose)

An IR examiner who opens the repo can diff prose against artifacts. Fix
before the viva or know the answer cold. Status 2026-07-12:

| # | Trap | Truth | Fix state |
|---|---|---|---|
| T1 | Ch4 S2 bullet says types-per-lemma is in S2 (`design_and_implementation.tex:226`) | Fitted artifact assigns all 25 types-per-lemma features to **S1** (better construct fit: paradigm size ≈ morphological richness) | ❌ OPEN — edit bullet + `feature_stratifier.py` docstring |
| T2 | `feature_stratifier.py` docstring lists "Honoré's statistic" in S2 | No Honoré feature exists in the 2,726 core set; pattern never fires. (Thesis prose is consistent: Honoré listed among 24 *excluded* measures, `design_and_implementation.tex:153`) | ❌ OPEN — remove from docstring |
| T3 | S2 pattern list contains `word entropy`, `letter entropy` (`feature_stratifier.py:120-121`) | Dead patterns — S4's `entropy` always matches first | ❌ OPEN — delete |
| T4 | "well-calibrated recommendations" (`design_and_implementation.tex:566`) | About length-regime coverage, not the confidence signal | Loose wording — reword or be ready to explain |
| T5 | LLM baseline named in EQ3 but absent from results | `analysis/llm_baseline.py` exists, never run; decision = RUN; `\candidatetodo` at `demonstration_and_evaluation.tex:117` and conclusion `:55,:114` own it | ❌ OUTSTANDING — run before submission or defend the owned limitation |
| T6 | Stratified-vs-global-PCA deferral sentence commented out (`methodology_chapter.tex:215`) | Live anchor is only the limitations bullet (`:405`) | Reinstate or run ablation (Q7) |
| T7 | Live `\candidatetodo`s in Ch3 (e.g. Beyer/Aggarwal check, `:209`) | TODO margin notes compile visibly | Sweep before submission |
| T8 | drafts/ stratum tables not `\input` | Q6's appendix citation only works after adoption | Adopt with T1–T3 edits in same commit |
| T9 | Zipf family split across S2/S4 | Deliberate; state proactively (Q6) | No fix — narrative ready |
| T10 | Ledger p=0.063 vs thesis p=0.0221 | 0.0221 is current (verified by script AND .tex) | Never quote 0.063 |

---

# Part D — Viva mechanics

## Using the dashboard as demonstration support

The Streamlit dashboard (5 panels, live inference via ModelRunner, UMAP
fingerprint walkthrough, baseline comparison) is the strongest possible answer
to "show me how a practitioner uses this" and makes the interpretability
claims (Q1, Q3) tangible — `trace_query()`-style evidence on screen beats
assertion. Launch: from the repo root,
`streamlit run src/lid_toolkit/explainer/dashboard.py` (env
`C:\Users\User\miniconda3\envs\thesis_final\python.exe`). **For the full demo
script, panel-by-panel talk track, and failure-recovery steps, load the
sibling skill `dashboard-demo-runbook` — do not improvise a demo from this
skill.** Rule: rehearse the demo end-to-end on the viva machine ≤48h before;
have static screenshots as fallback if the live app cannot run.

## Pre-viva re-verification (mandatory, within 7 days of the viva)

Every number quoted in the defense must be re-verified against artifacts
within one week of the viva. From the repo root
(`c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit`):

```powershell
# 1. Headline validation figures — expect: 3/17 (17.6%), mean gap 0.007803,
#    random 0.3832, constant 0.0127 / 0.0175, MRR 0.203, p = 0.0221,
#    Wilson [6.2%, 41.0%], re-identification 12/17 & 14/17
& C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\validation_statistics.py

# 2. Stratum numbers — expect totals 2,726 / 327 / 63
& C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\stratum_audit.py

# 3. Confirm the report artifact in use is current (not an *_old_* snapshot)
Get-ChildItem validation_report*.json | Sort-Object LastWriteTime
```

Figures must match `validation_report.json` (repo root) — if the script and
the thesis .tex disagree, STOP: the thesis needs an erratum before the viva,
and the number as printed by the script is what you defend. If the LLM
baseline (T5) or the frozen-protocol validation run has landed since
2026-07-12, add their figures to the canonical table above after verifying.

## Answer discipline

- Lead with the direct answer (one sentence), then the evidence, then the
  scoped limitation. Never open with the concession on a LOAD-BEARING item.
- For CONCEDE-GRACEFULLY items, concede in your first sentence — the thesis
  already owns each of these limitations in writing; point to where.
- Quote only numbers from the canonical table (post-re-verification). If you
  don't know, say "that analysis was not run; here is what was run instead."

## When NOT to use this skill

- Writing/editing thesis prose or deciding claim strength → `evidence-standards`
  and `thesis-writing-and-style`.
- Running a structured chapter review → `thesis-review-protocol`.
- Tracing a specific number to its artifact → `artifact-verification-playbook`.
- Executing the live dashboard demo → `dashboard-demo-runbook`.
- Framework internals reference (API, file map) → `lid-framework-reference`.
- Submission logistics/progress report → `thesis-completion-campaign`.

## Provenance and maintenance

- Authored 2026-07-12. Every thesis locator verified against the compiled
  chapter set resolved from `Thesis Template Legit\thesis.tex` that day;
  headline figures verified by running `analysis\validation_statistics.py`
  and `analysis\stratum_audit.py` (outputs matched the .tex).
- Volatile facts (re-check before relying): T1–T8 fix states; whether
  `drafts\stratum_*.tex` have been adopted
  (`Select-String -Path "..\..\..\..\..\Thesis\Thesis Template Legit\appendices\appendices.tex" -Pattern "stratum_audit"`
  — use the absolute path); whether the LLM baseline and frozen-protocol
  validation have run (look for new rows in `tab:baseline_comparison` and new
  results files newer than `validation_report.json`).
- One-line re-verification: run the two scripts in "Pre-viva re-verification";
  grep the thesis for resurrected stale claims:
  `Select-String -Path "c:\Users\User\OneDrive\Masters\Thesis\Thesis Template Legit\chapters\*.tex" -Pattern "calibrated confidence|five model families|3,?066|p = 0\.063"`
  (expect zero live hits).
- Ledger figure "2/3 vs 1/14, p=0.063" is superseded — do not reintroduce.
