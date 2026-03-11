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
    
    # path to CSV file: first column holds the text values
    CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'simple_sentences_all_measures.csv')
    RESULT_CSV_PATH = os.path.join(os.path.dirname(__file__), 'profiler_results_wili2018_with_spacy_small_models_all_measures.csv')

    print(f"[{time.strftime('%H:%M:%S')}] Loading data from {CSV_PATH}...")
    
    # read first column, respecting quoted fields (so embedded newlines stay inside a document)
    texts = pd.read_csv(
        CSV_PATH,
        header=None,
        usecols=[0],
        quoting=csv.QUOTE_MINIMAL,
        engine='python'  # python engine handles multiline quoted fields reliably
    )
    texts = texts.iloc[:,0].astype(str)
    # strip whitespace/newlines and drop any empty rows
    texts = texts.str.strip().dropna()
    
    # OPTIMIZATION 2: Memory Deallocation
    # Delete the original dataframe to free up RAM before the heavy NLP processing begins
    # del f
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

    print(f"[{time.strftime('%H:%M:%S')}] Saving report to CSV...")
    report.to_csv(RESULT_CSV_PATH, index=True)
    
    total_time = time.time() - start_time
    print(f"[{time.strftime('%H:%M:%S')}] Done! Total execution time: {total_time:.2f} seconds.")

if __name__ == "__main__":
    main()