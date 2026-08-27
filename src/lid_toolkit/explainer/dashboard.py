"""
LID Framework — Interactive Dashboard
=====================================
Six-panel Streamlit app for exploring, explaining, and running LID model
recommendations produced by the LID recommendation framework.

Visual identity is defined in ``.streamlit/config.toml`` (surfaces, typeface,
semantic palette) and in the token block below (Plotly, which the Streamlit
theme cannot reach). Both are deliberately built against generated-interface
defaults: warm charcoal rather than blue-slate, one desaturated accent, colour
reserved for meaning, small radii, IBM Plex rather than Inter, and no gradients,
glows or decorative iconography.

The corpus is profiled **once** (the expensive phase).  The priority metric is
a live control in the main pane: changing it re-queries the Meta-Knowledge Base
from the cached fingerprint, which is a nearest-neighbour lookup over the stored
dataset fingerprints and costs milliseconds rather than a second profiling pass.

Run from the project root:
    streamlit run src/lid_toolkit/explainer/dashboard.py

Environment variable overrides (optional):
    LID_STORE_PATH        Path to mkb.pkl  (default: ./mkb.pkl)
    LID_EXPERIMENTS_DIR   Path to LID_experiments/ folder
"""
from __future__ import annotations

import os
import time
import warnings
from collections import Counter, OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LID Framework",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Visual identity ────────────────────────────────────────────────────────────
# Palette and chart styling live here so every panel draws from one source.
# Surfaces and typography come from .streamlit/config.toml; these are the tokens
# Plotly needs, which Streamlit's theme cannot reach.
#
# The system is Gentelella v4 (Colorlib, MIT) in its dark theme — see the design
# note at the head of .streamlit/config.toml. Values are transcribed from that
# template's _tokens.scss rather than approximated, so the Plotly charts and the
# surrounding chrome resolve to the same hexes.
#
# Surfaces stack in three steps: the body recedes, cards sit on it, inset tiles
# drop below the card again.
_BODY     = "#0F1623"   # --body-bg
_SURFACE  = "#1A2332"   # --bg-surface        (cards, sidebar, topbar)
_SURFACE2 = "#141D2B"   # --bg-surface-secondary (inset tiles, table headers)
_BORDER   = "#242E3D"   # --border-color, resolved opaque
_BORDER_L = "#1F2836"   # --border-color-light

_INK      = "#E6EBF2"   # --text
_TEXT2    = "#B3BCCB"   # --text-secondary
_MUTED    = "#8A93A3"   # --text-muted
_DISABLED = "#5A6473"   # --text-disabled
_FAINT    = "#232C3A"   # gridlines, axis rules
_NEUTRAL  = "#5A6473"   # non-highlighted series

# Brand accent — interactive affordances only (buttons, active tab, focus).
_PRIMARY    = "#1ABB9C"  # --primary
_PRIMARY_DK = "#169F85"  # --primary-dk

# Named hues from the Gentelella palette. The three below keep the roles the
# recommender's logic depends on, so the coverage guard and the error paths have
# a stable colour even though the chart series now draw from the full palette.
_SAGE  = "#2FB344"   # --green   : covered / recommended
_AMBER = "#F59F00"   # --yellow  : coverage gap / advisory
_CLAY  = "#D63939"   # --red     : error / uncoverable
_STEEL = "#4299E1"   # --azure   : first chart series, neutral emphasis

# Full 11-hue Gentelella palette for chart series, as the template's own demo
# pages use it. This is deliberately decorative: hue no longer implies a warning
# on its own, so anything that must be READ as a warning is also labelled.
_SERIES = ["#4299E1", "#1ABB9C", "#F59F00", "#AE3EC9", "#2FB344", "#F76707",
           "#4263EB", "#D6336C", "#17A2B8", "#74B816", "#D63939"]

# The Gentelella component layer. Streamlit renders its own DOM, so the template
# cannot be imported — what is reproduced here is its design system: the token
# set, the card/stat-tile/nav-tab geometry, and the type scale. Selectors are
# written against Streamlit 1.58's stable data-testid hooks, with the older
# alias included where one exists, since those attributes are the only public
# styling surface Streamlit offers.
_CSS = """
<style>
  :root {
    --g-body:        #0F1623;
    --g-surface:     #1A2332;
    --g-surface-2:   #141D2B;
    --g-border:      #242E3D;
    --g-border-lt:   #1F2836;
    --g-text:        #E6EBF2;
    --g-text-2:      #B3BCCB;
    --g-muted:       #8A93A3;
    --g-disabled:    #5A6473;
    --g-primary:     #1ABB9C;
    --g-primary-dk:  #169F85;
    --g-primary-lt:  rgba(26,187,156,0.14);
    --g-radius:      6px;
    --g-radius-sm:   4px;
    --g-radius-lg:   8px;
    --g-shadow:      rgba(0,0,0,0.30) 0 2px 4px 0;
    --g-sidebar-text: #7B8FA3;
  }

  /* ── Frame ──────────────────────────────────────────────────────────────── */
  /* Gentelella runs edge-to-edge with a compact gutter; the default Streamlit
     hero gap belongs to a document, not to a console. */
  .block-container { padding-top: 1.1rem; padding-bottom: 2.5rem;
                     max-width: 100%; }
  [data-testid="stHeader"] { background: transparent; }

  /* Figures are read as data: lock the numerals to tabular so columns align. */
  [data-testid="stMetricValue"], [data-testid="stDataFrame"],
  .stDataFrame, code, pre, table { font-variant-numeric: tabular-nums; }

  /* ── Topbar ─────────────────────────────────────────────────────────────── */
  .g-topbar {
      display: flex; align-items: center; justify-content: space-between;
      gap: 16px;
      background: var(--g-surface);
      border: 1px solid var(--g-border);
      border-radius: var(--g-radius-lg);
      box-shadow: var(--g-shadow);
      padding: 0 16px; height: 52px; margin-bottom: 16px;
  }
  .g-brand { display: flex; align-items: center; gap: 10px; }
  .g-logo {
      display: inline-flex; align-items: center; justify-content: center;
      width: 28px; height: 28px; border-radius: var(--g-radius-sm);
      background: var(--g-primary); color: #06231D;
      font-size: 11px; font-weight: 600; letter-spacing: 0.02em;
  }
  .g-brandname { font-size: 14px; font-weight: 600; color: var(--g-text); }
  .g-topbar-meta {
      font-size: 12px; color: var(--g-muted); text-align: right;
  }

  /* ── Page header (pretitle / title / breadcrumb) ─────────────────────────── */
  .g-pagehead { margin: 0 0 16px 2px; }
  .g-pretitle {
      font-size: 11px; font-weight: 600; letter-spacing: 0.4px;
      text-transform: uppercase; color: var(--g-muted); margin-bottom: 3px;
  }
  .g-title {
      font-size: 1.35rem; font-weight: 600; letter-spacing: -0.015em;
      color: var(--g-text); margin: 0 0 5px 0; line-height: 1.2;
  }
  .g-breadcrumb { font-size: 12px; color: var(--g-muted); }
  .g-breadcrumb span { color: var(--g-disabled); margin: 0 6px; }

  /* ── Nav tabs + card body ───────────────────────────────────────────────── */
  /* The tab strip is the card header and the panel is the card body, so the six
     panels read as one Gentelella card rather than six loose regions. */
  .stTabs [data-baseweb="tab-list"] {
      gap: 2px;
      background: var(--g-surface);
      border: 1px solid var(--g-border);
      border-bottom: 1px solid var(--g-border);
      border-radius: var(--g-radius-lg) var(--g-radius-lg) 0 0;
      padding: 0 6px;
  }
  .stTabs [data-baseweb="tab"] {
      height: 44px; padding: 0 15px;
      font-size: 13px; font-weight: 500;
      color: var(--g-muted); background: transparent;
      border-radius: 0;
      transition: color 120ms, box-shadow 120ms;
  }
  .stTabs [data-baseweb="tab"]:hover { color: var(--g-text-2); }
  .stTabs [data-baseweb="tab"][aria-selected="true"] {
      color: var(--g-primary);
      box-shadow: inset 0 -2px 0 0 var(--g-primary);
  }
  /* Streamlit paints its own sliding underline; the inset shadow above is the
     one that stays put, so the stock highlight is removed rather than recoloured. */
  .stTabs [data-baseweb="tab-highlight"] { background: transparent; }
  .stTabs [data-baseweb="tab-border"] { background: var(--g-border); }
  .stTabs [data-baseweb="tab-panel"] {
      background: var(--g-surface);
      border: 1px solid var(--g-border);
      border-top: none;
      border-radius: 0 0 var(--g-radius-lg) var(--g-radius-lg);
      box-shadow: var(--g-shadow);
      padding: 20px 22px 24px 22px;
  }

  /* ── Stat tiles ─────────────────────────────────────────────────────────── */
  /* Inset one step below the card they sit in, per Gentelella's surface stack. */
  [data-testid="stMetric"], [data-testid="metric-container"] {
      background: var(--g-surface-2);
      border: 1px solid var(--g-border);
      border-radius: var(--g-radius-lg);
      padding: 13px 15px;
  }
  [data-testid="stMetricLabel"] p {
      font-size: 11px; font-weight: 600; letter-spacing: 0.3px;
      text-transform: uppercase; color: var(--g-muted);
  }
  [data-testid="stMetricValue"] {
      font-size: 1.5rem; font-weight: 600; letter-spacing: -0.02em;
      color: var(--g-text);
  }

  /* ── Section titles (Gentelella's x_title: label over a hairline rule) ───── */
  [data-testid="stHeadingWithActionElements"] h3,
  [data-testid="stMarkdownContainer"] h3 {
      font-size: 0.95rem; font-weight: 600; color: var(--g-text);
      padding-bottom: 8px; margin-bottom: 14px;
      border-bottom: 1px solid var(--g-border-lt);
  }

  /* ── Controls ───────────────────────────────────────────────────────────── */
  .stButton button, .stDownloadButton button {
      height: 34px; padding: 0 13px;
      border-radius: var(--g-radius-sm);
      font-size: 12.5px; font-weight: 500;
      transition: background 120ms, border-color 120ms, color 120ms;
  }
  .stButton button[kind="primary"] {
      background: var(--g-primary); border-color: var(--g-primary-dk);
      color: #06231D;
  }
  .stButton button[kind="primary"]:hover {
      background: var(--g-primary-dk); border-color: var(--g-primary-dk);
      color: #062720;
  }
  label, [data-testid="stWidgetLabel"] p {
      font-size: 12.5px !important; font-weight: 500; color: var(--g-text-2);
  }

  /* ── Sidebar ────────────────────────────────────────────────────────────── */
  [data-testid="stSidebar"] { border-right: 1px solid var(--g-border); }
  [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
      font-size: 11px !important; font-weight: 600; letter-spacing: 0.4px;
      text-transform: uppercase; color: var(--g-sidebar-text);
      border-bottom: none; padding-bottom: 0; margin-bottom: 10px;
  }

  /* ── Tables, captions, rules ────────────────────────────────────────────── */
  [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
      font-size: 12px; color: var(--g-muted); line-height: 1.5;
  }
  hr { margin: 1.3rem 0 1.15rem 0; border-color: var(--g-border-lt); }

  /* ── Alerts ─────────────────────────────────────────────────────────────── */
  /* Gentelella alerts are a low-alpha tint carrying a solid left accent, not
     Streamlit's saturated slab. The variant is read off the inner content node
     (stAlertContentInfo / …Warning / …Error / …Success) — that data-testid is
     the only hook Streamlit exposes for which kind of alert this is. */
  [data-testid="stAlertContainer"] {
      border-radius: var(--g-radius);
      border: 1px solid var(--g-border);
      border-left-width: 3px;
      font-size: 13px;
      color: var(--g-text);
  }
  [data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {
      background: rgba(6,111,209,0.18);   /* --blue-lt  */
      border-left-color: #066FD1;
  }
  [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {
      background: rgba(245,159,0,0.16);   /* --yellow-lt */
      border-left-color: #F59F00;
  }
  [data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {
      background: rgba(214,57,57,0.16);   /* --red-lt   */
      border-left-color: #D63939;
  }
  [data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {
      background: rgba(47,179,68,0.16);   /* --green-lt */
      border-left-color: #2FB344;
  }

  /* ── Expanders ──────────────────────────────────────────────────────────── */
  [data-testid="stExpander"] details {
      background: var(--g-surface-2);
      border: 1px solid var(--g-border);
      border-radius: var(--g-radius);
  }
  [data-testid="stExpander"] summary { font-size: 13px; font-weight: 500; }
</style>
"""


def _style_fig(fig, height: int, *, showlegend: bool | None = None):
    """Apply the one chart style used everywhere.

    Charts carry no titles — the surrounding subheader and caption name them,
    which is also what the department's figure checklist asks for. Backgrounds
    are transparent so a chart reads as part of the panel rather than as a
    pasted-in card.
    """
    fig.update_layout(
        height=height,
        # title_text="" clears the title; title=None leaves an empty title object
        # that plotly.js renders as the literal string "undefined".
        title_text="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", size=12, color=_MUTED),
        margin=dict(t=8, b=8, l=8, r=8),
        colorway=_SERIES,
        hoverlabel=dict(font_family="IBM Plex Sans, sans-serif"),
        legend=dict(font=dict(size=11, color=_MUTED)),
    )
    if showlegend is not None:
        fig.update_layout(showlegend=showlegend)
    axis = dict(gridcolor=_FAINT, zerolinecolor=_FAINT, linecolor=_FAINT,
                tickfont=dict(size=11, color=_MUTED),
                title_font=dict(size=11, color=_MUTED))
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    return fig

# ── Defaults from environment ──────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[3]   # project root (toolkit_dev/lid_toolkit/)

_DEFAULT_STORE = str(
    Path(os.environ.get(
        "LID_STORE_PATH",
        _ROOT / "mkb.pkl",
    ))
)
_DEFAULT_EXPERIMENTS = str(
    Path(os.environ.get(
        "LID_EXPERIMENTS_DIR",
        r"C:\Users\User\OneDrive\Masters\LID_experiments",
    ))
)

_METRICS = [
    "f1_weighted", "f1_macro", "accuracy",
    "precision_macro", "precision_weighted",
    "recall_macro", "recall_weighted",
    "inference_time_total_s", "inference_time_ms_per_sample",
    "throughput_samples_per_sec",
]

_STRATUM_LABELS: dict[str, str] = {
    "S1_morphological":     "Morphological Richness (S1)",
    "S2_lexical_diversity": "Lexical Diversity (S2)",
    "S3_structural":        "Structural / Syntactic (S3)",
    "S4_info_theoretic":    "Information-Theoretic (S4)",
    "S5_cross_level":       "Cross-Level Cohesion (S5)",
    "cat":                  "Typological Flags (S6)",
}

_CONFIDENCE_NOTE = (
    "Consensus confidence is the fraction of retrieved neighbours whose own "
    "best model agrees with the recommendation. It measures neighbourhood "
    "agreement, not the probability that the recommendation is optimal."
)


# ── Cached resources ───────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading Meta-Knowledge Base…")
def _load_recommender(store_path: str):
    """Load the recommendation engine once per MKB path (survives reruns)."""
    from lid_toolkit import LID_Recommender
    return LID_Recommender(store_path)


@st.cache_resource(show_spinner=False)
def _load_runner(experiments_dir: str, datasets: tuple[str, ...]):
    """Cache the ModelRunner so a loaded model survives across reruns."""
    from lid_toolkit.explainer.model_runner import ModelRunner
    return ModelRunner(experiments_dir, list(datasets))


# ── Small helpers ──────────────────────────────────────────────────────────────

def _strip_dataset(variant: str, datasets: list[str]) -> str:
    """Return just the architecture part of a composite variant name."""
    for ds in sorted(datasets, key=len, reverse=True):
        if variant.endswith(f"_{ds}"):
            return variant[: -(len(ds) + 1)]
    return variant


def _family_label(arch: str) -> str:
    """Map an architecture string to the model family names used in the thesis."""
    if arch.startswith("fasttext"):
        return "FastText (trained)"
    if arch.startswith(("lid.", "cld3", "xlm")):
        return "Zero-shot (off-the-shelf)"
    if "lr" in arch.split("_"):
        return "Logistic Regression"
    return "Naïve Bayes"


def _short(name: str, n: int = 35) -> str:
    return name if len(name) <= n else name[:n] + "…"


# ══════════════════════════════════════════════════════════════════════════════
# Panel 1 — Corpus Profile (Phase 1 output: raw text → structured fingerprint)
# ══════════════════════════════════════════════════════════════════════════════

def _tab_corpus(config, profile, texts: pd.Series | None, profiling_time: float, store):
    st.markdown(
        "The framework's first phase turns **raw, unlabelled text** into a "
        "structured corpus fingerprint. Everything below is derived from the "
        "uploaded file alone — no language labels are supplied by the user."
    )

    in_scope = sorted(config.query_iso_codes)
    counts: dict[str, int] = dict(profile.attrs.get("detected_language_counts", {}))
    n_docs = len(texts) if texts is not None else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Documents Profiled", f"{n_docs:,}")
    c2.metric("Languages in Census", len(counts) if counts else len(in_scope))
    c3.metric("In-Scope Languages", len(in_scope))
    c4.metric("Profiling Time", f"{profiling_time:.1f} s")

    st.caption(
        "The census is the profiler's `lid.176` language survey over every "
        f"document; {sum(counts.values()):,} of the {n_docs:,} documents "
        "received a high-confidence assignment. *In-scope* languages are the "
        "subset the annotation pipelines can characterise — out-of-scope "
        "segments are excluded from the fingerprint rather than characterised "
        "unreliably."
        if counts else
        "In-scope languages are the subset the annotation pipelines can "
        "characterise; out-of-scope segments are excluded from the fingerprint."
    )
    st.divider()

    # ── Detected-language census ──────────────────────────────────────────────
    st.subheader("Detected-Language Census")
    if counts:
        census_df = pd.DataFrame(
            [{"Language": code,
              "Documents": n,
              "Status": "Profiled (in scope)" if code in in_scope else "Detected, out of scope"}
             for code, n in sorted(counts.items(), key=lambda kv: -kv[1])]
        )
        st.caption(
            f"High-confidence detections per language, top 40 of {len(census_df)}."
        )
        fig_census = px.bar(
            census_df.head(40), x="Language", y="Documents", color="Status",
            color_discrete_map={"Profiled (in scope)": _STEEL,
                                "Detected, out of scope": _DISABLED},
        )
        _style_fig(fig_census, 330)
        fig_census.update_layout(
            legend_title_text="",
            legend=dict(orientation="h", y=1.14, x=0),
            bargap=0.25,
        )
        st.plotly_chart(fig_census, width='stretch')
    else:
        st.info("No census counts were attached to this profile.")

    st.markdown(
        "**In-scope languages profiled:** "
        + "  ".join(f"`{c}`" for c in in_scope)
    )

    st.divider()

    # ── Document-length summary ───────────────────────────────────────────────
    st.subheader("Document-Length Summary")
    if texts is not None and len(texts):
        lengths = texts.astype(str).str.len()
        l1, l2, l3, l4 = st.columns(4)
        l1.metric("Median Characters", f"{int(lengths.median()):,}")
        l2.metric("Mean Characters", f"{int(lengths.mean()):,}")
        l3.metric("Shortest", f"{int(lengths.min()):,}")
        l4.metric("Longest", f"{int(lengths.max()):,}")
        st.caption("Distribution of document length, in characters.")
        fig_len = px.histogram(
            pd.DataFrame({"Characters": lengths}), x="Characters", nbins=50,
            color_discrete_sequence=[_STEEL],
        )
        _style_fig(fig_len, 270)
        fig_len.update_layout(bargap=0.06)
        st.plotly_chart(fig_len, width='stretch')
    else:
        st.info("Upload a corpus to see the length distribution.")

    st.divider()

    # ── Fingerprint composition ───────────────────────────────────────────────
    st.subheader("Resulting Fingerprint Composition")
    try:
        strat = store.stratifier.stratum_summary()
        comp = pd.DataFrame([
            {"Stratum": _STRATUM_LABELS.get(s, s),
             "Raw Features": int(row.n_raw_features),
             "PCA Components": int(row.n_pcs),
             "Variance Retained (%)": float(row.var_explained_pct)}
            for s, row in strat.iterrows()
        ]).sort_values("Stratum")
        st.dataframe(comp.set_index("Stratum"), width='stretch')
        st.caption(
            f"{int(strat.n_raw_features.sum()):,} raw features per language are "
            f"compressed to {int(strat.n_pcs.sum())} principal components across "
            "the five continuous strata; the typological stratum (S6) contributes "
            "binary flags directly and is not reduced."
        )
    except Exception as exc:            # pragma: no cover — diagnostic path
        st.info(f"Stratifier summary unavailable: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# Panel 2 — Recommendation Overview
# ══════════════════════════════════════════════════════════════════════════════

def _render_advisories(result, config, *, coverage: bool = True, typology: bool = False):
    """Surface the recommender's own warnings in the UI, not just in the text
    explanation. ``coverage`` renders the language-coverage guard; ``typology``
    renders the S6 script/tonality advisories."""
    shown = False
    if coverage:
        rec = result.recommended_model
        gap: frozenset[str] = frozenset()
        for nb in config.neighbours:
            if rec in nb.per_model_gaps:
                gap = nb.per_model_gaps[rec]
                break
        if gap:
            st.warning(
                f"**COVERAGE WARNING** — `{rec}` was not trained on "
                f"{len(gap)} of your {len(config.query_iso_codes)} languages: "
                f"`{', '.join(sorted(gap))}`. These languages will be silently "
                "misclassified. Fully-covering alternatives appear further down "
                "the ranked shortlist."
            )
            shown = True
        if result.uncoverable_languages:
            st.error(
                "**UNCOVERABLE LANGUAGES** — "
                f"`{', '.join(sorted(result.uncoverable_languages))}` appear in "
                "your corpus but in none of the historical benchmark datasets. "
                "No reliable recommendation can be made for them."
            )
            shown = True

    if typology:
        fp = config.trace.get("query_fingerprint", {}) or {}
        n_tonal = int(fp.get("cat__n_tonal", 0))
        has_cjk = int(fp.get("cat__has_cjk", 0))
        notes = []
        if n_tonal:
            notes.append(
                f"**{n_tonal} tonal language(s) detected** — character-aware "
                "models generally perform better on tonal languages."
            )
        if has_cjk:
            notes.append(
                "**CJK script detected** — check that the chosen model was "
                "trained on CJK data."
            )
        if notes:
            st.info("Typological advisories (stratum S6)\n\n- " + "\n- ".join(notes))
            shown = True
    return shown


def _tab_overview(result, config, query_ms: float, store_datasets: list[str]):
    rec = result.recommended_model
    conf = result.confidence
    iso_codes = config.query_iso_codes

    # ── Top metric strip ──────────────────────────────────────────────────────
    arch = _strip_dataset(rec, store_datasets)
    train_ds = rec[len(arch) + 1:] if rec.startswith(f"{arch}_") else ""

    c1, c2, c3, c4 = st.columns([2.4, 1, 1, 1])
    c1.metric("Recommended Architecture", arch)
    c1.caption(f"trained on `{train_ds}`" if train_ds
               else "zero-shot / off-the-shelf")
    c2.metric("Consensus Confidence", f"{conf:.0%}")
    c3.metric("Languages Covered", len(iso_codes))
    c4.metric("Query Time", f"{query_ms:.0f} ms")

    st.caption(f"Metric optimised: **{config.priority_metric}**  ·  "
               f"Query languages: {', '.join(sorted(iso_codes))}  ·  "
               "Query time excludes the one-off profiling pass.")

    _render_advisories(result, config, coverage=True)
    st.divider()

    # ── Ranked shortlist ──────────────────────────────────────────────────────
    st.subheader("Ranked Shortlist")
    st.caption(
        "The framework returns a ranked candidate list with scores, not a single "
        "opaque answer. When consensus is low, the practitioner evaluates the top "
        "few candidates rather than committing to rank 1."
    )
    agreeing = Counter(nb.best_model for nb in config.neighbours)
    ranked = sorted(result.all_model_scores.items(), key=lambda kv: -kv[1])
    shortlist_rows = []
    for i, (model, score) in enumerate(ranked[:5], 1):
        gap_sizes = [len(nb.per_model_gaps.get(model, frozenset()))
                     for nb in config.neighbours if nb.per_model_gaps]
        worst_gap = max(gap_sizes) if gap_sizes else 0
        shortlist_rows.append({
            "Rank": i,
            "Model": model,
            "IDW Score": round(score, 4),
            "Neighbours Backing": f"{agreeing.get(model, 0)}/{len(config.neighbours)}",
            "Coverage": "full" if worst_gap == 0 else f"{worst_gap}-language gap",
            "": "recommended" if model == rec else "",
        })
    st.dataframe(pd.DataFrame(shortlist_rows).set_index("Rank"), width='stretch')

    st.divider()

    # ── Confidence gauge + paradigm pie ───────────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.subheader("Consensus Confidence")
        colour = _SAGE if conf >= 0.67 else (_AMBER if conf >= 0.34 else _CLAY)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=conf * 100,
            number={"suffix": "%", "font": {"size": 34, "color": _INK}},
            gauge={
                "axis": {"range": [0, 100], "ticksuffix": "%",
                         "tickcolor": _FAINT, "tickwidth": 1,
                         "tickfont": {"size": 11, "color": _MUTED}},
                "bar": {"color": colour, "thickness": 0.34},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                # Bands are structural, not semantic: keep them near-invisible so
                # the reading itself is the only thing carrying colour.
                "steps": [
                    {"range": [0, 34], "color": "#141D2B"},
                    {"range": [34, 67], "color": "#1B2534"},
                    {"range": [67, 100], "color": "#222D3E"},
                ],
            },
        ))
        _style_fig(fig_gauge, 290)
        fig_gauge.update_layout(margin=dict(t=24, b=16, l=58, r=58))
        st.plotly_chart(fig_gauge, width='stretch')
        st.caption(_CONFIDENCE_NOTE)

    with right:
        st.subheader("Winning Model Family (Top-k Neighbours)")
        archs = [_strip_dataset(nb.best_model, store_datasets) for nb in config.neighbours]
        families = [_family_label(a) for a in archs]
        counts = Counter(families)
        if counts:
            fig_pie = px.pie(
                names=list(counts.keys()),
                values=list(counts.values()),
                color_discrete_sequence=_SERIES,
                hole=0.62,
            )
            fig_pie.update_traces(
                textinfo="label+value", textposition="outside",
                textfont=dict(size=11, color=_MUTED),
                marker=dict(line=dict(color=_SURFACE, width=2)),
            )
            _style_fig(fig_pie, 290, showlegend=False)
            fig_pie.update_layout(margin=dict(t=34, b=34, l=44, r=44))
            st.plotly_chart(fig_pie, width='stretch')
            st.caption(
                "Family of each retrieved neighbour's own best-performing model. "
                "A split ring is what a consensus confidence below 1.0 looks like."
            )
        else:
            st.info("No neighbour data available.")

    st.divider()

    # ── Top-k neighbours table ────────────────────────────────────────────────
    st.subheader("Top-k Nearest Historical Datasets")
    nb_rows = []
    for i, nb in enumerate(config.neighbours, 1):
        nb_rows.append({
            "Rank": i,
            "Dataset": nb.dataset_name,
            "Similarity": f"{nb.similarity_pct:.1f}%",
            "Best Model": _short(nb.best_model),
            config.priority_metric: f"{nb.best_score:.4f}",
            "Coverage Gap": (", ".join(sorted(nb.coverage_gap))
                             if nb.coverage_gap else "full coverage"),
        })
    st.dataframe(pd.DataFrame(nb_rows).set_index("Rank"), width='stretch')

    st.divider()

    # ── All model IDW scores ──────────────────────────────────────────────────
    st.subheader("All Model IDW Scores (Coverage-Penalised)")
    scores = result.all_model_scores
    score_df = pd.DataFrame([
        {"Model": _short(m, 50), "IDW Score": s,
         "Winner": "Recommended" if m == rec else "Other candidate"}
        for m, s in sorted(scores.items(), key=lambda x: -x[1])
    ])
    fig_scores = px.bar(
        score_df, x="IDW Score", y="Model", orientation="h",
        color="Winner",
        color_discrete_map={"Recommended": _SAGE, "Other candidate": _NEUTRAL},
        labels={"IDW Score": f"IDW {config.priority_metric}"},
    )
    _style_fig(fig_scores, max(220, len(score_df) * 24 + 60), showlegend=False)
    fig_scores.update_layout(margin=dict(t=8, b=8, l=8, r=8), bargap=0.32)
    fig_scores.update_yaxes(categoryorder="total ascending",
                            tickfont=dict(size=10, color=_MUTED))
    st.plotly_chart(fig_scores, width='stretch')

    with st.expander("Full text explanation (as returned by the API)"):
        st.code(result.explanation, language="text")


# ══════════════════════════════════════════════════════════════════════════════
# Panel 3 — Mathematical Interpretability Walkthrough
# ══════════════════════════════════════════════════════════════════════════════

def _tab_walkthrough(result, config, store):
    trace = config.trace

    st.markdown(
        "This panel traces **every mathematical step** from your uploaded corpus "
        "to the final recommendation. Each step mirrors the methodology described in the thesis."
    )

    # ── Step 1: Corpus fingerprint ────────────────────────────────────────────
    with st.expander("**Step 1 — Corpus Fingerprint**", expanded=True):
        st.markdown(
            "**DeepProfiler** extracts 2,726 linguistic features per language across "
            "6 semantic strata. These are reduced via per-stratum PCA into a compact "
            "**fingerprint** representing your corpus's linguistic character."
        )
        iso_codes = trace.get("query_iso_codes", [])
        st.markdown(
            f"**Detected languages ({len(iso_codes)}):** "
            + "  ".join(f"`{c}`" for c in sorted(iso_codes))
        )
        pca_info = trace.get("pca_pipeline", {})
        if pca_info:
            st.markdown("**PCA summary per stratum:**")
            pca_rows = []
            for s, info in pca_info.items():
                pca_rows.append({
                    "Stratum": _STRATUM_LABELS.get(s, s),
                    "PCA Components": info.get("n_components", "?"),
                    "Variance Explained (%)": info.get("cumulative_pct", "?"),
                })
            st.dataframe(
                pd.DataFrame(pca_rows).set_index("Stratum"),
                width='stretch',
            )
        weights = trace.get("stratum_weights", {})
        if weights:
            w_df = pd.DataFrame([
                {"Stratum": _STRATUM_LABELS.get(s, s), "Weight": round(w, 4)}
                for s, w in weights.items()
            ])
            st.caption("Stratum weights — higher means more influential in the "
                       "composite distance.")
            fig_w = px.bar(
                w_df, x="Weight", y="Stratum", orientation="h",
                color_discrete_sequence=[_STEEL],
            )
            _style_fig(fig_w, 260, showlegend=False)
            fig_w.update_layout(coloraxis_showscale=False, bargap=0.35)
            st.plotly_chart(fig_w, width='stretch')

    # ── Step 2: Fingerprint space ─────────────────────────────────────────────
    with st.expander("**Step 2 — Nearest Neighbour Matching in Fingerprint Space**",
                     expanded=False):
        st.markdown(r"""
The composite distance between your query $q$ and each historical dataset $c$ is:

$$D(q,\,c) = \frac{\displaystyle\sum_s w_s \cdot \|\mathbf{v}_q^s - \mathbf{v}_c^s\|_2}{\displaystyle\sum_s w_s}$$

where $\mathbf{v}^s$ is the PCA-projected vector for stratum $s$ and $w_s$ is its learned weight.

The scatter below is a 2-D projection (UMAP if available, else PCA) of the full
fingerprint space. The ringed marker is your corpus; the highlighted points are the
retrieved top-k neighbours.
""")
        _render_fingerprint_scatter(config, store)

    # ── Step 3: Stratum distances ─────────────────────────────────────────────
    with st.expander("**Step 3 — Per-Stratum Distance Breakdown**", expanded=False):
        st.markdown(
            "Overall similarity is decomposed by linguistic stratum. "
            "Each bar shows the Euclidean distance between your corpus and a top-k neighbour "
            "within that stratum's PCA subspace. **Lower = more similar in that dimension.**"
        )
        if config.neighbours:
            nn = config.neighbours[0]
            st.markdown(
                f"**Nearest neighbour — `{nn.dataset_name}` "
                f"({nn.similarity_pct:.1f}% similarity):**"
            )
            nn_df = pd.DataFrame(
                [{"Stratum": _STRATUM_LABELS.get(s, s), "Distance": round(d, 4)}
                 for s, d in sorted(nn.per_stratum_distances.items(), key=lambda kv: kv[1])]
            ).set_index("Stratum")
            st.dataframe(nn_df, width='stretch')
            st.caption(
                "Read top-down: the strata the query shares with its nearest "
                "neighbour, then the strata that separate them. This is the "
                "decomposition the stratified PCA design exists to provide."
            )
        _render_stratum_distances(config.neighbours)
        _render_advisories(result, config, coverage=False, typology=True)

    # ── Step 4: IDW voting ────────────────────────────────────────────────────
    with st.expander("**Step 4 — Inverse-Distance-Weighted (IDW) Voting**", expanded=False):
        st.markdown(r"""
Each neighbour casts weighted votes for its best-performing model. Closer neighbours carry
more weight ($w_n = 1/D_n$). The final model score is:

$$\text{Score}(m) = \frac{\displaystyle\sum_{n \in \text{top-}k} \frac{1}{D_n} \cdot f(m,n) \cdot c_n^m}{\displaystyle\sum_{n \in \text{top-}k} \frac{1}{D_n}}$$

where $f(m,n)$ is model $m$'s benchmark score on dataset $n$ and
$c_n^m \in [0,1]$ is the language coverage factor
(1 = full coverage; penalised proportionally if the model's training set doesn't cover all user languages).
""")
        _render_idw_breakdown(trace)

    # ── Step 5: Confidence ────────────────────────────────────────────────────
    with st.expander("**Step 5 — Consensus Confidence**", expanded=False):
        conf_info = trace.get("confidence", {})
        n_agree = conf_info.get("n_agreeing", 0)
        k_total = conf_info.get("k", len(config.neighbours))
        confidence = conf_info.get("confidence", result.confidence)
        st.markdown(r"""
Confidence is the **fraction of top-k neighbours** that independently agree on the winning model:

$$\text{Confidence} = \frac{\left|\left\{n \in \text{top-}k : \text{best\_model}(n) = M^*\right\}\right|}{k}$$
""")
        st.info(
            f"**{n_agree} of {k_total} neighbours** agree on `{result.recommended_model}` "
            f"→ Confidence = {n_agree}/{k_total} = **{confidence:.0%}**"
        )
        cols = st.columns(max(1, k_total))
        for i, (col, nb) in enumerate(zip(cols, config.neighbours)):
            agrees = nb.best_model == result.recommended_model
            col.markdown(
                f"<div style='font-size:0.78rem;letter-spacing:0.04em;"
                f"text-transform:uppercase;color:{_MUTED}'>Neighbour {i + 1}</div>"
                f"<div style='font-size:1.05rem;font-weight:500;"
                f"color:{_SAGE if agrees else _MUTED}'>"
                f"{'Agrees' if agrees else 'Differs'}</div>"
                f"<div style='font-size:0.78rem;color:{_MUTED};"
                f"font-family:\"IBM Plex Mono\",monospace'>"
                f"{_short(nb.best_model, 26)}</div>",
                unsafe_allow_html=True,
            )
        st.caption(_CONFIDENCE_NOTE)


def _render_fingerprint_scatter(config, store):
    try:
        from lid_toolkit.recommender.fingerprint_builder import FingerprintBuilder

        matrix, dataset_names, _ = store.fingerprints_matrix(exclude_cat=True)
        if matrix.shape[0] < 3:
            st.info("Not enough datasets in the MKB to compute a meaningful projection.")
            return

        # Build query vector from stored fingerprint
        query_fp_dict = config.trace.get("query_fingerprint")
        if query_fp_dict is not None:
            q_arr, _ = FingerprintBuilder.to_array(
                OrderedDict(query_fp_dict), continuous_only=True
            )
            q_arr = q_arr.reshape(1, -1)
        else:
            # Fallback: reconstruct from stratum_details of first all_candidates entry
            candidates = config.trace.get("all_candidates", [])
            if not candidates:
                st.info("Query fingerprint not available in trace.")
                return
            details = candidates[0].get("stratum_details", {})
            q_arr = np.concatenate(
                [np.array(details[s]["query_vec"]) for s in sorted(details)]
            ).reshape(1, -1)

        # Align dimensions
        min_dim = min(q_arr.shape[1], matrix.shape[1])
        q_arr = q_arr[:, :min_dim]
        matrix_trim = matrix[:, :min_dim]
        combined = np.vstack([matrix_trim, q_arr])

        # Dimensionality reduction
        try:
            from umap import UMAP
            reducer = UMAP(
                n_components=2,
                random_state=42,
                n_neighbors=min(5, len(dataset_names) - 1),
            )
            coords = reducer.fit_transform(combined)
            method = "UMAP"
        except ImportError:
            from sklearn.decomposition import PCA
            coords = PCA(n_components=2, random_state=42).fit_transform(combined)
            method = "PCA"

        hist_xy = coords[:-1]
        q_xy = coords[-1]
        top_k_names = {nb.dataset_name for nb in config.neighbours}

        plot_df = pd.DataFrame({
            "x": hist_xy[:, 0],
            "y": hist_xy[:, 1],
            "Dataset": dataset_names,
            "Type": [
                "Top-k Neighbour" if n in top_k_names else "Historical Dataset"
                for n in dataset_names
            ],
        })

        st.caption(f"Fingerprint space, {method} projection to two dimensions.")
        fig = px.scatter(
            plot_df, x="x", y="y", color="Type", text="Dataset",
            color_discrete_map={
                "Top-k Neighbour": _STEEL,
                "Historical Dataset": _NEUTRAL,
            },
            labels={"x": f"{method} dim 1", "y": f"{method} dim 2"},
        )
        fig.update_traces(
            selector={"name": "Historical Dataset"},
            textposition="top center", marker_size=8,
            textfont=dict(size=10, color=_MUTED),
        )
        fig.update_traces(
            selector={"name": "Top-k Neighbour"},
            textposition="top center", marker_size=13,
            marker_line_width=1.5, marker_line_color=_INK,
            textfont=dict(size=10, color=_INK),
        )

        # The query itself: a ringed marker, distinguished by form rather than
        # by another hue.
        fig.add_trace(go.Scatter(
            x=[q_xy[0]], y=[q_xy[1]],
            mode="markers+text",
            marker=dict(symbol="circle-open-dot", size=20, color=_AMBER,
                        line=dict(width=2.5, color=_AMBER)),
            text=["your corpus"],
            textposition="top center",
            textfont=dict(size=11, color=_AMBER),
            name="Your corpus",
            showlegend=True,
        ))
        _style_fig(fig, 470)
        fig.update_layout(
            legend_title_text="",
            legend=dict(orientation="h", y=1.1, x=0),
        )
        st.plotly_chart(fig, width='stretch')

    except Exception as exc:
        st.warning(f"Fingerprint scatter unavailable: {exc}")


def _render_stratum_distances(neighbours):
    rows = []
    for nb in neighbours:
        for stratum, dist in nb.per_stratum_distances.items():
            rows.append({
                "Stratum": _STRATUM_LABELS.get(stratum, stratum),
                "Distance": dist,
                "Neighbour": _short(nb.dataset_name, 30),
            })
    if not rows:
        st.info("Stratum distances not available.")
        return
    df = pd.DataFrame(rows)
    st.caption("Per-stratum Euclidean distance, query against each top-k neighbour.")
    fig = px.bar(
        df, x="Distance", y="Stratum", color="Neighbour",
        orientation="h", barmode="group",
        color_discrete_sequence=_SERIES,
    )
    _style_fig(fig, 350)
    fig.update_layout(
        legend_title_text="",
        legend=dict(orientation="h", y=1.16, x=0),
        bargap=0.28, bargroupgap=0.06,
    )
    st.plotly_chart(fig, width='stretch')


def _render_idw_breakdown(trace):
    idw = trace.get("idw", {})
    per_nb = idw.get("per_neighbour", [])
    if not per_nb:
        st.info("IDW breakdown not available in trace.")
        return

    # Stacked bar: each model's contributions across neighbours
    contrib_rows = []
    for nb_rec in per_nb:
        for model, info in nb_rec.get("per_model", {}).items():
            contrib_rows.append({
                "Neighbour": _short(nb_rec["dataset"], 28),
                "Model": _short(model, 40),
                "Contribution": info["contribution"],
                "Coverage Factor": info["coverage_factor"],
                "Score": info["score"],
                "1/D": nb_rec["inv_d"],
            })

    if contrib_rows:
        df_c = pd.DataFrame(contrib_rows)
        st.caption("Each neighbour's weighted contribution to every candidate's score.")
        fig_stack = px.bar(
            df_c, x="Neighbour", y="Contribution", color="Model",
            barmode="stack",
            color_discrete_sequence=_SERIES,
            labels={"Contribution": "Contribution to score"},
        )
        _style_fig(fig_stack, 380)
        fig_stack.update_layout(
            legend_title_text="",
            legend=dict(font=dict(size=10)),
            bargap=0.45,
        )
        st.plotly_chart(fig_stack, width='stretch')

        with st.expander("Detailed contribution table"):
            st.dataframe(df_c.round(5), width='stretch')

    # Final normalised scores
    norm = idw.get("normalized_idw_scores", {})
    if norm:
        st.markdown("**Final Normalised IDW Scores (after dividing by Σ(1/D)):**")
        norm_df = pd.DataFrame([
            {"Model": _short(m, 50), "Normalised IDW Score": round(s, 5)}
            for m, s in sorted(norm.items(), key=lambda x: -x[1])
        ]).set_index("Model")
        st.dataframe(norm_df, width='stretch')

    denom = idw.get("denominator", None)
    if denom is not None:
        st.caption(f"Global denominator Σ(1/D) = {denom:.6f}")


# ══════════════════════════════════════════════════════════════════════════════
# Panel 4 — Run Model (Live Inference)
# ══════════════════════════════════════════════════════════════════════════════

def _tab_run_model(result, config, texts: pd.Series | None, experiments_dir: str, store):
    if texts is None or len(texts) == 0:
        st.info("Upload a corpus CSV in the sidebar to enable live model inference.")
        return

    if not Path(experiments_dir).exists():
        st.error(
            f"LID_experiments directory not found: `{experiments_dir}`  \n"
            "Update the path in the sidebar."
        )
        return

    all_models = sorted(result.all_model_scores, key=lambda m: -result.all_model_scores[m])
    rec = result.recommended_model

    st.markdown(
        "Select a model from the ranked list below and run it directly on your uploaded dataset. "
        "All models are loaded from `LID_experiments/` — no internet connection required."
    )

    col_sel, col_n = st.columns([3, 1])
    with col_sel:
        selected = st.selectbox(
            "Model to run",
            options=all_models,
            index=0,
            format_func=lambda m: (
                f"{_short(m, 50)}  "
                f"[IDW: {result.all_model_scores[m]:.4f}]"
                + ("   · recommended" if m == rec else "")
            ),
        )
    with col_n:
        n_sample = st.number_input(
            "Sample size",
            min_value=50,
            max_value=len(texts),
            value=min(2000, len(texts)),
            step=100,
        )

    # Availability check
    runner = _load_runner(experiments_dir, tuple(store.datasets))

    available = runner.is_available(selected)
    if not available:
        try:
            path = runner.model_path(selected)
            st.warning(f"Model file not found on disk:\n\n`{path}`")
        except ValueError as e:
            st.error(str(e))

    run_btn = st.button(
        "Run model on dataset",
        type="primary",
        disabled=not available,
    )

    if run_btn and available:
        sample_texts = (
            texts.sample(n=n_sample, random_state=42)
            .reset_index(drop=True)
            .tolist()
        )
        with st.spinner(f"Running `{_short(selected, 50)}` on {n_sample} samples…"):
            t0 = time.perf_counter()
            preds = runner.predict(selected, sample_texts)
            elapsed = time.perf_counter() - t0

        st.success(
            f"Inference complete · {elapsed:.2f}s · "
            f"{1000 * elapsed / len(preds):.2f} ms/sample · "
            f"{len(preds) / elapsed:,.0f} samples/sec"
        )

        st.session_state["run_preds"] = preds
        st.session_state["run_texts"] = sample_texts
        st.session_state["run_model"] = selected

    # Display results (persist across reruns via session_state)
    if "run_preds" in st.session_state and st.session_state.get("run_model") == selected:
        preds = st.session_state["run_preds"]
        sample_texts = st.session_state["run_texts"]

        st.divider()

        # Per-language distribution
        pred_counts = (
            pd.Series(preds)
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Language", 0: "Count"})
        )
        pred_counts.columns = ["Language", "Count"]
        st.caption(f"Predicted language distribution over {len(preds):,} samples.")
        fig_dist = px.bar(
            pred_counts.head(30), x="Language", y="Count",
            color_discrete_sequence=[_STEEL],
        )
        _style_fig(fig_dist, 330, showlegend=False)
        fig_dist.update_layout(coloraxis_showscale=False, bargap=0.3)
        st.plotly_chart(fig_dist, width='stretch')

        # Sample predictions table
        st.markdown(f"**Sample Predictions (first 50 of {len(preds)}):**")
        preview_df = pd.DataFrame({
            "Text": sample_texts[:50],
            "Predicted Language": preds[:50],
        })
        st.dataframe(preview_df, width='stretch', height=300)

        # Download button
        full_df = pd.DataFrame({"text": sample_texts, "predicted_lang": preds})
        st.download_button(
            label="Download full predictions as CSV",
            data=full_df.to_csv(index=False).encode("utf-8"),
            file_name=f"predictions_{selected[:40]}.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
# Panel 5 — Baseline Comparison
# ══════════════════════════════════════════════════════════════════════════════

def _tab_baseline(result, config, store):
    st.markdown(
        "Compare the framework's recommendation against naive baselines — all measured "
        "as IDW-weighted scores on **your specific query**. "
        "A positive delta means the framework outperforms the baseline for this corpus."
    )

    all_scores = result.all_model_scores
    rec = result.recommended_model
    rec_score = all_scores.get(rec, 0.0)

    # Always-best-default: model that wins the most datasets globally
    try:
        best_per_ds = store.best_model_per_dataset(config.priority_metric)
        win_counts = Counter(best_per_ds.values())
        global_default = win_counts.most_common(1)[0][0] if win_counts else None
        default_score = all_scores.get(global_default, 0.0) if global_default else 0.0
        default_label = _short(global_default, 45) if global_default else "N/A"
        default_wins = win_counts.get(global_default, 0) if global_default else 0
    except Exception as exc:
        global_default = None
        default_score = 0.0
        default_label = f"N/A ({exc})"
        win_counts = {}
        default_wins = 0

    # Random: mean IDW score across all models
    random_score = float(np.mean(list(all_scores.values()))) if all_scores else 0.0

    comp_df = pd.DataFrame({
        "Strategy": [
            f"LID Framework  ·  {_short(rec, 40)}",
            f"Always-best default  ({default_wins} wins)",
            "Random selection (mean)",
        ],
        "IDW Score": [rec_score, default_score, random_score],
        "Category": ["Framework", "Baseline", "Baseline"],
    })

    st.caption("Framework recommendation against the two naive selection policies, "
               "scored on this query.")
    fig_comp = px.bar(
        comp_df, x="IDW Score", y="Strategy", orientation="h",
        color="Category",
        color_discrete_map={"Framework": _SAGE, "Baseline": _NEUTRAL},
        labels={"IDW Score": f"IDW {config.priority_metric}"},
        text="IDW Score",
    )
    fig_comp.update_traces(texttemplate="%{text:.4f}", textposition="outside",
                           textfont=dict(size=11, color=_MUTED), cliponaxis=False)
    _style_fig(fig_comp, 250, showlegend=False)
    fig_comp.update_layout(xaxis_range=[0, None], bargap=0.42,
                           margin=dict(t=8, b=8, l=8, r=44))
    fig_comp.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig_comp, width='stretch')

    d1, d2 = st.columns(2)
    delta_vs_default = rec_score - default_score
    delta_vs_random = rec_score - random_score
    d1.metric(
        "Δ vs Always-best Default",
        f"{delta_vs_default:+.4f}",
        f"{delta_vs_default / max(abs(default_score), 1e-9):.1%} relative",
        delta_color="normal",
    )
    d2.metric(
        "Δ vs Random Selection",
        f"{delta_vs_random:+.4f}",
        f"{delta_vs_random / max(abs(random_score), 1e-9):.1%} relative",
        delta_color="normal",
    )

    st.markdown("""
**How to interpret:**
- *LID Framework* selects the model with the highest expected performance for **this specific corpus**.
- *Always-best default* picks whichever model wins the most historical datasets globally — a strong zero-effort baseline.
- *Random selection* establishes the floor: the expected score if a model were picked at random.

A positive delta against the default indicates that the meta-learning approach adds value over
simply always recommending the globally best model.
""")

    if win_counts:
        with st.expander("Global model win distribution (across all MKB datasets)"):
            wdf = (
                pd.DataFrame(win_counts.items(), columns=["Model", "Datasets Won"])
                .sort_values("Datasets Won", ascending=False)
                .set_index("Model")
            )
            st.dataframe(wdf, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# Panel 6 — Coverage & Scope
# ══════════════════════════════════════════════════════════════════════════════

def _tab_coverage(result, config):
    st.markdown(
        "Shows which languages in your corpus are covered by the top-k recommended models. "
        "A language is *covered* when it appears in the model's training dataset."
    )

    iso_codes = sorted(config.query_iso_codes)
    neighbours = config.neighbours
    uncoverable = sorted(result.uncoverable_languages)
    rec = result.recommended_model

    if not iso_codes:
        st.info("No language information available.")
        return

    # Collect top models sorted by IDW score (cap at 8 for legible heatmap)
    scored_models = sorted(result.all_model_scores, key=lambda m: -result.all_model_scores[m])
    top_models = scored_models[:8]

    # Build binary coverage matrix
    def _is_covered(lang: str, model: str) -> bool | None:
        for nb in neighbours:
            if model in nb.per_model_gaps:
                return lang not in nb.per_model_gaps[model]
        return None   # unknown

    z_vals: list[list[float]] = []
    text_vals: list[list[str]] = []
    for lang in iso_codes:
        z_row, t_row = [], []
        for model in top_models:
            cov = _is_covered(lang, model)
            if cov is True:
                z_row.append(1.0);  t_row.append("●")
            elif cov is False:
                z_row.append(0.0);  t_row.append("○")
            else:
                z_row.append(0.5);  t_row.append("–")
        z_vals.append(z_row)
        text_vals.append(t_row)

    model_labels = [_short(m, 32) for m in top_models]

    st.caption(
        "Language coverage matrix — filled = covered, hollow = gap, dash = unknown. "
        "Models are ordered by IDW score, best on the left."
    )
    fig_heat = go.Figure(go.Heatmap(
        z=z_vals,
        x=model_labels,
        y=iso_codes,
        text=text_vals,
        texttemplate="%{text}",
        textfont=dict(size=12, color=_INK),
        # Muted fills on charcoal: a gap is the only cell that carries a warm
        # hue, so the eye lands on the problem rather than on the wall of ticks.
        colorscale=[
            # Tints of the Gentelella red / neutral / green over the card
            # surface — the same three roles the legend names in words.
            [0.0,  "#4A2230"],   # gap
            [0.45, "#4A2230"],
            [0.5,  "#1F2836"],   # unknown
            [0.55, "#1F2836"],
            [1.0,  "#1C3A2A"],   # covered
        ],
        zmin=0, zmax=1,
        showscale=False,
        xgap=3, ygap=3,
    ))
    _style_fig(fig_heat, max(300, len(iso_codes) * 26 + 110), showlegend=False)
    fig_heat.update_layout(
        xaxis_title="Model", yaxis_title="Detected language",
        xaxis_tickangle=-30,
        margin=dict(t=8, b=8, l=8, r=8),
    )
    fig_heat.update_xaxes(showgrid=False)
    fig_heat.update_yaxes(showgrid=False)
    st.plotly_chart(fig_heat, width='stretch')

    st.caption(
        "Only top-8 models by IDW score are shown. "
        "Coverage is inferred from training dataset iso_codes — "
        "the same logic used in the recommender's coverage penalty."
    )

    # Per-language status summary
    summary_rows = []
    for lang in iso_codes:
        rec_cov = _is_covered(lang, rec)
        if lang in result.uncoverable_languages:
            status = "Uncoverable — absent from all MKB datasets"
        elif rec_cov is False:
            status = "Gap in the recommended model"
        elif rec_cov is True:
            status = "Covered by the recommended model"
        else:
            status = "Coverage unknown"
        summary_rows.append({"ISO Code": lang, "Status": status})
    st.dataframe(pd.DataFrame(summary_rows).set_index("ISO Code"), width='stretch')

    # Alerts
    if uncoverable:
        st.error(
            f"**Uncoverable languages:** {', '.join(uncoverable)}  \n"
            "These appear in your corpus but are absent from ALL historical benchmark datasets. "
            "No reliable recommendation can be made for these languages — "
            "consider sourcing training data for them."
        )
    elif not any(nb.coverage_gap for nb in neighbours):
        st.success("All detected languages are fully covered by the recommended model.")

    # Scope note
    with st.expander("Note on framework scope"):
        st.markdown("""
The current MKB covers **24 languages** (ca, da, de, el, en, es, fi, fr, hr, it, ja, ko,
lt, mk, nb, nl, pl, pt, ro, ru, sl, sv, uk, zh) across European, East Asian, and Slavic
language families.

Languages outside this set — including low-resource African, Indigenous American, and
South/Southeast Asian languages — are not represented in the benchmark datasets and
**will not receive reliable recommendations**. This is a known limitation of the current
benchmark scope, discussed in the thesis.
""")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.markdown(_CSS, unsafe_allow_html=True)
    # Gentelella's shell is a fixed topbar over a page header carrying a
    # pretitle, an h1 and a breadcrumb. Streamlit owns the sidebar and the
    # scroll container, so the topbar is rendered as the first block in the
    # main pane rather than as a fixed element — the reading order is the same.
    st.markdown(
        '<div class="g-topbar">'
        '  <div class="g-brand">'
        '    <span class="g-logo">LID</span>'
        '    <span class="g-brandname">LID Framework</span>'
        '  </div>'
        '  <div class="g-topbar-meta">Werner Hugo &nbsp;·&nbsp; '
        'MEng thesis, Stellenbosch University</div>'
        '</div>'
        '<div class="g-pagehead">'
        '  <div class="g-pretitle">Model recommendation</div>'
        '  <h1 class="g-title">Interactive Dashboard</h1>'
        '  <div class="g-breadcrumb">Meta-Knowledge Base<span>/</span>'
        'Corpus fingerprint<span>/</span>Recommendation</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.subheader("Configuration")
        store_path = st.text_input(
            "MKB path (mkb.pkl)",
            value=_DEFAULT_STORE,
            help="Path to the serialised Meta-Knowledge Base.",
        )
        experiments_dir = st.text_input(
            "LID_experiments directory",
            value=_DEFAULT_EXPERIMENTS,
            help="Root of the LID_experiments/ folder (used for live model inference).",
        )

        st.divider()
        st.subheader("Corpus")
        uploaded = st.file_uploader(
            "Upload CSV file",
            type=["csv", "tsv"],
            help="Your text corpus. Must contain a column with raw text samples.",
        )
        text_col = st.text_input(
            "Text column name",
            value="text",
            help="Name of the column that contains the text samples.",
        )

        st.divider()
        analyse = st.button("Profile corpus", type="primary", width='stretch')
        st.caption(
            "Profiling runs once. The priority metric is then a live control in "
            "the main pane — re-querying does not re-profile."
        )

        if "profile" in st.session_state:
            if st.button("Clear session", width='stretch'):
                for key in ["profile", "texts", "profiling_time",
                            "run_preds", "run_texts", "run_model"]:
                    st.session_state.pop(key, None)
                st.rerun()

    # ── Phase 1: profile the corpus (expensive, run once) ──────────────────────
    if analyse:
        if not uploaded:
            st.sidebar.error("Please upload a CSV file first.")
            st.stop()
        if not Path(store_path).exists():
            st.sidebar.error(f"MKB file not found:\n{store_path}")
            st.stop()

        sep = "\t" if uploaded.name.endswith(".tsv") else ","
        try:
            df = pd.read_csv(uploaded, sep=sep, dtype=str)
        except Exception as e:
            st.sidebar.error(f"Could not read file: {e}")
            st.stop()

        if text_col not in df.columns:
            st.sidebar.error(
                f"Column '{text_col}' not found.  "
                f"Available columns: {list(df.columns)}"
            )
            st.stop()

        texts = df[text_col].dropna().reset_index(drop=True)
        if len(texts) == 0:
            st.sidebar.error("No text samples found after dropping nulls.")
            st.stop()

        with st.spinner(
            f"Profiling corpus ({len(texts):,} samples)…  "
            "This may take several minutes for large corpora."
        ):
            lid = _load_recommender(store_path)
            t0 = time.perf_counter()
            profile = lid.profile(texts)
            elapsed = time.perf_counter() - t0

        st.session_state.update({
            "profile": profile,
            "texts": texts,
            "profiling_time": elapsed,
        })
        # Clear any stale inference results
        for k in ["run_preds", "run_texts", "run_model"]:
            st.session_state.pop(k, None)
        st.rerun()

    # ── Landing state ──────────────────────────────────────────────────────────
    if "profile" not in st.session_state:
        st.info(
            "Upload a corpus CSV in the sidebar and click **Profile corpus** "
            "to get a recommendation."
        )
        with st.expander("How to use this dashboard"):
            st.markdown("""
1. **Configure** — set the paths to `mkb.pkl` and the `LID_experiments/` folder.
2. **Upload** — provide a CSV file with a column of text samples.
3. **Profile** — click the button; DeepProfiler characterises your corpus once
   (a few minutes for large corpora).
4. **Query** — set the priority metric in the main pane. Each change re-queries
   the Meta-Knowledge Base from the cached fingerprint in milliseconds.
5. **Explore** six panels:
   - **Corpus Profile** — language census, document lengths, fingerprint composition.
   - **Recommendation** — model, consensus confidence, ranked shortlist, all model scores.
   - **How It Works** — step-by-step mathematical walkthrough with interactive charts.
   - **Run Model** — load and run the recommended model directly on your dataset.
   - **Baselines** — compare the framework against naive selection policies.
   - **Coverage** — language × model support matrix and scope warnings.
""")
        return

    profile = st.session_state["profile"]
    texts = st.session_state.get("texts")
    profiling_time = st.session_state.get("profiling_time", 0.0)

    # ── Phase 2: live query controls (cheap, re-run on every interaction) ──────
    ctrl_l, ctrl_r = st.columns([2, 3])
    with ctrl_l:
        metric = st.selectbox(
            "Priority metric",
            _METRICS,
            index=0,
            help=(
                "Metric to optimise: accuracy/F1/precision/recall (higher=better), "
                "inference_time_* (lower=better) or throughput (higher=better). "
                "Changing this re-queries the knowledge base immediately."
            ),
        )

    lid = _load_recommender(store_path)
    store = lid.store
    try:
        t0 = time.perf_counter()
        result, config = lid.explain_from_profile(profile, metric=metric)
        query_ms = (time.perf_counter() - t0) * 1000
    except Exception as exc:
        st.error(f"Query failed for metric `{metric}`: {exc}")
        return

    with ctrl_r:
        st.markdown(
            f"<div style='padding-top:2.05rem;color:{_MUTED};font-size:12.5px'>"
            f"Corpus profiled in <b style='color:{_INK}'>{profiling_time:.1f}&nbsp;s</b>"
            f" (once) &nbsp;·&nbsp; this query answered in "
            f"<b style='color:{_PRIMARY}'>{query_ms:.0f}&nbsp;ms</b> from the cached "
            f"fingerprint</div>",
            unsafe_allow_html=True,
        )

    # ── 6 Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Corpus profile",
        "Recommendation",
        "How it works",
        "Run model",
        "Baselines",
        "Coverage",
    ])

    with tab1:
        _tab_corpus(config, profile, texts, profiling_time, store)
    with tab2:
        _tab_overview(result, config, query_ms, store.datasets)
    with tab3:
        _tab_walkthrough(result, config, store)
    with tab4:
        _tab_run_model(result, config, texts, experiments_dir, store)
    with tab5:
        _tab_baseline(result, config, store)
    with tab6:
        _tab_coverage(result, config)


if __name__ == "__main__":
    main()
