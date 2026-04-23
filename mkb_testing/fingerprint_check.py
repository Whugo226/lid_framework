import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from lid_toolkit.recommender.mkb_store import MKBStore

# Load the MKB
mkb = MKBStore.load('mkb.pkl')

# Get the fingerprint builder
builder = mkb.builder
stratifier = mkb.stratifier

print(f"Stratifier output dimensions: {sum([15, 14, 15, 3, 7])} PCs")
print(f"Fingerprint builder output: 287 dimensions\n")

# Inspect one fingerprint
entry = mkb.get_entry('europarl')
fp = entry.fingerprint
print(f"Fingerprint for europarl: {len(fp)} dimensions")
print(f"Keys: {list(fp.keys())[:20]}")  # First 20 keys