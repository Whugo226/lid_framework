import stanza
import pandas as pd
import numpy as np
from collections import Counter
import logging
import gc 
import torch
import math
from wordfreq import zipf_frequency
from scipy.stats import entropy
from tqdm import tqdm

# Mute Stanza noise
logging.getLogger('stanza').setLevel(logging.WARNING)

class DeepProfiler:
    def __init__(self):
        print("⏳ Initializing DeepProfiler (Lingualyzer Implementation)...")
        self.use_gpu = torch.cuda.is_available()
        
        # Define UD Tag Groups based on Lingualyzer definitions
        self.TAG_GROUPS = {
            'Lexical item': {'ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB'},
            'Grammatical item': {'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'},
            'Verb_All': {'VERB', 'AUX'}, # "Verb count" in Lingualyzer = Verb + Aux
            'Conjunction': {'CCONJ', 'SCONJ'}
        }
        
        # Load Stanza LID
        print("   Loading Stanza LID...")
        try:
            stanza.download(lang="multilingual", processors="langid", verbose=False)
            self.lid_pipeline = stanza.Pipeline(lang="multilingual", processors="langid", verbose=False, use_gpu=self.use_gpu)
        except Exception as e:
            print(f"❌ Error loading LID: {e}")
            raise

    # =========================================================================
    # HELPER: Feature Extraction Logic
    # =========================================================================
    def _check_feature(self, word, feat_name):
        """Checks if a Stanza word has a specific morphological feature."""
        if not word.feats: return False
        features = word.feats.split('|')
        
        # Mapping Lingualyzer definitions to UD v2 Tags
        checks = {
            'Personal pronoun': 'PronType=Prs',
            'First person': 'Person=1',
            'Second person': 'Person=2',
            'Third person': 'Person=3',
            'Interrogative': 'PronType=Int',
            'Demonstrative': 'PronType=Dem',
            'Singular': 'Number=Sing',
            'Plural': 'Number=Plur',
            'Indefinite': 'Definite=Ind',
            'Definite': 'Definite=Def',
            'Finite': 'VerbForm=Fin',
            'Infinitive': 'VerbForm=Inf',
            'Verbal adjective': 'VerbForm=Part', # Participles often treated as verbal adjectives
            'Past': 'Tense=Past',
            'Present': 'Tense=Pres',
            'Passive': 'Voice=Pass'
        }
        
        target = checks.get(feat_name)
        return target in features if target else False

    def _calc_burstiness(self, positions, doc_len):
        """
        Calculates burstiness (clustering) of items.
        Returns: -1 (Periodic) to +1 (Bursty). 0 = Random.
        Using Coefficient of Variation (r-1)/(r+1) approx.
        """
        if len(positions) < 2: return 0.0
        
        # Calculate inter-arrival times (gaps)
        gaps = np.diff(positions)
        if len(gaps) == 0: return 0.0
        
        mean_gap = np.mean(gaps)
        std_gap = np.std(gaps)
        
        if mean_gap == 0: return 0.0
        
        # Coefficient of Variation
        cv = std_gap / mean_gap
        # Burstiness Score (-1 to 1)
        return (cv - 1) / (cv + 1)

    # =========================================================================
    # CORE: Measure Extraction
    # =========================================================================
    def _extract_measures(self, doc, lang_code):
        stats = {}
        
        # 1. PRE-CALCULATE LISTS FOR SPEED
        # --------------------------------
        tokens = []
        pos_map = {tag: [] for tag in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON','PUNCT','SYM','X']}
        feat_map = {k: [] for k in ['Personal pronoun','First person','Second person','Third person','Interrogative','Demonstrative','Singular','Plural','Indefinite','Definite','Finite','Infinitive','Verbal adjective','Past','Present','Passive']}
        
        zipf_scores = []
        word_lengths = []
        
        total_words = 0
        total_chars = 0
        
        for sent_idx, sentence in enumerate(doc.sentences):
            for word_idx, word in enumerate(sentence.words):
                tokens.append(word.text)
                total_words += 1
                total_chars += len(word.text)
                word_lengths.append(len(word.text))
                
                # Store position (0.0 to 1.0) for distributional measures
                # Approximate global position
                global_pos = len(tokens) 
                
                # --- A. PoS Bucketing ---
                if word.upos in pos_map:
                    pos_map[word.upos].append(global_pos)
                    
                # --- B. Feature Bucketing ---
                for feat_name in feat_map.keys():
                    if self._check_feature(word, feat_name):
                        feat_map[feat_name].append(global_pos)
                
                # --- C. Zipf & Frequencies ---
                if word.upos not in ['PUNCT', 'NUM', 'SYM']:
                    z = zipf_frequency(word.text, lang_code)
                    if z >= 3.0: # Threshold: 1 per million
                        zipf_scores.append(z)

        doc_len = total_words if total_words > 0 else 1

        # 2. CALCULATE CATEGORIES
        # -----------------------
        
        # --- Group 1: General Counts & Descriptive ---
        stats['Word count'] = total_words
        stats['Letter count'] = total_chars
        stats['Sentence count'] = len(doc.sentences)
        stats['Type count'] = len(set(tokens))
        stats['Type-token ratio'] = len(set(tokens)) / doc_len
        
        # --- Group 2: PoS Counts & Incidence (Per 1000 words) ---
        # Helper to safely get count
        def get_cnt(tags):
            if isinstance(tags, str): tags = {tags}
            return sum(len(pos_map.get(t, [])) for t in tags)

        # Standard Tags
        for tag in pos_map:
            cnt = len(pos_map[tag])
            stats[f'{tag} count'] = cnt
            stats[f'{tag} incidence'] = (cnt / doc_len) * 1000
            stats[f'{tag} type count'] = len(set(tokens[i-1] for i in pos_map[tag])) # Approx type count

        # Combined Groups (Lingualyzer Specifics)
        for name, tag_set in self.TAG_GROUPS.items():
            cnt = get_cnt(tag_set)
            stats[f'{name} count'] = cnt
            stats[f'{name} incidence'] = (cnt / doc_len) * 1000

        # --- Group 3: Morphological Features ---
        for feat, positions in feat_map.items():
            cnt = len(positions)
            stats[f'{feat} count'] = cnt
            stats[f'{feat} incidence'] = (cnt / doc_len) * 1000
            # Burstiness
            stats[f'{feat} burstiness'] = self._calc_burstiness(positions, doc_len)

        # --- Group 4: Complexity (Entropy & Zipf) ---
        if zipf_scores:
            stats['Lexical sophistication (Zipf)'] = np.mean(zipf_scores)
            stats['Frequent word count'] = sum(1 for z in zipf_scores if z > 6.0)
            stats['Infrequent word count'] = sum(1 for z in zipf_scores if z < 4.0)
        else:
            stats['Lexical sophistication (Zipf)'] = 0
            stats['Frequent word count'] = 0
            stats['Infrequent word count'] = 0

        # Word Entropy
        word_counts = Counter(tokens)
        probs = [freq / doc_len for freq in word_counts.values()]
        stats['Word entropy'] = entropy(probs, base=2)

        # --- Group 5: Ratios (Sample of the many required) ---
        # Example: Noun / Lexical Item
        noun_c = get_cnt('NOUN')
        lex_c = get_cnt(self.TAG_GROUPS['Lexical item'])
        stats['Noun-lexical item ratio'] = noun_c / lex_c if lex_c > 0 else 0

        # --- Group 6: Distributional (Sentence-to-Sentence) ---
        # Measures overlap between adjacent sentences
        overlaps = []
        if len(doc.sentences) > 1:
            for i in range(len(doc.sentences) - 1):
                s1 = set(w.text for w in doc.sentences[i].words)
                s2 = set(w.text for w in doc.sentences[i+1].words)
                if len(s1) > 0 and len(s2) > 0:
                    overlap = len(s1.intersection(s2)) / len(s1.union(s2)) # Jaccard approx
                    overlaps.append(overlap)
        
        stats['Sentence overlap (Avg)'] = np.mean(overlaps) if overlaps else 0
        
        # Placeholder for Cosine (Green AI)
        stats['Cosine distance'] = 0.0

        return stats

    def get_multilingual_profile(self, text_series: pd.Series, samples_per_lang=100):
        # 1. Census
        print("🔍 Phase 1: Census...")
        texts = text_series.dropna().astype(str).tolist()
        # Simple batch census
        langs = []
        for i in range(0, len(texts), 100):
            batch = texts[i:i+100]
            docs = self.lid_pipeline(batch)
            langs.extend([d.lang for d in docs])
        
        lang_series = pd.Series(langs, index=text_series.dropna().index)
        top_langs = lang_series.value_counts().head(5).index.tolist()
        
        final_report = {}

        # 2. Stratified Profile
        for lang in top_langs:
            print(f"📊 Profiling '{lang}'...")
            subset = text_series[lang_series == lang].sample(min(samples_per_lang, len(text_series[lang_series == lang])))
            subset_txt = subset.astype(str).tolist()
            
            try:
                stanza.download(lang, processors='tokenize,mwt,pos,lemma', verbose=False)
                nlp = stanza.Pipeline(lang=lang, processors='tokenize,mwt,pos,lemma', verbose=False, use_gpu=self.use_gpu)
                
                # Process docs
                in_docs = [stanza.Document([], text=t) for t in subset_txt]
                out_docs = nlp(in_docs)
                
                # Extract & Aggregate
                all_stats = [self._extract_measures(d, lang) for d in out_docs]
                df = pd.DataFrame(all_stats)
                
                # Calculate Means
                final_report[lang] = df.mean().round(4).to_dict()
                
                del nlp
                gc.collect()
            except Exception as e:
                print(f"Skipping {lang}: {e}")

        return pd.DataFrame(final_report)