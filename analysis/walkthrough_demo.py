"""R18 walkthrough demo: run the deployed framework end-to-end on the WiLI-2018
sample (a corpus genuinely outside the MKB) and capture real outputs for the
Ch5 practitioner walkthrough subsection.

Three queries against one profile:
  1. default quality priority (f1_weighted)
  2. latency priority (inference_time_ms_per_sample)
  3. explicit language requirement including a language that exposes
     coverage gaps (detected set + extras), to exercise the coverage guard
"""
import json
import sys
import time
from pathlib import Path

import pandas as pd

TK = Path(r"c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit")
sys.path.insert(0, str(TK / "src"))
OUT = Path(__file__).parent / "walkthrough_results.json"

lines = [l.strip() for l in
         (TK / "test_examples" / "wili2018_test.txt").read_text(encoding="utf-8").splitlines()
         if len(l.strip()) > 30]
texts = pd.Series(lines[:600])
print(f"loaded {len(texts)} lines from wili2018_test.txt")

from lid_toolkit.recommender import Recommender
rec = Recommender.from_store(TK / "mkb.pkl", k=3)

from lid_toolkit.logic.profiler_knowledge_base import DeepProfiler
prof = DeepProfiler()
t0 = time.perf_counter()
profile = prof.run_profile("user", text_series=texts)
t_prof = time.perf_counter() - t0
print(f"profiled: {profile.shape[0]} features x {profile.shape[1]} languages "
      f"in {t_prof:.1f}s: {sorted(profile.columns)}")

results = {"n_texts": len(texts), "profile_seconds": round(t_prof, 1),
           "detected_languages": sorted(profile.columns)}

def capture(tag, r):
    top3 = sorted(r.all_model_scores, key=r.all_model_scores.get, reverse=True)[:3]
    results[tag] = {
        "recommended_model": r.recommended_model,
        "confidence": round(r.confidence, 4),
        "neighbours": [
            {"dataset": nb.dataset_name, "sim_pct": nb.similarity_pct,
             "best_model": nb.best_model}
            for nb in r.neighbours[:3]
        ],
        "top3_idw": {m: round(r.all_model_scores[m], 6) for m in top3},
        "explanation": r.explanation,
    }
    print(f"\n===== {tag} =====")
    print(f"recommended: {r.recommended_model}  conf={r.confidence:.2f}")
    for nb in r.neighbours[:3]:
        print(f"  neighbour: {nb.dataset_name} ({nb.similarity_pct:.1f}%) best={nb.best_model}")
    print(r.explanation[:1200])

# 1. quality priority
capture("q1_f1_weighted", rec.recommend_from_profile(profile, priority_metric="f1_weighted"))

# 2. latency priority
capture("q2_latency", rec.recommend_from_profile(profile, priority_metric="inference_time_ms_per_sample"))

# 3. explicit language requirement with extras to exercise the coverage guard
builder = rec.store.builder
fp = builder.build(profile)
required = frozenset(set(profile.columns) | {"lt", "ko", "mk"})
r3 = rec.engine.query(fp, priority_metric="f1_weighted", user_iso_codes=required)
results["q3_required_langs"] = sorted(required)
capture("q3_coverage", r3)

OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nsaved -> {OUT}")
