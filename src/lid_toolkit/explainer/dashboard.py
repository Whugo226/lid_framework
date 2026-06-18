"""
LID Toolkit — Interactive Dashboard
=====================================
Five-panel Streamlit app for exploring, explaining, and running LID model
recommendations produced by the LID Toolkit.

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
    page_title="LID Toolkit",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Defaults from environment ──────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[4]   # project root

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

_METRICS = ["f1_weighted", "f1_macro", "accuracy", "precision_macro", "recall_macro"]

_STRATUM_LABELS: dict[str, str] = {
    "S1_morphological":     "Morphological Richness (S1)",
    "S2_lexical_diversity": "Lexical Diversity (S2)",
    "S3_structural":        "Structural / Syntactic (S3)",
    "S4_info_theoretic":    "Information-Theoretic (S4)",
    "S5_cross_level":       "Cross-Level Cohesion (S5)",
    "cat":                  "Typological Flags (S6)",
}


# ── Cached resources ───────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading Meta-Knowledge Base…")
def _load_store(store_path: str):
    from lid_toolkit.recommender.mkb_store import MKBStore
    return MKBStore.load(store_path)


# ── Small helpers ──────────────────────────────────────────────────────────────

def _strip_dataset(variant: str, datasets: list[str]) -> str:
    """Return just the architecture part of a composite variant name."""
    for ds in sorted(datasets, key=len, reverse=True):
        if variant.endswith(f"_{ds}"):
            return variant[: -(len(ds) + 1)]
    return variant


def _family_label(arch: str) -> str:
    if arch.startswith("fasttext"):
        return "FastText (custom)"
    if arch.startswith("lid."):
        return "FastText (off-the-shelf)"
    if "lr" in arch:
        return "Logistic Regression"
    return "Naïve Bayes"


def _short(name: str, n: int = 35) -> str:
    return name if len(name) <= n else name[:n] + "…"


# ══════════════════════════════════════════════════════════════════════════════
# Panel 1 — Recommendation Overview
# ══════════════════════════════════════════════════════════════════════════════

def _tab_overview(result, config, profiling_time: float, store_datasets: list[str]):
    rec = result.recommended_model
    conf = result.confidence
    iso_codes = config.query_iso_codes

    # ── Top metric strip ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Recommended Model", _short(rec, 40))
    c2.metric("Confidence", f"{conf:.0%}")
    c3.metric("Languages Detected", len(iso_codes))
    c4.metric("Profiling Time", f"{profiling_time:.1f} s")

    st.caption(f"Metric optimised: **{config.priority_metric}**  ·  "
               f"Detected: {', '.join(sorted(iso_codes))}")
    st.divider()

    # ── Confidence gauge + paradigm pie ───────────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.subheader("Confidence Gauge")
        colour = "#2ecc71" if conf >= 0.67 else ("#f39c12" if conf >= 0.34 else "#e74c3c")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=conf * 100,
            number={"suffix": "%", "font": {"size": 32}},
            gauge={
                "axis": {"range": [0, 100], "ticksuffix": "%"},
                "bar": {"color": colour},
                "steps": [
                    {"range": [0,  34], "color": "#fdecea"},
                    {"range": [34, 67], "color": "#fef9e7"},
                    {"range": [67, 100], "color": "#eafaf1"},
                ],
                "threshold": {"line": {"color": "black", "width": 2}, "value": conf * 100},
            },
        ))
        fig_gauge.update_layout(height=240, margin=dict(t=10, b=0, l=20, r=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with right:
        st.subheader("Paradigm Breakdown (Top-k Neighbours)")
        archs = [_strip_dataset(nb.best_model, store_datasets) for nb in config.neighbours]
        families = [_family_label(a) for a in archs]
        counts = Counter(families)
        if counts:
            fig_pie = px.pie(
                names=list(counts.keys()),
                values=list(counts.values()),
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.45,
            )
            fig_pie.update_traces(textinfo="label+percent")
            fig_pie.update_layout(height=240, margin=dict(t=10, b=0, l=0, r=0),
                                  showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
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
                             if nb.coverage_gap else "✓ Full coverage"),
        })
    st.dataframe(pd.DataFrame(nb_rows).set_index("Rank"), use_container_width=True)

    st.divider()

    # ── All model IDW scores ──────────────────────────────────────────────────
    st.subheader("All Model IDW Scores (Coverage-Penalised)")
    scores = result.all_model_scores
    score_df = pd.DataFrame([
        {"Model": _short(m, 50), "IDW Score": s,
         "Winner": "✓ Recommended" if m == rec else ""}
        for m, s in sorted(scores.items(), key=lambda x: -x[1])
    ])
    fig_scores = px.bar(
        score_df, x="IDW Score", y="Model", orientation="h",
        color="Winner",
        color_discrete_map={"✓ Recommended": "#2ecc71", "": "#95a5a6"},
        labels={"IDW Score": f"IDW {config.priority_metric}"},
    )
    fig_scores.update_layout(
        showlegend=False,
        height=max(220, len(score_df) * 26 + 60),
    )
    fig_scores.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig_scores, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Panel 2 — Mathematical Interpretability Walkthrough
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
            "**DeepProfiler** extracts ~3,066 linguistic features per language across "
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
                use_container_width=True,
            )
        weights = trace.get("stratum_weights", {})
        if weights:
            w_df = pd.DataFrame([
                {"Stratum": _STRATUM_LABELS.get(s, s), "Weight": round(w, 4)}
                for s, w in weights.items()
            ])
            fig_w = px.bar(
                w_df, x="Weight", y="Stratum", orientation="h",
                color="Weight", color_continuous_scale="Blues",
                title="Stratum Weights (higher = more influential in distance calculation)",
            )
            fig_w.update_layout(height=280, coloraxis_showscale=False)
            st.plotly_chart(fig_w, use_container_width=True)

    # ── Step 2: Fingerprint space ─────────────────────────────────────────────
    with st.expander("**Step 2 — Nearest Neighbour Matching in Fingerprint Space**",
                     expanded=False):
        st.markdown(r"""
The composite distance between your query $q$ and each historical dataset $c$ is:

$$D(q,\,c) = \frac{\displaystyle\sum_s w_s \cdot \|\mathbf{v}_q^s - \mathbf{v}_c^s\|_2}{\displaystyle\sum_s w_s}$$

where $\mathbf{v}^s$ is the PCA-projected vector for stratum $s$ and $w_s$ is its learned weight.

The scatter plot below shows a 2D projection (UMAP if available, else PCA) of the full
fingerprint space. **★ = your dataset**, red dots = selected top-k neighbours.
""")
        _render_fingerprint_scatter(config, store)

    # ── Step 3: Stratum distances ─────────────────────────────────────────────
    with st.expander("**Step 3 — Per-Stratum Distance Breakdown**", expanded=False):
        st.markdown(
            "Overall similarity is decomposed by linguistic stratum. "
            "Each bar shows the Euclidean distance between your corpus and a top-k neighbour "
            "within that stratum's PCA subspace. **Lower = more similar in that dimension.**"
        )
        _render_stratum_distances(config.neighbours)

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
    with st.expander("**Step 5 — Confidence Calculation**", expanded=False):
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
            col.metric(
                label=f"Neighbour {i+1}",
                value="✅ Agrees" if agrees else "❌ Differs",
                delta=_short(nb.best_model, 25),
                delta_color="normal" if agrees else "off",
            )


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

        fig = px.scatter(
            plot_df, x="x", y="y", color="Type", text="Dataset",
            color_discrete_map={
                "Top-k Neighbour":  "#e74c3c",
                "Historical Dataset": "#bdc3c7",
            },
            labels={"x": f"{method} Dim 1", "y": f"{method} Dim 2"},
            title=f"Fingerprint Space ({method} projection)",
        )
        fig.update_traces(
            selector={"name": "Historical Dataset"},
            textposition="top center",
            marker_size=9,
        )
        fig.update_traces(
            selector={"name": "Top-k Neighbour"},
            textposition="top center",
            marker_size=14,
            marker_line_width=2,
            marker_line_color="#c0392b",
        )

        # Query point as gold star
        fig.add_trace(go.Scatter(
            x=[q_xy[0]], y=[q_xy[1]],
            mode="markers+text",
            marker=dict(symbol="star", size=22, color="#f39c12",
                        line=dict(width=1.5, color="#d68910")),
            text=["★ Your Dataset"],
            textposition="top center",
            name="Your Dataset",
            showlegend=True,
        ))
        fig.update_layout(height=480, legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)

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
    fig = px.bar(
        df, x="Distance", y="Stratum", color="Neighbour",
        orientation="h", barmode="group",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Per-Stratum Euclidean Distance (query vs each top-k neighbour)",
    )
    fig.update_layout(height=360)
    st.plotly_chart(fig, use_container_width=True)


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
        fig_stack = px.bar(
            df_c, x="Neighbour", y="Contribution", color="Model",
            barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Set3,
            title="IDW Contributions per Neighbour",
            labels={"Contribution": f"Contribution to Score"},
        )
        fig_stack.update_layout(height=370)
        st.plotly_chart(fig_stack, use_container_width=True)

        with st.expander("Detailed contribution table"):
            st.dataframe(df_c.round(5), use_container_width=True)

    # Final normalised scores
    norm = idw.get("normalized_idw_scores", {})
    if norm:
        st.markdown("**Final Normalised IDW Scores (after dividing by Σ(1/D)):**")
        norm_df = pd.DataFrame([
            {"Model": _short(m, 50), "Normalised IDW Score": round(s, 5)}
            for m, s in sorted(norm.items(), key=lambda x: -x[1])
        ]).set_index("Model")
        st.dataframe(norm_df, use_container_width=True)

    denom = idw.get("denominator", None)
    if denom is not None:
        st.caption(f"Global denominator Σ(1/D) = {denom:.6f}")


# ══════════════════════════════════════════════════════════════════════════════
# Panel 3 — Run Model (Live Inference)
# ══════════════════════════════════════════════════════════════════════════════

def _tab_run_model(result, config, texts: pd.Series | None, experiments_dir: str):
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
                + ("  ← recommended" if m == rec else "")
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
    from lid_toolkit.recommender.mkb_store import MKBStore
    store = MKBStore.load(config.store_path)
    from lid_toolkit.explainer.model_runner import ModelRunner
    runner = ModelRunner(experiments_dir, store.datasets)

    available = runner.is_available(selected)
    if not available:
        try:
            path = runner.model_path(selected)
            st.warning(f"Model file not found on disk:\n\n`{path}`")
        except ValueError as e:
            st.error(str(e))

    run_btn = st.button(
        "▶  Run Model on Dataset",
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
        fig_dist = px.bar(
            pred_counts.head(30),
            x="Language", y="Count",
            color="Count",
            color_continuous_scale="Blues",
            title=f"Predicted Language Distribution  ({len(preds)} samples)",
        )
        fig_dist.update_layout(height=350, coloraxis_showscale=False)
        st.plotly_chart(fig_dist, use_container_width=True)

        # Sample predictions table
        st.markdown(f"**Sample Predictions (first 50 of {len(preds)}):**")
        preview_df = pd.DataFrame({
            "Text": sample_texts[:50],
            "Predicted Language": preds[:50],
        })
        st.dataframe(preview_df, use_container_width=True, height=300)

        # Download button
        full_df = pd.DataFrame({"text": sample_texts, "predicted_lang": preds})
        st.download_button(
            label="⬇  Download full predictions as CSV",
            data=full_df.to_csv(index=False).encode("utf-8"),
            file_name=f"predictions_{selected[:40]}.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
# Panel 4 — Baseline Comparison
# ══════════════════════════════════════════════════════════════════════════════

def _tab_baseline(result, config, store):
    st.markdown(
        "Compare the toolkit's recommendation against naive baselines — all measured "
        "as IDW-weighted scores on **your specific query**. "
        "A positive delta means the toolkit outperforms the baseline for this corpus."
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
            f"LID Toolkit  →  {_short(rec, 40)}",
            f"Always-best Default  ({default_wins} wins)",
            "Random Selection (mean)",
        ],
        "IDW Score": [rec_score, default_score, random_score],
        "Category": ["Toolkit", "Baseline", "Baseline"],
    })

    fig_comp = px.bar(
        comp_df, x="IDW Score", y="Strategy", orientation="h",
        color="Category",
        color_discrete_map={"Toolkit": "#2ecc71", "Baseline": "#95a5a6"},
        labels={"IDW Score": f"IDW {config.priority_metric}"},
        title="Toolkit vs Baseline Strategies",
        text="IDW Score",
    )
    fig_comp.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig_comp.update_layout(height=260, showlegend=False, xaxis_range=[0, None])
    fig_comp.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig_comp, use_container_width=True)

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
- *LID Toolkit* selects the model with the highest expected performance for **this specific corpus**.
- *Always-best Default* picks whichever model wins the most historical datasets globally — a strong zero-effort baseline.
- *Random Selection* establishes the floor: expected score if a model were picked at random.

A positive delta against the default confirms the meta-learning approach adds value over simply
always recommending the globally best model.
""")

    if win_counts:
        with st.expander("Global model win distribution (across all MKB datasets)"):
            wdf = (
                pd.DataFrame(win_counts.items(), columns=["Model", "Datasets Won"])
                .sort_values("Datasets Won", ascending=False)
                .set_index("Model")
            )
            st.dataframe(wdf, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Panel 5 — Coverage & Scope
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
                z_row.append(1.0);  t_row.append("✓")
            elif cov is False:
                z_row.append(0.0);  t_row.append("✗")
            else:
                z_row.append(0.5);  t_row.append("?")
        z_vals.append(z_row)
        text_vals.append(t_row)

    model_labels = [_short(m, 32) for m in top_models]

    fig_heat = go.Figure(go.Heatmap(
        z=z_vals,
        x=model_labels,
        y=iso_codes,
        text=text_vals,
        texttemplate="%{text}",
        colorscale=[
            [0.0,  "#fdecea"],   # gap     → red tint
            [0.45, "#fdecea"],
            [0.5,  "#fef9e7"],   # unknown → yellow tint
            [0.55, "#fef9e7"],
            [1.0,  "#d5f5e3"],   # covered → green tint
        ],
        zmin=0, zmax=1,
        showscale=False,
        xgap=2, ygap=2,
    ))
    fig_heat.update_layout(
        title="Language Coverage Matrix (✓ = covered · ✗ = gap · ? = unknown)",
        height=max(300, len(iso_codes) * 28 + 100),
        xaxis_title="Model (sorted by IDW score, best = leftmost)",
        yaxis_title="Detected Language",
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

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
            status = "⚠️ Uncoverable (absent from all MKB datasets)"
        elif rec_cov is False:
            status = "⚠️ Gap in recommended model"
        elif rec_cov is True:
            status = "✓ Covered by recommended model"
        else:
            status = "? Coverage unknown"
        summary_rows.append({"ISO Code": lang, "Status": status})
    st.dataframe(pd.DataFrame(summary_rows).set_index("ISO Code"), use_container_width=True)

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
    with st.expander("Note on toolkit scope"):
        st.markdown("""
The current MKB covers **24 languages** (ca, da, de, el, en, es, fi, fr, hr, it, ja, ko,
lt, mk, nb, nl, pl, pt, ro, ru, sl, sv, uk, zh) across European, East Asian, and Slavic
language families.

Languages outside this set — including low-resource African, Indigenous American, and
South/Southeast Asian languages — are not represented in the benchmark datasets and
**will not receive reliable recommendations**. This is a known limitation of the current
benchmark scope, discussed in the thesis (§ 4.5).
""")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.title("🌐  LID Toolkit — Interactive Dashboard")
    st.caption(
        "Language Identification Model Recommender  ·  Werner Hugo  ·  MEng Thesis  "
        "·  Stellenbosch University"
    )

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️  Configuration")
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
        metric = st.selectbox(
            "Optimisation metric",
            _METRICS,
            index=0,
            help="Benchmark metric to maximise when ranking models.",
        )

        st.divider()
        st.header("📂  Upload Corpus")
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
        analyse = st.button("🔍  Analyse Corpus", type="primary", use_container_width=True)

        if "result" in st.session_state:
            if st.button("🗑  Clear Results", use_container_width=True):
                for key in ["result", "config", "texts", "profiling_time",
                            "run_preds", "run_texts", "run_model"]:
                    st.session_state.pop(key, None)
                st.rerun()

    # ── Run analysis ───────────────────────────────────────────────────────────
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
            from lid_toolkit import LID_Recommender
            lid = LID_Recommender(store_path)
            t0 = time.perf_counter()
            result, config = lid.recommend(texts, metric=metric, mode="explain")
            elapsed = time.perf_counter() - t0

        st.session_state.update({
            "result": result,
            "config": config,
            "texts": texts,
            "profiling_time": elapsed,
        })
        # Clear any stale inference results
        for k in ["run_preds", "run_texts", "run_model"]:
            st.session_state.pop(k, None)
        st.rerun()

    # ── Show results ───────────────────────────────────────────────────────────
    if "result" not in st.session_state:
        st.info(
            "Upload a corpus CSV in the sidebar and click **Analyse Corpus** "
            "to get a recommendation."
        )
        with st.expander("How to use this dashboard"):
            st.markdown("""
1. **Configure** — set the paths to `mkb.pkl` and the `LID_experiments/` folder.
2. **Upload** — provide a CSV file with a column of text samples.
3. **Analyse** — click the button; DeepProfiler will profile your corpus
   (a few minutes for large corpora).
4. **Explore** five panels:
   - **Recommendation** — model, confidence, top-k neighbours, all model scores.
   - **How It Works** — step-by-step mathematical walkthrough with interactive charts.
   - **Run Model** — load and run the recommended model directly on your dataset.
   - **Baseline** — compare the toolkit against naive strategies.
   - **Coverage** — language × model support matrix and scope warnings.
""")
        return

    result = st.session_state["result"]
    config = st.session_state["config"]
    texts = st.session_state.get("texts")
    profiling_time = st.session_state.get("profiling_time", 0.0)

    store = _load_store(store_path)

    # ── 5 Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊  Recommendation",
        "🔍  How It Works",
        "▶  Run Model",
        "📈  Baseline",
        "🌍  Coverage",
    ])

    with tab1:
        _tab_overview(result, config, profiling_time, store.datasets)
    with tab2:
        _tab_walkthrough(result, config, store)
    with tab3:
        _tab_run_model(result, config, texts, experiments_dir)
    with tab4:
        _tab_baseline(result, config, store)
    with tab5:
        _tab_coverage(result, config)


if __name__ == "__main__":
    main()
