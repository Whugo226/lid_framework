import sys
from pathlib import Path
import pickle
import pandas as pd

# Add src to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from lid_toolkit.recommender.mkb_store import MKBStore

def verify_language_coverage():
    # Paths
    eval_profiles_dir = Path(__file__).parent.parent / 'eval_profiles'
    mkb_path = Path(__file__).parent.parent / 'mkb.pkl'
    report_path = Path(__file__).parent.parent / 'language_coverage_mismatch_report.md'
    
    # Load MKB
    print(f"Loading MKB from {mkb_path}...")
    mkb = MKBStore.load(str(mkb_path))
    mkb_datasets = set(mkb.datasets)
    
    # Track results
    perfect_matches = []
    missing_in_mkb = {}
    missing_in_eval = {}
    datasets_not_in_mkb = []
    
    # Iterate through eval profiles
    print(f"Iterating through eval profiles in {eval_profiles_dir}...")
    for pkl_file in eval_profiles_dir.glob('*.pkl'):
        dataset_name = pkl_file.stem
        
        # Load eval profile dataframe
        try:
            with open(pkl_file, 'rb') as f:
                df = pickle.load(f)
            eval_languages = set(df.columns)
        except Exception as e:
            print(f"Error loading {pkl_file}: {e}")
            continue
            
        # Check against MKB
        if dataset_name not in mkb_datasets:
            datasets_not_in_mkb.append(dataset_name)
            continue
            
        mkb_entry = mkb.get_entry(dataset_name)
        mkb_languages = set(mkb_entry.iso_codes)
        
        # Compare
        if eval_languages == mkb_languages:
            perfect_matches.append(dataset_name)
        else:
            in_eval_not_mkb = eval_languages - mkb_languages
            in_mkb_not_eval = mkb_languages - eval_languages
            
            if in_eval_not_mkb:
                missing_in_mkb[dataset_name] = sorted(list(in_eval_not_mkb))
            if in_mkb_not_eval:
                missing_in_eval[dataset_name] = sorted(list(in_mkb_not_eval))
                
    # Generate Markdown Report
    print(f"Generating report at {report_path}...")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Language Coverage Consistency Report\n\n")
        
        f.write("## Perfect Matches\n")
        f.write("Datasets where evaluation profiles and MKB have exactly the same languages:\n")
        f.write(" ".join(perfect_matches) + "\n\n")
        
        f.write("## Languages in Eval Profile but Missing from MKB\n")
        if missing_in_mkb:
            for ds, langs in missing_in_mkb.items():
                f.write(f"- **{ds}**: {', '.join(langs)}\n")
        else:
            f.write("None\n")
        f.write("\n")
        
        f.write("## Languages in MKB but Missing from Eval Profile\n")
        if missing_in_eval:
            for ds, langs in missing_in_eval.items():
                f.write(f"- **{ds}**: {', '.join(langs)}\n")
        else:
            f.write("None\n")
        f.write("\n")
        
        if datasets_not_in_mkb:
            f.write("## Datasets in Eval Profiles but Not in MKB\n")
            for ds in datasets_not_in_mkb:
                f.write(f"- {ds}\n")
    print("Done!")

if __name__ == "__main__":
    verify_language_coverage()
