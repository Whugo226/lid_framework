"""
LID Toolkit — End-to-End Demonstration
=======================================
Demonstrates the full public API:
  - load_text()       : load a text corpus
  - LID_Recommender   : recommend the best LID model for your corpus
  - ExplainerConfig   : inspect the reasoning behind the recommendation

Run from the project root:
    python examples/demonstration.py
"""

from pathlib import Path

from lid_toolkit import LID_Recommender, ExplainerConfig
from lid_toolkit.loader import load_text

# ---------------------------------------------------------------------------
# Paths (resolved relative to this file so the script works from any cwd)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
STORE_PATH = ROOT / "mkb.pkl"

# ---------------------------------------------------------------------------
# 1. Load corpus — sample limits profiling time for demonstration purposes
# ---------------------------------------------------------------------------
texts = load_text(Path(__file__).parent / "test.csv", text_column="text")
print(f"Loaded {len(texts)} text samples.\n")

# ---------------------------------------------------------------------------
# 2. Instantiate the recommender (loads mkb.pkl once)
# ---------------------------------------------------------------------------
lid = LID_Recommender(STORE_PATH)

# ---------------------------------------------------------------------------
# 3. Run once in explain mode — returns both recommendation and full config
#    (avoids profiling the corpus twice)
# ---------------------------------------------------------------------------
print("=" * 60)
print("PROFILING & RECOMMENDATION")
print("=" * 60)

result, config = lid.recommend(texts, metric="f1_weighted", mode="explain")

# --- Core result ---
print(f"\n  Recommended model : {result.recommended_model}")
print(f"  Confidence        : {result.confidence:.0%}")
print(f"  Metric optimised  : {result.priority_metric}")

if result.uncoverable_languages:
    print(f"  Coverage warning  : {sorted(result.uncoverable_languages)}")

print(f"\n  Explanation:\n  {result.explanation}\n")

print("  All model scores (IDW-weighted):")
for model, score in sorted(result.all_model_scores.items(), key=lambda x: -x[1]):
    print(f"    {model:<30} {score:.4f}")

# --- Explainer detail ---
print("\n" + "=" * 60)
print("EXPLAINER — NEAREST NEIGHBOURS")
print("=" * 60)

print(f"  Detected languages : {config.query_iso_codes}")
print(f"  Recommended model  : {config.recommended_model}")
print(f"  Confidence         : {config.confidence:.0%}\n")

print("  Top neighbours:")
for i, nb in enumerate(config.neighbours, 1):
    print(f"    [{i}] {nb.dataset_name}")
    print(f"        Similarity : {nb.similarity_pct:.1f}%  |  Best model: {nb.best_model}  |  Score: {nb.best_score:.4f}")
    if nb.coverage_gap:
        print(f"        Coverage gap : {sorted(nb.coverage_gap)}")

print("\n  Per-stratum distances (query vs nearest neighbour):")
first_nb = config.neighbours[0]
for stratum, dist in first_nb.per_stratum_distances.items():
    print(f"    {stratum:<30} {dist:.4f}")

# --- Trace keys ---
print("\n" + "=" * 60)
print("TRACE KEYS (available for dashboard)")
print("=" * 60)
for key in config.trace.keys():
    print(f"  config.trace['{key}']")
