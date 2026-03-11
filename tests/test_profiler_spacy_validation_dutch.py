import sys
import csv
import os
import math
import numpy as np
import sklearn
import pytest
import spacy
import threading
from collections import defaultdict
from scipy.stats import pearsonr, spearmanr
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from lid_toolkit.logic.profiler_spacy import DeepProfiler



CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lingualyzer_ground_truth_dutch.csv')
RESULT_CSV_PATH = os.path.join(os.path.dirname(__file__), 'profiler_spacy_test_results_dutch.csv')
CORRELATION_SUMMARY_CSV_PATH = os.path.join(os.path.dirname(__file__), 'profiler_spacy_correlation_dutch_summary.csv')
TOLERANCE = 1e-2

profiler = DeepProfiler()
# Initialize spaCy pipeline once for all tests using the profiler's own method
nlp = profiler._make_pipeline('nl')

# Thread-safe list for results
test_results = []
results_lock = threading.Lock()

def get_profiler_stats(sentence):
    doc = nlp(sentence)
    return profiler._extract_measures(doc, 'en', sentence)

def load_ground_truth():
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            measure = row['Measure'].strip()
            sentence = row['Sentence'].strip()
            value = row['Value'].strip()
            if not measure or not sentence or not value:
                continue
            yield measure, sentence, value


@pytest.mark.parametrize('measure,sentence,value', list(load_ground_truth()))
def test_profiler_measures_explicit(measure, sentence, value):
    status = "PASS"
    actual = None
    diff = None
    stats = get_profiler_stats(sentence)
    if measure not in stats:
        pytest.skip(f"Profiler output does not contain key '{measure}' for measure '{measure}'")
    result = stats[measure]
    try:
        expected = float(value)
        actual = float(result)
        diff = abs(actual - expected)
        # Integer count measures: require exact match
        if measure.lower().endswith("count (doc)") or measure.lower().endswith("count"):
            if int(expected) != int(actual):
                status = "FAIL"
            assert int(expected) == int(actual), f"Mismatch for {measure} on '{sentence}': got {actual}, expected {expected}"
        else:
            if diff >= TOLERANCE:
                status = "FAIL"
            assert diff < TOLERANCE, f"Mismatch for {measure} on '{sentence}': got {actual}, expected {expected}"
    except ValueError:
        expected = str(value)
        actual = str(result)
        diff = "N/A"
        if actual != expected:
            status = "FAIL"
        assert actual == expected, f"Mismatch for {measure} on '{sentence}': got {actual}, expected {expected}"
    finally:
        with results_lock:
            test_results.append({
                "Measure": measure,
                "Sentence": sentence,
                "Status": status,
                "Expected": expected,
                "Actual": actual,
                "Difference": diff
            })




# Manual function to write correlation summary to CSV
def write_correlation_summary():
    if not test_results:
        return

    # Group numeric expected/actual pairs by measure
    measure_data = defaultdict(lambda: {'expected': [], 'actual': []})
    for row in test_results:
        expected = row['Expected']
        actual = row['Actual']
        # Skip rows with string or N/A values
        if expected == 'N/A' or actual == 'N/A':
            continue
        try:
            e = float(expected)
            a = float(actual)
        except (TypeError, ValueError):
            continue
        measure_data[row['Measure']]['expected'].append(e)
        measure_data[row['Measure']]['actual'].append(a)

    with open(CORRELATION_SUMMARY_CSV_PATH, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Measure', 'MAE', 'Pearson', 'Spearman'])
        writer.writeheader()
        for measure, vals in sorted(measure_data.items()):
            expected_arr = np.array(vals['expected'])
            actual_arr = np.array(vals['actual'])
            mae = float(np.mean(np.abs(actual_arr - expected_arr)))
            # Pearson: requires variance in both arrays
            if len(expected_arr) >= 2 and np.std(expected_arr) > 0 and np.std(actual_arr) > 0:
                pearson, _ = pearsonr(expected_arr, actual_arr)
            else:
                pearson = float('nan')
            # Spearman: requires at least 2 data points
            if len(expected_arr) >= 2:
                spearman, _ = spearmanr(expected_arr, actual_arr)
            else:
                spearman = float('nan')
            writer.writerow({
                'Measure': measure,
                'MAE': mae,
                'Pearson': pearson,
                'Spearman': spearman,
            })
    print(f"Wrote correlation summary to {CORRELATION_SUMMARY_CSV_PATH}")


# Manual function to write results to CSV
def write_results_to_csv():
    if not test_results:
        print("No test results to write.")
        return
    with open(RESULT_CSV_PATH, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Measure", "Sentence", "Status", "Expected", "Actual", "Difference"])
        writer.writeheader()
        for row in test_results:
            writer.writerow(row)
    print(f"Wrote test results to {RESULT_CSV_PATH}")


# Session-scoped fixture to write results after all tests
@pytest.fixture(scope="session", autouse=True)
def write_results_fixture(request):
    yield
    write_results_to_csv()
    write_correlation_summary()




