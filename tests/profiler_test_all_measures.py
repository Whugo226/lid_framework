import pandas as pd
import sys
import os
import time
import csv

# Ensure the src directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from lid_toolkit.logic.profiler_spacy_more_measures import DeepProfiler

def main():
    # 1. Start the benchmarking timer
    start_time = time.time()
    
    CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'simple_all_measures.txt')
    RESULT_EXCEL_PATH = os.path.join(os.path.dirname(__file__), 'profiler_results_wili2018_with_spacy_small_models_all_measures.xlsx')

    print(f"[{time.strftime('%H:%M:%S')}] Loading data from {CSV_PATH}...")
    
    # OPTIMIZATION 1: C-Engine Pandas Read
    # This bypasses native Python loops entirely and uses compiled C code to read the text.
    # It is massively faster and more memory-efficient for 117k+ lines.
    # OPTIMIZATION 1: Direct File-to-Series Loading
    # Bypasses Python 'for' loops and Pandas CSV parsing overhead entirely.
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        # Load directly from the C-level file iterator
        texts = pd.Series(f)
        
    # Strip the trailing newlines (\n) using vectorized string operations
    texts = texts.str.rstrip('\n').dropna()
    
    # OPTIMIZATION 2: Memory Deallocation
    # Delete the original dataframe to free up RAM before the heavy NLP processing begins
    del f
    load_time = time.time() - start_time
    print(f"[{time.strftime('%H:%M:%S')}] Loaded {len(texts)} messages in {load_time:.2f} seconds.")

    print(f"[{time.strftime('%H:%M:%S')}] Initializing DeepProfiler...")
    prof = DeepProfiler()
    
    print(f"[{time.strftime('%H:%M:%S')}] Starting Multilingual Profiling...")
    profile_start = time.time()
    
    # OPTIMIZATION 3: Execution
    report = prof.get_multilingual_profile(texts)
    
    profile_time = time.time() - profile_start
    print(f"[{time.strftime('%H:%M:%S')}] Profiling completed in {profile_time:.2f} seconds.")

    print(f"[{time.strftime('%H:%M:%S')}] Saving report to Excel...")
    report.to_excel(RESULT_EXCEL_PATH, index=True)
    
    total_time = time.time() - start_time
    print(f"[{time.strftime('%H:%M:%S')}] Done! Total execution time: {total_time:.2f} seconds.")

if __name__ == "__main__":
    main()