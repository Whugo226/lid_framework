import sys
import os

# Ensure lid_toolkit is importable
sys.path.append(os.path.abspath('src'))
from lid_toolkit.recommender.mkb_store import MKBStore

def extract_datasets_info():
    mkb = MKBStore.load('mkb.pkl')
    
    print("| Dataset Name | Language Count | Language Codes |")
    print("|---|---|---|")
    
    for dataset_name in sorted(mkb.datasets):
        entry = mkb.get_entry(dataset_name)
        lang_codes = sorted(list(entry.iso_codes))
        count = len(lang_codes)
        codes_str = ", ".join(lang_codes)
        print(f"| {dataset_name} | {count} | {codes_str} |")

extract_datasets_info()