import pandas as pd
import sys
import csv
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from lid_toolkit.logic.profiler import DeepProfiler

CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'x_test.txt')
RESULT_CSV_PATH = os.path.join(os.path.dirname(__file__), 'profiler_results_wili2018.csv')

# read a file where each line is a message
# the `sep='\n'` trick keeps line breaks from being treated as delimiters
with open(CSV_PATH, encoding="utf-8") as f:
    lines = [line.rstrip("\n") for line in f]
texts = pd.Series(lines, name="text")            # each row/line becomes one element

# quick sanity check
bad = [t for t in texts if not isinstance(t, str)]
if bad:
    print("non-string entries found:", bad[:10])
    # you can even drop or convert them here:
    texts = texts[texts.map(lambda x: isinstance(x, str))]
    # or texts = texts.astype(str)

prof = DeepProfiler()
report = prof.get_multilingual_profile(texts)

# write results to an Excel workbook instead of CSV
excel_path = os.path.splitext(RESULT_CSV_PATH)[0] + '.xlsx'
report.to_excel(excel_path, index=True)
print(f"saved report to {excel_path}")