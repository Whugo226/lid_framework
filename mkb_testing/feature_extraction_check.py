import pickle
from pathlib import Path

profiles_dir = Path("profiles")

# Load one profile
with open(profiles_dir / "xnli.pkl", "rb") as f:
    df = pickle.load(f)

print(f"xnli profile: {df.shape[0]} features, {df.shape[1]} languages\n")
print("Feature names (first 30):")
for i, feat in enumerate(df.index[:30], 1):
    print(f"  {i:3}. {feat}")

print(f"\n... and {df.shape[0] - 30} more features\n")

# Show all features
print("All features:")
for i, feat in enumerate(df.index, 1):
    print(f"{i:4}. {feat}")