import pickle
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def show_matrix():
    mkb_path = Path(__file__).parent.parent / "mkb.pkl"
    with open(mkb_path, "rb") as f:
        mkb = pickle.load(f)
    
    # Extract the NumPy matrix, row names (datasets), and column names (features)
    matrix, dataset_names, feature_names = mkb.fingerprints_matrix()
    
    # Wrap it in a Pandas DataFrame for a nice visual table
    df = pd.DataFrame(matrix, index=dataset_names, columns=feature_names)
    
    print("=" * 80)
    print(f"MKB FINGERPRINTS MATRIX")
    print(f"Shape: {df.shape} (Rows = Datasets, Columns = Features)")
    print("=" * 80)
    
    # Pandas display options for better terminal viewing
    pd.set_option('display.max_columns', 8)
    pd.set_option('display.width', 150)
    pd.set_option('display.precision', 4)
    
    print("\n[ Top Left Corner of the Matrix (First 5 datasets, First 6 features) ]")
    print(df.iloc[:5, :6])
    
    print("\n[ Bottom Right Corner (Last 5 datasets, Last 6 features) ]")
    print(df.iloc[-5:, -6:])

if __name__ == "__main__":
    show_matrix()
