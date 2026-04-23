
"""
MKB Quality Assurance Inspection Script

Validates the integrity, structure, and completeness of mkb.pkl
"""

import pickle
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add src/ to path so lid_toolkit is importable without pip install
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def inspect_mkb(mkb_path):
    """Load and inspect the MKBStore."""
    mkb_path = Path(mkb_path).resolve()

    print("=" * 70)
    print("MKB QUALITY ASSURANCE INSPECTION")
    print("=" * 70)
    print(f"\nMKB Path: {mkb_path}")
    print(f"File exists: {mkb_path.exists()}")

    if not mkb_path.exists():
        print(f"ERROR: File not found at {mkb_path}")
        return False

    # Load the MKB
    print("\n[1] Loading MKBStore...")
    try:
        with open(mkb_path, "rb") as fh:
            mkb = pickle.load(fh)
        print("    ✓ Successfully loaded mkb.pkl")
    except Exception as e:
        print(f"    ✗ Failed to load: {e}")
        return False

    # Verify type
    print("\n[2] Verifying MKBStore type...")
    try:
        from lid_toolkit.recommender.mkb_store import MKBStore
        if isinstance(mkb, MKBStore):
            print("    ✓ Type is MKBStore (correct)")
        else:
            print(f"    ✗ Type mismatch: expected MKBStore, got {type(mkb)}")
            return False
    except ImportError:
        print("    ⚠ Could not import MKBStore for type check (continuing anyway)")

    # Count datasets
    print("\n[3] Dataset Count...")
    datasets = mkb.datasets
    print(f"    Total datasets: {len(datasets)}")
    print(f"    Dataset names: {sorted(datasets)}")

    if len(datasets) == 0:
        print("    ✗ ERROR: No datasets found in MKB!")
        return False
    else:
        print(f"    ✓ Found {len(datasets)} datasets")

    # Verify fingerprints exist and check dimensions
    # Target is derived from the first valid fingerprint (all must be consistent)
    fingerprint_dims = {}
    for dataset_name in sorted(datasets):
        entry = mkb.get_entry(dataset_name)
        if entry.fingerprint is not None:
            fingerprint_dims[dataset_name] = len(entry.fingerprint)

    target_dim = next(iter(fingerprint_dims.values())) if fingerprint_dims else None
    print(f"\n[4] Fingerprint Dimensions (actual target: {target_dim})...")
    dim_mismatch = []

    for dataset_name in sorted(datasets):
        entry = mkb.get_entry(dataset_name)
        if entry.fingerprint is None:
            print(f"    ✗ {dataset_name}: No fingerprint computed!")
            dim_mismatch.append(dataset_name)
        else:
            dim = len(entry.fingerprint)
            status = "✓" if dim == target_dim else "✗"
            print(f"    {status} {dataset_name}: {dim} dimensions")
            if dim != target_dim:
                dim_mismatch.append(dataset_name)

    if dim_mismatch:
        print(f"\n    ⚠ {len(dim_mismatch)} dataset(s) with inconsistent fingerprint dimensions:")
        for ds in dim_mismatch:
            print(f"      - {ds}: {fingerprint_dims.get(ds, 'None')} (expected {target_dim})")
    else:
        print(f"    ✓ All {len(fingerprint_dims)} datasets have consistent fingerprint dimensions ({target_dim})")

    # Check language coverage
    print("\n[5] Language Coverage per Dataset...")
    lang_stats = {}
    for dataset_name in sorted(datasets):
        entry = mkb.get_entry(dataset_name)
        n_langs = len(entry.iso_codes)
        lang_stats[dataset_name] = (n_langs, entry.iso_codes)
        print(f"    {dataset_name}: {n_langs} languages → {', '.join(sorted(entry.iso_codes)[:5])}" +
              ("..." if n_langs > 5 else ""))

    # Check benchmarking results
    print("\n[6] Benchmarking Results Integration...")
    has_benchmarks = []
    no_benchmarks = []

    for dataset_name in sorted(datasets):
        entry = mkb.get_entry(dataset_name)
        if entry.performances:
            n_variants = len(entry.performances)
            # Count total metrics stored
            all_metrics = set()
            for perf_dict in entry.performances.values():
                all_metrics.update(perf_dict.keys())
            has_benchmarks.append((dataset_name, n_variants, sorted(all_metrics)))
            print(f"    ✓ {dataset_name}: {n_variants} model variants, {len(all_metrics)} metrics")
            print(f"      Metrics: {', '.join(sorted(all_metrics)[:4])}" +
                  ("..." if len(all_metrics) > 4 else ""))
        else:
            no_benchmarks.append(dataset_name)
            print(f"    ⚠ {dataset_name}: No benchmarking results")

    if no_benchmarks:
        print(f"\n    Note: {len(no_benchmarks)} dataset(s) without benchmarks: {no_benchmarks}")

    if has_benchmarks:
        print(f"\n    ✓ {len(has_benchmarks)} dataset(s) have benchmarking results")

    # Summary statistics
    print("\n[7] Summary Statistics...")
    print(f"    ├─ Datasets profiled: {len(datasets)}")
    print(f"    ├─ Fingerprint dimensions: {len(set(fingerprint_dims.values()))} unique value(s)")
    print(f"    ├─ Datasets with benchmarks: {len(has_benchmarks)}")
    print(f"    ├─ Total languages covered: {len(set().union(*[set(langs) for _, langs in lang_stats.values()]))}")

    if has_benchmarks:
        all_model_variants = set()
        all_benchmark_metrics = set()
        for _, variants, metrics in has_benchmarks:
            all_model_variants.add(variants)
            all_benchmark_metrics.update(metrics)
        print(f"    ├─ Model variants per dataset: {min([v for _, v, _ in has_benchmarks])} - {max([v for _, v, _ in has_benchmarks])}")
        print(f"    └─ Unique benchmark metrics: {len(all_benchmark_metrics)}")
        print(f"       Metrics: {', '.join(sorted(all_benchmark_metrics))}")

    # Test querying capability
    print("\n[8] Testing Query Capability...")
    try:
        # Try to get the stratifier
        stratifier = mkb.stratifier
        print(f"    ✓ Stratifier accessible ({len(stratifier.stratum_names)} strata, {stratifier.total_pcs} total PCs)")

        # Try to get fingerprints matrix
        matrix, names, keys = mkb.fingerprints_matrix()
        print(f"    ✓ Fingerprints matrix: shape {matrix.shape} ({len(names)} datasets, {len(keys)} features)")

        # Try best_model_per_dataset
        best_models = mkb.best_model_per_dataset()
        print(f"    ✓ best_model_per_dataset() callable: {len(best_models)} datasets with benchmarks")

        # Try summary
        summary_df = mkb.summary()
        print(f"    ✓ summary() callable: {len(summary_df)} rows, {len(summary_df.columns)} columns")
        print(f"      Columns: {', '.join(summary_df.columns[:5].tolist())}...")

    except Exception as e:
        print(f"    ✗ Query test failed: {e}")
        return False

    # Final verdict
    print("\n" + "=" * 70)
    success = (len(datasets) > 0 and
               len(dim_mismatch) == 0 and
               len(has_benchmarks) > 0)

    if success:
        print("VERDICT: ✓ MKB PASSED QA INSPECTION")
    else:
        print("VERDICT: ✗ MKB FAILED QA INSPECTION")
        if len(datasets) == 0:
            print("  - No datasets found")
        if dim_mismatch:
            print(f"  - Fingerprint dimension mismatches: {dim_mismatch}")
        if len(has_benchmarks) == 0:
            print("  - No benchmarking results integrated")
    print("=" * 70)

    return success

if __name__ == "__main__":
    mkb_path = Path(__file__).parent.parent / "mkb.pkl"
    if len(sys.argv) > 1:
        mkb_path = sys.argv[1]

    success = inspect_mkb(mkb_path)
    sys.exit(0 if success else 1)
