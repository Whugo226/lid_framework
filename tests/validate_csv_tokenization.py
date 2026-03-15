#!/usr/bin/env python3
"""
CSV Tokenization Validation Script

Investigates if CSV quote-escaping is corrupting linguistic counts by comparing
raw CSV text vs. cleaned text through the spaCy pipeline.

Author: Generated script for LID Toolkit validation
"""

import csv
import sys
import os
import re
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from lid_toolkit.logic.profiler_spacy_bttm_up_approach import DeepProfiler


def clean_text(text: str) -> str:
    """
    Sanitization function that removes CSV formatting artifacts.
    
    Args:
        text: Raw text from CSV
        
    Returns:
        Cleaned text with CSV artifacts removed
    """
    # Strip leading/trailing whitespace
    cleaned = text.strip()
    
    # Remove CSV-wrapped double quotes (e.g., "Text" becomes Text)
    # Handle standard CSV quoting: if text starts and ends with quotes, remove them
    if cleaned.startswith('"') and cleaned.endswith('"') and len(cleaned) >= 2:
        cleaned = cleaned[1:-1]
    
    # Handle triple quotes (""") often found in multi-line paragraph fields
    # Replace triple quotes with single quotes or remove them entirely
    cleaned = cleaned.replace('"""', '')
    
    # Handle escaped quotes within CSV (double quotes become single quotes)
    cleaned = cleaned.replace('""', '"')
    
    return cleaned


def count_punctuation(doc):
    """Count total punctuation tokens in a spaCy doc."""
    return sum(1 for token in doc if token.is_punct)


def analyze_tokenization_differences(csv_path: str):
    """
    Main analysis function that compares raw vs cleaned text processing.
    
    Args:
        csv_path: Path to the CSV file to analyze
    """
    print("🔍 Starting CSV Tokenization Validation")
    print(f"📁 Loading data from: {csv_path}")
    
    # Initialize the profiler with the exact same pipeline as main toolkit
    profiler = DeepProfiler()
    nlp = profiler._make_pipeline('en')
    
    differences_found = []
    total_rows = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as file:  # Handle BOM
            reader = csv.DictReader(file)
            
            for row in reader:
                total_rows += 1
                
                # Check if required keys exist (handle potential BOM issues)
                measure_key = 'Measure'
                sentence_key = 'Sentence' 
                value_key = 'Value'
                
                # Find actual keys in case of encoding issues
                actual_keys = list(row.keys())
                if measure_key not in row:
                    # Look for BOM-prefixed version
                    bom_measure = next((k for k in actual_keys if k.endswith('Measure')), None)
                    if bom_measure:
                        measure_key = bom_measure
                
                if measure_key not in row or sentence_key not in row or value_key not in row:
                    continue  # Skip malformed rows silently
                    
                measure_name = row[measure_key]
                raw_sentence = row[sentence_key]
                expected_value = row[value_key]
                
                # Clean the text
                cleaned_sentence = clean_text(raw_sentence)
                
                # Process both versions through spaCy
                raw_doc = nlp(raw_sentence)
                cleaned_doc = nlp(cleaned_sentence)
                
                # Compare key metrics
                raw_len = len(raw_doc)
                cleaned_len = len(cleaned_doc)
                
                raw_first_token = raw_doc[0].text if raw_len > 0 else ""
                cleaned_first_token = cleaned_doc[0].text if cleaned_len > 0 else ""
                
                raw_first_pos = raw_doc[0].pos_ if raw_len > 0 else ""
                cleaned_first_pos = cleaned_doc[0].pos_ if cleaned_len > 0 else ""
                
                raw_punct_count = count_punctuation(raw_doc)
                cleaned_punct_count = count_punctuation(cleaned_doc)
                
                # Check for sentence start corruption
                corruption_flag = False
                if raw_len > 0 and not raw_doc[0].is_sent_start:
                    corruption_flag = True
                
                # Check if there are any differences
                has_differences = (
                    raw_len != cleaned_len or
                    raw_first_token != cleaned_first_token or
                    raw_first_pos != cleaned_first_pos or
                    raw_punct_count != cleaned_punct_count or
                    corruption_flag
                )
                
                if has_differences:
                    differences_found.append({
                        'measure': measure_name,
                        'expected_value': expected_value,
                        'raw_sentence': raw_sentence,
                        'cleaned_sentence': cleaned_sentence,
                        'raw_len': raw_len,
                        'cleaned_len': cleaned_len,
                        'raw_first_token': raw_first_token,
                        'cleaned_first_token': cleaned_first_token,
                        'raw_first_pos': raw_first_pos,
                        'cleaned_first_pos': cleaned_first_pos,
                        'raw_punct_count': raw_punct_count,
                        'cleaned_punct_count': cleaned_punct_count,
                        'corruption_flag': corruption_flag,
                        'raw_tokens': [token.text for token in raw_doc],
                        'cleaned_tokens': [token.text for token in cleaned_doc]
                    })
    
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        import traceback
        traceback.print_exc()
        return
    print(f"\n📊 Analysis Results:")
    print(f"   Total measures analyzed: {total_rows}")
    print(f"   Measures with differences: {len(differences_found)}")
    
    if differences_found:
        print(f"\n🚨 DETAILED CORRUPTION REPORT:")
        print("=" * 80)
        
        for i, diff in enumerate(differences_found, 1):
            print(f"\n{i}. Measure: {diff['measure']}")
            print(f"   Expected Value: {diff['expected_value']}")
            print(f"   Raw Sentence: {repr(diff['raw_sentence'])}")
            print(f"   Cleaned Sentence: {repr(diff['cleaned_sentence'])}")
            
            print(f"\n   📈 Token Count Comparison:")
            print(f"      Raw: {diff['raw_len']} tokens")
            print(f"      Cleaned: {diff['cleaned_len']} tokens")
            
            print(f"\n   🎯 First Token Comparison:")
            print(f"      Raw: '{diff['raw_first_token']}' (POS: {diff['raw_first_pos']})")
            print(f"      Cleaned: '{diff['cleaned_first_token']}' (POS: {diff['cleaned_first_pos']})")
            
            print(f"\n   📝 Punctuation Count:")
            print(f"      Raw: {diff['raw_punct_count']}")
            print(f"      Cleaned: {diff['cleaned_punct_count']}")
            
            if diff['corruption_flag']:
                print(f"\n   🔴 CORRUPTION FLAG: First word not marked as sentence start!")
            
            print(f"\n   🧩 Raw Tokens: {diff['raw_tokens']}")
            print(f"   ✨ Cleaned Tokens: {diff['cleaned_tokens']}")
            print("   " + "-" * 76)
        
        print(f"\n🎯 SUMMARY: Found {len(differences_found)} measures potentially affected by CSV formatting artifacts")
        
        # Create a summary list of affected measures
        affected_measures = [diff['measure'] for diff in differences_found]
        print(f"\n📋 AFFECTED MEASURES LIST:")
        for measure in affected_measures:
            print(f"   • {measure}")
            
    else:
        print(f"\n✅ No tokenization differences found between raw and cleaned text!")
        print("   CSV formatting does not appear to be corrupting linguistic analysis.")


def main():
    """Main execution function."""
    csv_path = Path(__file__).parent / "tests" / "data" / "lingualyzer_ground_truth_english.csv"
    
    if not csv_path.exists():
        print(f"❌ Error: CSV file not found at {csv_path}")
        print("   Please check the file path and try again.")
        sys.exit(1)
    
    try:
        analyze_tokenization_differences(str(csv_path))
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)
    
    print(f"\n🏁 Analysis complete!")


if __name__ == "__main__":
    main()