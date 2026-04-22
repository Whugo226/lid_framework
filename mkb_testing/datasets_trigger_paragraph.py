# Example: inspect xnli to see why it has no paragraph features
from anyio import Path
import pandas as pd

# Load one xnli parquet file to inspect
xnli_parquet = Path("~/LID_Experiments/datasets/01b_knowledge_benchmark_20_cleaned/xnli").expanduser()
df = pd.read_parquet(list(xnli_parquet.glob("*.parquet"))[0])
print(df.head())
print(f"\nSample text:\n{df['text'].iloc[0][:500]}")