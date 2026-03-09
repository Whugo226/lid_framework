import pandas as pd
import os
from scipy.stats import pearsonr, spearmanr
from sklearn.discriminant_analysis import StandardScaler

# 1. Setup Path
base_dir = os.path.dirname(__file__)
CSV_PATH = os.path.join(base_dir, 'data', 'lingualyzer_human_comparison.csv')

# def calculate_global_alignment(path):
#     print(f"Loading comparison data from: {path}")
    
#     try:
#         # Load the CSV
#         df = pd.read_csv(path, encoding='utf-8-sig')
        
#         # 2. Convert values to numeric, forcing errors to NaN so we can drop them
#         # This cleans strings like 'ERR' or 'N/A' automatically
#         df['Human value'] = pd.to_numeric(df['Human value'], errors='coerce')
#         df['Lingualyzer_value'] = pd.to_numeric(df['Lingualyzer_value'], errors='coerce')
        
#         # 3. Drop rows where either value is missing
#         clean_df = df.dropna(subset=['Human value', 'Lingualyzer_value'])
        
#         h_vals = clean_df['Human value'].values
#         l_vals = clean_df['Lingualyzer_value'].values
        
#         n_points = len(h_vals)
        
#         if n_points < 2:
#             print("Error: Not enough numeric data points to calculate correlation.")
#             return

#         # 4. Compute Statistics
#         pearson_r, _ = pearsonr(h_vals, l_vals)
#         spearman_rho, _ = spearmanr(h_vals, l_vals)
#         mae = (abs(h_vals - l_vals)).mean()

#         # 5. Output to Console
#         print("\n" + "="*45)
#         print("📊 GLOBAL LINGUISTIC ALIGNMENT SUMMARY")
#         print("="*45)
#         print(f"Total Data Points (n):  {n_points}")
#         print(f"Mean Absolute Error:    {mae:.4f}")
#         print("-" * 45)
#         print(f"Pearson Correlation (r): {pearson_r:.4f}")
#         print(f"Spearman Rank (rho):     {spearman_rho:.4f}")
#         print("="*45)
        
#         if pearson_r > 0.95:
#             print("✅ Interpretation: Excellent system-wide alignment.")
#         elif pearson_r > 0.80:
#             print("⚠️ Interpretation: Strong alignment with some local variances.")
#         else:
#             print("❌ Interpretation: Low alignment; check for tagging discrepancies.")

#     except Exception as e:
#         print(f"An error occurred: {e}")

# if __name__ == "__main__":
#     calculate_global_alignment(CSV_PATH)


def calculate_normalized_alignment(path):
    df = pd.read_csv(path, encoding='utf-8-sig')
    
    # Clean data
    df['Human value'] = pd.to_numeric(df['Human value'], errors='coerce')
    df['Lingualyzer_value'] = pd.to_numeric(df['Lingualyzer_value'], errors='coerce')
    clean_df = df.dropna(subset=['Human value', 'Lingualyzer_value'])

    # --- NORMALIZATION STEP ---
    # We reshape and scale both columns so they are on a 0-centered scale
    scaler = StandardScaler()
    h_norm = scaler.fit_transform(clean_df[['Human value']])
    l_norm = scaler.fit_transform(clean_df[['Lingualyzer_value']])

    # Calculate Pearson on the normalized data
    r_norm, _ = pearsonr(h_norm.flatten(), l_norm.flatten())
    r_raw, _ = pearsonr(clean_df['Human value'], clean_df['Lingualyzer_value'])

    # Calculate Spearman rank order correlation (non-parametric)
    r_spearman_raw, _ = spearmanr(clean_df['Human value'], clean_df['Lingualyzer_value'])
    r_spearman_norm, _ = spearmanr(h_norm.flatten(), l_norm.flatten())

    # Output results
    print(f"Raw Global Pearson Correlation:        r = {r_raw:.4f}")
    print(f"Normalized Global Pearson Correlation: r = {r_norm:.4f}")
    print(f"Raw Spearman Rank Correlation:          rho = {r_spearman_raw:.4f}")
    print(f"Normalized Spearman Rank Correlation:   rho = {r_spearman_norm:.4f}")
    
    # return dictionary of metrics in case callers want them
    return {
        'pearson_raw': r_raw,
        'pearson_norm': r_norm,
        'spearman_raw': r_spearman_raw,
        'spearman_norm': r_spearman_norm,
    }

if __name__ == "__main__":
    calculate_normalized_alignment(CSV_PATH)