import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import logging
import math
from wordfreq import zipf_frequency
from scipy.stats import entropy, linregress
from tqdm import tqdm
import re
import random
from scipy.spatial.distance import cosine
from scipy.optimize import root_scalar
from scipy.stats import pearsonr
from huggingface_hub import hf_hub_download
import compress_fasttext
from pathlib import Path
import functools
import editdistance
import fasttext
from pathlib import Path
import spacy 



class DeepProfiler:
    # Human-readable labels for spaCy UPOS tags (used in output column names)
    POS_LABELS: dict = {
        'ADJ':  'Adjective',
        'ADV':  'Adverb',
        'ADP':  'Adposition',
        'AUX':  'Auxiliary',
        'DET':  'Determiner',
        'INTJ': 'Interjection',
        'NOUN': 'Noun',
        'NUM':  'Numeral',
        'PART': 'Particle',
        'PRON': 'Pronoun',
        'PROPN':'Proper noun',
        'VERB': 'Lexical verb',
        # CCONJ / SCONJ intentionally absent – they keep their spaCy tag
        # in per-tag rows; the merged Conjunction group covers the expected column.
    }

    # Expanded human-readable labels for morphological feature keys
    FEAT_LABELS: dict = {
        'First person':    'First person pronoun',
        'Second person':   'Second person pronoun',
        'Third person':    'Third person pronoun',
        'Singular':        'Singular word',
        'Plural':          'Plural word',
        'Indefinite':      'Indefinite word',
        'Definite':        'Definite word',
        'Finite':          'Finite verb',
        'Infinitive':      'Infinitive verb',
        'Past':            'Past tense',
        'Present':         'Present tense',
        'Passive':         'Passive voice',
        # These map to themselves:
        'Personal pronoun':'Personal pronoun',
        'Interrogative':   'Interrogative',
        'Demonstrative':   'Demonstrative',
        'Verbal adjective':'Verbal adjective',
    }

    def __init__(self):
        print("⏳ Initializing DeepProfiler (Lingualyzer Implementation)...")
        
        # 1. Dynamically find the path to the model relative to this python script
        # __file__ is profiler.py. We go up one level to 'lid_toolkit', then into 'resources'
        base_dir = Path(__file__).parent.parent 
        model_path = base_dir / "models" / "fasttext" / "lid.176.bin"
        
        # 2. Check if it exists so we don't crash silently
        if not model_path.exists():
            raise FileNotFoundError(f"Missing FastText LID model at {model_path}")
            
        # 3. Load the lightning-fast model into memory!
        # (fasttext suppresses its own internal C++ warnings to keep the terminal clean)
        fasttext.FastText.eprint = lambda x: None 
        self.lid_model = fasttext.load_model(str(model_path))
        

        # Map FastText ISO codes to spaCy's small, fast models
        self.SPACY_MODELS = {
            'en': 'en_core_web_sm',   # English
            'ca': 'ca_core_news_sm',  # Catalan
            'zh': 'zh_core_web_sm',   # Chinese
            'hr': 'hr_core_news_sm',  # Croatian
            'da': 'da_core_news_sm',  # Danish
            'nl': 'nl_core_news_sm',  # Dutch
            'fi': 'fi_core_news_sm',  # Finnish
            'fr': 'fr_core_news_sm',  # French
            'de': 'de_core_news_sm',  # German
            'el': 'el_core_news_sm',  # Greek
            'it': 'it_core_news_sm',  # Italian
            'ja': 'ja_ginza',         # Japanese
            'ko': 'ko_core_news_sm',  # Korean
            'lt': 'lt_core_news_sm',  # Lithuanian
            'mk': 'mk_core_news_sm',  # Macedonian
            'nb': 'nb_core_news_sm',  # Norwegian Bokmål
            'pl': 'pl_core_news_sm',  # Polish
            'pt': 'pt_core_news_sm',  # Portuguese
            'ro': 'ro_core_news_sm',  # Romanian
            'ru': 'ru_core_news_sm',  # Russian
            'sl': 'sl_core_news_sm',  # Slovenian
            'es': 'es_core_news_sm',  # Spanish
            'sv': 'sv_core_news_sm',  # Swedish
            'uk': 'uk_core_news_sm'   # Ukrainian
        }

        self.FASTTEXT_TO_SPACY = {
            'no': 'nb',  # FastText outputs 'no' for Norwegian, but spaCy model is 'nb'
        }

        self.fasttext_model = None
        self.current_fasttext_lang = None
        # cache for per‑language spaCy pipelines
        self._nlp_cache: dict[str, spacy.Language] = {}
        self._centroid_cache: dict[tuple, np.ndarray] = {}
        # wrap wordfreq.zipf_frequency with lru cache
        self._zipf_cache = functools.lru_cache(maxsize=None)(zipf_frequency)
        # Define UD Tag Groups based on Lingualyzer definitions
        self.TAG_GROUPS = {
            'Lexical item': {'ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB'},
            'Grammatical item': {'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'},
            'Verb': {'VERB', 'AUX'},  # "Verb count" in Lingualyzer = Verb + Aux
            'Conjunction': {'CCONJ', 'SCONJ'}
        }
        


    def _make_pipeline(self, lang: str) -> spacy.Language:
        """Return a cached spaCy NLP pipeline for the given language; download model if needed."""
        if lang not in self._nlp_cache:
            model_name = self.SPACY_MODELS[lang]
            if not spacy.util.is_package(model_name):
                print(f"   Downloading spaCy model '{model_name}'...")
                spacy.cli.download(model_name)

            # --- 1. LOAD MODEL & APPLY LANGUAGE-SPECIFIC FIXES ---
            if lang == 'ja':
                # confection>=1.3.x enforces strict types; ja_ginza's compound_splitter
                # ships split_mode=None which fails validation — override to "C" (long units).
                ja_config = {"components": {"compound_splitter": {"split_mode": "C"}}}
                nlp = spacy.load(model_name, disable=["ner"], config=ja_config)
            elif lang == 'ko':
                # Force pure-Python rule-based tokenizer (Perfect for Korean eojeols, bypasses C++)
                ko_config = {"nlp": {"tokenizer": {"@tokenizers": "spacy.Tokenizer.v1"}}}
                nlp = spacy.load(model_name, disable=[ "ner"], config=ko_config)
            else:
                nlp = spacy.load(model_name, disable=[ "ner"])

            # --- 2. THE SENTENCE BOUNDARY FIX ---
            # If the smart statistical senter is bundled but asleep, wake it up!
            if "senter" in nlp.disabled:
                nlp.enable_pipe("senter")
            # Fallback: If a specific language model lacks a neural senter, use the rule-based one so it doesn't crash
            elif "senter" not in nlp.pipe_names:
                nlp.add_pipe("sentencizer") 
            
            self._nlp_cache[lang] = nlp
            
            
        return self._nlp_cache[lang]

    def _load_fasttext_model(self, lang_code: str):
        """
        Dynamically downloads and loads the correct compressed FastText model 
        from Hugging Face based on the target language code.
        """
        filename = f"fasttext-{lang_code}-mini.bin"
        cache_dir = Path("./fasttext_cache")
        repo_id = "werner1hugo/compressed-fasttext-models"
        
        try:
            # 1. Download the file (or retrieve from local cache if it exists)
            model_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                cache_dir=cache_dir
            )
            
            # 2. Load the model into the class instance
            self.fasttext_model = compress_fasttext.CompressedFastTextKeyedVectors.load(str(model_path))
        except Exception as e:
            # If the download fails (e.g., no internet, or language doesn't exist in your repo)
            print(f"Warning: Could not load FastText model for '{lang_code}'. Error: {e}")
            self.fasttext_model = None

    # =========================================================================
    # HELPER: Feature Extraction Logic
    # =========================================================================
    def _check_feature_optimized(self, word_pos_, morph, feat_name):
        """Check morphological features using spaCy's morph API."""
        # Compound checks requiring multiple morph conditions
        if feat_name == 'First person':
            return (word_pos_ == 'PRON' and 'Prs' in morph.get("PronType") and '1' in morph.get("Person"))
        elif feat_name == 'Second person':
            return (word_pos_ == 'PRON' and 'Prs' in morph.get("PronType") and '2' in morph.get("Person"))
        elif feat_name == 'Third person':
            return (word_pos_ == 'PRON' and 'Prs' in morph.get("PronType") and '3' in morph.get("Person"))
        elif feat_name == 'Personal pronoun':
            return (word_pos_ == 'PRON' and 'Prs' in morph.get("PronType"))
        elif feat_name == 'Singular':
            return (word_pos_ in ('NOUN', 'PROPN', 'PRON') and 'Sing' in morph.get("Number"))
        elif feat_name == 'Plural':
            return (word_pos_ in ('NOUN', 'PROPN', 'PRON') and 'Plur' in morph.get("Number"))

        # Single-key checks: (morph_feature_name, expected_value)
        checks = {
            'Interrogative':    ('PronType', 'Int'),
            'Demonstrative':    ('PronType', 'Dem'),
            'Indefinite':       ('Definite',  'Ind'),
            'Definite':         ('Definite',  'Def'),
            'Finite':           ('VerbForm',  'Fin'),
            'Infinitive':       ('VerbForm',  'Inf'),
            'Verbal adjective': ('VerbForm',  'Part'),
            'Past':             ('Tense',     'Past'),
            'Present':          ('Tense',     'Pres'),
            'Passive':          ('Voice',     'Pass'),
        }
        target = checks.get(feat_name)
        if target:
            feat_key, feat_val = target
            return feat_val in morph.get(feat_key)
        return False
    
    # …existing code…
    def _calc_burstiness(self, positions, doc_len):
        """Finite‑size corrected burstiness (Kim & Jo 2016) – vectorised."""
        arr = np.asarray(positions, dtype=np.int32)
        n = arr.size
        if n == 0:
            return 0.0

        if n >= 2:
            gaps = np.diff(arr)
            if np.std(gaps) == 0:
                return -1.0          # perfect regularity

        gaps = np.diff(arr)
        if gaps.size == 0:
            return 0.0

        std_gap = np.std(gaps, ddof=1)
        mean_gap = np.mean(gaps)
        if mean_gap == 0:
            return 0.0

        r = std_gap / mean_gap
        sqrt_np1 = np.sqrt(n + 1)
        sqrt_nm1 = np.sqrt(n - 1)
        num = (sqrt_np1 * r) - sqrt_nm1
        den = ((sqrt_np1 - 2) * r) + sqrt_nm1
        return num / den



    # def _calc_burstiness(self, positions, doc_len):
    #     """
    #     Calculates burstiness using the finite-size corrected measure A_n(r) 
    #     from Kim and Jo (2016).
    #     """
    #     n = len(positions)
        
    #     # 1. Edge Case: Need at least 1 item
    #     if n == 0: 
    #         return 0.0
            
    #     # 2. Check for "Perfect Internal Regularity" (The Adjective Case)
    #     if n >= 2:
    #         internal_gaps = np.diff(positions)
    #         if np.std(internal_gaps) == 0:
    #             return -1.0

    #     # 3. Standard Calculation
    #     gaps = list(np.diff(positions))
        
    #     if len(gaps) == 0: 
    #         return 0.0
        
    #     # Use standard Sample SD (ddof=1) and True Mean
    #     std_gap = np.std(gaps, ddof=1)
    #     mean_gap = np.mean(gaps)
        
    #     if mean_gap == 0: 
    #         return 0.0
            
    #     r = std_gap / mean_gap
        
    #     # 4. Kim and Jo (2016) Finite-Size Correction A_n(r)
    #     sqrt_n_plus_1 = np.sqrt(n + 1)
    #     sqrt_n_minus_1 = np.sqrt(n - 1)
        
    #     numerator = (sqrt_n_plus_1 * r) - sqrt_n_minus_1
    #     denominator = ((sqrt_n_plus_1 - 2) * r) + sqrt_n_minus_1
        
    #     return numerator / denominator
    
    #     # # 4. Final Calculation
    #     # cv = std_gap / mean_gap 
    #     # return (cv - 1) / (cv + 1)
    
    # def _levenshtein_distance(self, s1, s2):
    #     """Calculate Levenshtein (edit) distance between two strings or sequences."""
    #     # Handle sequences (lists) directly for word-level comparison
    #     if isinstance(s1, list) and isinstance(s2, list):
    #         if len(s1) < len(s2):
    #             s1, s2 = s2, s1
    #         if len(s2) == 0:
    #             return len(s1)
    #         previous_row = list(range(len(s2) + 1))
    #         for i, w1 in enumerate(s1):
    #             current_row = [i + 1]
    #             for j, w2 in enumerate(s2):
    #                 insertions = previous_row[j + 1] + 1
    #                 deletions = current_row[j] + 1
    #                 substitutions = previous_row[j] + (w1 != w2)
    #                 current_row.append(min(insertions, deletions, substitutions))
    #             previous_row = current_row
    #         return previous_row[-1]
    #     else:
    #         # Fallback: treat as strings for character-level comparison
    #         if len(s1) < len(s2):
    #             return self._levenshtein_distance(s2, s1)
    #         if len(s2) == 0:
    #             return len(s1)
    #         previous_row = range(len(s2) + 1)
    #         for i, c1 in enumerate(s1):
    #             current_row = [i + 1]
    #             for j, c2 in enumerate(s2):
    #                 insertions = previous_row[j + 1] + 1
    #                 deletions = current_row[j] + 1
    #                 substitutions = previous_row[j] + (c1 != c2)
    #                 current_row.append(min(insertions, deletions, substitutions))
    #             previous_row = current_row
    #         return previous_row[-1]


    def _levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein distance using C-optimized backend."""
        # editdistance handles both strings and lists of strings natively and is ~100x faster
        return editdistance.eval(s1, s2)


    def _filter_valid_sentences(self, sentences):
        """Filter out empty or whitespace-only sentence spans.
        
        Parameters
        ----------
        sentences : iterator of spacy.tokens.Span
            Sentence spans from doc.sents
            
        Returns
        -------
        list of spacy.tokens.Span
            Filtered list containing only sentences with actual content
        """
        valid_sentences = []
        for sent in sentences:
            # Check if sentence has actual content (not just whitespace)
            if sent.text.strip() and len(sent.text.strip()) > 0:
                valid_sentences.append(sent)
        return valid_sentences
    
    def _get_sentence_centroid(self, words):
        """Compute the centroid vector for a sentence by averaging FastText vectors of words."""
        if self.fasttext_model is None:
            return None
        vectors = []
        for word in words:
            if word in self.fasttext_model:
                vectors.append(self.fasttext_model[word])
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return None


        # def _get_sentence_centroid(self, words):
        # if self.fasttext_model is None:
        #     return None
        # model = self.fasttext_model                   # local ref
        # vecs = [model[w] for w in words if w in model]
        # return np.mean(vecs, axis=0) if vecs else None
    
    # =========================================================================
    # SUB-METHODS: Modular Measure Calculation
    # =========================================================================
    
    def _calc_paragraph_measures(self, text, sentences):
        """Calculate paragraph-level measures."""
        stats = {}
        
        # Detect paragraphs by double newlines
        paragraphs = re.split(r'\n\s*\n', text.strip())
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        stats['Paragraph count'] = paragraph_count
        if paragraph_count > 0:
            stats['Sentence per paragraph'] = len(sentences) / paragraph_count
        else:
            stats['Sentence per paragraph'] = 0
        
        return stats
    
    def _calc_lexical_diversity(self, lower_non_punct_tokens, pos_map_lower_non_punct, doc_len):
        """Calculate lexical diversity measures."""
        stats = {}

        # Use lower_non_punct_tokens for type-based calculations
        type_count = len(set(lower_non_punct_tokens))

        # Hapax legomena (words appearing exactly once, using lower_non_punct_tokens)
        word_counts = Counter(lower_non_punct_tokens)
        hapax_words = {word for word, count in word_counts.items() if count == 1}
        hapax_count = len(hapax_words)
        stats['Hapax legomena count'] = hapax_count
        stats['Hapax legomena incidence'] = (hapax_count / doc_len * 1000) if doc_len > 0 else 0

        # Hapax legomena distributional measures (positions of words occurring only once, using lower_non_punct_tokens)
        hapax_positions = [i + 1 for i, token in enumerate(lower_non_punct_tokens) if token in hapax_words]
        stats['Hapax legomena burstiness'] = self._calc_burstiness(hapax_positions, doc_len)

        # Hapax legomena concentration: < 0 = first half, > 0 = second half
        # Hapax legomena concentration: < 0 = first half, > 0 = second half
        if hapax_positions and doc_len > 0:
            if doc_len % 2 == 0:
                # Standard split for even-length sentences
                midpoint = doc_len / 2.0
                first_half = sum(1 for p in hapax_positions if p <= midpoint)
                second_half = sum(1 for p in hapax_positions if p > midpoint)
            else:
                # Human-pivot split for odd-length sentences
                pivot = (doc_len + 1) / 2.0
                first_half = sum(1 for p in hapax_positions if p < pivot)
                second_half = sum(1 for p in hapax_positions if p > pivot)
            
            total_valid_items = first_half + second_half
            stats['Hapax legomena concentration'] = (second_half - first_half) / total_valid_items if total_valid_items > 0 else 0
        else:
            stats['Hapax legomena concentration'] = 0

        # Hapax legomena average position (normalized 0 to 1) and SD: use original token positions
        # Only count the first occurrence of each hapax word (case-insensitive, non-punct) in the original tokens
       
        stats['Hapax legomena avg position'] = ((np.mean(hapax_positions))-1) / (doc_len-1) if hapax_positions and doc_len > 1 else 0

        if hapax_positions and doc_len > 1 and len(hapax_positions) >= 2:
            # normalized = [p / (doc_len-1) for p in hapax_positions]
            sample_sd = np.std(hapax_positions, ddof=1)
            stats['Hapax legomena position SD'] = sample_sd / (doc_len - 1) if doc_len > 1 else 0
            # return sample_sd / (doc_len - 1)
            # stats['Hapax legomena position SD'] = np.std(normalized)
        else:
            stats['Hapax legomena position SD'] = 0

        # Honoré's statistic
        def moving_average_ttr(lower_non_punct_tokens, window_size=100):
            if len(lower_non_punct_tokens) < window_size:
                # Fallback: TTR for the whole text
                return len(set(lower_non_punct_tokens)) / len(lower_non_punct_tokens) if lower_non_punct_tokens else 0
            ttrs = []
            for i in range(len(lower_non_punct_tokens) - window_size + 1):
                window = lower_non_punct_tokens[i:i+window_size]
                ttrs.append(len(set(window)) / window_size)
            return sum(ttrs) / len(ttrs) if ttrs else 0

        # ...existing code...

        # At the end of _calc_lexical_diversity, after defining moving_average_ttr:
        stats['Moving average type-token ratio'] = moving_average_ttr(lower_non_punct_tokens, window_size=100)

        # ...existing code...
        # Per-PoS TTRs
        pos_tags = ['ADJ', 'ADV', 'INTJ', 'VERB', 'NOUN', 'PROPN', 'ADP', 'AUX', 
                 'DET', 'NUM', 'PART', 'PRON']
        for tag in pos_tags:
            label = self.POS_LABELS.get(tag, tag)
            positions = pos_map_lower_non_punct.get(tag, [])
            if positions:
                # Get tokens at these positions
                pos_tokens = [lower_non_punct_tokens[i-1] for i in positions if i > 0]
                if pos_tokens:
                    stats[f'{label} type-token ratio'] = len(set(pos_tokens)) / len(pos_tokens)
                else:
                    stats[f'{label} type-token ratio'] = 0
            else:
                stats[f'{label} type-token ratio'] = 0
        
        # Combined group TTRs
        # Lexical item TTR (open class: ADJ, ADV, INTJ, NOUN, PROPN, VERB)
        lexical_tags = {'ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB'}
        lexical_positions = []
        for tag in lexical_tags:
            lexical_positions.extend(pos_map_lower_non_punct.get(tag, []))
        if lexical_positions:
            lexical_tokens = [lower_non_punct_tokens[i-1] for i in lexical_positions if i > 0]
            stats['Lexical item type-token ratio'] = len(set(lexical_tokens)) / len(lexical_tokens) if lexical_tokens else 0
        else:
            stats['Lexical item type-token ratio'] = 0
        
        # Grammatical item TTR (closed class: ADP, AUX, CCONJ, DET, NUM, PART, PRON, SCONJ)
        grammatical_tags = {'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'}
        grammatical_positions = []
        for tag in grammatical_tags:
            grammatical_positions.extend(pos_map_lower_non_punct.get(tag, []))
        if grammatical_positions:
            grammatical_tokens = [lower_non_punct_tokens[i-1] for i in grammatical_positions if i > 0]
            stats['Grammatical item type-token ratio'] = len(set(grammatical_tokens)) / len(grammatical_tokens) if grammatical_tokens else 0
        else:
            stats['Grammatical item type-token ratio'] = 0
        
        # Verb_All TTR (VERB + AUX)
        verb_all_tags = {'VERB', 'AUX'}
        verb_all_positions = []
        for tag in verb_all_tags:
            verb_all_positions.extend(pos_map_lower_non_punct.get(tag, []))
        if verb_all_positions:
            verb_all_tokens = [lower_non_punct_tokens[i-1] for i in verb_all_positions if i > 0]
            stats['Verb type-token ratio'] = len(set(verb_all_tokens)) / len(verb_all_tokens) if verb_all_tokens else 0
        else:
            stats['Verb type-token ratio'] = 0

        # Conjunction type-token ratio (CCONJ + SCONJ)
        conjunction_tags = {'CCONJ', 'SCONJ'}
        conjunction_positions = []
        for tag in conjunction_tags:
            conjunction_positions.extend(pos_map_lower_non_punct.get(tag, []))
        if conjunction_positions:
            conjunction_tokens = [lower_non_punct_tokens[i-1] for i in conjunction_positions if i > 0]
            distinct_conjunctions = set(conjunction_tokens)
            stats['Conjunction type-token ratio'] = len(distinct_conjunctions) / len(conjunction_tokens) if conjunction_tokens else 0
        else:
            stats['Conjunction type-token ratio'] = 0
        
        return stats
    
    def _calc_word_lengths(self, doc, pos_map_lower_non_punct, lower_non_punct_tokens):
        
        stats = {}
    
        # Per-PoS average word lengths (using positions in pos_map_lower_non_punct)
        pos_tags = ['ADJ', 'ADV', 'INTJ', 'VERB', 'NOUN', 'PROPN', 'ADP', 'AUX', 
                    'DET', 'NUM', 'PART', 'PRON']
        for tag in pos_tags:
            label = self.POS_LABELS.get(tag, tag)
            positions = pos_map_lower_non_punct.get(tag, [])
            lengths = [len(lower_non_punct_tokens[i-1]) for i in positions if 0 < i <= len(lower_non_punct_tokens)]
            stats[f'{label} length'] = np.mean(lengths) if lengths else 0
    
        # Combined group word lengths
        group_defs = {
            'Lexical item': {'ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB'},
            'Grammatical item': {'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'},
            'Verb': {'VERB', 'AUX'},
            'Conjunction': {'CCONJ', 'SCONJ'}
        }
        for group, tags in group_defs.items():
            group_positions = []
            for tag in tags:
                group_positions.extend(pos_map_lower_non_punct.get(tag, []))
            lengths = [len(lower_non_punct_tokens[i-1]) for i in group_positions if 0 < i <= len(lower_non_punct_tokens)]
            stats[f'{group} length'] = np.mean(lengths) if lengths else 0
    
        return stats

    
    def _calc_zipf_variants(self, zipf_scores, lower_non_punct_tokens, lang_code, doc_len):
        """Calculate Zipf frequency variants."""
        stats = {}
        
        if not zipf_scores:
            stats['Zipf steepness of curve'] = 0
            stats['Zipf goodness of fit'] = 0
            stats['Frequent word incidence'] = 0
            return stats
        
        # # Zipf curve steepness using MLE (Clauset et al., 2009)
        # # More accurate than log-log linear regression
        # word_counts = Counter(lower_non_punct_tokens)
        # frequencies = np.array(sorted(word_counts.values(), reverse=True))
        # if len(frequencies) > 1:
        #     x_min = 1  # minimum frequency threshold
        #     # Filter frequencies >= x_min
        #     freq_above_min = frequencies[frequencies >= x_min]
        #     n = len(freq_above_min)
        #     if n > 1:
        #         # MLE estimator for discrete power law: α = 1 + n / Σ ln(x_i / (x_min - 0.5))
        #         alpha_mle = 1 + n / np.sum(np.log(freq_above_min / (x_min - 0.5)))
        #         stats['Zipf curve steepness'] = alpha_mle
                
        #         # Goodness-of-fit: R² determination coefficient
        #         # Compare observed frequencies to theoretical Zipf frequencies
        #         ranks = np.arange(1, len(freq_above_min) + 1)
        #         # Theoretical frequencies: f(r) = C / r^α, where C is fitted to match total
        #         theoretical_freqs = 1 / (ranks ** alpha_mle)
        #         # Scale theoretical to match observed total
        #         theoretical_freqs = theoretical_freqs * (np.sum(freq_above_min) / np.sum(theoretical_freqs))
        #         # Calculate R² = 1 - SS_res / SS_tot
        #         ss_res = np.sum((freq_above_min - theoretical_freqs) ** 2)
        #         ss_tot = np.sum((freq_above_min - np.mean(freq_above_min)) ** 2)
        #         r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        #         stats['Zipf goodness-of-fit'] = max(0, r_squared)  # Clamp to [0, 1]
        #     else:
        #         stats['Zipf curve steepness'] = 0
        #         stats['Zipf goodness-of-fit'] = 0
        # else:
        #     stats['Zipf curve steepness'] = 0
        #     stats['Zipf goodness-of-fit'] = 0

        # Zipf curve steepness using discrete MLE on the rank-frequency distribution
        word_counts = Counter(lower_non_punct_tokens)
        frequencies = np.array(sorted(word_counts.values(), reverse=True))
        
        if len(frequencies) > 1:
            x_min = 1  # minimum frequency threshold
            freq_above_min = frequencies[frequencies >= x_min]
            n = len(freq_above_min)
            
            if n > 1:
                ranks = np.arange(1, n + 1)
                N = np.sum(freq_above_min)
                
                # Empirical expected value of ln(rank)
                emp_mean_log_r = np.sum(freq_above_min * np.log(ranks)) / N
                
                # Objective function: Theoretical expected value must equal Empirical
                def mle_objective(s):
                    weights = ranks ** -s
                    theo_mean_log_r = np.sum(weights * np.log(ranks)) / np.sum(weights)
                    return theo_mean_log_r - emp_mean_log_r
                
                try:
                    # Find the steepness (s) that satisfies the discrete MLE objective
                    res = root_scalar(mle_objective, bracket=[0.0, 10.0])
                    s_mle = res.root
                except ValueError:
                    # Fallback if extremely flat/skewed 
                    s_mle = 1.0 
                
                stats['Zipf steepness of curve'] = abs(s_mle)
                
                # Goodness-of-fit: Squared Pearson correlation between actual and predicted
                weights = ranks ** -s_mle
                theo_freqs = N * weights / np.sum(weights)
                r_val, _ = pearsonr(freq_above_min, theo_freqs)
                
                # Clamp to [0, 1] just in case of floating point anomalies
                stats['Zipf goodness of fit'] = max(0.0, min(1.0, r_val ** 2))
            else:
                stats['Zipf steepness of curve'] = 0
                stats['Zipf goodness of fit'] = 0
        else:
            stats['Zipf steepness of curve'] = 0
            stats['Zipf goodness of fit'] = 0    
        
        # Average contextual diversity (approximated by Zipf score)
        
        # Frequency incidence counts
        freq_count = sum(1 for z in zipf_scores if z > 6.0)
        infreq_count = sum(1 for z in zipf_scores if z < 4.0)
        
        stats['Frequent word incidence'] = (freq_count / doc_len * 1000) if doc_len > 0 else 0
        
        # Unknown words (Zipf < 3.0 or not found in wordfreq)
        unknown_count = 0
        for token in lower_non_punct_tokens:
            z = zipf_frequency(token, lang_code)
            if z < 3.0:
                unknown_count += 1
        
            
        return stats
    
    def _calc_morphological_complexity(self, doc):
        """Calculate morphological complexity measures."""
        stats = {}
        
        # Word-lemma Levenshtein distances
        distances = []
        # Key by (lemma, PoS) tuple - lemmas with different PoS tags are differentiated
        lemmas_per_word = defaultdict(set)
        
        for token in doc:
            if token.text and token.lemma_ and token.pos_ not in ['PUNCT', 'SYM', 'X']:
                dist = self._levenshtein_distance(token.text.lower(), token.lemma_.lower())
                distances.append(dist)
                # Differentiate lemmas by PoS tag (e.g., "run" as NOUN vs "run" as VERB)
                lemmas_per_word[(token.lemma_, token.pos_)].add(token.text.lower())
        
        if distances:
            stats['Word-lemma Levenshtein dist.'] = np.mean(distances)
        else:
            stats['Word-lemma Levenshtein dist.'] = 0
        
        # Word-types per lemma (overall) - differentiated by PoS
        if lemmas_per_word:
            types_per_lemma = [len(word_forms) for word_forms in lemmas_per_word.values()]
            stats['Word types per lemma'] = np.mean(types_per_lemma)
        else:
            stats['Word types per lemma'] = 0
        
        # Word-types per lemma for specific PoS
        pos_filter_labels = {
            'noun':        'nouns',
            'verb':        'verbs',
            'lexical':     'lexical items',
            'grammatical': 'grammatical items',
        }
        for pos_filter, pos_tags in [('noun', {'NOUN'}), ('verb', {'VERB', 'AUX'}), 
                                       ('lexical', {'ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB'}),
                                       ('grammatical', {'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'})]:
            lemma_map = defaultdict(set)
            for token in doc:
                if token.pos_ in pos_tags and token.lemma_:
                    lemma_map[token.lemma_].add(token.text.lower())
            
            col = f'Word types per lemma ({pos_filter_labels[pos_filter]})'
            if lemma_map:
                types_per_lemma = [len(word_forms) for word_forms in lemma_map.values()]
                stats[col] = np.mean(types_per_lemma)
            else:
                stats[col] = 0
        
        return stats
    
    def _calc_ratios(self, pos_map_lower_non_punct, feat_map_lower_non_punct):
        """Calculate all 60+ comparative ratios."""
        stats = {}
        
        def safe_ratio(numerator, denominator):
            return numerator / denominator if denominator > 0 else 0
        
        def get_cnt(tags):
            if isinstance(tags, str): tags = {tags}
            return sum(len(pos_map_lower_non_punct.get(t, [])) for t in tags)
        
        # PoS-to-PoS ratios
        adj_c = get_cnt('ADJ')
        adv_c = get_cnt('ADV')
        noun_c = get_cnt('NOUN')
        propn_c = get_cnt('PROPN')
        verb_c = get_cnt('VERB')
        aux_c = get_cnt('AUX')
        adp_c = get_cnt('ADP')
        det_c = get_cnt('DET')
        pron_c = get_cnt('PRON')
        intj_c = get_cnt('INTJ')
        cconj_c = get_cnt('CCONJ')
        sconj_c = get_cnt('SCONJ')
        conj_c = cconj_c + sconj_c
        num_c = get_cnt('NUM')
        part_c = get_cnt('PART')
        
        lex_c = get_cnt({'ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB'})
        gram_c = get_cnt({'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'})
        
        # Adjective ratios
        stats['Adverb-adjective ratio'] = safe_ratio(adv_c, adj_c)
        stats['Determiner-adjective ratio'] = safe_ratio(det_c, adj_c)
        stats['Interjection-adjective ratio'] = safe_ratio(intj_c, adj_c)
        
        # Noun ratios
        stats['Adjective-noun ratio'] = safe_ratio(adj_c, noun_c)
        stats['Interjection-noun ratio'] = safe_ratio(intj_c, noun_c)
        stats['Proper noun-noun ratio'] = safe_ratio(propn_c, noun_c)
        stats['Verb-noun ratio'] = safe_ratio(verb_c, noun_c)
        stats['Adposition-noun ratio'] = safe_ratio(adp_c, noun_c)
        stats['Conjunction-noun ratio'] = safe_ratio(conj_c, noun_c)
        stats['Determiner-noun ratio'] = safe_ratio(det_c, noun_c)
        stats['Numeral-noun ratio'] = safe_ratio(num_c, noun_c)
        stats['Pronoun-noun ratio'] = safe_ratio(pron_c, noun_c)
        
        # Verb ratios
        stats['Adverb-verb ratio'] = safe_ratio(adv_c, verb_c)
        stats['Interjection-verb ratio'] = safe_ratio(intj_c, verb_c)
        stats['Adposition-verb ratio'] = safe_ratio(adp_c, verb_c)
        stats['Conjunction-verb ratio'] = safe_ratio(conj_c, verb_c)
        stats['Particle-verb ratio'] = safe_ratio(part_c, verb_c)
        stats['Auxiliary-lexical verb ratio'] = safe_ratio(aux_c, verb_c)
        
        # Lexical item ratios
        stats['Adjective-lexical item ratio'] = safe_ratio(adj_c, lex_c)
        stats['Adverb-lexical item ratio'] = safe_ratio(adv_c, lex_c)
        stats['Interjection-lexical item ratio'] = safe_ratio(intj_c, lex_c)
        stats['Lexical verb-lexical item ratio'] = safe_ratio(verb_c, lex_c)
        stats['Noun-lexical item ratio'] = safe_ratio(noun_c, lex_c)
        stats['Proper noun-lexical item ratio'] = safe_ratio(propn_c, lex_c)
        
        # Conjunction ratios
        
        # Determiner ratios
        stats['Adposition-determiner ratio'] = safe_ratio(adp_c, det_c)
        stats['Proper noun-determiner ratio'] = safe_ratio(propn_c, det_c)
        
        # Pronoun ratios
        stats['Proper noun-pronoun ratio'] = safe_ratio(propn_c, pron_c)
        
        # Grammatical item ratios
        stats['Auxiliary-grammatical item ratio'] = safe_ratio(aux_c, gram_c)
        stats['Conjunction-grammatical item ratio'] = safe_ratio(conj_c, gram_c)
        stats['Determiner-grammatical item ratio'] = safe_ratio(det_c, gram_c)
        stats['Numeral-grammatical item ratio'] = safe_ratio(num_c, gram_c)
        stats['Particle-grammatical item ratio'] = safe_ratio(part_c, gram_c)
        stats['Pronoun-grammatical item ratio'] = safe_ratio(pron_c, gram_c)
        
        # Lexical-grammatical ratio
        stats['Lexical-grammatical item ratio'] = safe_ratio(lex_c, gram_c)
        
        # Person pronoun ratios
        pers_pron_c = len(feat_map_lower_non_punct.get('Personal pronoun', []))
        first_c = len(feat_map_lower_non_punct.get('First person', []))
        second_c = len(feat_map_lower_non_punct.get('Second person', []))
        third_c = len(feat_map_lower_non_punct.get('Third person', []))
        
        stats['First person-personal pronoun ratio'] = safe_ratio(first_c, pers_pron_c)
        stats['Second person-personal pronoun ratio'] = safe_ratio(second_c, pers_pron_c)
        stats['Third person-personal pronoun ratio'] = safe_ratio(third_c, pers_pron_c)
        stats['First-third person pronoun ratio'] = safe_ratio(first_c, third_c)
        stats['First-second person pronoun ratio'] = safe_ratio(first_c, second_c)
        stats['Second-third person pronoun ratio'] = safe_ratio(second_c, third_c)
        
        # Feature ratios
        sing_c = len(feat_map_lower_non_punct.get('Singular', []))
        plur_c = len(feat_map_lower_non_punct.get('Plural', []))
        def_c = len(feat_map_lower_non_punct.get('Definite', []))
        indef_c = len(feat_map_lower_non_punct.get('Indefinite', []))
        inf_c = len(feat_map_lower_non_punct.get('Infinitive', []))
        fin_c = len(feat_map_lower_non_punct.get('Finite', []))
        vadj_c = len(feat_map_lower_non_punct.get('Verbal adjective', []))
        pres_c = len(feat_map_lower_non_punct.get('Present', []))
        past_c = len(feat_map_lower_non_punct.get('Past', []))
        
        stats['Plural-singular word ratio'] = safe_ratio(plur_c, sing_c)
        stats['Definite-indefinite word ratio'] = safe_ratio(def_c, indef_c)
        stats['Infinitive-finite verb ratio'] = safe_ratio(inf_c, fin_c)
        stats['Present-past tense ratio'] = safe_ratio(pres_c, past_c)
        
        return stats
    
    def _calc_distributional_measures(self, pos_map_lower_non_punct, feat_map_lower_non_punct, doc_len, lang_code, lower_non_punct_tokens):
        """Calculate concentration, average position, and position SD for all categories."""
        stats = {}
        
        def calc_concentration(positions, doc_len):
            """Calculate concentration using human-pivot logic for odd-length sequences."""
            if not positions or doc_len == 0:
                return 0
                
            if doc_len % 2 == 0:
                # Standard split for even-length sentences
                midpoint = doc_len / 2.0
                first_half = sum(1 for p in positions if p <= midpoint)
                second_half = sum(1 for p in positions if p > midpoint)
            else:
                # Human-pivot split for odd-length sentences
                pivot = (doc_len + 1) / 2.0
                first_half = sum(1 for p in positions if p < pivot)
                second_half = sum(1 for p in positions if p > pivot)
                # Note: any position exactly equal to the pivot is ignored.

            # We must only divide by the items that successfully made it into a bucket
            total_valid_items = first_half + second_half
            
            if total_valid_items == 0:
                return 0
                
            return (second_half - first_half) / total_valid_items
        
        def calc_avg_position(positions, doc_len):
            """Calculate average normalized position (0 to 1)."""
            if not positions or doc_len == 0:
                return 0
            return ((np.mean(positions))-1) / (doc_len-1)
        
        def calc_position_sd(positions, doc_len):
            """Calculate standard deviation of normalized positions."""
            if not positions or doc_len == 0 or len(positions) < 2:
                return 0
            sample_sd = np.std(positions, ddof=1)
            return sample_sd / (doc_len - 1)
            # normalized = [p / doc_len for p in positions]
            # return np.std(normalized)
        
        # PoS-based distributional measures (restricted to specific tags)
        pos_tags = ['ADJ', 'ADV', 'INTJ', 'VERB', 'NOUN', 'PROPN', 'ADP', 'AUX', 
                    'DET', 'NUM', 'PART', 'PRON']
        for tag in pos_tags:
            label = self.POS_LABELS.get(tag, tag)
            positions = pos_map_lower_non_punct.get(tag, [])
            stats[f'{label} concentration'] = calc_concentration(positions, doc_len)
            stats[f'{label} avg position'] = calc_avg_position(positions, doc_len)
            stats[f'{label} position SD'] = calc_position_sd(positions, doc_len)

        # Tag group distributional measures (using self.TAG_GROUPS)
        for group_name, tag_set in self.TAG_GROUPS.items():
            group_positions = []
            for tag in tag_set:
                group_positions.extend(pos_map_lower_non_punct.get(tag, []))
            group_positions_sorted = sorted(group_positions)
            stats[f'{group_name} concentration'] = calc_concentration(group_positions_sorted, doc_len)
            stats[f'{group_name} avg position'] = calc_avg_position(group_positions_sorted, doc_len)
            stats[f'{group_name} position SD'] = calc_position_sd(group_positions_sorted, doc_len)
        
        # Feature-based distributional measures
        for feat in feat_map_lower_non_punct:
            label = self.FEAT_LABELS.get(feat, feat)
            positions = feat_map_lower_non_punct[feat]
            stats[f'{label} concentration'] = calc_concentration(positions, doc_len)
            stats[f'{label} avg position'] = calc_avg_position(positions, doc_len)
            stats[f'{label} position SD'] = calc_position_sd(positions, doc_len)
        
        # Frequency-based distributional measures
        freq_positions = []
        infreq_positions = []
        unknown_positions = []
        # Use lower_non_punct_tokens for frequency-based distributional measures
        for i, token in enumerate(lower_non_punct_tokens, 1):
            z = zipf_frequency(token, lang_code)
            if z > 6.0:
                freq_positions.append(i)
            elif z < 4.0:
                infreq_positions.append(i)
            if z < 3.0:
                unknown_positions.append(i)
        
        stats['Frequent word concentration'] = calc_concentration(freq_positions, doc_len)
        stats['Frequent word avg position'] = calc_avg_position(freq_positions, doc_len)
        stats['Frequent word position SD'] = calc_position_sd(freq_positions, doc_len)
        stats['Frequent word burstiness'] = self._calc_burstiness(freq_positions, doc_len)
        
        stats['Infrequent word concentration'] = calc_concentration(infreq_positions, doc_len)
        stats['Infrequent word avg position'] = calc_avg_position(infreq_positions, doc_len)
        stats['Infrequent word position SD'] = calc_position_sd(infreq_positions, doc_len)
        stats['Infrequent word burstiness'] = self._calc_burstiness(infreq_positions, doc_len)
        
        
        return stats

    # =========================================================================
    # BOTTOM-UP CASCADE: metric classification constants
    # =========================================================================

    # Keys whose values sum correctly when aggregating sentences → paragraph → document.
    ADDITIVE_COUNT_KEYS: frozenset = frozenset({
        'Adjective count',
        'Adposition count',
        'Adverb count',
        'Auxiliary count',
        'Conjunction count',
        'Definite word count',
        'Demonstrative count',
        'Determiner count',
        'Finite verb count',
        'First person pronoun count',
        'Frequent word count',
        'Grammatical item count',
        'Indefinite word count',
        'Infinitive verb count',
        'Interjection count',
        'Letter count',
        'Lexical item count',
        'Lexical verb count',
        'Noun count',
        'Numeral count',
        'Particle count',
        'Past tense count',
        'Personal pronoun count',
        'Plural word count',
        'Present tense count',
        'Pronoun count',
        'Proper noun count',
        'Punctuation count',
        'Second person pronoun count',
        'Sentence count',
        'Singular word count',
        'Third person pronoun count',
        'Token count',
        'Word count'
    })

    # Maps incidence key → (count_key, denominator_key); value = sum(count) / sum(denom) × 1000.
    INCIDENCE_TO_COUNT_MAP: dict = {
        'Adjective incidence': ('Adjective count', 'Word count'),
        'Adverb incidence': ('Adverb count', 'Word count'),
        'Adposition incidence': ('Adposition count', 'Word count'),
        'Auxiliary incidence': ('Auxiliary count', 'Word count'),
        'Noun incidence': ('Noun count', 'Word count'),
        'Numeral incidence': ('Numeral count', 'Word count'),
        'Particle incidence': ('Particle count', 'Word count'),
        'Pronoun incidence': ('Pronoun count', 'Word count'),
        'Proper noun incidence': ('Proper noun count', 'Word count'),
        'Lexical item incidence': ('Lexical item count', 'Word count'),
        'Personal pronoun incidence': ('Personal pronoun count', 'Word count'),
        'First person pronoun incidence': ('First person pronoun count', 'Word count'),
        'Second person pronoun incidence': ('Second person pronoun count', 'Word count'),
        'Third person pronoun incidence': ('Third person pronoun count', 'Word count'),
        'Demonstrative incidence': ('Demonstrative count', 'Word count'),
        'Singular word incidence': ('Singular word count', 'Word count'),
        'Plural word incidence': ('Plural word count', 'Word count'),
        'Indefinite word incidence': ('Indefinite word count', 'Word count'),
        'Definite word incidence': ('Definite word count', 'Word count'),
        'Finite verb incidence': ('Finite verb count', 'Word count'),
        'Infinitive verb incidence': ('Infinitive verb count', 'Word count'),
        'Past tense incidence': ('Past tense count', 'Word count'),
        'Frequent word incidence': ('Frequent word count', 'Word count'),
        'Punctuation incidence': ('Punctuation count', 'Token count'),
    }

    # Maps ratio key → (numerator_count_key, denominator_count_key).
    # Aggregated as: sum(numerator_count) / sum(denominator_count) — exact bottom-up.
    RATIO_PAIRS_MAP: dict = {
        'Adverb-adjective ratio': ('Adverb count', 'Adjective count'),
        'Determiner-adjective ratio': ('Determiner count', 'Adjective count'),
        'Interjection-adjective ratio': ('Interjection count', 'Adjective count'),
        'Adjective-noun ratio': ('Adjective count', 'Noun count'),
        'Interjection-noun ratio': ('Interjection count', 'Noun count'),
        'Proper noun-noun ratio': ('Proper noun count', 'Noun count'),
        'Verb-noun ratio': ('Lexical verb count', 'Noun count'),
        'Adposition-noun ratio': ('Adposition count', 'Noun count'),
        'Conjunction-noun ratio': ('Conjunction count', 'Noun count'),
        'Determiner-noun ratio': ('Determiner count', 'Noun count'),
        'Numeral-noun ratio': ('Numeral count', 'Noun count'),
        'Pronoun-noun ratio': ('Pronoun count', 'Noun count'),
        'Adverb-verb ratio': ('Adverb count', 'Lexical verb count'),
        'Interjection-verb ratio': ('Interjection count', 'Lexical verb count'),
        'Adposition-verb ratio': ('Adposition count', 'Lexical verb count'),
        'Conjunction-verb ratio': ('Conjunction count', 'Lexical verb count'),
        'Particle-verb ratio': ('Particle count', 'Lexical verb count'),
        'Auxiliary-lexical verb ratio': ('Auxiliary count', 'Lexical verb count'),
        'Adjective-lexical item ratio': ('Adjective count', 'Lexical item count'),
        'Adverb-lexical item ratio': ('Adverb count', 'Lexical item count'),
        'Interjection-lexical item ratio': ('Interjection count', 'Lexical item count'),
        'Lexical verb-lexical item ratio': ('Lexical verb count', 'Lexical item count'),
        'Noun-lexical item ratio': ('Noun count', 'Lexical item count'),
        'Proper noun-lexical item ratio': ('Proper noun count', 'Lexical item count'),
        'Adposition-determiner ratio': ('Adposition count', 'Determiner count'),
        'Proper noun-determiner ratio': ('Proper noun count', 'Determiner count'),
        'Proper noun-pronoun ratio': ('Proper noun count', 'Pronoun count'),
        'Auxiliary-grammatical item ratio': ('Auxiliary count', 'Grammatical item count'),
        'Conjunction-grammatical item ratio': ('Conjunction count', 'Grammatical item count'),
        'Determiner-grammatical item ratio': ('Determiner count', 'Grammatical item count'),
        'Numeral-grammatical item ratio': ('Numeral count', 'Grammatical item count'),
        'Particle-grammatical item ratio': ('Particle count', 'Grammatical item count'),
        'Pronoun-grammatical item ratio': ('Pronoun count', 'Grammatical item count'),
        'Lexical-grammatical item ratio': ('Lexical item count', 'Grammatical item count'),
        'First person-personal pronoun ratio': ('First person pronoun count', 'Personal pronoun count'),
        'Second person-personal pronoun ratio': ('Second person pronoun count', 'Personal pronoun count'),
        'Third person-personal pronoun ratio': ('Third person pronoun count', 'Personal pronoun count'),
        'First-third person pronoun ratio': ('First person pronoun count', 'Third person pronoun count'),
        'First-second person pronoun ratio': ('First person pronoun count', 'Second person pronoun count'),
        'Second-third person pronoun ratio': ('Second person pronoun count', 'Third person pronoun count'),
        'Plural-singular word ratio': ('Plural word count', 'Singular word count'),
        'Definite-indefinite word ratio': ('Definite word count', 'Indefinite word count'),
        'Infinitive-finite verb ratio': ('Infinitive verb count', 'Finite verb count'),
        'Present-past tense ratio': ('Present tense count', 'Past tense count'),
    }

    # Keys that are aggregated as an unweighted mean across sentences.
    MEAN_KEYS: frozenset = frozenset({
        'Word types per lemma',
        'Word-lemma Levenshtein dist.'
    })

    # Keys that require the full contiguous token sequence and CANNOT be derived
    # by aggregating sentence-level values.  _aggregate_to_one sets these to 0.0
    # as a placeholder; callers must overwrite them from the full-doc/par extraction.
    NON_CASCADABLE_KEYS: frozenset = frozenset({
        'Adjective avg position',
        'Adjective burstiness',
        'Adjective concentration',
        'Adjective position SD',
        'Adjective type count',
        'Adjective type-token ratio',
        'Adposition avg position',
        'Adposition burstiness',
        'Adposition concentration',
        'Adposition position SD',
        'Adposition type count',
        'Adposition type-token ratio',
        'Adverb avg position',
        'Adverb burstiness',
        'Adverb concentration',
        'Adverb position SD',
        'Adverb type count',
        'Adverb type-token ratio',
        'Auxiliary avg position',
        'Auxiliary burstiness',
        'Auxiliary concentration',
        'Auxiliary position SD',
        'Auxiliary type count',
        'Auxiliary type-token ratio',
        'Conjunction avg position',
        'Conjunction burstiness',
        'Conjunction concentration',
        'Conjunction position SD',
        'Conjunction type count',
        'Conjunction type-token ratio',
        'Definite word avg position',
        'Definite word burstiness',
        'Definite word concentration',
        'Definite word position SD',
        'Demonstrative avg position',
        'Demonstrative burstiness',
        'Demonstrative concentration',
        'Demonstrative position SD',
        'Determiner type-token ratio',
        'Finite verb avg position',
        'Finite verb burstiness',
        'Finite verb concentration',
        'Finite verb position SD',
        'First person pronoun avg position',
        'First person pronoun burstiness',
        'First person pronoun concentration',
        'First person pronoun position SD',
        'Frequent word avg position',
        'Frequent word burstiness',
        'Frequent word concentration',
        'Frequent word position SD',
        'Grammatical item type count',
        'Grammatical item type-token ratio',
        'Hapax legomena avg position',
        'Hapax legomena burstiness',
        'Hapax legomena concentration',
        'Hapax legomena count',
        'Hapax legomena incidence',
        'Hapax legomena position SD',
        'Indefinite word avg position',
        'Indefinite word burstiness',
        'Indefinite word concentration',
        'Indefinite word position SD',
        'Infinitive verb avg position',
        'Infinitive verb burstiness',
        'Infinitive verb concentration',
        'Infinitive verb position SD',
        'Infrequent word avg position',
        'Infrequent word burstiness',
        'Infrequent word concentration',
        'Infrequent word position SD',
        'Interjection type-token ratio',
        'Letter entropy',
        'Lexical item avg position',
        'Lexical item burstiness',
        'Lexical item concentration',
        'Lexical item position SD',
        'Lexical item type count',
        'Lexical item type-token ratio',
        'Lexical verb concentration',
        'Lexical verb type count',
        'Lexical verb type-token ratio',
        'Moving average type-token ratio',
        'Noun avg position',
        'Noun burstiness',
        'Noun concentration',
        'Noun position SD',
        'Noun type count',
        'Noun type-token ratio',
        'Numeral avg position',
        'Numeral burstiness',
        'Numeral concentration',
        'Numeral position SD',
        'Numeral type count',
        'Numeral type-token ratio',
        'Particle avg position',
        'Particle burstiness',
        'Particle concentration',
        'Particle position SD',
        'Particle type count',
        'Particle type-token ratio',
        'Past tense avg position',
        'Past tense burstiness',
        'Past tense concentration',
        'Past tense position SD',
        'Personal pronoun avg position',
        'Personal pronoun burstiness',
        'Personal pronoun concentration',
        'Personal pronoun position SD',
        'Plural word avg position',
        'Plural word burstiness',
        'Plural word concentration',
        'Plural word position SD',
        'Present tense concentration',
        'Pronoun avg position',
        'Pronoun burstiness',
        'Pronoun concentration',
        'Pronoun position SD',
        'Pronoun type count',
        'Pronoun type-token ratio',
        'Proper noun avg position',
        'Proper noun burstiness',
        'Proper noun concentration',
        'Proper noun position SD',
        'Proper noun type count',
        'Proper noun type-token ratio',
        'Second person pronoun avg position',
        'Second person pronoun burstiness',
        'Second person pronoun concentration',
        'Second person pronoun position SD',
        'Singular word avg position',
        'Singular word burstiness',
        'Singular word concentration',
        'Singular word position SD',
        'Third person pronoun avg position',
        'Third person pronoun burstiness',
        'Third person pronoun concentration',
        'Third person pronoun position SD',
        'Type count',
        'Type-token ratio',
        'Verb avg position',
        'Verb burstiness',
        'Verb concentration',
        'Verb position SD',
        'Verb type count',
        'Verb type-token ratio',
        'Word entropy',
        'Zipf goodness of fit',
        'Zipf steepness of curve'
    })

    # Keys added internally to feat dicts for cascade arithmetic; excluded from output rows.
    INTERNAL_KEYS: frozenset = frozenset({
        'Conjunction count',
        'Determiner count',
        'Grammatical item count',
        'Interjection count',
        'Lexical verb count',
        'Present tense count',
        'Token count'
    })

    # =========================================================================
    # SKIP SETS: keys excluded from sentence / paragraph summarisation
    # =========================================================================
    SKIP_AT_SENT_LEVEL: set = {
        # Internal cascade-arithmetic keys – never appear in segment summaries
        "Token count", "CCONJ count", "SCONJ count",
        "Moving average type-token ratio",
        "Honoré's statistic",
        "Sentence count",
        "Zipf steepness of curve",
        "Zipf goodness of fit",
        # Burstiness measures are undefined at sentence level (expected list has only Doc + Par)
        "Hapax legomena burstiness",
        "Adjective burstiness",
        "Adverb burstiness",
        "Interjection burstiness",
        "Lexical verb burstiness",
        "Noun burstiness",
        "Proper noun burstiness",
        "Adposition burstiness",
        "Auxiliary burstiness",
        "Determiner burstiness",
        "Numeral burstiness",
        "Particle burstiness",
        "Pronoun burstiness",
        "Lexical item burstiness",
        "Grammatical item burstiness",
        "Verb burstiness",
        "Conjunction burstiness",
        "Personal pronoun burstiness",
        "First person pronoun burstiness",
        "Second person pronoun burstiness",
        "Third person pronoun burstiness",
        "Interrogative burstiness",
        "Demonstrative burstiness",
        "Singular word burstiness",
        "Plural word burstiness",
        "Indefinite word burstiness",
        "Definite word burstiness",
        "Finite verb burstiness",
        "Infinitive verb burstiness",
        "Verbal adjective burstiness",
        "Past tense burstiness",
        "Present tense burstiness",
        "Passive voice burstiness",
        "Frequent word burstiness",
        "Infrequent word burstiness",
        "Unknown word burstiness",
    }
    SKIP_AT_PAR_LEVEL: set = {
        # Internal cascade-arithmetic keys – never appear in segment summaries
        "Token count", "CCONJ count", "SCONJ count",
        "Zipf steepness of curve",
        "Zipf goodness of fit",
    }

    # =========================================================================
    # STATISTICAL HELPER
    # =========================================================================
    def _summarize(self, list_of_dicts: list, level_prefix: str, skip_keys: set = None) -> dict:
        """Aggregate a list of per-segment feature dicts into Avg/SD/Max/Min entries.

        Parameters
        ----------
        list_of_dicts : list[dict]
            One dict per segment (paragraph or sentence) as returned by
            ``_extract_measures``.
        level_prefix : str
            The infix label inserted into the output key, e.g. ``"Par"`` or
            ``"Sent"``.  Output keys look like ``"Word count (Par Avg)"``.
        skip_keys : set, optional
            Keys to exclude from summarisation entirely (e.g. measures that are
            meaningless or undefined at a given granularity level).
        """
        if not list_of_dicts:
            return {}
        skip_keys = skip_keys or set()
        aggregated: dict[str, list] = defaultdict(list)
        for d in list_of_dicts:
            for k, v in d.items():
                if k not in skip_keys:
                    aggregated[k].append(float(v) if v is not None else np.nan)
        result: dict = {}
        for k, values in aggregated.items():
            arr = np.array(values, dtype=float)
            result[f"{k} ({level_prefix} Avg)"] = float(np.nanmean(arr))
            result[f"{k} ({level_prefix} SD)"]  = float(np.nanstd(arr, ddof=1)) if len(arr) > 1 else 0.0
            result[f"{k} ({level_prefix} Max)"] = float(np.nanmax(arr))
            result[f"{k} ({level_prefix} Min)"] = float(np.nanmin(arr))
        return result

    # =========================================================================
    # BOTTOM-UP AGGREGATOR
    # =========================================================================
    def _aggregate_to_one(self, feat_dicts: list) -> dict:
        """Collapse a list of sentence-level feature dicts into one representative dict.

        This is the core of the bottom-up verification architecture.  Every
        metric is derived from sentence-level data using the most exact strategy
        available:

        1. **Additive counts** — summed directly (word counts, PoS counts, …).
        2. **Derived scalars** — computed from summed counts (``Word length``,
           ``Sentence length``).
        3. **Incidences** — recomputed as ``sum(count) / sum(denominator) × 1000``
           so the denominator is always the true total, not an average of averages.
        4. **Ratios** — recomputed as ``sum(numerator_count) / sum(denominator_count)``
           (exact; avoids Jensen's-inequality bias).
        5. **Mean keys** — unweighted mean across segments (acceptable for
           measures without a natural additive denominator, e.g. Zipf frequency).
        6. **Non-cascadable keys** — set to ``0.0`` as a placeholder; callers
           must overwrite them from the corresponding full-doc / full-paragraph
           ``_extract_measures`` call before using the result.
        """
        if not feat_dicts:
            return {}

        def _safe_div(n, d, mult=1.0):
            return (n / d * mult) if d != 0 else 0.0

        result: dict = {}

        # 1. Sum additive counts
        for key in self.ADDITIVE_COUNT_KEYS:
            result[key] = sum(d.get(key, 0) for d in feat_dicts)

        total_words  = result.get('Word count',    0) or 1
        total_sents  = result.get('Sentence count',0) or 1
        total_letters = result.get('Letter count', 0)
        total_tokens  = result.get('Token count',  0) or 1

        # 2. Derived scalar metrics from additive counts
        result['Word length']     = _safe_div(total_letters, total_words)
        result['Sentence length'] = _safe_div(total_words, total_sents)

        # 2b. Bottom-up weighted aggregation for POS/item length measures.
        # This prevents average-of-averages bias by weighting each segment
        # length mean by its corresponding category count.
        LENGTH_TO_COUNT_MAP = {
            'Adjective length': 'Adjective count',
            'Adverb length': 'Adverb count',
            'Interjection length': 'Interjection count',
            'Lexical verb length': 'Lexical verb count',
            'Noun length': 'Noun count',
            'Proper noun length': 'Proper noun count',
            'Adposition length': 'Adposition count',
            'Auxiliary length': 'Auxiliary count',
            'Determiner length': 'Determiner count',
            'Numeral length': 'Numeral count',
            'Particle length': 'Particle count',
            'Pronoun length': 'Pronoun count',
            'Lexical item length': 'Lexical item count',
            'Grammatical item length': 'Grammatical item count',
            'Verb length': 'Verb count',
            'Conjunction length': 'Conjunction count',
        }

        for length_key, count_key in LENGTH_TO_COUNT_MAP.items():
            denom = sum(d.get(count_key, 0) for d in feat_dicts)
            numer = sum((d.get(length_key, 0.0) or 0.0) * d.get(count_key, 0) for d in feat_dicts)
            result[length_key] = _safe_div(numer, denom)

        # 3. Incidences: sum(count) / sum(denominator) × 1000
        for inc_key, (cnt_key, denom_key) in self.INCIDENCE_TO_COUNT_MAP.items():
            cnt   = sum(d.get(cnt_key,  0) for d in feat_dicts)
            denom = sum(d.get(denom_key,0) for d in feat_dicts)
            result[inc_key] = _safe_div(cnt, denom, 1000.0)

        # 4. Ratios: sum(numerator_count) / sum(denominator_count)
        for ratio_key, (num_key, denom_key) in self.RATIO_PAIRS_MAP.items():
            num   = sum(d.get(num_key,  0) for d in feat_dicts)
            denom = sum(d.get(denom_key,0) for d in feat_dicts)
            result[ratio_key] = _safe_div(num, denom)

        # 5. Simple-mean keys
        for key in self.MEAN_KEYS:
            vals = [d[key] for d in feat_dicts if key in d and d[key] is not None]
            result[key] = float(np.mean(vals)) if vals else 0.0

        # 6. Non-cascadable: zero placeholder (caller overwrites from full extraction)
        for key in self.NON_CASCADABLE_KEYS:
            result[key] = 0.0

        return result

    # =========================================================================
    # OVERLAP HELPER: single pair
    # =========================================================================
    def _calc_overlap(self, doc_a, doc_b) -> dict:
        """Return overlap / distance metrics between two spaCy Docs (or Spans).

        All 13 metrics are returned even when one doc is empty (values default
        to 0.0 so downstream aggregation remains numerically stable).
        """
        def _words(d):
            return [t for t in d if t.pos_ not in ('PUNCT', 'SYM', 'X')]

        wa = _words(doc_a)
        wb = _words(doc_b)

        # --- word sets ---
        sa = set(t.text for t in wa)
        sb = set(t.text for t in wb)
        # --- lemma sets ---
        la = set(t.lemma_ for t in wa if t.lemma_)
        lb = set(t.lemma_ for t in wb if t.lemma_)
        # --- PoS sequences (Counter for multiset overlap) ---
        pa = [t.pos_ for t in wa]
        pb = [t.pos_ for t in wb]
        ca, cb = Counter(pa), Counter(pb)
        # --- morphological feature multisets ---
        def _feats(tokens):
            feats = []
            for t in tokens:
                ms = str(t.morph)
                if ms:
                    feats.extend(ms.split('|'))
            return feats
        fa, fb = _feats(wa), _feats(wb)
        cfa, cfb = Counter(fa), Counter(fb)

        out: dict[str, float] = {}

        def _normalized_lev_distance(a, b):
            """Return normalized Levenshtein distance in [0, 1] with explicit empty handling.

            - both empty -> 0.0
            - one empty  -> 1.0
            - otherwise  -> editdistance / max(len(a), len(b))
            """
            len_a = len(a)
            len_b = len(b)
            if len_a == 0 and len_b == 0:
                return 0.0
            if len_a == 0 or len_b == 0:
                return 1.0
            return self._levenshtein_distance(a, b) / max(len_a, len_b)

        # word overlap
        if sa and sb:
            woc = len(sa & sb)
            wor = woc / min(len(sa), len(sb))
        else:
            woc, wor = 0.0, 0.0
        out['Word overlap count'] = float(woc)
        out['Word overlap ratio'] = float(wor)

        # lemma overlap
        if la and lb:
            loc = len(la & lb)
            lor = loc / min(len(la), len(lb))
        else:
            loc, lor = 0.0, 0.0
        out['Lemma overlap count'] = float(loc)
        out['Lemma overlap ratio'] = float(lor)

        # PoS overlap (multiset)
        if pa and pb:
            poc = sum(min(ca[t], cb[t]) for t in ca if t in cb)
            por = poc / min(len(pa), len(pb))
        else:
            poc, por = 0.0, 0.0
        out['PoS overlap count'] = float(poc)
        out['PoS overlap ratio'] = float(por)

        # Feature overlap (multiset)
        if fa and fb:
            foc = sum(min(cfa[f], cfb[f]) for f in cfa if f in cfb)
            fovr = foc / min(len(fa), len(fb))
        else:
            foc, fovr = 0.0, 0.0
        out['Feature overlap count'] = float(foc)
        out['Feature overlap ratio'] = float(fovr)

        # Levenshtein character distance (normalised)
        ta_text = doc_a.text; tb_text = doc_b.text
        out['Levenshtein character dist.'] = _normalized_lev_distance(ta_text, tb_text)

        # Levenshtein word distance (normalised, non-punct word lists)
        wa_txt = [t.text for t in wa]; wb_txt = [t.text for t in wb]
        out['Levenshtein word dist.'] = _normalized_lev_distance(wa_txt, wb_txt)

        # Levenshtein lemma distance (normalised)
        la_list = [t.lemma_ for t in wa if t.lemma_]
        lb_list = [t.lemma_ for t in wb if t.lemma_]
        out['Levenshtein lemma dist.'] = _normalized_lev_distance(la_list, lb_list)

        # Levenshtein PoS distance (normalised)
        out['Levenshtein PoS dist.'] = _normalized_lev_distance(pa, pb)

        # Cosine distance via FastText centroids
        c1 = self._get_sentence_centroid([t.text for t in doc_a])
        c2 = self._get_sentence_centroid([t.text for t in doc_b])
        if (c1 is not None and c2 is not None
                and np.linalg.norm(c1) > 0 and np.linalg.norm(c2) > 0):
            out['Cosine dist.'] = float(cosine(c1, c2))
        else:
            out['Cosine dist.'] = 0.0

        return out

    # =========================================================================
    # CROSS-LEVEL OVERLAP BUILDER
    # =========================================================================
    def _build_sent_to_par_map(self, raw_text: str, filtered_sentences, par_docs) -> list:
        """Return a list mapping each filtered sentence index to its parent paragraph index.

        Uses character offsets: each paragraph's start position in *raw_text* is
        compared against each sentence's ``start_char`` in the original document.
        
        Parameters
        ----------
        raw_text : str
            Original raw text
        filtered_sentences : list of spacy.tokens.Span
            Pre-filtered sentences (no empty/whitespace-only sentences)
        par_docs : list of spacy.tokens.Doc
            Paragraph documents
        """
        n_pars = len(par_docs)
        if n_pars <= 1:
            return [0] * len(filtered_sentences)

        # Find the character start of each paragraph in raw_text
        par_starts: list[int] = []
        search_start = 0
        for pd_doc in par_docs:
            par_text = pd_doc.text.strip()
            idx = raw_text.find(par_text, search_start)
            if idx == -1:
                idx = search_start
            par_starts.append(idx)
            search_start = idx + max(len(par_text), 1)

        # Assign each filtered sentence to a paragraph
        mapping: list[int] = []
        for sent in filtered_sentences:
            sc = sent.start_char
            par_idx = 0
            for pi, ps in enumerate(par_starts):
                if sc >= ps:
                    par_idx = pi
                else:
                    break
            mapping.append(par_idx)
        return mapping

    def _calc_cross_level_overlaps(self, full_doc, par_docs: list, sent_docs: list,
                                    sent_to_par: list, lang_code: str) -> dict:
        """Calculate overlap / distance metrics for all 5 cross-level pair types.

        Each pair type produces Avg / SD / Max / Min entries for every metric
        returned by ``_calc_overlap``.  The resulting flat dict is merged directly
        into the per-document row.
        """
        pair_specs: list[tuple[str, list]] = []
        overlap_metric_keys = [
            'Word overlap count',
            'Word overlap ratio',
            'Lemma overlap count',
            'Lemma overlap ratio',
            'PoS overlap count',
            'PoS overlap ratio',
            'Feature overlap count',
            'Feature overlap ratio',
            'Levenshtein character dist.',
            'Levenshtein word dist.',
            'Levenshtein lemma dist.',
            'Levenshtein PoS dist.',
            'Cosine dist.',
        ]

        # Par-Doc
        if par_docs:
            pair_specs.append(('Par-Doc', [(pd, full_doc) for pd in par_docs]))

        # Sent-Doc
        if sent_docs:
            pair_specs.append(('Sent-Doc', [(sd, full_doc) for sd in sent_docs]))

        # Par-Par (adjacent)
        if len(par_docs) >= 2:
            pair_specs.append(('Par-Par', list(zip(par_docs[:-1], par_docs[1:]))))

        # Sent-Par
        if sent_docs and par_docs:
            pair_specs.append(('Sent-Par',
                                [(sent_docs[i], par_docs[sent_to_par[i]])
                                 for i in range(len(sent_docs))
                                 if i < len(sent_to_par)]))

        # Sent-Sent (adjacent)
        if len(sent_docs) >= 2:
            pair_specs.append(('Sent-Sent', list(zip(sent_docs[:-1], sent_docs[1:]))))

        result: dict = {}
        for label, pairs in pair_specs:
            if not pairs:
                continue
            overlap_dicts = [self._calc_overlap(a, b) for a, b in pairs]
            metric_keys = overlap_dicts[0].keys()
            for mk in metric_keys:
                vals = np.array([d[mk] for d in overlap_dicts], dtype=float)
                result[f"{mk} ({label} Avg)"] = float(np.nanmean(vals))
                result[f"{mk} ({label} SD)"]  = float(np.nanstd(vals, ddof=1)) if len(vals) > 1 else 0.0
                result[f"{mk} ({label} Max)"] = float(np.nanmax(vals))
                result[f"{mk} ({label} Min)"] = float(np.nanmin(vals))

        # Schema stabilization: always include Par-Par keys, even when no adjacent
        # paragraph pair exists (e.g., 0 or 1 paragraph in the document).
        if len(par_docs) < 2:
            for mk in overlap_metric_keys:
                result.setdefault(f"{mk} (Par-Par Avg)", 0.0)
                result.setdefault(f"{mk} (Par-Par SD)", 0.0)
                result.setdefault(f"{mk} (Par-Par Max)", 0.0)
                result.setdefault(f"{mk} (Par-Par Min)", 0.0)
        return result

    # =========================================================================
    # CORE: Measure Extraction
    # =========================================================================
    def _extract_measures(self, doc, lang_code: str) -> dict:
        """Extract a flat dictionary of linguistic features from a spaCy Doc.

        This is a pure feature extractor: it accepts any granularity (full
        document, paragraph doc, or ``sent.as_doc()``), performs no model
        loading, and returns bare key names with no level suffixes.
        """
        stats = {}
        
        # Defensive validation: skip empty documents
        if not doc.text or not doc.text.strip():
            # Return zero-valued dictionary for empty documents
            return self._get_empty_metrics_dict()

        # 1. PRE-CALCULATE LISTS FOR SPEED
        # --------------------------------
        
        # Standard maps (includes punctuation)
        pos_map = {tag: [] for tag in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON', 'PUNCT']}
        feat_map = {k: [] for k in ['Personal pronoun','First person','Second person','Third person','Interrogative','Demonstrative','Singular','Plural','Indefinite','Definite','Finite','Infinitive','Verbal adjective','Past','Present','Passive']}

        # Lowercased, non-punct maps
        pos_map_lower_non_punct = {tag: [] for tag in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON']}
        feat_map_lower_non_punct = {k: [] for k in ['Personal pronoun','First person','Second person','Third person','Interrogative','Demonstrative','Singular','Plural','Indefinite','Definite','Finite','Infinitive','Verbal adjective','Past','Present','Passive']}

        # Metrics Trackers
        tokens = []
        lower_non_punct_tokens = []
        lower_non_punct_tags = []
        zipf_scores = []
        word_lengths = []
        total_words = 0
        total_chars = 0
        
        global_pos = 0      # Tracks 1-based index including punctuation
        non_punct_pos = 0   # Tracks 1-based index excluding punctuation
        
        # SINGLE UNIFIED PASS OVER THE DOCUMENT
        for token in doc:
            word_pos_ = token.pos_
            word_lower = token.text.lower()
            morph = token.morph

            # --- A. Global Tracking ---
            global_pos += 1
            tokens.append(token.text)
            
            if word_pos_ in pos_map:
                pos_map[word_pos_].append(global_pos)
            
            for feat_name in feat_map.keys():
                if self._check_feature_optimized(word_pos_, morph, feat_name):
                    feat_map[feat_name].append(global_pos)

            # --- B. Non-Punctuation Tracking ---
            if word_pos_ not in ('PUNCT', 'SYM', 'X'):
                non_punct_pos += 1
                total_words += 1
                total_chars += len(token.text)
                word_lengths.append(len(token.text))
                
                lower_non_punct_tokens.append(word_lower)
                lower_non_punct_tags.append(word_pos_)
                
                if word_pos_ in pos_map_lower_non_punct:
                    pos_map_lower_non_punct[word_pos_].append(non_punct_pos)
                    
                for feat_name in feat_map_lower_non_punct.keys():
                    if self._check_feature_optimized(word_pos_, morph, feat_name):
                        feat_map_lower_non_punct[feat_name].append(non_punct_pos)





    
        # --- C. Zipf & Frequencies ---
        # Compute Zipf scores using lower_non_punct_tokens (already lowercased, non-punct)
        for token in lower_non_punct_tokens:
            z = zipf_frequency(token, lang_code)
            if z >= 3.0: # Threshold: 1 per million
                zipf_scores.append(z)

        doc_len = total_words if total_words > 0 else 1

        # 2. CALCULATE CATEGORIES
        # -----------------------
        
        # --- Group 1: General Counts & Descriptive ---
        stats['Word count'] = total_words
        stats['Letter count'] = total_chars
        sents = list(doc.sents)
        stats['Sentence count'] = len(sents)
        # Exclude punctuation tokens from type counts and TRR calculations
        stats['Type count'] = len(set(lower_non_punct_tokens))
        stats['Type-token ratio'] = len(set(lower_non_punct_tokens)) / doc_len
        
        # Average word length
        stats['Word length'] = np.mean(word_lengths) if word_lengths else 0
        
        # Average sentence length
        stats['Sentence length'] = total_words / len(sents) if len(sents) > 0 else 0
        
        # --- Group 3: PoS Counts & Incidence (Per 1000 words) ---
        # Helper to safely get count
        def get_cnt(tags):
            if isinstance(tags, str): tags = {tags}
            return sum(len(pos_map_lower_non_punct.get(t, [])) for t in tags)

        # Standard Tags
        for tag in pos_map_lower_non_punct:
            if tag in ('CCONJ', 'SCONJ'):
                continue
            label = self.POS_LABELS.get(tag, tag)
            cnt = len(pos_map_lower_non_punct[tag])
            stats[f'{label} count'] = cnt
            stats[f'{label} incidence'] = (cnt / doc_len) * 1000
            # Type count for this PoS
            pos_tokens = [lower_non_punct_tokens[i-1] for i in pos_map_lower_non_punct[tag] if i > 0 and i <= len(lower_non_punct_tokens)]
            stats[f'{label} type count'] = len(set(pos_tokens))
            # Burstiness for this PoS
            stats[f'{label} burstiness'] = self._calc_burstiness(pos_map_lower_non_punct[tag], doc_len)

        # Punctuation measures (tracked separately in pos_map)
        punct_count = len(pos_map.get('PUNCT', []))
        stats['Punctuation count'] = punct_count
        stats['Punctuation incidence'] = (punct_count / len(tokens)) * 1000 if doc_len > 0 else 0

        # Internal keys used by _aggregate_to_one for cascade arithmetic
        stats['Token count'] = len(tokens)

        # Combined Groups (Lingualyzer Specifics)
        for name, tag_set in self.TAG_GROUPS.items():
            cnt = get_cnt(tag_set)
            stats[f'{name} count'] = cnt
            stats[f'{name} incidence'] = (cnt / doc_len) * 1000
            # Type count for combined group (distinct words with these PoS tags)
            group_positions = []
            for t in tag_set:
                group_positions.extend(pos_map_lower_non_punct.get(t, []))
            group_positions_sorted = sorted(group_positions)
            group_tokens = [lower_non_punct_tokens[i-1] for i in group_positions if i > 0 and i <= len(lower_non_punct_tokens)]
            stats[f'{name} type count'] = len(set(group_tokens))
            # Burstiness for combined group
            stats[f'{name} burstiness'] = self._calc_burstiness(group_positions_sorted, doc_len)


        # --- Group 4: Morphological Features ---
        for feat, positions in feat_map_lower_non_punct.items():
            label = self.FEAT_LABELS.get(feat, feat)
            cnt = len(positions)
            stats[f'{label} count'] = cnt
            stats[f'{label} incidence'] = (cnt / doc_len) * 1000
            # Burstiness
            stats[f'{label} burstiness'] = self._calc_burstiness(positions, doc_len)

        # --- Group 5: Lexical Diversity ---
        lex_div_stats = self._calc_lexical_diversity(lower_non_punct_tokens, pos_map_lower_non_punct, doc_len)
        stats.update(lex_div_stats)
        
        # --- Group 6: Word Lengths (Per-PoS) ---
        word_len_stats = self._calc_word_lengths(doc,  pos_map_lower_non_punct, lower_non_punct_tokens)
        stats.update(word_len_stats)
        
        # --- Group 7: Complexity (Entropy & Zipf) ---
        if zipf_scores:
            stats['Frequent word count'] = sum(1 for z in zipf_scores if z > 6.0)
        else:
            stats['Frequent word count'] = 0

        # Zipf variants
        zipf_var_stats = self._calc_zipf_variants(zipf_scores, lower_non_punct_tokens, lang_code, doc_len)
        stats.update(zipf_var_stats)
        
        # Word Entropy
        word_counts = Counter(lower_non_punct_tokens)
        probs = [freq / doc_len for freq in word_counts.values()]
        stats['Word entropy'] = entropy(probs, base=2)
        
        # Letter Entropy (Bentz et al., 2017)
        letters = [c.lower() for c in ''.join(lower_non_punct_tokens) if c.isalpha()]
        if letters:
            letter_counts = Counter(letters)
            letter_probs = [freq / len(letters) for freq in letter_counts.values()]
            stats['Letter entropy'] = entropy(letter_probs, base=2)
        else:
            stats['Letter entropy'] = 0

        # --- Group 8: Morphological Complexity ---
        morph_stats = self._calc_morphological_complexity(doc)
        stats.update(morph_stats)
        
        # --- Group 9: Ratios (60+ comparative ratios) ---
        ratio_stats = self._calc_ratios(pos_map_lower_non_punct, feat_map_lower_non_punct)
        stats.update(ratio_stats)

        # --- Group 10: Distributional Measures ---
        dist_stats = self._calc_distributional_measures(pos_map_lower_non_punct, feat_map_lower_non_punct, doc_len, lang_code, lower_non_punct_tokens)
        stats.update(dist_stats)

        return stats
        
    def _get_empty_metrics_dict(self) -> dict:
        """Return a dictionary of metrics with zero/default values for empty documents."""
        empty_metrics = {
            'Word count': 0,
            'Letter count': 0,
            'Sentence count': 0,
            'Type count': 0,
            'Type-token ratio': 0.0,
            'Word length': 0.0,
            'Sentence length': 0.0,
            'Punctuation count': 0,
            'Punctuation incidence': 0.0,
            'Token count': 0,
            'CCONJ count': 0,
            'SCONJ count': 0,
        }
        
        # Add zero counts for all POS tags
        for tag in ['ADJ', 'ADV', 'INTJ', 'VERB', 'NOUN', 'PROPN', 'ADP', 'AUX', 'DET', 'NUM', 'PART', 'PRON']:
            label = self.POS_LABELS.get(tag, tag)
            empty_metrics[f'{label} count'] = 0
            empty_metrics[f'{label} incidence'] = 0.0
            
        # Add zero counts for tag groups
        for group_name in self.TAG_GROUPS.keys():
            empty_metrics[f'{group_name} count'] = 0
            empty_metrics[f'{group_name} incidence'] = 0.0
            
        # Add zero counts for morphological features
        for feat_name in self.FEAT_LABELS.keys():
            label = self.FEAT_LABELS[feat_name]
            empty_metrics[f'{label} count'] = 0
            empty_metrics[f'{label} incidence'] = 0.0
            
        return empty_metrics

    # =========================================================================
    # PUBLIC PROFILING API (two-mode architecture)
    # =========================================================================

    def _run_census(
        self,
        cleaned_texts: list,
        original_index,
        conf_threshold: float,
    ) -> tuple:
        """Run FastText LID on cleaned_texts and return (lang_series, conf_series).

        The confidence threshold is NOT applied here — callers apply it to
        allow each mode to handle filtering differently.
        """
        n = len(cleaned_texts)
        langs = np.empty(n, dtype=object)
        confs = np.zeros(n, dtype=float)
        LID_CHUNK_SIZE = 5_000
        for start in tqdm(range(0, n, LID_CHUNK_SIZE), desc="Census Progress"):
            batch = cleaned_texts[start: start + LID_CHUNK_SIZE]
            predictions, probs = self.lid_model.predict(batch)
            langs[start: start + len(batch)] = [
                p[0].replace('__label__', '') for p in predictions
            ]
            confs[start: start + len(batch)] = [float(p[0]) for p in probs]
        return (
            pd.Series(langs, index=original_index),
            pd.Series(confs, index=original_index),
        )

    def _profile_language_group(
        self,
        lang: str,
        subset_txt: list,
    ):
        """Run the full three-level spaCy profiling pipeline for one language.

        Parameters
        ----------
        lang : str
            ISO 639-1 code for the language group.
        subset_txt : list[str]
            Pre-sampled raw texts (≤ 100 items). Caller is responsible for
            sampling and SUPPORTED_SPACY_LANGS filtering.

        Returns
        -------
        dict | None
            Mean feature dict (ready to become a DataFrame column), or None
            on failure or empty output.
        """
        if not subset_txt:
            return None

        _logger = logging.getLogger(__name__)
        all_rows: list = []

        try:
            nlp = self._make_pipeline(lang)

            # Load FastText word-vector model once per language (for cosine distance)
            if self.fasttext_model is None or self.current_fasttext_lang != lang:
                print(f"   Loading FastText model for '{lang}'...")
                self._load_fasttext_model(lang)
                self.current_fasttext_lang = lang

            # ── Batch paragraph processing ──────────────────────────────
            all_par_texts: list = []
            doc_par_indices: list = []
            for raw in subset_txt:
                par_texts = [p.strip() for p in re.split(r'\n\s*\n', raw.strip()) if p.strip()]
                if not par_texts:
                    par_texts = [raw.strip() or " "]
                start_idx = len(all_par_texts)
                all_par_texts.extend(par_texts)
                doc_par_indices.append(list(range(start_idx, start_idx + len(par_texts))))

            print(f"   Processing {len(subset_txt)} docs / {len(all_par_texts)} paragraphs...")
            all_par_docs = list(nlp.pipe(all_par_texts))

            # ── Full-document pass ─────────────────────────────────────
            full_docs = list(nlp.pipe(subset_txt))

            for doc_idx, full_doc in enumerate(tqdm(full_docs, desc=f"Processing {lang}")):
                raw_text = subset_txt[doc_idx]
                par_docs = [all_par_docs[i] for i in doc_par_indices[doc_idx]]
                n_pars   = len(par_docs)

                sents_all = self._filter_valid_sentences(full_doc.sents)
                n_sents   = len(sents_all)

                # ── STEP 1: Sentences (atomic unit) ──────────────────────────────
                sent_docs       = [sent.as_doc() for sent in sents_all]
                sent_feats_list = [self._extract_measures(sd, lang) for sd in sent_docs]

                # ── STEP 2: Sentence-level summary ───────────────────────────────
                row: dict = {}
                row.update(self._summarize(sent_feats_list, 'Sent', self.SKIP_AT_SENT_LEVEL))

                # ── STEP 3: Map sentences → paragraphs ───────────────────────────
                sent_to_par = self._build_sent_to_par_map(raw_text, sents_all, par_docs)

                # ── STEP 4: Paragraph level ──────────────────────────────────────
                par_feats_list: list = []
                for par_idx, par_doc in enumerate(par_docs):
                    sents_in_par = [sent_feats_list[i]
                                    for i, pi in enumerate(sent_to_par)
                                    if pi == par_idx]
                    par_supplement = self._extract_measures(par_doc, lang)
                    if sents_in_par:
                        par_cascade = self._aggregate_to_one(sents_in_par)
                        par_feats   = {**par_cascade,
                                       **{k: par_supplement[k]
                                          for k in self.NON_CASCADABLE_KEYS
                                          if k in par_supplement}}
                    else:
                        par_feats = par_supplement
                    par_feats_list.append(par_feats)

                row.update(self._summarize(par_feats_list, 'Par', self.SKIP_AT_PAR_LEVEL))

                par_sent_counts = [f.get('Sentence count', 0) for f in par_feats_list]
                if par_sent_counts:
                    arr = np.array(par_sent_counts, dtype=float)
                    row['Paragraph length (Par Avg)'] = float(np.nanmean(arr))
                    row['Paragraph length (Par SD)']  = float(np.nanstd(arr, ddof=1)) if len(arr) > 1 else 0.0
                    row['Paragraph length (Par Max)'] = float(np.nanmax(arr))
                    row['Paragraph length (Par Min)'] = float(np.nanmin(arr))

                # ── STEP 5: Document level ───────────────────────────────────────
                doc_supplement = self._extract_measures(full_doc, lang)
                doc_cascade    = self._aggregate_to_one(sent_feats_list)
                doc_feats      = {**doc_cascade,
                                  **{k: doc_supplement[k]
                                     for k in self.NON_CASCADABLE_KEYS
                                     if k in doc_supplement}}

                for k, v in doc_feats.items():
                    if k not in self.INTERNAL_KEYS:
                        row[f"{k} (Doc)"] = v

                row['Paragraph count (Doc)']  = n_pars
                row['Paragraph length (Doc)'] = n_sents / n_pars if n_pars > 0 else 0.0

                # ── STEP 6: Cross-level overlaps ─────────────────────────────────
                row.update(self._calc_cross_level_overlaps(
                    full_doc, par_docs, sent_docs, sent_to_par, lang
                ))

                all_rows.append(row)

        except Exception as e:
            import traceback
            _logger.error("Profiling failed for '%s': %s", lang, e)
            traceback.print_exc()
            return None

        if not all_rows:
            _logger.warning("No rows produced for '%s'.", lang)
            return None

        return pd.DataFrame(all_rows).mean().round(4).to_dict()

    def _profile_building_mode(self, parquet_dir: Path) -> pd.DataFrame:
        """Path A — Ground-Truth Directed Profiling.

        Reads all *.parquet files in ``parquet_dir``, extracts the ISO 639-1
        code from each filename stem (pattern ``^([a-z]{2,3})_``), pools
        texts per language, stochastically shuffles, samples ≤ 100, and
        profiles each language using the shared spaCy pipeline.

        The returned DataFrame has ``attrs["source_environment"]`` set to
        ``parquet_dir.name`` (NOT preserved by pandas concat/merge).
        """
        lang_texts: dict = {}
        _logger = logging.getLogger(__name__)

        for f in sorted(parquet_dir.glob("*.parquet")):
            m = re.match(r'^([a-z]{2,3})_', f.stem)
            if not m:
                _logger.warning("Skipping '%s': cannot extract ISO code.", f.name)
                continue
            lang = m.group(1)
            if lang not in self.SPACY_MODELS:
                _logger.warning("Skipping '%s': no spaCy model for '%s'.", f.name, lang)
                continue
            try:
                df_file = pd.read_parquet(f)
                if "text" not in df_file.columns:
                    _logger.warning("Skipping '%s': no 'text' column.", f.name)
                    continue
                texts = df_file["text"].dropna().astype(str).tolist()
                lang_texts.setdefault(lang, []).extend(texts)
            except Exception as exc:
                _logger.warning("Could not read '%s': %s", f.name, exc)

        if not lang_texts:
            _logger.warning("No usable parquet files found in '%s'.", parquet_dir)
            return pd.DataFrame()

        final_report: dict = {}
        MAX_SAMPLES = 100
        for lang, texts in lang_texts.items():
            random.shuffle(texts)          # stochastic, no fixed seed
            subset_txt = texts[:MAX_SAMPLES]
            print(f"📊 Building '{lang}' ({len(subset_txt)}/{len(texts)} texts)...")
            result = self._profile_language_group(lang, subset_txt)
            if result is not None:
                final_report[lang] = result

        df = pd.DataFrame(final_report)
        df.attrs["source_environment"] = parquet_dir.name
        return df

    def _profile_user_mode(self, text_series: pd.Series) -> pd.DataFrame:
        """Path B — Diagnostic Discovery Profiling.

        Takes a stochastic snapshot of up to 10 000 rows, runs FastText LID
        with CONF_THRESHOLD = 0.0 (profile the data *as-is*, noise and all),
        discovers language candidates, then profiles ≤ 100 samples per
        discovered language.
        """
        _logger = logging.getLogger(__name__)
        clean = text_series.dropna().astype(str)
        SNAPSHOT_SIZE = 10_000

        print(f"🔍 Phase 1: Snapshot Census ({min(len(clean), SNAPSHOT_SIZE)} rows)...")
        snapshot = clean.sample(n=min(len(clean), SNAPSHOT_SIZE), random_state=None)
        cleaned_texts = [t.replace('\n', ' ') for t in snapshot.values]

        CONF_THRESHOLD = 0.0          # CRITICAL: profile as-is, no confidence filtering
        lang_series, conf_series = self._run_census(
            cleaned_texts, snapshot.index, conf_threshold=CONF_THRESHOLD
        )
        # All texts pass at threshold 0.0
        mask = conf_series >= CONF_THRESHOLD
        filtered = snapshot[mask]
        grouped = filtered.groupby(lang_series[mask])

        final_report: dict = {}
        MAX_SAMPLES = 100
        for lang, subset in grouped:
            # Map FastText codes to spaCy codes if needed
            spacy_lang = self.FASTTEXT_TO_SPACY.get(lang, lang)
            if spacy_lang not in self.SPACY_MODELS:
                print(f"⏭️  Skipping '{lang}' (unsupported spaCy language).")
                continue
            subset_txt = (
                subset.sample(n=min(len(subset), MAX_SAMPLES), random_state=None)
                .values.tolist()
            )
            print(f"📊 Profiling '{spacy_lang}' ({len(subset_txt)} texts)...")
            result = self._profile_language_group(spacy_lang, subset_txt)
            if result is not None:
                final_report[spacy_lang] = result

        # ── Census-detected language inventory (for the coverage guard) ──────
        # Two DECOUPLED uses of the same lid.176 census:
        #   • Coverage — WHICH languages are present, driving the coverage guard
        #     — is derived only from HIGH-CONFIDENCE detections
        #     (prob ≥ COVERAGE_MIN_CONF), as a fraction of the FULL census.  The
        #     high bar drops lid.176's low-confidence mislabels (e.g. tagging
        #     German text 'als'/Alemannic), which would otherwise inflate the
        #     language set models are vetted against; the fixed full-census
        #     denominator keeps the threshold's effect monotonic.  This detects
        #     languages BEYOND the 24 the profiler can characterise, so a
        #     recommendation is not made blind to languages present in the data.
        #   • Per-language SAMPLING for profiling (the loop above) keeps every
        #     top-1 assignment at confidence 0.0, so the profiled text — and the
        #     resulting fingerprint — reflect the data as-is, noise and all.
        # Consumed opt-in by the recommender (use_detected_coverage=True); by
        # default nothing reads these attrs, so existing behaviour is unchanged.
        COVERAGE_MIN_CONF = 0.50   # a detection counts toward coverage only if this confident
        DETECT_MIN_FRAC   = 0.01   # …and the language must be ≥1% of the full census
        n_census = int(len(conf_series)) or 1
        hi_codes = lang_series[conf_series >= COVERAGE_MIN_CONF].map(
            lambda c: self.FASTTEXT_TO_SPACY.get(c, c)
        )
        detected_counts = {str(code): int(n) for code, n in hi_codes.value_counts().items()}
        detected_languages = frozenset(
            code for code, n in detected_counts.items()
            if n / n_census >= DETECT_MIN_FRAC
        )

        df = pd.DataFrame(final_report)
        df.attrs["detected_languages"] = detected_languages
        df.attrs["detected_language_counts"] = detected_counts
        return df

    def run_profile(
        self,
        mode: str,
        *,
        text_series: pd.Series = None,
        parquet_dir=None,
    ) -> pd.DataFrame:
        """High-level entry point for dataset profiling.

        Parameters
        ----------
        mode : {"building", "user"}
            ``"building"`` — Ground-Truth Directed Profiling (Path A).
                Requires ``parquet_dir``. Extracts language labels from
                Parquet filenames; no FastText census performed.
            ``"user"`` — Diagnostic Discovery Profiling (Path B).
                Requires ``text_series``. Runs a snapshot census at
                CONF_THRESHOLD=0.0 to profile unlabelled user data as-is.
        text_series : pd.Series, optional
            Required for ``mode="user"``.
        parquet_dir : Path or str, optional
            Required for ``mode="building"``. Must be a directory containing
            ``*.parquet`` files named ``{iso}_{id}.parquet``.

        Returns
        -------
        pd.DataFrame
            Rows = linguistic features, columns = ISO 639-1 language codes.
            Both modes produce the same feature schema (S1–S6 + overlaps).
        """
        if mode == "building":
            if parquet_dir is None:
                raise ValueError("'parquet_dir' is required for mode='building'.")
            if text_series is not None:
                raise ValueError(
                    "'text_series' must not be provided for mode='building'. "
                    "Use 'parquet_dir' instead."
                )
            return self._profile_building_mode(Path(parquet_dir))

        elif mode == "user":
            if text_series is None:
                raise ValueError("'text_series' is required for mode='user'.")
            if parquet_dir is not None:
                raise ValueError(
                    "'parquet_dir' must not be provided for mode='user'. "
                    "Use 'text_series' instead."
                )
            return self._profile_user_mode(text_series)

        else:
            raise ValueError(
                f"Unknown mode '{mode}'. Expected 'building' or 'user'."
            )

    def get_multilingual_profile(self, text_series: pd.Series) -> pd.DataFrame:
        """Return a multilingual feature profile for each language detected in
        ``text_series``.

        .. deprecated::
            Use ``run_profile(mode='user', text_series=text_series)`` directly.
            This wrapper is kept for backward compatibility.
        """
        return self.run_profile("user", text_series=text_series)
