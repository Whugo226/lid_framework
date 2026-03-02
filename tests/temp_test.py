import stanza
import sys
import csv
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from lid_toolkit.logic.profiler import DeepProfiler


prof=DeepProfiler()
nlp=stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma', verbose=False, use_gpu=prof.use_gpu)

text='He was still sleeping deeply the birds started chirping outside.'
doc=nlp(text)
stats=prof._extract_measures(doc,'en')
print('noun',stats.get('NOUN count'))
print('lex',stats.get('Lexical item count'))
print('ratio',stats.get('Noun-lexical item ratio'))
# print(stats)
