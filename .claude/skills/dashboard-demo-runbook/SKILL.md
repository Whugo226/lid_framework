---
name: dashboard-demo-runbook
description: Runbook for launching and demonstrating the Streamlit explainer dashboard of the LID toolkit (src/lid_toolkit/explainer/dashboard.py) — panel inventory, exact launch command, prerequisites, known failure modes with fixes, and a suggested oral-defense walkthrough tuned for an IR-expert external examiner. Load this when the task is "run the dashboard", "demo the toolkit", "prepare the live demonstration for the defense", or diagnosing why the dashboard fails to start or a panel misbehaves. Do NOT load for changing dashboard code (regular dev work — use the codebase directly), for running validation experiments or re-verifying thesis numbers (use artifact-verification-playbook), or for defense Q&A content beyond the demo itself (use examiner-defense-pack).
---

# Dashboard Demo Runbook

The dashboard is a **five-panel Streamlit app** that takes an uploaded text
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

## Panel inventory (verified against code, 2026-07-12)

Workflow: sidebar → upload CSV/TSV, name the text column (default `text`),
pick an optimisation metric (10 options, default `f1_weighted`), click
**Analyse Corpus**. This runs `LID_Recommender.recommend(texts, metric,
mode="explain")` — DeepProfiler extracts 2,726 features per detected
language, PCA-reduces them per stratum into a fingerprint, and the
recommendation plus a full math trace land in `st.session_state`. Then five
tabs:

| # | Tab | Function | Shows |
|---|---|---|---|
| 1 | 📊 Recommendation | `_tab_overview` | Metric strip (model, confidence %, languages detected, profiling time); confidence gauge (green ≥67%, amber ≥34%, red below); paradigm-family pie of top-k neighbours' best models; top-k neighbour table (similarity %, best model, metric score, coverage gap); horizontal bar of ALL model IDW scores, winner in green |
| 2 | 🔍 How It Works | `_tab_walkthrough` | Five expandable steps mirroring the methodology: **(1) Corpus fingerprint** — detected languages, per-stratum PCA components + variance table, stratum-weights bar; **(2) NN matching** — LaTeX composite-distance formula + 2D scatter of fingerprint space (UMAP if installed, **else PCA** — PCA on this machine), query = gold star, top-k = red; **(3) Per-stratum distance breakdown** grouped bars; **(4) IDW voting** — formula, stacked per-neighbour contribution bars, detail table, normalised scores, Σ(1/D) denominator; **(5) Confidence** — n_agree/k formula + per-neighbour agree/differ cards |
| 3 | ▶ Run Model | `_tab_run_model` | Live inference via `ModelRunner`: ranked model selectbox (IDW score shown), sample-size input (default min(2000, n)), availability check against `LID_experiments` (missing file → warning + disabled button), run → wall time / ms-per-sample / throughput, predicted-language distribution bar, first-50 predictions table, full-CSV download |
| 4 | 📈 Baseline | `_tab_baseline` | Toolkit recommendation vs **Always-best Default** (model winning most MKB datasets globally) vs **Random** (mean IDW across models), all scored on THIS query; Δ metrics absolute + relative; global win-distribution expander |
| 5 | 🌍 Coverage | `_tab_coverage` | Language × top-8-model coverage heatmap (✓ covered / ✗ gap / ? unknown — same logic as the recommender's coverage penalty); per-language status table; red alert for uncoverable languages; scope note: MKB covers exactly 24 languages (ca da de el en es fi fr hr it ja ko lt mk nb nl pl pt ro ru sl sv uk zh — reconfirmed from mkb.pkl 2026-07-12) |

**ModelRunner** (`src/lid_toolkit/explainer/model_runner.py`): resolves
composite variant names `{architecture}_{training_dataset}` by
longest-suffix match against MKB dataset names; maps to
`model.bin` (FastText custom), `off_the_shelf_models/fasttext/lid.176.bin`
(OTS), or `best_pipeline.pkl` (LR / Naïve Bayes); lazy-loads with an
in-instance cache. Note: the runner is re-created on every Streamlit rerun,
so each "Run Model" click reloads the model file — latency, not a bug.

## Known failure modes (from code reading, 2026-07-12)

| Symptom | Cause | Fix |
|---|---|---|
| Analyse → crash `Missing FastText LID model at …\src\lid_toolkit\models\fasttext\lid.176.bin` | DeepProfiler's language detector missing | Copy `lid.176.bin` from `LID_experiments\off_the_shelf_models\fasttext\` to that path (present 2026-07-12) |
| Sidebar error "MKB file not found" | Wrong `mkb.pkl` path, or launched somewhere the relative default breaks | Path is absolute-by-default (repo root via `parents[3]`); paste the absolute path in the sidebar or set `LID_STORE_PATH` |
| Analyse hangs then errors on a specific language / "Downloading spaCy model …" | DeepProfiler auto-downloads spaCy models per detected language on FIRST use (`spacy.cli.download`) — needs internet | **Pre-warm before an offline demo**: run the full analysis once on the exact demo corpus the day before; models cache in the env |
| Console warnings "Could not load FastText model for '<lang>'" / re-downloads each run | Embedding cache `./fasttext_cache` is **cwd-relative**; launching from another directory misses `<repo>\fasttext_cache\` | Always launch from the repo root |
| Panel 2 scatter titled "PCA projection" not "UMAP" | `umap` not installed in thesis_final (**verified 2026-07-12**) — dashboard silently falls back to sklearn PCA | Cosmetic; for UMAP: `pip install umap-learn` in thesis_final, then re-verify Panel 2. Either projection is defensible — say "2-D projection of the fingerprint space" |
| Panel 3 error "LID_experiments directory not found" | Default hardcoded `C:\Users\User\OneDrive\Masters\LID_experiments` absent (other machine) or renamed | Fix sidebar path / `LID_EXPERIMENTS_DIR` |
| Panel 3 "Model file not found on disk" + disabled Run button | That variant's `model.bin`/`best_pipeline.pkl` missing — OneDrive files-on-demand may hold cloud-only placeholders that hydrate slowly or fail offline | Before the defense, open the expected model folder in Explorer and "Always keep on this device" (at least the recommended model + lid.176.bin); test the Run button in the dry run |
| Sidebar "Column 'text' not found" | Upload has a different text column | The error lists available columns; retype the column name |
| Profiling takes many minutes | 70k-row demo corpus; spaCy pipeline per language | Use a pre-sampled CSV (~2,000 rows) for live demos |
| Stale results after switching corpora | Session state | Sidebar **Clear Results** button |

## Oral-defense demo script (~10 min, IR-examiner-tuned)

Do a **complete dry run the day before** (pre-warms spaCy models, hydrates
OneDrive model files, confirms timings). Have `test_examples\demonstration.md`
printed as fallback if anything fails live. Pre-run the analysis before the
room fills — profiling is the slow step; the five tabs are instant afterwards.

The framing for an information-retrieval examiner: **the framework IS a
retrieval system** — query representation → k-NN retrieval → score fusion →
result presentation. Walk the panels in pipeline order:

1. **Panel 2, Step 1 — Fingerprint** (thesis claim: corpus-level linguistic
   representation). "The uploaded corpus becomes a structured query: 2,726
   Lingualyzer-derived features per language, stratified into six blocks and
   PCA-compressed per stratum." IR framing: this is query representation —
   engineered linguistic features instead of TF-IDF/embeddings because the
   'documents' are whole corpora, not texts, and strata keep the
   representation interpretable.
2. **Panel 2, Step 2 — Retrieval** (claim: similarity-based matching is
   valid). Show the formula + scatter. Pre-empt the examiner: per-stratum
   **Euclidean in PCA space, not cosine — cosine suffers
   concentration-of-measure in high dimensions** (design rationale in
   `mkb_similarity.py` header). The star-vs-red-dots scatter is the
   retrieval result made visible.
3. **Panel 2, Steps 3–4 — Ranked evidence aggregation** (claim: the
   recommendation is fully traceable). Per-stratum distance decomposition =
   interpretable relevance breakdown; IDW voting = inverse-distance score
   fusion with a **language-coverage factor** (hard constraint filtering —
   models missing the user's languages are penalised or zeroed). Open the
   detailed contribution table: "every number in the final ranking is
   reproducible by hand from this trace." This is the explainability
   centrepiece — dwell here for an IR examiner.
4. **Panel 2, Step 5 + Panel 1 — Confidence and result** (claim: the toolkit
   signals its own certainty). Say **"consensus confidence signal — the
   fraction of retrieved neighbours that independently agree on the winner"**.
   ⚠️ NEVER say "calibrated confidence" — thesis evidence for calibration is
   directional only (2/2 vs 1/15, p = 0.022). Note: a stale docstring in
   `mkb_similarity.py` (~line 24) still says "calibrated signal"; do not
   quote it, and expect the fix on the open-items list. Then Panel 1 for the
   headline: model, gauge, neighbour table.
5. **Panel 4 — Baseline comparison** (claim: EQ3, meta-learning beats naive
   policies). Live per-query analogue of the thesis result — toolkit vs
   always-best-default vs random. Thesis-level numbers if asked: mean regret
   **0.0073** vs random 0.3830 vs best-constant 0.0127, with mean range capture
   **99.18%** as the headline (✅ re-verified 2026-07-31 against
   `analysis/reporting_measures_2026-07-21.json`). The old 0.0078 figure is
   pre-coverage-fix — do not quote it during a live demo.
6. **Panel 3 — Run Model** (claim: the recommendation is actionable, not
   advisory). Run the recommended model live on the sample; show throughput
   and the predicted-language distribution matching the corpus.
7. **Panel 5 — Coverage** (claim: honest scoping). 24-language heatmap,
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

Date-stamped 2026-07-12. Volatile facts and one-line re-checks (repo root,
thesis_final python):

- Dashboard parses / imports resolve:
  `python -m py_compile src\lid_toolkit\explainer\dashboard.py` and the
  pre-flight one-liner above.
- MKB contents (17 datasets / 24 languages / 1,785 records):
  `python -c "from lid_toolkit.recommender.mkb_store import MKBStore; m=MKBStore.load('mkb.pkl'); print(len(m.datasets), len({l for n in m.datasets for l in m.get_entry(n).iso_codes}), sum(len(m.get_entry(n).performances) for n in m.datasets))"`
- umap still absent (PCA fallback active): `python -c "import umap"` →
  ModuleNotFoundError expected (thesis_final, 2026-07-12).
- Model files on disk: `Test-Path "C:\Users\User\OneDrive\Masters\LID_experiments\off_the_shelf_models\fasttext\lid.176.bin"`.
- Never launched during authoring: startup banner, port 8501, and live-panel
  behaviour are static analysis only — do one real launch before relying on
  them for the defense dry run.
