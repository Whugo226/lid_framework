#!/usr/bin/env python
"""Quick test script for entropy and Gini features."""

import pandas as pd
import sys
sys.path.insert(0, r'src')

from lid_toolkit.logic.profiler_legacy import DataFrameProfiler

# Create test data with different characteristics
df = pd.DataFrame({
    'text': [
        'Hello world',           # Normal text
        'Testing entropy',       # Normal text
        'ABCDE',                 # Uniform distribution
        'aaaa',                  # Low entropy (repeated chars)
        'The quick brown fox'   # More varied
    ]
})

profiler = DataFrameProfiler(df)
result = profiler.profile(text_column='text')

print('=' * 60)
print('Text Stats (including new entropy and Gini features):')
print('=' * 60)
for key, value in result['text_stats'].items():
    print(f'{key:25s}: {value}')

print('\n' + '=' * 60)
print('New Features:')
print('=' * 60)
print(f"Character Entropy: {result['text_stats']['character_entropy']} bits")
print(f"Gini Coefficient:  {result['text_stats']['gini_coefficient']}")
print('\nEntropy interpretation: Higher = more uniform character distribution')
print('Gini interpretation: Higher = more inequality in character frequencies')
