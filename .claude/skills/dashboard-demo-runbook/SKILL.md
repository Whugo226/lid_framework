---
name: dashboard-demo-runbook
description: Runbook for launching and demonstrating the Streamlit explainer dashboard of the LID toolkit (src/lid_toolkit/explainer/dashboard.py) — six-panel inventory, exact launch command, prerequisites, known failure modes with fixes, and a suggested oral-defense walkthrough tuned for an IR-expert external examiner. Load this when the task is "run the dashboard", "demo the toolkit", "prepare the live demonstration for the defense", or diagnosing why the dashboard fails to start or a panel misbehaves. Do NOT load for changing dashboard code (regular dev work — use the codebase directly), for running validation experiments or re-verifying thesis numbers (use artifact-verification-playbook), or for defense Q&A content beyond the demo itself (use examiner-defense-pack).
---

# Dashboard Demo Runbook

The dashboard is a **six-panel Streamlit app** that takes an uploaded text
corpus, profiles it, recommends the best language-identification (LID) model
from a Meta-Knowledge Base (MKB — a pickled store of 17 historical dataset
fingerprints + 1,785 benchmark records), and exposes the full mathematical
trace of the recommendation. It is the thesis's interactive artifact
(demonstrates DSR artifact utility; Ch5 demonstration).

All facts below verified against code and disk on **2026-07-12** unless
labeled otherwise. Runtime behaviour of Streamlit itself is
**static analysis only — unverified at runtime, 2026-07-12** (the app was not
launched during authoring because `streamlit run` blocks).

## Launch procedure

```powershell
cd c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit
& C:\Users\User\miniconda3\envs\thesis_final\python.exe -m streamlit run src\lid_toolkit\explainer\dashboard.py
```

- Run **from the repo root** — the profiler's per-language embedding cache is
  `./fasttext_cache` relative to the working directory
  (`src/lid_toolkit/logic/profiler_knowledge_base.py:172`).
- Env: `thesis_final` (miniconda3, NOT anaconda3).
- Port: Streamlit default **8501** (`http://localhost:8501`); no port is set
  in code. Override with `--server.port 8502` if occupied.
  *(Static analysis only — unverified at runtime, 2026-07-12.)*
- Expected startup: Streamlit banner with Local/Network URLs, browser opens,
  page title "LID Toolkit", sidebar with configuration + upload controls.
  Nothing heavy loads until you click **Analyse Corpus**.

### Visual theme (added 2026-08-12)

The app ships a pinned dark theme in `<repo>\.streamlit\config.toml`: warm
charcoal surfaces (#17181A), one desaturated steel accent (#5E8CA8), colour
reserved for meaning (amber = coverage warning, sage = covered/recommended,
clay = error), small radii, and IBM Plex Sans/Mono. The header comment in that
file states the design rationale — quote it if an examiner asks why the
interface looks the way it does.

Two operational consequences:

* **`config.toml` is found relative to the WORKING directory**, so launching
  from anywhere but the repo root silently drops the whole theme (the app
  reverts to Streamlit's default light look). This is the same reason the
  profiler needs the repo root for `./fasttext_cache`.
* **Font files are resolved relative to the SCRIPT**, not the working
  directory, so they live at
  `src\lid_toolkit\explainer\staticonts\*.woff2` and are served through
  `enableStaticServing`. They are self-hosted precisely so the defence demo
  renders identically with no network.

Streamlit 1.58 rejects per-hue palette keys (`red`, `green`, …) — they log
"is not a valid config option" and are ignored. The tokens the app draws itself
live at the top of `dashboard.py`; keep the two in step if either changes.

### Prerequisites checklist (all ✅ present on this machine 2026-07-12)

| Item | Path / check | Used by |
|---|---|---|
| MKB pickle | `<repo>\mkb.pkl` (8.5 MB; 17 datasets, 24 languages, 1,785 perf records — verified by loading) | everything; default path computed as repo root via `Path(__file__).parents[3]` |
| Profiler LID model | `<repo>\src\lid_toolkit\models\fasttext\lid.176.bin` | DeepProfiler `__init__` — hard `FileNotFoundError` if missing |
| Experiments dir | `C:\Users\User\OneDrive\Masters\LID_experiments` (hardcoded default) | Panel 3 live inference only |
| Trained models | `LID_experiments\model_training\{fasttext,logistic_regression,naive_bayes}\<dataset>\<arch>\` (`model.bin` / `best_pipeline.pkl`) + `off_the_shelf_models\fasttext\lid.176.bin` | Panel 3 |
| Embedding cache | `<repo>\fasttext_cache\` (112 files present) | DeepProfiler per-language embeddings |
| Python deps | streamlit 1.58.0, plotly 6.8.0, pandas 2.3.3, numpy 2.2.5, fasttext, sklearn 1.7.2 — all import OK in thesis_final | — |
| Optional | `umap` — **NOT installed in thesis_final (verified 2026-07-12)** | Panel 2 scatter falls back to PCA (no crash) |

Env-var overrides (read at module import): `LID_STORE_PATH` (mkb.pkl path),
`LID_EXPERIMENTS_DIR`. Both also editable live in the sidebar.

### Pre-flight verification (no launch needed)

```powershell
cd c:\Users\User\OneDrive\Masters\Python\toolkit_dev\lid_toolkit
$py = "C:\Users\User\miniconda3\envs\thesis_final\python.exe"
& $py -m py_compile src\lid_toolkit\explainer\dashboard.py          # parses (✅ 2026-07-12)
& $py -c "from lid_toolkit import LID_Recommender; from lid_toolkit.explainer import ModelRunner; from lid_toolkit.recommender.mkb_store import MKBStore; MKBStore.load('mkb.pkl'); print('OK')"
Test-Path src\lid_toolkit\models\fasttext\lid.176.bin               # must be True
```

### Demo corpus

`<repo>\test_examples\test.csv` — single `text` column, 70,000 rows,
20 languages (WILI-2018-derived). A prior full run on it is written up in
`test_examples\demonstration.md`: recommended
`fasttext_subword_exorde-social-media-december-2024-week1`, confidence 67%
(2/3 neighbours), metric f1_weighted. Non-dashboard equivalent:
`python test_examples\demonstration.py` (same pipeline, console output).
For a snappy live demo, pre-sample a few thousand rows into a smaller CSV —
the profiling spinner itself warns "several minutes for large corpora".

**Ch5 figure corpus (2026-08-12).** `<repo>	est_examples\wili2018_walkthrough_600.csv`
— 600 rows, the same sample `analysis/walkthrough_demo.py` uses, and the corpus
the four Ch5 §5.7.2 dashboard figures were captured on. Cold-start profiling
≈100 s; expect `fasttext_subword_exorde-…` at 33% consensus under `f1_weighted`
and `fasttext_word_multi_eurlex` with an 8-of-24 coverage warning under
`inference_time_ms_per_sample`. Numbers: `analysis/dashboard_session_demo.py`
→ `analysis/dashboard_session_2026-08-12.json`.

## Panel inventory (verified against code and a live run, 2026-08-12)

**The workflow changed on 2026-08-12** (profile-once / re-query-live rework for
Ch5 §5.7.2). Sidebar now holds only setup: MKB path, `LID_experiments` path,
upload CSV/TSV, text column (default `text`), **Profile Corpus**, **Clear
Session**. That button runs `LID_Recommender.profile(texts)` — DeepProfiler
extracts 2,726 features per detected language — and caches the profile in
`st.session_state`.

The **priority metric selector now lives in the main pane**, above the tabs, and
is a live control: changing it calls `LID_Recommender.explain_from_profile()`,
a k-NN lookup over the 17 stored fingerprints that returns in well under a
second, with **no re-profiling**. A banner beside it reports both the one-off
profiling wall-clock and the current query time. Then six tabs:

| # | Tab | Function | Shows |
|---|---|---|---|
| 1 | 📄 Corpus Profile | `_tab_corpus` | **New 2026-08-12.** Metric strip (documents profiled, languages in the lid.176 census, in-scope languages, profiling seconds); census bar chart shaded profiled-vs-out-of-scope; document-length metrics + histogram; fingerprint-composition table (per-stratum raw features / PCs / variance retained, totalling 2,726 → 63) |
| 2 | 📊 Recommendation | `_tab_overview` | Metric strip (recommended architecture + "trained on" caption, **consensus** confidence %, languages covered, query ms); COVERAGE WARNING / UNCOVERABLE banners rendered in the UI (not only in the text explanation); **ranked shortlist** top-5 table (IDW score, neighbours backing, coverage verdict); consensus-confidence gauge (green >= 67%, amber >= 34%, red below) with the "not a probability" caption; winning-model-family donut; top-k neighbour table; horizontal bar of ALL model IDW scores; expander with the full text explanation |
| 3 | 🔍 How It Works | `_tab_walkthrough` | Five expandable steps mirroring the methodology: **(1) Corpus fingerprint** — detected languages, per-stratum PCA components + variance table, stratum-weights bar; **(2) NN matching** — LaTeX composite-distance formula + 2D scatter of fingerprint space (UMAP if installed, **else PCA** — PCA on this machine), query = gold star, top-k = red; **(3) Per-stratum distance breakdown** — nearest-neighbour S1–S6 table sorted ascending, grouped bars for all top-k, plus the S6 typological advisories (tonal / CJK); **(4) IDW voting** — formula, stacked per-neighbour contribution bars, detail table, normalised scores, sum(1/D) denominator; **(5) Consensus confidence** — n_agree/k formula + per-neighbour agree/differ cards |
| 4 | ▶ Run Model | `_tab_run_model` | Live inference via `ModelRunner`: ranked model selectbox (IDW score shown), sample-size input (default min(2000, n)), availability check against `LID_experiments` (missing file → warning + disabled button), run → wall time / ms-per-sample / throughput, predicted-language distribution bar, first-50 predictions table, full-CSV download |
| 5 | 📈 Baseline | `_tab_baseline` | Toolkit recommendation vs **Always-best Default** (model winning most MKB datasets globally) vs **Random** (mean IDW across models), all scored on THIS query; delta metrics absolute + relative; global win-distribution expander |
| 6 | 🌍 Coverage | `_tab_coverage` | Language x top-8-model coverage heatmap (covered / gap / unknown — same logic as the recommender's coverage penalty); per-language status table; red alert for uncoverable languages; scope note: MKB covers exactly 24 languages (ca da de el en es fi fr hr it ja ko lt mk nb nl pl pt ro ru sl sv uk zh — reconfirmed from mkb.pkl 2026-07-12) |

Model-family labels (`_family_label`) map to the thesis roster: FastText
(trained) / Zero-shot off-the-shelf (`lid.176`, `cld3`, `xlm_v_base…`) /
Logistic Regression (`*_lr_*`) / Naïve Bayes (the remaining `bow_*`/`tfidf_*`).

**ModelRunner** (`src/lid_toolkit/explainer/model_runner.py`): resolves
composite variant names `{architecture}_{training_dataset}` by
longest-suffix match against MKB dataset names; maps to
`model.bin` (FastText custom), `off_the_shelf_models/fasttext/lid.176.bin`
(OTS), or `best_pipeline.pkl` (LR / Naïve Bayes); lazy-loads with an
in-instance cache. Since 2026-08-12 the runner is `@st.cache_resource`-cached
per (experiments dir, dataset list), so a loaded model survives reruns instead
of being reloaded on every click.

## Known failure modes (code reading 2026-07-12; live run 2026-08-12)

| Symptom | Cause | Fix |
|---|---|---|
| Analyse → crash `Missing FastText LID model at …\src\lid_toolkit\models\fasttext\lid.176.bin` | DeepProfiler's language detector missing | Copy `lid.176.bin` from `LID_experiments\off_the_shelf_models\fasttext\` to that path (present 2026-07-12) |
| Sidebar error "MKB file not found" | Wrong `mkb.pkl` path, or launched somewhere the relative default breaks | Path is absolute-by-default (repo root via `parents[3]`); paste the absolute path in the sidebar or set `LID_STORE_PATH` |
| Analyse hangs then errors on a specific language / "Downloading spaCy model …" | DeepProfiler auto-downloads spaCy models per detected language on FIRST use (`spacy.cli.download`) — needs internet | **Pre-warm before an offline demo**: run the full analysis once on the exact demo corpus the day before; models cache in the env |
| Console warnings "Could not load FastText model for '<lang>'" / re-downloads each run | Embedding cache `./fasttext_cache` is **cwd-relative**; launching from another directory misses `<repo>\fasttext_cache\` | Always launch from the repo root |
| Panel 3 (How It Works) scatter titled "PCA projection" not "UMAP" | `umap` not installed in thesis_final (**verified 2026-07-12**) — dashboard silently falls back to sklearn PCA | Cosmetic; for UMAP: `pip install umap-learn` in thesis_final, then re-verify Step 2. Either projection is defensible — say "2-D projection of the fingerprint space" |
| Panel 4 (Run Model) error "LID_experiments directory not found" | Default hardcoded `C:\Users\User\OneDrive\Masters\LID_experiments` absent (other machine) or renamed | Fix sidebar path / `LID_EXPERIMENTS_DIR` |
| Panel 4 "Model file not found on disk" + disabled Run button | That variant's `model.bin`/`best_pipeline.pkl` missing — OneDrive files-on-demand may hold cloud-only placeholders that hydrate slowly or fail offline | Before the defense, open the expected model folder in Explorer and "Always keep on this device" (at least the recommended model + lid.176.bin); test the Run button in the dry run |
| Sidebar "Column 'text' not found" | Upload has a different text column | The error lists available columns; retype the column name |
| Profiling takes many minutes | 70k-row demo corpus; spaCy pipeline per language | Use a pre-sampled CSV (~2,000 rows) for live demos |
| Stale results after switching corpora | Session state | Sidebar **Clear session** button |
| App renders in Streamlit's default light theme, wrong fonts | Launched from somewhere other than the repo root, so `.streamlit/config.toml` was never found | `cd` to the repo root first |
| Text renders in a system sans, not IBM Plex | `enableStaticServing` off, or the woff2 files missing from `src/lid_toolkit/explainer/static/fonts/` | Check `curl -I http://localhost:8501/app/static/fonts/IBMPlexSans.woff2` returns 200 |
| A Plotly chart shows the literal word "undefined" above it | `fig.update_layout(title=None)` leaves an empty title object | Use `title_text=""` — `_style_fig` already does |
| Looking for the metric selector in the sidebar | It moved to the main pane on 2026-08-12 | It is above the tab strip; changing it re-queries live without re-profiling |
| Profiling wall-clock varies 55-105 s on the same 600-doc corpus | `_load_recommender` is `@st.cache_resource`-cached, so a second profile in the same server process reuses warm FastText/spaCy models | Expected. For a cold-start number (the one the Ch5 figures report, ~100 s) restart the Streamlit process first |

## Oral-defense demo script (~10 min, IR-examiner-tuned)

Do a **complete dry run the day before** (pre-warms spaCy models, hydrates
OneDrive model files, confirms timings). Have `test_examples\demonstration.md`
printed as fallback if anything fails live. **Profile the corpus before the room
fills** — profiling is the only slow step; every panel and every metric re-query
is instant afterwards.

The framing for an information-retrieval examiner: **the framework IS a
retrieval system** — query representation -> k-NN retrieval -> score fusion ->
result presentation. Walk the panels in pipeline order:

1. **Panel 1 — Corpus Profile** (claim: Phase 1 is user-facing, and scope is
   declared). Raw unlabelled text in; census out. Point at the split between
   languages detected and languages profiled: "the system tells you which part
   of your corpus it can actually characterise before it recommends anything."
   Then the fingerprint-composition table: 2,726 raw features -> 63 PCs.
2. **Panel 3, Step 1 — Fingerprint** (claim: corpus-level linguistic
   representation). "The uploaded corpus becomes a structured query: 2,726
   Lingualyzer-derived features per language, stratified into six blocks and
   PCA-compressed per stratum." IR framing: this is query representation —
   engineered linguistic features instead of TF-IDF/embeddings because the
   'documents' are whole corpora, not texts, and strata keep the
   representation interpretable.
3. **Panel 3, Step 2 — Retrieval** (claim: similarity-based matching is
   valid). Show the formula + scatter. Pre-empt the examiner: per-stratum
   **Euclidean in PCA space, not cosine — cosine suffers
   concentration-of-measure in high dimensions** (design rationale in
   `mkb_similarity.py` header). The star-vs-red-dots scatter is the
   retrieval result made visible.
4. **Panel 3, Steps 3–4 — Ranked evidence aggregation** (claim: the
   recommendation is fully traceable). Per-stratum distance decomposition =
   interpretable relevance breakdown, now with an explicit nearest-neighbour
   S1–S6 table; IDW voting = inverse-distance score fusion with a
   **language-coverage factor** (models missing the user's languages are
   penalised or zeroed). Open the detailed contribution table: "every number in
   the final ranking is reproducible by hand from this trace." This is the
   explainability centrepiece — dwell here for an IR examiner.
5. **Panel 3, Step 5 + Panel 2 — Confidence and result** (claim: the framework
   signals its own certainty). Say **"consensus confidence signal — the
   fraction of retrieved neighbours that independently agree on the winner"**.
   NEVER say "calibrated confidence". Ceiling as of 2026-07-31: the signal is
   **untested on this sample** — the earlier 2/2-vs-1/15, p = 0.022 result did
   NOT survive the coverage-guard correction, so do not cite it either. The
   panel itself now prints the safe wording under the gauge. Then Panel 2 for
   the headline: architecture + training corpus, gauge, **ranked shortlist**
   (lead with the shortlist, not the single name), neighbour table.
6. **Live re-query — the interactivity beat** (claim: Objective II). Change the
   priority metric selector above the tabs to `inference_time_ms_per_sample`.
   The ranking recomputes in a few hundred ms with no re-profiling, and the
   COVERAGE WARNING banner fires for `fasttext_word_multi_eurlex` (8 of 24
   languages uncovered). This is the Ch5 §5.7.2 Figure 5.4 moment; the banner
   shows the guard is a live constraint, not a footnote.
7. **Panel 5 — Baseline comparison** (claim: EQ3, meta-learning beats naive
   policies). Live per-query analogue of the thesis result — toolkit vs
   always-best-default vs random. Thesis-level numbers if asked: mean regret
   **0.0073** vs random 0.3830 vs best-constant 0.0127, with mean range capture
   **99.18%** as the headline (re-verified 2026-07-31 against
   `analysis/reporting_measures_2026-07-21.json`). The old 0.0078 figure is
   pre-coverage-fix — do not quote it during a live demo.
8. **Panel 4 — Run Model** (claim: the recommendation is actionable, not
   advisory). Run the recommended model live on the sample; show throughput
   and the predicted-language distribution matching the corpus. Measured
   2026-08-12 on the 600-doc WiLI sample: ~9 s wall, ~15 ms/sample.
9. **Panel 6 — Coverage** (claim: honest scoping). 24-language heatmap,
   uncoverable-language alerts. "The system knows and declares what it
   cannot answer" — a strength under examination, not a weakness.

## When NOT to use this skill

- **Changing dashboard code** (new panels, bug fixes, styling) — ordinary
  dev work on `src/lid_toolkit/explainer/`; this runbook only documents
  behaviour as of 2026-07-12 and goes stale on edit.
- **Running validations / re-verifying thesis numbers** →
  `artifact-verification-playbook`.
- **Defense Q&A beyond the demo** (methodology challenges, claims defense)
  → `examiner-defense-pack`; framework internals → `lid-framework-reference`.
- **Building/refreshing the MKB** — `Recommender.build_mkb` path; not a
  demo concern.

## Provenance and maintenance

Date-stamped **2026-08-12** (previous revision 2026-07-12). The app was
launched and driven end-to-end on 2026-08-12 to capture the Ch5 §5.7.2 figures,
so port 8501, the startup banner and all six panels are now runtime-verified,
not static analysis. Volatile facts and one-line re-checks (repo root,
thesis_final python):

- Dashboard parses / imports resolve:
  `python -m py_compile src\lid_toolkit\explainer\dashboard.py` and the
  pre-flight one-liner above.
- MKB contents (17 datasets / 24 languages / 1,785 records):
  `python -c "from lid_toolkit.recommender.mkb_store import MKBStore; m=MKBStore.load('mkb.pkl'); print(len(m.datasets), len({l for n in m.datasets for l in m.get_entry(n).iso_codes}), sum(len(m.get_entry(n).performances) for n in m.datasets))"`
- umap still absent (PCA fallback active): `python -c "import umap"` →
  ModuleNotFoundError expected (thesis_final, 2026-07-12).
- Model files on disk: `Test-Path "C:\Users\User\OneDrive\Masters\LID_experiments\off_the_shelf_models\fasttext\lid.176.bin"`.
- Ch5 figures + the code state they document:
  `figures/dashboard/fig{1..4}_*.png` in the thesis repo, captured 2026-08-12.
  If the dashboard layout changes, those figures go stale and Ch5 §5.7.2 must be
  re-captured; the capture is fully scripted (headless Edge via Playwright).
- Runtime-verified 2026-08-12: all six tabs render without a Streamlit
  exception, live inference runs from Panel 4, and switching the priority metric
  re-queries without re-profiling.
