"""
mkb_summary.py — read-only summary of the deployed Meta-Knowledge Base (mkb.pkl).

Prints, from the fitted artifact (never from prose):
  1. Dataset list (mkb.datasets is a LIST of names — use mkb.get_entry(name),
     NOT dict indexing).
  2. Per-stratum PCA summary via stratifier.stratum_summary() and total_pcs.
  3. Fingerprint structure of one entry: continuous keys
     (<stratum>_PC<nn>_{mean,std,min,max,het}) and the categorical S6 block
     (cat__* flags — never PCA'd).
  4. Performance-record shape (model variants x metrics) for one entry.

Usage (from the toolkit repo root, thesis_final env):
    C:\\Users\\User\\miniconda3\\envs\\thesis_final\\python.exe ^
        .claude\\skills\\artifact-verification-playbook\\scripts\\mkb_summary.py [path\\to\\mkb.pkl]

Expected headline numbers (mkb.pkl as of 2026-07-12):
    17 datasets | 2,726 core features | 327 families upstream | 63 PCs total
    fingerprint = 315 continuous + 17 cat__ = 332 dims
"""
import sys
from collections import Counter
from pathlib import Path

# Make `lid_toolkit` importable when run from the repo root without install.
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))

from lid_toolkit.recommender.mkb_store import MKBStore  # noqa: E402

MKB_PATH = sys.argv[1] if len(sys.argv) > 1 else str(REPO / "mkb.pkl")

mkb = MKBStore.load(MKB_PATH)

# ── 1. Datasets (a LIST of names) ────────────────────────────────────────────
print(f"MKB: {MKB_PATH}")
print(f"Datasets ({len(mkb.datasets)}):")
for name in mkb.datasets:
    entry = mkb.get_entry(name)          # <- correct access pattern
    print(f"  {name:45s} {len(entry.iso_codes):3d} langs  "
          f"{len(entry.performances):3d} model variants")

# ── 2. Stratifier summary ────────────────────────────────────────────────────
strat = mkb.stratifier
print("\nstratifier.stratum_summary():")
print(strat.stratum_summary().to_string())
total_feats = sum(len(f.feature_names) for f in strat._fits.values())
print(f"\ntotal core features: {total_feats}   total_pcs: {strat.total_pcs}")

# ── 3. Fingerprint structure of the first entry ─────────────────────────────
entry = mkb.get_entry(mkb.datasets[0])
fp = entry.fingerprint                   # OrderedDict[str, float]
cont = [k for k in fp if not k.startswith("cat__")]
cat = [k for k in fp if k.startswith("cat__")]
suffixes = Counter(k.rsplit("_", 1)[-1] for k in cont)
print(f"\nFingerprint of '{entry.name}': {len(fp)} dims "
      f"= {len(cont)} continuous + {len(cat)} cat__")
print(f"  continuous key pattern: <stratum>_PC<nn>_<stat>, stats: {dict(suffixes)}")
print(f"  first 3 continuous keys: {cont[:3]}")
print(f"  S6 categorical flags ({len(cat)}):")
for k in cat:
    print(f"    {k} = {fp[k]}")

# ── 4. Performance record shape ──────────────────────────────────────────────
variant, metrics = next(iter(entry.performances.items()))
print(f"\nSample performance record  entry.performances['{variant}']:")
print(f"  metrics: {sorted(metrics.keys())}")
