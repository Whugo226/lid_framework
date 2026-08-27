---
name: evidence-standards
description: >-
  Load this whenever you are about to ASSERT, WRITE, or STRENGTHEN an empirical
  claim in the LID-toolkit MEng thesis — any sentence that reports a number,
  compares against a baseline, calls a result "significant"/"calibrated"/
  "outperforms", or decides whether a finding is strong enough to enter a
  chapter. It defines what counts as examiner-safe proof: which statistical
  methods are actually implemented in analysis/*.py and how to read each, the
  thesis's own evidence conventions (regret, random/constant/LLM baselines,
  confidence-stratified analysis, small-n honesty phrasing), the six codified
  rules for admitting a result, and the hard claim ceiling on the confidence
  signal (never "calibrated"). Use it BEFORE writing an evidential sentence, not
  after. Do NOT use it to run a chapter re-review (that is thesis-review-protocol)
  or to trace a single number back to its artifact file (that is
  artifact-verification-playbook) — this skill governs evidence QUALITY and the
  claim ceiling, not review process or artifact-tracing mechanics.
---

# Evidence Standards — what counts as proof in this thesis

You are writing an MEng thesis (submission 2026-09-01, oral defense, external
examiner an information-retrieval expert, target grade ≥75%). An examiner will
challenge every empirical sentence. This skill is the standard every such
sentence must clear. It is a Master's thesis, **not** a journal submission or a
technical manual — calibrate rigour to that bar (do not over-engineer statistics
the design cannot support), but never overstate a claim beyond what the
evaluation demonstrates.

Definitions used throughout (each defined once):
- **Regret / performance gap (Δf1):** oracle-best model's `f1_weighted` score
  minus the recommended model's score on the same held-out split. Non-negative
  by construction; 0 = perfect recommendation. The thesis's primary validity
  metric (strict top-1 accuracy is the conservative secondary metric).
- **Constant policy:** "always recommend model X regardless of query" — the
  best-on-average heuristic. The strongest naive competitor a query-adaptive
  framework must beat.
- **MKB:** meta-knowledge base — the 17-dataset case base of fingerprints +
  performance records the recommender retrieves over.
- **n = 17:** the entire evaluation is 17 held-out splits. Everything here is a
  small-n regime. Point estimates without an interval or exact test are
  inadmissible at this n.

---

## 1. Statistical methods ACTUALLY implemented (confirmed by running the code, 2026-07-12)

Ground truth: the three scripts below were read line-by-line and
`validation_statistics.py` was executed against the live `validation_report.json`.
The numbers in the "live output" column are what the code prints today. Do not
cite any statistic the code does not compute.

### 1a. `analysis/validation_statistics.py` — the offline statistics engine

Pure read of `validation_report.json` (no new experiments; writes nothing). Run:
`C:\Users\User\miniconda3\envs\thesis_final\python.exe analysis\validation_statistics.py`
from the repo root. Live output (2026-07-12) confirmed below.

| # | Method implemented | What it IS | How to read it | Live output |
|---|---|---|---|---|
| [1] | Chance level + analytic random-policy mean gap | Deterministic expectation, not a test | Context floor. "18× chance" is a ratio, not significance | chance exact-match 0.95%; random-policy mean gap 0.3832 |
| [2] | Constant-policy sweep | Enumerates every universally-available variant as an "always pick X" policy; counts how many beat the framework | If **0** policies beat the framework's mean gap, the query-adaptive signal is real | 103 policies; best `fasttext_subword_exorde` 0.0127, `xlm_v_base` 0.0175; **0** beat framework 0.0078 |
| [3] | Top-k accuracy + **MRR** (Mean Reciprocal Rank) | MRR = mean of 1/rank of the ground-truth model in the IDW ranking | Shortlist quality: MRR≈0.2 ⇒ GT model sits ~rank 5 on average | top-1/3/5 = 3/17; MRR 0.203 |
| [4] | **Wilson score 95% CI** + **exact hypergeometric (one-sided) test** | Wilson = small-n-safe binomial interval (never exceeds [0,1], unlike normal-approx). Hypergeometric = Fisher-style exact p for the 2×2 confidence/correctness split | Wilson is mandatory for every proportion at n=17. The exact p is the ONLY defensible test for the 2/2-vs-1/15 split (no asymptotics) | non-zero-conf **2/2** correct, zero-conf **1/15**; one-sided **p = 0.0221**; Wilson accuracy 3/17 **[6.2%, 41.0%]**; Wilson 2/2 **[34.2%, 100%]** |
| [5] | Corpus re-identification rate | Counts query source-corpus as top-1 / top-3 neighbour | Fingerprint-stability test (precondition for retrieval to work) | top-1 12/17, top-3 14/17 |

`wilson(k, n, z=1.96)` is hand-implemented (lines 23-28): centre
`(p + z²/2n)/(1+z²/n)`, half-width `z·√(p(1-p)/n + z²/4n²)/(1+z²/n)`. The
hypergeometric p (lines 84-87) sums `comb(K,i)·comb(n-K,m-i)/comb(n,m)` over the
upper tail `i = x … min(K,m)` — the exact one-sided Fisher probability of ≥x
correct among the m non-zero-confidence draws.

> 🛑 **SUPERSEDED 2026-07-31 — this whole subsection describes a retired pipeline.**
> `validation_statistics.py` reads `validation_report.json` (2026-05-14), which
> predates the **coverage-guard correction (2026-07-17)** and the
> **reporting-measures rework (2026-07-21)**. It still prints 3/17, 0.0078 and
> the 2/2-vs-1/15 confidence split. **Chapter 5 no longer uses any of it.**
>
> The live source of record is **`analysis\reporting_measures_2026-07-21.json`**
> (generator `analysis\reporting_measures.py`). Current condition-A figures:
> mean range capture **99.18%** (min 96.89%), mean regret **0.007287**, strict
> top-1 **2/17**, max regret **0.0259**. Two further conditions now exist:
> B (reserved validation splits) and C (leave-one-corpus-out refit, the
> generalisation bound — 0/17, regret 0.0160).
>
> **The confidence result is retracted, not merely restated.** It "did not
> survive the coverage-guard correction"; under corrected inventories 13 of 17
> evaluations receive non-zero confidence and Ch5 reports the signal as
> **untested on this sample**. The §4 claim ceiling below is therefore LOWERED,
> not unchanged — see the notice in §4.
>
> The table below is retained only because rows [1], [2] and [5] (chance level,
> constant-policy sweep, corpus re-identification) are still methodologically
> sound descriptions of how those quantities are computed. Do not cite its
> numbers.

### 1b. `analysis/random_baseline_mc.py` — Monte-Carlo random baseline (EQ3 floor)

A **genuine simulated experiment**, not an analytic shortcut: `T = 100,000`
seeded trials (`--seed 42`), each drawing one variant uniformly at random from
every dataset's pool and recording the whole policy's mean/max gap. Yields the
full sampling distribution of the random policy. Writes
`random_baseline_mc_results.json` (already present, dated Jul 10 — do not
regenerate unless the report changes; regeneration mutates the estate).

| Quantity | What it IS | Live value (results JSON) |
|---|---|---|
| Analytic expected gap | Closed-form check the MC must reproduce | 0.38325 |
| MC per-trial mean gap | Sampling distribution centre + spread | 0.3830, sd 0.0669, 95% [0.2524, 0.5135], min 0.1314 |
| MC per-trial **max** gap | Worst-case a random policy inflicts | median 0.892 |
| Exact-match count | Expected exact IDs per random trial | analytic 0.162, MC 0.163 |
| P(≥ framework's 3 exact) | Chance of matching the framework's 3 exact hits | 5.0×10⁻⁴ |
| P(trial mean ≤ framework 0.0078) | Chance a random policy is as good as the framework | **0.0** over 100k trials |

Interpretation: report the **whole distribution and its 95% interval**, never
just the mean. "Not one of 100,000 random policies matched the framework, and
the best managed 0.1314" is the examiner-safe phrasing — it quantifies the floor
with its spread, not a bare average.

### 1c. `analysis/ablation_k.py` — neighbourhood-size ablation (k=1 vs k=3)

A **sensitivity analysis, not a significance test.** Genuinely re-runs the
`Recommender` engine over `eval_profiles/*.pkl` at k=1 and k=3, scoring against
the ground truth in `validation_report.json`. Reports per k: exact-match
accuracy, mean/max gap, re-identification, min-gap-over-top-3. Thesis
(`tab:k_ablation`) reports k=1 → 8/17 (47.1%), mean 0.0784, max 0.8766 vs k=3 →
3/17, 0.0078, 0.0489.

- **Purpose:** isolate the contribution of IDW aggregation. It demonstrates a
  *deliberate trade-off* — k=1 doubles exact-match accuracy but at 10× mean
  regret and a catastrophic 87.7pp worst case. This is the mechanism that
  explains the low strict accuracy (see §3 rule 2).
- **Caveat to state:** the thesis prose frames the k=1 numbers as
  "re-analysed from the recorded validation run," while `ablation_k.py` is a live
  engine re-run. Both should agree; if you re-run and they diverge, treat the
  divergence as a finding, not a rounding issue.

**One-line rule:** [1], [2], [5] and 1c are *descriptive/context* evidence;
[3] MRR is *ranking* evidence; [4] Wilson + hypergeometric and 1b's MC
distribution are the only *inferential* statistics in the thesis. Do not upgrade
a descriptive number into an inferential claim.

---

## 2. Established evidence conventions (from the thesis's own statistics sections)

Extracted from `chapters/demonstration_and_evaluation.tex` and
`chapters/methodology_chapter.tex` (`subsec:recommendation_eval`,
`sec:confidence_calibration`, `sec:failure_analysis`). Match these conventions
exactly when adding evidential prose.

1. **Range capture leads; regret second; strict accuracy is a strictness check.**
   (Reordered 2026-07-21.) Lead with mean range capture **99.18%** (worst case
   96.89%), then mean Δf1 **0.0073** (median 0.0029, max 0.0259). Strict
   exact-match is now **2/17** and is explicitly demoted — never a standalone
   headline, and never the lead.
2. **Baselines are now tiered, and the LLM arm IS DONE.** The chapter groups them
   by whether a practitioner could pick them in advance: *uninformed* — random
   Monte-Carlo 0.3830, blind constant pick 0.3902; *realistic defaults* — LLM
   `gpt-oss-120b` 0.0823, CLD3 0.0305, `lid.176` 0.0207, XLM-V 0.0175;
   *hindsight upper bound* — best constant policy 0.0127. Framework 0.0073.
   The LLM baseline has been **executed** (51 Groq calls, 3 draws × 17); the old
   "decision=RUN, not yet executed" note is retired.
3. **Confidence signal: UNTESTED — do not scope it, disclaim it.** The
   2/2-vs-1/15 result is retracted; it did not survive the coverage-guard
   correction. Under corrected inventories 13 of 17 evaluations carry non-zero
   confidence and 4 carry zero. Ch5's own words are now the ceiling: no scenario
   provides evidence the signal is informative, two were underpowered to do so
   at any outcome, and evaluation "requires a materially larger held-out set
   than the present 17 queries." Reproduce that, not "promising."
4. **The significance boundary is the thing to get right.** Paired sign tests
   (condition A): the framework beats CLD3 (17-0), XLM-V (**p = 0.0029**) and
   the LLM (**p = 0.000107**) significantly; it does **not** significantly beat
   the hindsight-chosen best constant policy (**p = 0.0645**) and is level with
   `lid.176` (8-9, p = 0.0478 nominal). Never write that the framework
   significantly outperforms the best constant policy.
5. **Failure cases sit beside the aggregates.** Every aggregate in the chapter is
   accompanied by its failure mode. An aggregate without its failure discussion
   is incomplete. (The specific worst case moved: max regret is now 0.0259, not
   the old 0.0489 Tweet Sentiment figure — re-read the chapter for the current
   named failure before citing one.)
5. **Small-n honesty phrasing (copy the register, not just the fact):**
   - "reflects the small evaluation sample" / "Wilson interval … reflects the
     small evaluation sample"
   - "promising rather than established" · "best-effort support signals rather
     than calibrated confidences"
   - "establishing calibration statistically will … require a larger evaluation
     sample than the present 17 queries"
   - Two qualifications bound every headline claim: (i) within-corpus
     generalisation only; (ii) improvement path is MKB expansion, not algorithmic.

---

## 3. The six codified rules (apply to every result before it enters the thesis)

| # | Rule | Why (incident it prevents) |
|---|---|---|
| 1 | **Hypothesis predicts the numbers BEFORE the run.** State the expected direction/magnitude first; then the experiment confirms or refutes it. No post-hoc story fitted to whatever came out. | Post-hoc narratives are unfalsifiable and an examiner spots them. |
| 2 | **One mechanism explains ALL observations, including negatives.** The generalist-neighbour-dominance mechanism must explain the successes (re-identification → correct), the misses (OpenLID-v2 outvotes specialist), AND the k-ablation trade-off. If a negative needs a *separate* excuse, the mechanism is wrong. | A theory that only explains the wins is confirmation bias. |
| 3 | **Claims scoped to exactly what the evaluation demonstrates.** "Within-corpus generalisation," not "generalisation." "Outperforms every constant policy over these 103 variants," not "outperforms all baselines." Name the boundary in the sentence. | Overclaim beyond the design is the fastest way to lose examiner trust. |
| 4 | **Every point estimate at small n carries a Wilson interval or an exact test.** A bare proportion (3/17, 2/2) is inadmissible. Attach `[6.2%, 41.0%]` or `p = 0.022`. | n=17 estimates are wide; hiding the width misrepresents certainty. |
| 5 | **Failure cases discussed alongside aggregates.** Ship the worst case and its mechanism in the same section as the mean. | See convention 4 — aggregates alone flatter the system. |
| 6 | **Admission gate — a result enters the thesis ONLY with all three:** (a) a **saved artifact** on disk behind the number, (b) the **appropriate statistic** for the sample size (Wilson/exact/MC distribution, not a normal approximation), (c) an explicit **limitation statement**. Missing any one ⇒ the result stays out. | The 3,066-vs-2,726 error survived drafts because it was never traced to an artifact (rule a); small-n splits were once reported bare (rule b); overclaims lacked scope (rule c). |

Admission-gate checklist (tick all three or do not write the sentence):
- [ ] **Artifact:** the number is reproducible from a file in the repo
  (`validation_report.json`, `random_baseline_mc_results.json`, `mkb.pkl`, a
  `*.pkl` profile) — see `artifact-verification-playbook` for the trace.
- [ ] **Statistic:** Wilson CI for proportions; exact hypergeometric for the 2×2
  split; full MC distribution (not just mean) for the random baseline; ratios
  (e.g. "18× chance") labelled as ratios, not tests.
- [ ] **Limitation:** the sentence (or its paragraph) names the boundary —
  small n, within-corpus only, fragile estimate, or MKB-expansion caveat.

---

## 4. The claim ceiling (hard limits — an examiner will probe these first)

**Never write "calibrated confidence" or call the confidence signal
"calibrated."** It is a **consensus signal** (fraction of the k=3 neighbours
agreeing on the best model).

> ⚠️ **The ceiling was LOWERED on 2026-07-21 — it is no longer "promising."**
> The favourable 2/2-vs-1/15 association did not survive the coverage-guard
> correction. Ch5 now reports the signal as **untested on this sample**: across
> every configuration examined, and on the reserved validation splits, no
> scenario provides evidence that it is informative, and two could not have
> provided such evidence at any outcome given only one or two non-zero
> observations. Under corrected inventories the split is **13 non-zero / 4 zero**,
> not 2/15.
>
> **Permitted:** "untested on this sample", "requires a materially larger
> held-out set than the present 17 queries", "a measure of neighbourhood
> agreement, not a calibrated probability".
> **Now forbidden (it was permitted before):** "promising rather than
> established", "promising support", "nominally significant", any citation of
> p = 0.022 or the 2/2-vs-1/15 split.

The thesis's own current words are the ceiling — restate, never exceed:

- `methodology_chapter.tex` (consensus-index paragraph): the IDW weighting and
  consensus index "should be read as **best-effort support signals rather than
  calibrated confidences**." (Still accurate.)
- `demonstration_and_evaluation.tex` §Confidence: "It is a measure of
  neighbourhood agreement, **not a calibrated probability** that the
  recommendation is optimal… The signal is therefore reported as **untested on
  this sample**."

Line numbers in this section were accurate at 2026-07-12 and have since drifted
— anchor on the quoted text, and re-grep before citing a locator.

Note: the section is *titled* "Confidence Calibration" and the design *asks
whether* the signal is calibrated — that framing is fine. What is forbidden is
*asserting* it IS calibrated. Discuss calibration as an open question; never as
a settled property.

**VERIFIED evidence vs directional support — the distinction to keep sharp:**

Rebuilt 2026-07-31 against the post-coverage-fix artifacts. A third column is
now needed, because some claims that were "directional" have become
**unsupported** — they are not to be hedged, they are not to be written.

| VERIFIED (state plainly) | DIRECTIONAL (hedge explicitly) | UNSUPPORTED (do not write) |
|---|---|---|
| Mean range capture 99.18%, worst case 96.89% | The k-ablation trade-off "will improve with MKB expansion" | The confidence signal discriminates correct from incorrect |
| Mean regret 0.0073 beats every baseline tier | Range capture will hold on corpus types absent from the MKB | Non-zero confidence ⇒ more reliable recommendations |
| No random policy in 100k trials matched the framework (P≤framework = 0.0) | Larger MKB narrows the gap to the oracle | Any citation of p = 0.022 or the 2/2-vs-1/15 split |
| Framework beats XLM-V (p = 0.0029) and the LLM (p = 0.000107) | | That the framework significantly beats the best constant policy (p = 0.0645 — it does not) |
| LLM baseline mean gap 0.0823 vs framework 0.0073, 14-2-1 paired | | Any statement that the confidence is a probability or calibrated |
| Leave-one-corpus-out: 0/17 exact, regret 0.0160, 98.21% capture | | That strict top-1 accuracy is the headline metric (it is a strictness check) |

Left column = confirmed by artifact + appropriate statistic; write as fact.
Middle = supported in direction only at n=17; always carries "suggestive",
"directional", or "expected to improve as the MKB grows". Right column = the
evidence was examined and does not support the claim; hedging does not rescue
it.

---

## 5. When NOT to use this skill

- **Running a chapter re-review** (finding + fix + locator, read-only) → use
  `thesis-review-protocol`. This skill sets the evidence bar; that one audits
  against it.
- **Tracing one number to its artifact file** (which `.pkl`/`.json`, how to
  load it, MKB API quirks) → use `artifact-verification-playbook`.
- **Stratum/feature counts, PCA config, S1–S6 semantics** → use
  `lid-framework-reference`.
- **General prose style, hedging register beyond evidence, house LaTeX** → use
  `thesis-writing-and-style`.
- **Defending the design orally (IR-framed questions)** → use
  `examiner-defense-pack`.
- Non-empirical prose (motivation, related work, method description with no
  numeric claim) — no evidential sentence, no need for this skill.

---

## 6. Provenance and maintenance

**§1a, §2, §4 and the VERIFIED/DIRECTIONAL/UNSUPPORTED table were regenerated
2026-07-31.** §1b, §1c, §3 and §5 still carry their 2026-07-12 verification.

- **Live source of record:** `analysis\reporting_measures_2026-07-21.json`
  (generator `analysis\reporting_measures.py`). Read the artifact:
  `Get-Content analysis\reporting_measures_2026-07-21.json`. Condition A is the
  headline — range capture 99.18/96.89, regret 0.007287, top-1 2/17, rank mean
  6.4. Conditions B (validation splits) and C (leave-one-corpus-out) sit
  alongside it, plus `llm_baseline` and `paired_framework_vs_policy`.
- 🛑 **`analysis\validation_statistics.py` is SUPERSEDED for headline figures.**
  It reads `validation_report.json` (2026-05-14), which predates the
  coverage-guard correction, and still prints 3/17 / 0.0078 / 2-2-vs-1-15.
  Its chance-level and constant-policy *methods* remain valid; its numbers do
  not. Do not quote its output.
- **Monte-Carlo baseline artifact:** `random_baseline_mc_results.json` (repo
  root; 100k trials, seed 42) — **still current and unchanged**. Regenerate ONLY
  if the report changes: `python analysis\random_baseline_mc.py` (this WRITES
  the file — a mutation; do not run casually).
- **Superseded numbers to watch (three generations now):** 2/3-vs-1/14 p=0.063
  → 2/2-vs-1/15 p=0.022 → **retracted entirely**. Also retired: 3/17 / 17.6% /
  0.0078 / max 0.0489 Tweet Sentiment. Any of these in a chapter or draft is a
  stale figure.
- **Claim-ceiling anchors:** line numbers from 2026-07-12 have drifted; re-grep
  rather than trusting them:
  `grep -niE "calibrat|untested on this sample|neighbourhood agreement" "Thesis Template Legit\chapters\demonstration_and_evaluation.tex" "Thesis Template Legit\chapters\methodology_chapter.tex"`
  — expect only disclaimers, never an assertion of calibration.
- **LLM baseline (EQ3 third arm): EXECUTED.** `gpt-oss-120b` (open-weights, via
  Groq), temperature 0.7, 3 repeats × 17 datasets = 51 calls. Mean gap 0.0823,
  median 0.0560, max 0.4182, exact-match 9.8%, self-consistency 0.569; paired
  vs framework 14-2-1, one-sided **p = 0.000107**. Raw:
  `llm_baseline_gptoss.json` (repo root). Note `llm_baseline_MIXED_do_not_use.json`
  sits beside it — the filename is the instruction.
- **Artifacts feeding these scripts:** `validation_report.json` (May 14),
  `eval_profiles/*.pkl` (13 profiles), `mkb.pkl` (current 17-dataset MKB).
