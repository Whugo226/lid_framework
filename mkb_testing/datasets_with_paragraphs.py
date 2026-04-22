import pickle
from pathlib import Path

profiles_dir = Path("profiles")

# Check all datasets for paragraph features
for pkl_file in sorted(profiles_dir.glob("*.pkl")):
    with open(pkl_file, "rb") as f:
        df = pickle.load(f)
    
    par_features = [col for col in df.index if "(Par" in col]
    print(f"{pkl_file.stem:50} | Features: {df.shape[0]:4} | Par-level: {len(par_features):3}")
