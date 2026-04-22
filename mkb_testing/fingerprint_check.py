from src.lid_toolkit.recommender.mkb_store import MKBStore

# Load the MKB
mkb = MKBStore.load('mkb.pkl')

# Get the fingerprint builder
builder = mkb.builder
stratifier = mkb.stratifier

print(f"Stratifier output dimensions: {sum([15, 14, 15, 3, 7])} PCs")
print(f"Fingerprint builder output: 287 dimensions\n")

# Inspect one fingerprint
entry = mkb.get_entry('xnli')
fp = entry.fingerprint
print(f"Fingerprint for xnli: {len(fp)} dimensions")
print(f"Keys: {list(fp.keys())[:20]}")  # First 20 keys