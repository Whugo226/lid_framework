import pickle
import sys
from pathlib import Path
import pandas as pd

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from lid_toolkit.recommender.mkb_store import MKBStore

def inspect():
    base_dir = Path(__file__).parent.parent
    profile_path = base_dir / "profiles" / "xnli.pkl"
    mkb_path = base_dir / "mkb.pkl"

    print("=" * 60)
    print(f"INSPECTING PROFILE: {profile_path.name}")
    print("=" * 60)
    if profile_path.exists():
        with open(profile_path, "rb") as f:
            profile_data = pickle.load(f)
        
        print(f"Type: {type(profile_data)}")
        if isinstance(profile_data, pd.DataFrame):
            print(f"Shape: {profile_data.shape}")
            print(f"Columns (first 10): {profile_data.columns.tolist()[:10]}")
            print(f"Columns (last 10): {profile_data.columns.tolist()[-10:]}")
        elif hasattr(profile_data, "keys"): # if dict-like
            print(f"Keys: {list(profile_data.keys())}")
    else:
        print(f"File not found: {profile_path}")

    print("\n" + "=" * 60)
    print("INSPECTING MKB STORE")
    print("=" * 60)
    if mkb_path.exists():
        with open(mkb_path, "rb") as f:
            mkb = pickle.load(f)
            
        print(f"Loaded MKBStore: {len(mkb.datasets)} datasets")
        
        dataset_name = "xnli"
        if dataset_name in mkb.datasets:
            entry = mkb.get_entry(dataset_name)
            print(f"\nMKBEntry for '{dataset_name}':")
            print(f"Type: {type(entry)}")
            
            # Inspect raw profile if present
            has_raw = getattr(entry, "raw_profile", None) is not None
            print(f"Contains raw_profile: {has_raw}")
            if has_raw:
                print(f"  raw_profile shape: {entry.raw_profile.shape}")
            
            # Inspect fingerprint
            print(f"Contains fingerprint: {getattr(entry, 'fingerprint', None) is not None}")
            if entry.fingerprint is not None:
                print(f"  Type: {type(entry.fingerprint)}")
                print(f"  fingerprint length: {len(entry.fingerprint)}")
                if isinstance(entry.fingerprint, dict):
                    print(f"  sample values (first 5): {list(entry.fingerprint.items())[:5]}")
                else:
                    print(f"  sample values (first 5): {entry.fingerprint[:5]}")
                
            # Inspect benchmarks
            print(f"Contains performances: {bool(getattr(entry, 'performances', dict()))}")
            if entry.performances:
                num_variants = len(entry.performances)
                print(f"  models benchmarked: {num_variants}")
                for model, metrics in entry.performances.items():
                    print(f"  - {model}: {list(metrics.keys())}")
            
    else:
        print(f"File not found: {mkb_path}")

if __name__ == '__main__':
    inspect()
