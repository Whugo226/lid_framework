import pandas as pd
import sys
import os
import time
import csv

# Ensure the src directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from lid_toolkit.logic.profiler_spacy_bttm_up_approach import DeepProfiler

def main():
    # 1. Start the benchmarking timer
    start_time = time.time()
    
    # for XLSX input we treat the first column as the text series
    XLSX_PATH = os.path.join(os.path.dirname(__file__), 'data', 'simple_sentences_all_measures.xlsx')
    RESULT_EXCEL_PATH = os.path.join(os.path.dirname(__file__), 'profiler_results_simple_sentence_all_measures.xlsx')

    print(f"[{time.strftime('%H:%M:%S')}] Loading data from {XLSX_PATH}...")
    
    # read the first column of the workbook (no header) into a Series
    # pandas returns a DataFrame so we select the 0th column afterwards
    texts = pd.read_excel(XLSX_PATH, header=None, usecols=[0], engine='openpyxl')
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

    print(f"[{time.strftime('%H:%M:%S')}] Saving report to Excel...")
    report.to_excel(RESULT_EXCEL_PATH, index=True)
    
    total_time = time.time() - start_time
    print(f"[{time.strftime('%H:%M:%S')}] Done! Total execution time: {total_time:.2f} seconds.")

if __name__ == "__main__":
    main()