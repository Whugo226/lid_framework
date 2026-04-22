import pickle
from pathlib import Path

profiles_dir = Path("profiles")

# Load one normal (2726) and one large (2926) profile
with open(profiles_dir / "xnli.pkl", "rb") as f:
    normal = pickle.load(f)

with open(profiles_dir / "wikipedia.pkl", "rb") as f:
    large = pickle.load(f)

print(f"Normal profile shape: {normal.shape}")
print(f"Large profile shape: {large.shape}")
print(f"\nFeature difference: {large.shape[0] - normal.shape[0]}")

# Find features unique to large profile
normal_features = set(normal.index)
large_features = set(large.index)

unique_to_large = large_features - normal_features
print(f"\nUnique features in wikipedia ({len(unique_to_large)}):")
for feat in sorted(unique_to_large)[:20]:  # First 20
    print(f"  {feat}")
if len(unique_to_large) > 20:
    print(f"  ... and {len(unique_to_large) - 20} more")

# Check if they're language-related
ja_feats = [f for f in unique_to_large if "ja" in f.lower()]
print(f"\nJapanese-related features: {len(ja_feats)}")
if ja_feats:
    for feat in ja_feats[:10]:
        print(f"  {feat}")

# Shared features (should be 2726)
shared = normal_features & large_features
print(f"\nShared features: {len(shared)}")