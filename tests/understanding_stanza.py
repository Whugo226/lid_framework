
import stanza
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import logging
import gc 
import torch
import math
from wordfreq import zipf_frequency
from scipy.stats import entropy, linregress
from tqdm import tqdm
import re
from scipy.spatial.distance import cosine
from scipy.optimize import root_scalar
from scipy.stats import pearsonr



def example():
    # pretend we’ve already run a Stanza pipeline and have a `doc`
    doc = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma')("He was still sleeping deeply when the birds started chirping outside.")
    print(doc.text)
    print('The list of sentences in this document:', doc.sentences)
    print('The total number of tokens in this document:', doc.num_tokens)
    # print('The tokens in this documen are the following:',doc.iter_tokens)
    print('The total number of words in this document:', doc.num_words)
    # print('The words in this document are the following:', doc.iter_words)
    # print('Whole document into a list of dictionaries:', doc.to_dict())

    print("=== TOKENS (Surface Text) ===")
    # Loop through the tokens iterator
    for token in doc.iter_tokens():
        print(token.text)

    print("\n=== WORDS (Syntactic Units) ===")
    # Loop through the words iterator
    for word in doc.iter_words():
        print(word.text)
        print(word.upos)
        print(word.feats)
        print("")

    # start with an empty list …
    lower_non_punct_tokens = []
    lower_non_punct_tags   = []
    
    # … then loop over every word in every sentence,
    # filtering out punctuation/SYM/X and lower‑casing.
    # for sent in doc.sentences:
    #     for word in sent.words:
    #         if word.upos not in ('PUNCT', 'SYM', 'X'):
    #             lower_non_punct_tokens.append(word.text.lower())
    #             lower_non_punct_tags.append(word.upos)
    
    # # Now `lower_non_punct_tokens` is a plain list of strings
    # print(lower_non_punct_tokens)
    # # → ['this', 'is', 'a', 'test', 'can', "'t"]
    
    # you can treat it exactly like any Python list:
    # print("types:", len(set(lower_non_punct_tokens)))
    # print("first token:", lower_non_punct_tokens[0])
    # print("iterate:")
    # for tok in lower_non_punct_tokens:
    #     print("  ", tok)
    
    # # later functions in the class expect the same list,
    # # e.g. passing it to _calc_lexical_diversity():
    # profiler = DeepProfiler()
    # stats = profiler._calc_lexical_diversity(
    #     lower_non_punct_tokens,
    #     pos_map_lower_non_punct={},  # just for illustration
    #     doc_len=len(lower_non_punct_tokens)
    # )
    # print(stats)

example()