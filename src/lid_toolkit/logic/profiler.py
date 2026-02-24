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

# Mute Stanza noise
logging.getLogger('stanza').setLevel(logging.WARNING)

class DeepProfiler:
    def __init__(self):
        print("⏳ Initializing DeepProfiler (Lingualyzer Implementation)...")
        self.use_gpu = torch.cuda.is_available()

        self.fasttext_model = None  # Define it as None so checks don't crash
        
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
        
        # Special compound checks for person pronouns (Lingualyzer requires PRON + PronType=Prs + Person=X)
        if feat_name == 'First person':
            return (word.upos == 'PRON' and 
                    'PronType=Prs' in features and 
                    'Person=1' in features)
        elif feat_name == 'Second person':
            return (word.upos == 'PRON' and 
                    'PronType=Prs' in features and 
                    'Person=2' in features)
        elif feat_name == 'Third person':
            return (word.upos == 'PRON' and 
                    'PronType=Prs' in features and 
                    'Person=3' in features)
        elif feat_name == 'Personal pronoun':
            return (word.upos == 'PRON' and 
                    'PronType=Prs' in features)
        elif feat_name == 'Singular':
            return (word.upos in ['NOUN', 'PROPN', 'PRON'] and 'Number=Sing' in features)
        elif feat_name == 'Plural':
            return (word.upos in ['NOUN', 'PROPN', 'PRON'] and 'Number=Plur' in features)
        # Mapping Lingualyzer definitions to UD v2 Tags (simple single-feature checks)
        checks = {
            'Interrogative': 'PronType=Int',
            'Demonstrative': 'PronType=Dem',
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
        Calculates burstiness using the finite-size corrected measure A_n(r) 
        from Kim and Jo (2016).
        """
        n = len(positions)
        
        # 1. Edge Case: Need at least 1 item
        if n == 0: 
            return 0.0
            
        # 2. Check for "Perfect Internal Regularity" (The Adjective Case)
        # if n >= 2:
        #     internal_gaps = np.diff(positions)
        #     if np.std(internal_gaps) == 0:
        #         return -1.0

        # 3. Standard Calculation
        gaps = list(np.diff(positions))
        
        if len(gaps) == 0: 
            return 0.0
        
        # Use standard Sample SD (ddof=1) and True Mean
        std_gap = np.std(gaps, ddof=1)
        mean_gap = np.mean(gaps)
        
        if mean_gap == 0: 
            return 0.0
            
        r = std_gap / mean_gap
        
        # 4. Kim and Jo (2016) Finite-Size Correction A_n(r)
        sqrt_n_plus_1 = np.sqrt(n + 1)
        sqrt_n_minus_1 = np.sqrt(n - 1)
        
        numerator = (sqrt_n_plus_1 * r) - sqrt_n_minus_1
        denominator = ((sqrt_n_plus_1 - 2) * r) + sqrt_n_minus_1
        
        return numerator / denominator
    
        # # 4. Final Calculation
        # cv = std_gap / mean_gap 
        # return (cv - 1) / (cv + 1)
    
    def _levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein (edit) distance between two strings or sequences."""
        # Handle sequences (lists) directly for word-level comparison
        if isinstance(s1, list) and isinstance(s2, list):
            if len(s1) < len(s2):
                s1, s2 = s2, s1
            if len(s2) == 0:
                return len(s1)
            previous_row = list(range(len(s2) + 1))
            for i, w1 in enumerate(s1):
                current_row = [i + 1]
                for j, w2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (w1 != w2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]
        else:
            # Fallback: treat as strings for character-level comparison
            if len(s1) < len(s2):
                return self._levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]
    
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
    
    def _calc_lexical_diversity(self, lower_non_punct_tokens, pos_map, pos_map_lower_non_punct, doc_len):
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
        if hapax_positions and doc_len > 0:
            midpoint = doc_len / 2
            first_half = sum(1 for p in hapax_positions if p <= midpoint)
            second_half = len(hapax_positions) - first_half
            total = len(hapax_positions)
            stats['Hapax legomena concentration'] = (second_half - first_half) / total if total > 0 else 0
        else:
            stats['Hapax legomena concentration'] = 0

        # Hapax legomena average position (normalized 0 to 1) and SD: use original token positions
        # Only count the first occurrence of each hapax word (case-insensitive, non-punct) in the original tokens
       
        stats['Hapax legomena average position'] = ((np.mean(hapax_positions))-1) / (doc_len-1) if hapax_positions and doc_len > 1 else 0

        if hapax_positions and doc_len > 1 and len(hapax_positions) >= 2:
            # normalized = [p / (doc_len-1) for p in hapax_positions]
            sample_sd = np.std(hapax_positions, ddof=1)
            stats['Hapax legomena position SD'] = sample_sd / (doc_len - 1) if doc_len > 1 else 0
            # return sample_sd / (doc_len - 1)
            # stats['Hapax legomena position SD'] = np.std(normalized)
        else:
            stats['Hapax legomena position SD'] = 0

        # Honoré's statistic
        if type_count > 0 and hapax_count < type_count:
            stats["Honoré's statistic"] = 100 * math.log10(doc_len) / (1 - (hapax_count / type_count)) if doc_len > 0 else 0
        else:
            stats["Honoré's statistic"] = 0

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
        stats['Moving average TTR'] = moving_average_ttr(lower_non_punct_tokens, window_size=100)

        # ...existing code...
        # Per-PoS TTRs
        pos_tags = ['ADJ', 'ADV', 'INTJ', 'VERB', 'NOUN', 'PROPN', 'ADP', 'AUX', 
                 'DET', 'NUM', 'PART', 'PRON']
        for tag in pos_tags:
            positions = pos_map_lower_non_punct.get(tag, [])
            if positions:
                # Get tokens at these positions
                pos_tokens = [lower_non_punct_tokens[i-1] for i in positions if i > 0]
                if pos_tokens:
                    stats[f'{tag} TTR'] = len(set(pos_tokens)) / len(pos_tokens)
                else:
                    stats[f'{tag} TTR'] = 0
            else:
                stats[f'{tag} TTR'] = 0
        
        # Combined group TTRs
        # Lexical item TTR (open class: ADJ, ADV, INTJ, NOUN, PROPN, VERB)
        lexical_tags = {'ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB'}
        lexical_positions = []
        for tag in lexical_tags:
            lexical_positions.extend(pos_map_lower_non_punct.get(tag, []))
        if lexical_positions:
            lexical_tokens = [lower_non_punct_tokens[i-1] for i in lexical_positions if i > 0]
            stats['Lexical item TTR'] = len(set(lexical_tokens)) / len(lexical_tokens) if lexical_tokens else 0
        else:
            stats['Lexical item TTR'] = 0
        
        # Grammatical item TTR (closed class: ADP, AUX, CCONJ, DET, NUM, PART, PRON, SCONJ)
        grammatical_tags = {'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'}
        grammatical_positions = []
        for tag in grammatical_tags:
            grammatical_positions.extend(pos_map_lower_non_punct.get(tag, []))
        if grammatical_positions:
            grammatical_tokens = [lower_non_punct_tokens[i-1] for i in grammatical_positions if i > 0]
            stats['Grammatical item TTR'] = len(set(grammatical_tokens)) / len(grammatical_tokens) if grammatical_tokens else 0
        else:
            stats['Grammatical item TTR'] = 0
        
        # Verb_All TTR (VERB + AUX)
        verb_all_tags = {'VERB', 'AUX'}
        verb_all_positions = []
        for tag in verb_all_tags:
            verb_all_positions.extend(pos_map_lower_non_punct.get(tag, []))
        if verb_all_positions:
            verb_all_tokens = [lower_non_punct_tokens[i-1] for i in verb_all_positions if i > 0]
            stats['Verb_All TTR'] = len(set(verb_all_tokens)) / len(verb_all_tokens) if verb_all_tokens else 0
        else:
            stats['Verb_All TTR'] = 0

        # Conjunction type-token ratio (CCONJ + SCONJ)
        conjunction_tags = {'CCONJ', 'SCONJ'}
        conjunction_positions = []
        for tag in conjunction_tags:
            conjunction_positions.extend(pos_map_lower_non_punct.get(tag, []))
        if conjunction_positions:
            conjunction_tokens = [lower_non_punct_tokens[i-1] for i in conjunction_positions if i > 0]
            distinct_conjunctions = set(conjunction_tokens)
            stats['Conjunction TTR'] = len(distinct_conjunctions) / len(conjunction_tokens) if conjunction_tokens else 0
        else:
            stats['Conjunction TTR'] = 0
        
        return stats
    
    def _calc_word_lengths(self, doc, pos_map_lower_non_punct, lower_non_punct_tokens):
        
        stats = {}
    
        # Global average word length (lowercased, non-punct tokens)
        if lower_non_punct_tokens:
            stats['Word length (non-punct)'] = np.mean([len(t) for t in lower_non_punct_tokens])
        else:
            stats['Word length (non-punct)'] = 0
    
        # Per-PoS average word lengths (using positions in pos_map_lower_non_punct)
        pos_tags = ['ADJ', 'ADV', 'INTJ', 'VERB', 'NOUN', 'PROPN', 'ADP', 'AUX', 
                    'DET', 'NUM', 'PART', 'PRON']
        for tag in pos_tags:
            positions = pos_map_lower_non_punct.get(tag, [])
            lengths = [len(lower_non_punct_tokens[i-1]) for i in positions if 0 < i <= len(lower_non_punct_tokens)]
            stats[f'{tag} word length'] = np.mean(lengths) if lengths else 0
    
        # Combined group word lengths
        group_defs = {
            'Lexical item': {'ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB'},
            'Grammatical item': {'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'},
            'Verb_All': {'VERB', 'AUX'},
            'Conjunction': {'CCONJ', 'SCONJ'}
        }
        for group, tags in group_defs.items():
            group_positions = []
            for tag in tags:
                group_positions.extend(pos_map_lower_non_punct.get(tag, []))
            lengths = [len(lower_non_punct_tokens[i-1]) for i in group_positions if 0 < i <= len(lower_non_punct_tokens)]
            stats[f'{group} word length'] = np.mean(lengths) if lengths else 0
    
        return stats

    
    def _calc_zipf_variants(self, zipf_scores, lower_non_punct_tokens, lang_code, doc_len):
        """Calculate Zipf frequency variants."""
        stats = {}
        
        if not zipf_scores:
            stats['Zipf curve steepness'] = 0
            stats['Zipf goodness-of-fit'] = 0
            stats['Average contextual diversity'] = 0
            stats['Frequent word incidence'] = 0
            stats['Infrequent word incidence'] = 0
            stats['Unknown word count'] = 0
            stats['Unknown word incidence'] = 0
            return stats
        
        # Zipf curve steepness using MLE (Clauset et al., 2009)
        # More accurate than log-log linear regression
        word_counts = Counter(lower_non_punct_tokens)
        frequencies = np.array(sorted(word_counts.values(), reverse=True))
        if len(frequencies) > 1:
            x_min = 1  # minimum frequency threshold
            # Filter frequencies >= x_min
            freq_above_min = frequencies[frequencies >= x_min]
            n = len(freq_above_min)
            if n > 1:
                # MLE estimator for discrete power law: α = 1 + n / Σ ln(x_i / (x_min - 0.5))
                alpha_mle = 1 + n / np.sum(np.log(freq_above_min / (x_min - 0.5)))
                stats['Zipf curve steepness'] = alpha_mle
                
                # Goodness-of-fit: R² determination coefficient
                # Compare observed frequencies to theoretical Zipf frequencies
                ranks = np.arange(1, len(freq_above_min) + 1)
                # Theoretical frequencies: f(r) = C / r^α, where C is fitted to match total
                theoretical_freqs = 1 / (ranks ** alpha_mle)
                # Scale theoretical to match observed total
                theoretical_freqs = theoretical_freqs * (np.sum(freq_above_min) / np.sum(theoretical_freqs))
                # Calculate R² = 1 - SS_res / SS_tot
                ss_res = np.sum((freq_above_min - theoretical_freqs) ** 2)
                ss_tot = np.sum((freq_above_min - np.mean(freq_above_min)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                stats['Zipf goodness-of-fit'] = max(0, r_squared)  # Clamp to [0, 1]
            else:
                stats['Zipf curve steepness'] = 0
                stats['Zipf goodness-of-fit'] = 0
        else:
            stats['Zipf curve steepness'] = 0
            stats['Zipf goodness-of-fit'] = 0
        
        # Average contextual diversity (approximated by Zipf score)
        stats['Average contextual diversity'] = np.mean(zipf_scores)
        
        # Frequency incidence counts
        freq_count = sum(1 for z in zipf_scores if z > 6.0)
        infreq_count = sum(1 for z in zipf_scores if z < 4.0)
        
        stats['Frequent word incidence'] = (freq_count / doc_len * 1000) if doc_len > 0 else 0
        stats['Infrequent word incidence'] = (infreq_count / doc_len * 1000) if doc_len > 0 else 0
        
        # Unknown words (Zipf < 3.0 or not found in wordfreq)
        unknown_count = 0
        for token in lower_non_punct_tokens:
            z = zipf_frequency(token, lang_code)
            if z < 3.0:
                unknown_count += 1
        
        stats['Unknown word count'] = unknown_count
        stats['Unknown word incidence'] = (unknown_count / doc_len * 1000) if doc_len > 0 else 0
            
        return stats
    
    def _calc_morphological_complexity(self, doc):
        """Calculate morphological complexity measures."""
        stats = {}
        
        # Word-lemma Levenshtein distances
        distances = []
        # Key by (lemma, PoS) tuple - lemmas with different PoS tags are differentiated
        lemmas_per_word = defaultdict(set)
        
        for sent in doc.sentences:
            for word in sent.words:
                if word.text and word.lemma and word.upos not in ['PUNCT', 'SYM', 'X']:
                    dist = self._levenshtein_distance(word.text.lower(), word.lemma.lower())
                    distances.append(dist)
                    # Differentiate lemmas by PoS tag (e.g., "run" as NOUN vs "run" as VERB)
                    lemmas_per_word[(word.lemma, word.upos)].add(word.text.lower())
        
        if distances:
            stats['Word-lemma distance (avg)'] = np.mean(distances)
            stats['Word-lemma distance (max)'] = np.max(distances)
        else:
            stats['Word-lemma distance (avg)'] = 0
            stats['Word-lemma distance (max)'] = 0
        
        # Word-types per lemma (overall) - differentiated by PoS
        if lemmas_per_word:
            types_per_lemma = [len(word_forms) for word_forms in lemmas_per_word.values()]
            stats['Word-types per lemma'] = np.mean(types_per_lemma)
        else:
            stats['Word-types per lemma'] = 0
        
        # Word-types per lemma for specific PoS
        for pos_filter, pos_tags in [('noun', {'NOUN'}), ('verb', {'VERB', 'AUX'}), 
                                       ('lexical', {'ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB'}),
                                       ('grammatical', {'ADP', 'AUX', 'CCONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'})]:
            lemma_map = defaultdict(set)
            for sent in doc.sentences:
                for word in sent.words:
                    if word.upos in pos_tags and word.lemma:
                        lemma_map[word.lemma].add(word.text.lower())
            
            if lemma_map:
                types_per_lemma = [len(word_forms) for word_forms in lemma_map.values()]
                stats[f'Word-types per lemma ({pos_filter})'] = np.mean(types_per_lemma)
            else:
                stats[f'Word-types per lemma ({pos_filter})'] = 0
        
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
        stats['Sub-coordinating conjunction ratio'] = safe_ratio(sconj_c, cconj_c)
        
        # Determiner ratios
        stats['Adposition-determiner ratio'] = safe_ratio(adp_c, det_c)
        stats['Pronoun-determiner ratio'] = safe_ratio(pron_c, det_c)
        stats['Proper noun-determiner ratio'] = safe_ratio(propn_c, det_c)
        
        # Pronoun ratios
        stats['Proper noun-pronoun ratio'] = safe_ratio(propn_c, pron_c)
        
        # Grammatical item ratios
        stats['Adposition-grammatical item ratio'] = safe_ratio(adp_c, gram_c)
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
        stats['Verbal adjective-finite verb ratio'] = safe_ratio(vadj_c, fin_c)
        stats['Verbal adjective-infinitive verb ratio'] = safe_ratio(vadj_c, inf_c)
        stats['Present-past tense ratio'] = safe_ratio(pres_c, past_c)
        
        return stats
    
    def _calc_distributional_measures(self, pos_map_lower_non_punct, feat_map_lower_non_punct, pos_map, feat_map, zipf_scores, tokens, doc_len, lang_code, lower_non_punct_tokens):
        """Calculate concentration, average position, and position SD for all categories."""
        stats = {}
        
        def calc_concentration(positions, doc_len):
            """Calculate concentration: < 0 = first half, > 0 = second half."""
            if not positions or doc_len == 0:
                return 0
            midpoint = doc_len / 2
            first_half = sum(1 for p in positions if p <= midpoint)
            second_half = len(positions) - first_half
            total = len(positions)
            if total == 0:
                return 0
            return (second_half - first_half) / total
        
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
            positions = pos_map_lower_non_punct.get(tag, [])
            stats[f'{tag} concentration'] = calc_concentration(positions, doc_len)
            stats[f'{tag} average position'] = calc_avg_position(positions, doc_len)
            stats[f'{tag} position SD'] = calc_position_sd(positions, doc_len)

        # Tag group distributional measures (using self.TAG_GROUPS)
        for group_name, tag_set in self.TAG_GROUPS.items():
            group_positions = []
            for tag in tag_set:
                group_positions.extend(pos_map_lower_non_punct.get(tag, []))
            group_positions_sorted = sorted(group_positions)
            stats[f'{group_name} concentration'] = calc_concentration(group_positions_sorted, doc_len)
            stats[f'{group_name} average position'] = calc_avg_position(group_positions_sorted, doc_len)
            stats[f'{group_name} position SD'] = calc_position_sd(group_positions_sorted, doc_len)
        
        # Feature-based distributional measures
        for feat in feat_map_lower_non_punct:
            positions = feat_map_lower_non_punct[feat]
            stats[f'{feat} concentration'] = calc_concentration(positions, doc_len)
            stats[f'{feat} average position'] = calc_avg_position(positions, doc_len)
            stats[f'{feat} position SD'] = calc_position_sd(positions, doc_len)
        
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
        stats['Frequent word average position'] = calc_avg_position(freq_positions, doc_len)
        stats['Frequent word position SD'] = calc_position_sd(freq_positions, doc_len)
        stats['Frequent word burstiness'] = self._calc_burstiness(freq_positions, doc_len)
        
        stats['Infrequent word concentration'] = calc_concentration(infreq_positions, doc_len)
        stats['Infrequent word average position'] = calc_avg_position(infreq_positions, doc_len)
        stats['Infrequent word position SD'] = calc_position_sd(infreq_positions, doc_len)
        stats['Infrequent word burstiness'] = self._calc_burstiness(infreq_positions, doc_len)
        
        stats['Unknown word concentration'] = calc_concentration(unknown_positions, doc_len)
        stats['Unknown word average position'] = calc_avg_position(unknown_positions, doc_len)
        stats['Unknown word position SD'] = calc_position_sd(unknown_positions, doc_len)
        stats['Unknown word burstiness'] = self._calc_burstiness(unknown_positions, doc_len)
        
        return stats

    # =========================================================================
    # CORE: Measure Extraction
    # =========================================================================
    def _extract_measures(self, doc, lang_code, original_text=""):
        stats = {}
        
        # 1. PRE-CALCULATE LISTS FOR SPEED
        # --------------------------------
        tokens = []
        pos_map = {tag: [] for tag in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON', 'PUNCT']}
        feat_map = {k: [] for k in ['Personal pronoun','First person','Second person','Third person','Interrogative','Demonstrative','Singular','Plural','Indefinite','Definite','Finite','Infinitive','Verbal adjective','Past','Present','Passive']}

        # New: pos_map based on lowercased, non-punct tokens
        pos_map_lower_non_punct = {tag: [] for tag in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON']}
        lower_non_punct_tokens = []
        lower_non_punct_tags = []
        for sent in doc.sentences:
            for word in sent.words:
                if word.upos not in ('PUNCT', 'SYM', 'X'):
                    lower_non_punct_tokens.append(word.text.lower())
                    lower_non_punct_tags.append(word.upos)
        # Assign positions (1-based) for each tag
        for idx, (token, tag) in enumerate(zip(lower_non_punct_tokens, lower_non_punct_tags), 1):
            if tag in pos_map_lower_non_punct:
                pos_map_lower_non_punct[tag].append(idx)

        # New: feat_map based on lowercased, non-punct tokens
        feat_map_lower_non_punct = {k: [] for k in ['Personal pronoun','First person','Second person','Third person','Interrogative','Demonstrative','Singular','Plural','Indefinite','Definite','Finite','Infinitive','Verbal adjective','Past','Present','Passive']}
        # Assign feature positions (1-based) for filtered tokens
        for idx, (token, tag) in enumerate(zip(lower_non_punct_tokens, lower_non_punct_tags), 1):
            # Find the corresponding word in doc.sentences
            for sent in doc.sentences:
                for word in sent.words:
                    if word.text.lower() == token and word.upos == tag:
                        for feat_name in feat_map_lower_non_punct.keys():
                            if self._check_feature(word, feat_name):
                                feat_map_lower_non_punct[feat_name].append(idx)
                        break
        
        zipf_scores = []
        word_lengths = []
        
        total_words = 0
        total_chars = 0
        
        for sent_idx, sentence in enumerate(doc.sentences):
            for word_idx, word in enumerate(sentence.words):
                tokens.append(word.text)
                if word.upos not in ('PUNCT', 'SYM', 'X'):
                    total_words += 1
                    total_chars += len(word.text)
                    word_lengths.append(len(word.text))
                
                # Store position (1-indexed) for distributional measures
                global_pos = len(tokens)
                
                # --- A. PoS Bucketing ---
                if word.upos in pos_map:
                    pos_map[word.upos].append(global_pos)
                    
                # --- B. Feature Bucketing ---
                for feat_name in feat_map.keys():
                    if self._check_feature(word, feat_name):
                        feat_map[feat_name].append(global_pos)
                
                # --- C. Zipf & Frequencies ---
                if word.upos not in ['PUNCT', 'SYM', 'X']:
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
        # Exclude punctuation tokens from type counts and TRR calculations
        stats['Type count'] = len(set(lower_non_punct_tokens))
        stats['Type-token ratio'] = len(set(lower_non_punct_tokens)) / doc_len
        
        # Average word length
        stats['Word length'] = np.mean(word_lengths) if word_lengths else 0
        
        # Average sentence length
        stats['Sentence length'] = total_words / len(doc.sentences) if len(doc.sentences) > 0 else 0
        
        # --- Group 2: Paragraph Measures ---
        para_stats = self._calc_paragraph_measures(original_text if original_text else "", doc.sentences)
        stats.update(para_stats)
        
        # Average paragraph length
        if para_stats['Paragraph count'] > 0:
            stats['Paragraph length'] = len(doc.sentences) / para_stats['Paragraph count']
        else:
            stats['Paragraph length'] = 0
        
        # --- Group 3: PoS Counts & Incidence (Per 1000 words) ---
        # Helper to safely get count
        def get_cnt(tags):
            if isinstance(tags, str): tags = {tags}
            return sum(len(pos_map_lower_non_punct.get(t, [])) for t in tags)

        # Standard Tags
        for tag in pos_map_lower_non_punct:
            cnt = len(pos_map_lower_non_punct[tag])
            stats[f'{tag} count'] = cnt
            stats[f'{tag} incidence'] = (cnt / doc_len) * 1000
            # Type count for this PoS
            pos_tokens = [lower_non_punct_tokens[i-1] for i in pos_map_lower_non_punct[tag] if i > 0 and i <= len(lower_non_punct_tokens)]
            stats[f'{tag} type count'] = len(set(pos_tokens))
            # Burstiness for this PoS
            stats[f'{tag} burstiness'] = self._calc_burstiness(pos_map_lower_non_punct[tag], doc_len)

        # Punctuation measures (tracked separately in pos_map)
        punct_count = len(pos_map.get('PUNCT', []))
        stats['PUNCT count'] = punct_count
        stats['PUNCT incidence'] = (punct_count / len(tokens)) * 1000 if doc_len > 0 else 0

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
            cnt = len(positions)
            stats[f'{feat} count'] = cnt
            stats[f'{feat} incidence'] = (cnt / doc_len) * 1000
            # Burstiness
            stats[f'{feat} burstiness'] = self._calc_burstiness(positions, doc_len)

        # --- Group 5: Lexical Diversity ---
        lex_div_stats = self._calc_lexical_diversity(lower_non_punct_tokens, pos_map, pos_map_lower_non_punct, doc_len)
        stats.update(lex_div_stats)
        
        # --- Group 6: Word Lengths (Per-PoS) ---
        word_len_stats = self._calc_word_lengths(doc,  pos_map_lower_non_punct, lower_non_punct_tokens)
        stats.update(word_len_stats)
        
        # --- Group 7: Complexity (Entropy & Zipf) ---
        if zipf_scores:
            stats['Lexical sophistication (Zipf frequency)'] = np.mean(zipf_scores)
            stats['Frequent word count'] = sum(1 for z in zipf_scores if z > 6.0)
            stats['Infrequent word count'] = sum(1 for z in zipf_scores if z < 4.0)
        else:
            stats['Lexical sophistication (Zipf frequency)'] = 0
            stats['Frequent word count'] = 0
            stats['Infrequent word count'] = 0

        # Zipf variants
        zipf_var_stats = self._calc_zipf_variants(zipf_scores, tokens, lang_code, doc_len)
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
        dist_stats = self._calc_distributional_measures(pos_map_lower_non_punct,feat_map_lower_non_punct, pos_map, feat_map, zipf_scores, tokens, doc_len, lang_code, lower_non_punct_tokens)
        stats.update(dist_stats)
        
        # --- Group 11: Distributional (Sentence-to-Sentence) ---
        # Measures overlap between adjacent sentences
        overlaps = []
        overlap_counts = []
        overlap_ratios = []
        lemma_overlap_counts = []
        lemma_overlap_ratios = []
        pos_overlap_counts = []
        pos_overlap_ratios = []
        feature_overlap_counts = []
        feature_overlap_ratios = []
        levenshtein_word_distances = []
        levenshtein_lemma_distances = []
        levenshtein_pos_distances = []
        levenshtein_char_distances = []
        cosine_distances = []
        if len(doc.sentences) > 1:
            for i in range(len(doc.sentences) - 1):
                s1 = set(w.text for w in doc.sentences[i].words if w.upos not in ('PUNCT', 'SYM', 'X'))
                s2 = set(w.text for w in doc.sentences[i+1].words if w.upos not in ('PUNCT', 'SYM', 'X'))
                l1 = set(w.lemma for w in doc.sentences[i].words if w.lemma)
                l2 = set(w.lemma for w in doc.sentences[i+1].words if w.lemma)
                p1 = [w.upos for w in doc.sentences[i].words if w.upos not in ('PUNCT', 'SYM', 'X')]
                p2 = [w.upos for w in doc.sentences[i+1].words if w.upos not in ('PUNCT', 'SYM', 'X')]
                f1_feats = []
                for w in doc.sentences[i].words:
                    if w.upos not in ('PUNCT', 'SYM', 'X') and w.feats:
                        f1_feats.extend(w.feats.split('|'))
                f2_feats = []
                for w in doc.sentences[i+1].words:
                    if w.upos not in ('PUNCT', 'SYM', 'X') and w.feats:
                        f2_feats.extend(w.feats.split('|'))
                if len(s1) > 0 and len(s2) > 0:
                    overlap = len(s1.intersection(s2)) / len(s1.union(s2)) # Jaccard approx
                    overlaps.append(overlap)
                    overlap_count = len(s1.intersection(s2))  # Raw count of overlapping words
                    overlap_counts.append(overlap_count)
                    # Word overlap ratio: overlap_count / min non-punct words in shortest segment
                    min_words = min(len(s1), len(s2))
                    if min_words > 0:
                        overlap_ratio = overlap_count / min_words
                        overlap_ratios.append(overlap_ratio)
                if len(l1) > 0 and len(l2) > 0:
                    lemma_overlap_count = len(l1.intersection(l2))  # Raw count of overlapping lemmas
                    lemma_overlap_counts.append(lemma_overlap_count)
                    # Lemma overlap ratio: lemma_overlap_count / min non-punct lemmas in shortest segment
                    min_words = min(len(l1), len(l2))
                    if min_words > 0:
                        lemma_overlap_ratio = lemma_overlap_count / min_words
                        lemma_overlap_ratios.append(lemma_overlap_ratio)
                if len(p1) > 0 and len(p2) > 0:
                    c1 = Counter(p1)
                    c2 = Counter(p2)
                    # Count overlap including duplicates: sum of minimum counts for each tag
                    pos_overlap_count = sum(min(c1[tag], c2[tag]) for tag in c1 if tag in c2)
                    pos_overlap_counts.append(pos_overlap_count)
                    # PoS overlap ratio: overlap_count / min words in shortest segment
                    min_words = min(len(p1), len(p2))
                    if min_words > 0:
                        pos_overlap_ratio = pos_overlap_count / min_words
                        pos_overlap_ratios.append(pos_overlap_ratio)
                if len(f1_feats) > 0 and len(f2_feats) > 0:
                    c1 = Counter(f1_feats)
                    c2 = Counter(f2_feats)
                    feature_overlap_count = sum(min(c1[feat], c2[feat]) for feat in c1 if feat in c2)
                    feature_overlap_counts.append(feature_overlap_count)
                    min_feats = min(len(f1_feats), len(f2_feats))
                    if min_feats > 0:
                        feature_overlap_ratio = feature_overlap_count / min_feats
                        feature_overlap_ratios.append(feature_overlap_ratio)
                
                # Levenshtein distances for sequences
                # Only use non-punctuation tokens for Levenshtein word distance
                w1 = [w.text for w in doc.sentences[i].words if w.upos not in ('PUNCT', 'SYM', 'X')]
                w2 = [w.text for w in doc.sentences[i+1].words if w.upos not in ('PUNCT', 'SYM', 'X')]
                if w1 and w2:
                    word_dist = self._levenshtein_distance(w1, w2)
                    max_len = max(len(w1), len(w2))
                    if max_len > 0:
                        normalized_word_dist = word_dist / max_len
                        levenshtein_word_distances.append(normalized_word_dist)
                
                # Only use non-punctuation tokens for Levenshtein lemma distance
                lem1 = [w.lemma for w in doc.sentences[i].words if w.lemma and w.upos not in ('PUNCT', 'SYM', 'X')]
                lem2 = [w.lemma for w in doc.sentences[i+1].words if w.lemma and w.upos not in ('PUNCT', 'SYM', 'X')]
                if lem1 and lem2:
                    lemma_dist = self._levenshtein_distance(lem1, lem2)
                    max_len = max(len(lem1), len(lem2))
                    if max_len > 0:
                        normalized_lemma_dist = lemma_dist / max_len
                        levenshtein_lemma_distances.append(normalized_lemma_dist)
                
                # Only use non-punctuation tokens for Levenshtein PoS distance
                pos_seq1 = [w.upos for w in doc.sentences[i].words if w.upos not in ('PUNCT', 'SYM', 'X')]
                pos_seq2 = [w.upos for w in doc.sentences[i+1].words if w.upos not in ('PUNCT', 'SYM', 'X')]
                if pos_seq1 and pos_seq2:
                    pos_dist = self._levenshtein_distance(pos_seq1, pos_seq2)
                    max_len = max(len(pos_seq1), len(pos_seq2))
                    if max_len > 0:
                        normalized_pos_dist = pos_dist / max_len
                        levenshtein_pos_distances.append(normalized_pos_dist)
                
                # Levenshtein character distance for raw text segments (including punctuation)
                text1 = doc.sentences[i].text
                text2 = doc.sentences[i+1].text
                if text1 and text2:
                    char_dist = self._levenshtein_distance(text1, text2)
                    max_len = max(len(text1), len(text2))
                    if max_len > 0:
                        normalized_char_dist = char_dist / max_len
                        levenshtein_char_distances.append(normalized_char_dist)
                
                # Cosine distance using sentence centroids
                centroid1 = self._get_sentence_centroid([w.text for w in doc.sentences[i].words])
                centroid2 = self._get_sentence_centroid([w.text for w in doc.sentences[i+1].words])
                if centroid1 is not None and centroid2 is not None and np.linalg.norm(centroid1) > 0 and np.linalg.norm(centroid2) > 0:
                    cos_dist = cosine(centroid1, centroid2)
                    cosine_distances.append(cos_dist)
        
        # stats['Sentence overlap (Avg)'] = np.mean(overlaps) if overlaps else 0
        stats['Word overlap (Count)'] = np.sum(overlap_counts) if overlap_counts else 0
        stats['Word overlap (Ratio)'] = np.mean(overlap_ratios) if overlap_ratios else 0
        stats['Lemma overlap (Count)'] = np.sum(lemma_overlap_counts) if lemma_overlap_counts else 0
        stats['Lemma overlap (Ratio)'] = np.mean(lemma_overlap_ratios) if lemma_overlap_ratios else 0
        stats['PoS overlap (Count)'] = np.sum(pos_overlap_counts) if pos_overlap_counts else 0
        stats['PoS overlap (Ratio)'] = np.mean(pos_overlap_ratios) if pos_overlap_ratios else 0
        stats['Feature overlap (Count)'] = np.sum(feature_overlap_counts) if feature_overlap_counts else 0
        stats['Feature overlap (Ratio)'] = np.mean(feature_overlap_ratios) if feature_overlap_ratios else 0
        stats['Levenshtein word distance'] = np.mean(levenshtein_word_distances) if levenshtein_word_distances else 0
        stats['Levenshtein lemma distance'] = np.mean(levenshtein_lemma_distances) if levenshtein_lemma_distances else 0
        stats['Levenshtein PoS distance'] = np.mean(levenshtein_pos_distances) if levenshtein_pos_distances else 0
        stats['Levenshtein character distance'] = np.mean(levenshtein_char_distances) if levenshtein_char_distances else 0
        stats['Cosine distance'] = np.mean(cosine_distances) if cosine_distances else 0.0

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
                
                # Extract & Aggregate (pass original text for paragraph detection)
                all_stats = [self._extract_measures(d, lang, subset_txt[i]) for i, d in enumerate(out_docs)]
                df = pd.DataFrame(all_stats)
                
                # Calculate Means
                final_report[lang] = df.mean().round(4).to_dict()
                
                del nlp
                gc.collect()
            except Exception as e:
                print(f"Skipping {lang}: {e}")

        return pd.DataFrame(final_report)