import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# 3. Load and inspect the MKB:

from lid_toolkit.recommender.mkb_store import MKBStore

mkb = MKBStore.load('mkb.pkl')
print(f"Datasets in MKB: {len(mkb.datasets)}")
print(f"Dataset names: {mkb.datasets}")

# Summary statistics
summary = mkb.summary()
print(summary)
# 4. Check which metrics were stored:

# Get an entry to see available metrics
entry = mkb.get_entry(mkb.datasets[0])
print(f"First dataset: {entry.name}")
print(f"Languages: {entry.iso_codes}")
print(f"Available model variants & metrics:")
for model, metrics in entry.performances.items():
    print(f"  {model}: {list(metrics.keys())}")