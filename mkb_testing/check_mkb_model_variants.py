import pickle
import sys
from pathlib import Path

# Provide access to the local src/lid_toolkit module without needing to pip install
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def inspect_model_variants(mkb_path: str | Path):
    """
    Safely load the mkb.pkl file and aggregate all unique model variants
    evaluated across all datasets.
    """
    mkb_path = Path(mkb_path).resolve()
    
    print("=" * 60)
    print("MKB MODEL VARIANT INSPECTION")
    print("=" * 60)
    
    # 1. Check if file exists
    if not mkb_path.exists():
        print(f"[ERROR] File not found at: {mkb_path}")
        sys.exit(1)
        
    print(f"Loading MKBStore from: {mkb_path.name}...")
    
    # 2. Load the pickle file safely
    try:
        with open(mkb_path, "rb") as f:
            mkb = pickle.load(f)
        print("✓ Successfully loaded MKBStore\n")
    except Exception as e:
        print(f"[ERROR] Failed to load the pickle file: {e}")
        sys.exit(1)
        
    unique_variants = set()
    datasets_without_benchmarks = []
    
    # Validate structure
    if not hasattr(mkb, "datasets"):
        print("[ERROR] Loaded object does not have a 'datasets' attribute.")
        sys.exit(1)
        
    if not mkb.datasets:
        print("[WARNING] No datasets found in the MKBStore.")
        sys.exit(0)
        
    # 3. Iterate through datasets and aggregate model variants
    for dataset_name in mkb.datasets:
        try:
            entry = mkb.get_entry(dataset_name)
            
            # Check if performances exist and are not empty
            if not getattr(entry, "performances", None):
                datasets_without_benchmarks.append(dataset_name)
                continue
                
            # Aggregate keys (model variant names) from the performances dict
            unique_variants.update(entry.performances.keys())
            
        except Exception as e:
            print(f"[WARNING] Error reading data for dataset '{dataset_name}': {e}")
            
    # 4. Print results clearly
    print("--- Results ---")
    if unique_variants:
        print(f"Found {len(unique_variants)} unique model variant(s):")
        for variant in sorted(unique_variants):
            print(f"  - {variant}")
    else:
        print("No model variants found in any of the datasets.")
        
    # Standard Error / Warning Handling for missing benchmarks
    if datasets_without_benchmarks:
        print(f"\n[INFO] Note: {len(datasets_without_benchmarks)} dataset(s) lacked benchmarking results.")
        # Uncomment the line below if you want to see exactly which datasets are missing benchmarks
        # print(f"       ({', '.join(datasets_without_benchmarks)})")
        
    print("=" * 60)

if __name__ == "__main__":
    # Point to the mkb.pkl file in the parent directory by default
    default_path = Path(__file__).parent.parent / "mkb.pkl"
    
    # Allow overriding the path via command line argument
    target_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    inspect_model_variants(target_path)
