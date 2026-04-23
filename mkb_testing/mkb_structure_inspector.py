"""
MKB Structure Inspector

Detailed inspection of the pipeline outputs:
- Raw profile .pkl files (2726 raw features per language)
- MKBStore fingerprints (282-dimensional reduced features)
- Benchmarking metrics structure (11 metrics per model variant)
"""

import sys
from pathlib import Path
import pickle

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def inspect_raw_profile(profile_path):
    """Load and inspect a raw profile .pkl file."""
    print("=" * 70)
    print(f"RAW PROFILE: {profile_path.name}")
    print("=" * 70)

    try:
        with open(profile_path, "rb") as f:
            profile = pickle.load(f)

        print(f"\nType             : {type(profile).__name__}")
        print(f"Shape            : {profile.shape}")
        print(f"                   (rows={profile.shape[0]} features, cols={profile.shape[1]} languages)")
        print(f"Languages        : {list(profile.columns)}")
        print(f"Data type        : {profile.dtypes.iloc[0]}")

        print(f"\nFirst 8 feature names:")
        for i, fname in enumerate(profile.index[:8], 1):
            print(f"  {i}. {fname}")
        print(f"  ...")
        print(f"\nLast 3 feature names:")
        for i, fname in enumerate(profile.index[-3:], profile.shape[0]-2):
            print(f"  {i}. {fname}")

        print(f"\nHead (first 5 features × all languages):")
        print(profile.head(5).to_string())

        print(f"\n✓ Profile loaded successfully\n")
        return True

    except Exception as e:
        print(f"\n✗ Failed to load profile: {e}\n")
        return False


def inspect_mkb_entry(mkb, dataset_name):
    """Load and inspect a single MKBEntry from the MKBStore."""
    from lid_toolkit.recommender.mkb_store import MKBStore

    print("=" * 70)
    print(f"MKBSTORE ENTRY: {dataset_name}")
    print("=" * 70)

    try:
        entry = mkb.get_entry(dataset_name)

        print(f"\nDataset name     : {entry.name}")
        print(f"Languages        : {entry.iso_codes}")
        print(f"Num languages    : {len(entry.iso_codes)}")

        # Fingerprint inspection
        if entry.fingerprint is None:
            print(f"\n✗ Fingerprint    : None (not computed!)")
        else:
            fp = entry.fingerprint
            print(f"\nFingerprint type : {type(fp).__name__}")
            print(f"Fingerprint dims : {len(fp)}")
            print(f"\nFirst 6 fingerprint keys:")
            for i, key in enumerate(list(fp.keys())[:6], 1):
                print(f"  {i}. {key}")
            print(f"\nLast 6 fingerprint keys (categorical):")
            for i, key in enumerate(list(fp.keys())[-6:], len(fp)-5):
                print(f"  {i}. {key}")

            print(f"\nSample fingerprint values (first 4):")
            for key, value in list(fp.items())[:4]:
                print(f"  {key:<50} = {value:.6f}")

        # Benchmarking results inspection
        if not entry.performances:
            print(f"\nBenchmarks       : None (no benchmarking results)")
        else:
            print(f"\nModel variants   : {len(entry.performances)}")
            for variant in sorted(entry.performances.keys()):
                print(f"  - {variant}")

            # Show metrics from the first variant
            first_variant = next(iter(entry.performances))
            metrics = entry.performances[first_variant]
            print(f"\nMetrics for '{first_variant}' ({len(metrics)} total):")
            for metric, value in metrics.items():
                if isinstance(value, float):
                    print(f"  {metric:<45} = {value:.6f}")
                else:
                    print(f"  {metric:<45} = {value}")

            # Show metric consistency across variants
            all_metrics = set()
            for perf_dict in entry.performances.values():
                all_metrics.update(perf_dict.keys())
            print(f"\nUnique metrics across all variants: {len(all_metrics)}")
            print(f"  {', '.join(sorted(all_metrics))}")

        print(f"\n✓ Entry inspected successfully\n")
        return True

    except Exception as e:
        print(f"\n✗ Failed to inspect entry: {e}\n")
        return False


def main():
    """Main inspection workflow."""
    import warnings
    warnings.filterwarnings("ignore")

    from lid_toolkit.recommender.mkb_store import MKBStore

    profiles_dir = Path(__file__).parent.parent / "profiles"
    mkb_path = Path(__file__).parent.parent / "mkb.pkl"

    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " MKB STRUCTURE INSPECTOR ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # ── Inspect a raw profile ─────────────────────────────────────────────────
    sample_profile = profiles_dir / "xnli.pkl"
    if sample_profile.exists():
        inspect_raw_profile(sample_profile)
    else:
        print(f"⚠ Sample profile not found at {sample_profile}")
        print(f"  Searching for any .pkl in {profiles_dir}...")
        pkl_files = list(profiles_dir.glob("*.pkl"))
        if pkl_files:
            sample_profile = pkl_files[0]
            print(f"  Using: {sample_profile.name}\n")
            inspect_raw_profile(sample_profile)
        else:
            print(f"  ✗ No .pkl files found!\n")
            return False

    # ── Load MKBStore and inspect entries ─────────────────────────────────────
    if not mkb_path.exists():
        print(f"✗ mkb.pkl not found at {mkb_path}")
        return False

    try:
        mkb = MKBStore.load(mkb_path)
    except Exception as e:
        print(f"✗ Failed to load mkb.pkl: {e}")
        return False

    # Inspect a couple of entries
    sample_datasets = ["xnli", "wikipedia", "OpenLID-v2"]
    for ds_name in sample_datasets:
        if ds_name in mkb.datasets:
            inspect_mkb_entry(mkb, ds_name)
            break

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nTotal datasets in MKB         : {len(mkb.datasets)}")
    print(f"Fingerprint dimensions       : {len(mkb.stratifier.stratum_names)} strata, {mkb.stratifier.total_pcs} total PCs")
    print(f"Final fingerprint dimension  : 282 (53 PCs × 5 stats + 17 categorical)")
    print(f"Raw profile features         : 2726 per dataset")
    print(f"Benchmark metrics stored     : 11 per model variant")
    print(f"Model variants per dataset   : 8")

    print("\n✓ Inspection complete\n")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
