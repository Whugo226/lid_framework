import csv
import os
import sys
import stanza
import numpy as np
from collections import Counter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from lid_toolkit.logic.profiler import DeepProfiler

# --- CONFIG ---
CSV_PATH = os.path.join(os.path.dirname(__file__), 'profiler_test_results_english.csv')
MEASURE_MAP = {
    # Only include mappings for measures that can fail (see test_profiler_validation.py)
    'Hapax legomena burstiness (Doc)': 'Hapax legomena burstiness',
    'Pronoun type count (Doc)': 'PRON type count',
    'Lexical verb burstiness (Doc)': 'VERB burstiness',
    'Noun burstiness (Doc)': 'NOUN burstiness',
    'Proper noun burstiness (Doc)': 'PROPN burstiness',
    'Lexical item burstiness (Doc)': 'Lexical item burstiness',
    'Adposition burstiness (Doc)': 'ADP burstiness',
    'Conjunction burstiness (Doc)': 'Conjunction burstiness',
    'Determiner burstiness (Doc)': 'DET burstiness',
    'Numeral burstiness (Doc)': 'NUM burstiness',
    'Particle burstiness (Doc)': 'PART burstiness',
    'Pronoun burstiness (Doc)': 'PRON burstiness',
    'Grammatical item burstiness (Doc)': 'Grammatical item burstiness',
    'Verb burstiness (Doc)': 'Verb_All burstiness',
    'Personal pronoun burstiness (Doc)': 'Personal pronoun burstiness',
    'First person pronoun burstiness (Doc)': 'First person burstiness',
    'Second person pronoun burstiness (Doc)': 'Second person burstiness',
    'Third person pronoun burstiness (Doc)': 'Third person burstiness',
    'Demonstrative burstiness (Doc)': 'Demonstrative burstiness',
    'Indefinite word burstiness (Doc)': 'Indefinite burstiness',
    'Definite word burstiness (Doc)': 'Definite burstiness',
    'Infinitive verb burstiness (Doc)': 'Infinitive burstiness',
    'Verbal adjective burstiness (Doc)': 'Verbal adjective burstiness',
    'Past tense burstiness (Doc)': 'Past burstiness',
    'Present tense burstiness (Doc)': 'Present burstiness',
    'Passive voice burstiness (Doc)': 'Passive burstiness',
    'Unknown word burstiness (Doc)': 'Unknown word burstiness',
    'Zipf steepness of curve (Doc)': 'Zipf curve steepness',
    'Zipf goodness of fit (Doc)': 'Zipf goodness-of-fit',
    'Zipf frequency (Doc)': 'Lexical sophistication (Zipf frequency)',
    'Average contextual diversity (Doc)': 'Average contextual diversity',
    'Infrequent word count (Doc)': 'Infrequent word count',
    'Unknown word count (Doc)': 'Unknown word count',
    'Infrequent word incidence (Doc)': 'Infrequent word incidence',
    'Unknown word incidence (Doc)': 'Unknown word incidence',
    'Noun-lexical item ratio (Doc)': 'Noun-lexical item ratio',
    'Sub-coordinating conjunction ratio (Doc)': 'Sub-coordinating conjunction ratio',
    'Feature overlap count (Sent-Sent Avg)': 'Feature overlap (Count)',
    'Feature overlap ratio (Sent-Sent Avg)': 'Feature overlap (Ratio)',
    'Cosine dist. (Sent-Sent Avg)': 'Cosine distance',
    'Grammatical item count (Doc)': 'Grammatical item count',
    'Grammatical item incidence (Doc)': 'Grammatical item incidence',
    'Grammatical item type count (Doc)': 'Grammatical item type count',
    'Grammatical item length (Doc)': 'Grammatical item word length',
    'Grammatical item concentration (Doc)': 'Grammatical item concentration',
    'Grammatical item position SD (Doc)': 'Grammatical item position SD',
    # Add more as needed
}

# --- STEP 1: Extract FAILs ---
def get_failed_measures():
    failed = []
    with open(CSV_PATH, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Status'].strip().upper() == 'FAIL':
                failed.append({
                    'measure': row['Measure'].strip(),
                    'sentence': row['Sentence'].strip(),
                    'expected': row['Expected'].strip(),
                    'actual': row['Actual'].strip(),
                    'diff': row['Difference'].strip()
                })
    return failed

# --- Logging to file instead of terminal ---
LOG_PATH = os.path.join(os.path.dirname(__file__), 'debug_output.txt')
# Clear previous log
with open(LOG_PATH, 'w', encoding='utf-8') as _f:
    pass

def log(*args, sep=' ', end='\n'):
    s = sep.join(str(a) for a in args) + end
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(s)

# Global seen messages for deduplication across a single target
SEEN_MESSAGES = set()
SEEN_GROUPS = set()

# --- STEP 2: Debug Profiler Subclass ---
class DebugProfiler(DeepProfiler):
    def _log(self, *args, sep=' ', end='\n', dedupe=True):
        """Prefix with current debug target and dedupe messages per-target."""
        # Global suppression flag: if True, skip logging (used during full extraction)
        if getattr(self, '_suppress_global_logs', False):
            return
        prefix = getattr(self, '_debug_target', None)
        msg = sep.join(str(a) for a in args)
        key = (prefix, msg) if dedupe else None
        if dedupe and key in SEEN_MESSAGES:
            return
        if dedupe:
            SEEN_MESSAGES.add(key)
        if prefix:
            log(f"[DEBUG:{prefix}] {msg}", end=end)
        else:
            log(msg, end=end)

    def _log_group(self, group, lines):
        """Log a sequence of lines once per (target, group)."""
        prefix = getattr(self, '_debug_target', None)
        key = (prefix, group)
        if key in SEEN_GROUPS:
            return
        SEEN_GROUPS.add(key)
        for line in lines:
            if prefix:
                log(f"[DEBUG:{prefix}] {line}")
            else:
                log(line)

    def debug_group_count(self, doc, lang_code, group_name):
        """Recompute a combined group count and log Step A-D for that group only.

        Step A: input tokens and tag positions
        Step B: raw counts and positional arrays
        Step C: intermediate math (type count, incidence calculation)
        Step D: final output value
        """
        # Reconstruct lower_non_punct_tokens and pos_map_lower_non_punct
        lower_non_punct_tokens = []
        lower_non_punct_tags = []
        for sent in doc.sentences:
            for word in sent.words:
                if word.upos not in ('PUNCT', 'SYM', 'X'):
                    lower_non_punct_tokens.append(word.text.lower())
                    lower_non_punct_tags.append(word.upos)

        pos_map_lower_non_punct = {tag: [] for tag in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON']}
        for idx, (token, tag) in enumerate(zip(lower_non_punct_tokens, lower_non_punct_tags), 1):
            if tag in pos_map_lower_non_punct:
                pos_map_lower_non_punct[tag].append(idx)

        # Step A
        self._log_group(f"{group_name}_input", [f"Step A: tokens={lower_non_punct_tokens}", f"Step A: pos_map={pos_map_lower_non_punct}"])

        # Build group positions
        tag_set = self.TAG_GROUPS.get(group_name)
        if not tag_set:
            self._log_group(f"{group_name}_error", [f"Unknown group: {group_name}"])
            return None

        group_positions = []
        for tag in tag_set:
            group_positions.extend(pos_map_lower_non_punct.get(tag, []))
        group_positions_sorted = sorted(group_positions)

        # Step B: raw counts/positions
        cnt = len(group_positions_sorted)
        self._log_group(f"{group_name}_raw", [f"Step B: positions={group_positions_sorted}", f"Step B: raw_count={cnt}"])

        # Step C: intermediate math
        doc_len = len(lower_non_punct_tokens) if lower_non_punct_tokens else 1
        type_count = len(set([lower_non_punct_tokens[i-1] for i in group_positions_sorted if 0 < i <= len(lower_non_punct_tokens)]))
        incidence = (cnt / doc_len) * 1000 if doc_len > 0 else 0
        self._log_group(f"{group_name}_intermediate", [f"Step C: doc_len={doc_len}", f"Step C: type_count={type_count}", f"Step C: incidence={incidence}"])

        # Step D: final outputs (count, incidence, type_count, burstiness)
        burst = self._calc_burstiness(group_positions_sorted, doc_len)
        self._log_group(f"{group_name}_final", [f"Step D: final_count={cnt}", f"Step D: incidence={incidence}", f"Step D: type_count={type_count}", f"Step D: burstiness={burst}"])
        return {'count': cnt, 'incidence': incidence, 'type_count': type_count, 'burstiness': burst}

    def debug_pos_count(self, doc, tag):
        """Focused debug for a single PoS tag count."""
        # Reconstruct tokens and pos map
        lower_non_punct_tokens = []
        lower_non_punct_tags = []
        for sent in doc.sentences:
            for word in sent.words:
                if word.upos not in ('PUNCT', 'SYM', 'X'):
                    lower_non_punct_tokens.append(word.text.lower())
                    lower_non_punct_tags.append(word.upos)

        pos_map_lower_non_punct = {tag_name: [] for tag_name in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON']}
        for idx, (token, t) in enumerate(zip(lower_non_punct_tokens, lower_non_punct_tags), 1):
            if t in pos_map_lower_non_punct:
                pos_map_lower_non_punct[t].append(idx)

        positions = pos_map_lower_non_punct.get(tag, [])
        cnt = len(positions)
        doc_len = len(lower_non_punct_tokens) if lower_non_punct_tokens else 1
        type_count = len(set([lower_non_punct_tokens[i-1] for i in positions if 0 < i <= len(lower_non_punct_tokens)]))
        incidence = (cnt / doc_len) * 1000 if doc_len > 0 else 0

        self._log_group(f"{tag}_input", [f"Step A: tokens={lower_non_punct_tokens}", f"Step A: positions={positions}"])
        self._log_group(f"{tag}_raw", [f"Step B: raw_count={cnt}", f"Step B: positions={positions}"])
        self._log_group(f"{tag}_intermediate", [f"Step C: doc_len={doc_len}", f"Step C: type_count={type_count}", f"Step C: incidence={incidence}"])
        burst = self._calc_burstiness(positions, doc_len)
        self._log_group(f"{tag}_final", [f"Step D: final_count={cnt}", f"Step D: incidence={incidence}", f"Step D: type_count={type_count}", f"Step D: burstiness={burst}"])
        return {'count': cnt, 'incidence': incidence, 'type_count': type_count, 'burstiness': burst}

    def debug_burstiness_tag(self, doc, tag):
        """Focused debug for burstiness of a PoS tag."""
        # Rebuild positions
        lower_non_punct_tokens = []
        lower_non_punct_tags = []
        for sent in doc.sentences:
            for word in sent.words:
                if word.upos not in ('PUNCT', 'SYM', 'X'):
                    lower_non_punct_tokens.append(word.text.lower())
                    lower_non_punct_tags.append(word.upos)
        pos_map_lower_non_punct = {tag_name: [] for tag_name in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON']}
        for idx, (token, t) in enumerate(zip(lower_non_punct_tokens, lower_non_punct_tags), 1):
            if t in pos_map_lower_non_punct:
                pos_map_lower_non_punct[t].append(idx)
        positions = pos_map_lower_non_punct.get(tag, [])
        doc_len = len(lower_non_punct_tokens) if lower_non_punct_tokens else 1

        self._log_group(f"{tag}_burst_input", [f"Step A: positions={positions}", f"Step A: doc_len={doc_len}"])
        if not positions:
            self._log_group(f"{tag}_burst_final", ["Step D: Final Output = 0.0 (no positions)"])
            return 0.0
        if len(positions) >= 2:
            internal_gaps = np.diff(positions)
            std_internal = np.std(internal_gaps)
            self._log_group(f"{tag}_burst_internal", [f"Step B: internal_gaps={internal_gaps}", f"Step C: internal_std={std_internal}"])
            if std_internal == 0:
                self._log_group(f"{tag}_burst_final", ["Step D: Final Output = -1.0 (perfect regularity)"])
                return -1.0
        gaps = [positions[0]] + list(np.diff(positions))
        mean_gap = np.mean(gaps)
        std_gap = np.std(gaps, ddof=1) if len(gaps) >= 2 else 0
        self._log_group(f"{tag}_burst_gaps", [f"Step B: gaps={gaps}", f"Step C: mean_gap={mean_gap}, std_gap={std_gap}"])
        if mean_gap == 0:
            self._log_group(f"{tag}_burst_final", ["Step D: Final Output = 0.0 (mean_gap=0)"])
            return 0.0
        cv = std_gap / mean_gap
        output = (cv - 1) / (cv + 1)
        self._log_group(f"{tag}_burst_final", [f"Step D: Final Output = {output}"])
        return output

    def debug_distribution_for_tag(self, doc, tag):
        """Focused debug for concentration/avg position/SD for a PoS tag."""
        lower_non_punct_tokens = []
        lower_non_punct_tags = []
        for sent in doc.sentences:
            for word in sent.words:
                if word.upos not in ('PUNCT', 'SYM', 'X'):
                    lower_non_punct_tokens.append(word.text.lower())
                    lower_non_punct_tags.append(word.upos)
        pos_map_lower_non_punct = {tag_name: [] for tag_name in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON']}
        for idx, (token, t) in enumerate(zip(lower_non_punct_tokens, lower_non_punct_tags), 1):
            if t in pos_map_lower_non_punct:
                pos_map_lower_non_punct[t].append(idx)

        positions = pos_map_lower_non_punct.get(tag, [])
        doc_len = len(lower_non_punct_tokens) if lower_non_punct_tokens else 1

        self._log_group(f"{tag}_dist_input", [f"Step A: positions={positions}", f"Step A: doc_len={doc_len}"])
        # Step B
        midpoint = doc_len / 2
        first_half = sum(1 for p in positions if p <= midpoint)
        second_half = len(positions) - first_half
        total = len(positions)
        self._log_group(f"{tag}_dist_raw", [f"Step B: first_half={first_half}", f"Step B: second_half={second_half}", f"Step B: total={total}", f"Step B: midpoint={midpoint}"])
        # Step C
        concentration = (second_half - first_half) / total if total > 0 else 0
        avg_pos = ((np.mean(positions))-1) / (doc_len-1) if positions and doc_len > 1 else 0
        sample_sd = np.std(positions, ddof=1) if positions and len(positions) >= 2 else 0
        pos_sd = sample_sd / (doc_len - 1) if doc_len > 1 else 0
        self._log_group(f"{tag}_dist_intermediate", [f"Step C: concentration={concentration}", f"Step C: avg_pos={avg_pos}", f"Step C: pos_sd={pos_sd}"])
        # Step D
        self._log_group(f"{tag}_dist_final", [f"Step D: concentration={concentration}", f"Step D: avg_pos={avg_pos}", f"Step D: pos_sd={pos_sd}"])
        return {'concentration': concentration, 'avg_pos': avg_pos, 'pos_sd': pos_sd}

    def debug_ratio(self, doc, ratio_name):
        """Focused debug for simple ratios like 'Adjective-noun ratio'."""
        # Rebuild pos_map counts
        lower_non_punct_tokens = []
        lower_non_punct_tags = []
        for sent in doc.sentences:
            for word in sent.words:
                if word.upos not in ('PUNCT', 'SYM', 'X'):
                    lower_non_punct_tokens.append(word.text.lower())
                    lower_non_punct_tags.append(word.upos)
        pos_map_lower_non_punct = {tag_name: [] for tag_name in ['ADJ','ADV','INTJ','VERB','NOUN','PROPN','ADP','AUX','CCONJ','SCONJ','DET','NUM','PART','PRON']}
        for idx, (token, t) in enumerate(zip(lower_non_punct_tokens, lower_non_punct_tags), 1):
            if t in pos_map_lower_non_punct:
                pos_map_lower_non_punct[t].append(idx)

        # Try to parse 'X-Y ratio' pattern
        key = ratio_name.replace(' ratio','')
        parts = key.split('-') if '-' in key else None
        if not parts or len(parts) != 2:
            self._log_group(f"ratio_error", [f"Cannot parse ratio name: {ratio_name}"])
            return None
        num_label = parts[0].strip()
        den_label = parts[1].strip()
        # Map human labels to tags if possible (simple heuristic)
        label_to_tag = {
            'Adjective':'ADJ','Adverb':'ADV','Noun':'NOUN','Verb':'VERB','Proper noun':'PROPN','Determiner':'DET','Pronoun':'PRON','Adposition':'ADP','Particle':'PART','Auxiliary':'AUX','Conjunction':'CCONJ'
        }
        num_tag = label_to_tag.get(num_label, num_label.upper())
        den_tag = label_to_tag.get(den_label, den_label.upper())

        num_cnt = len(pos_map_lower_non_punct.get(num_tag, []))
        den_cnt = len(pos_map_lower_non_punct.get(den_tag, []))
        self._log_group(f"ratio_input", [f"Step A: numerator={num_tag}, denominator={den_tag}", f"Step B: numerator_count={num_cnt}, denominator_count={den_cnt}"])
        ratio = num_cnt / den_cnt if den_cnt > 0 else 0
        self._log_group(f"ratio_final", [f"Step C: ratio={ratio}"])
        return {'numerator': num_cnt, 'denominator': den_cnt, 'ratio': ratio}
    # Override burstiness for verbose tracing
    def _calc_burstiness(self, positions, doc_len):
        # Group the full logic steps so they are logged once per measure
        self._log_group('burstiness', [
            "\n_calc_burstiness called",
            f"Step A: Input positions={positions}, doc_len={doc_len}",
        ])
        if not positions:
            self._log_group('burstiness', ["Step D: Final Output = 0.0 (no positions)"])
            return 0.0
        if len(positions) >= 2:
            internal_gaps = np.diff(positions)
            std_internal = np.std(internal_gaps)
            # log internal gaps and std once
            self._log_group('burstiness_internal', [f"Step B: Internal gaps={internal_gaps}", f"Step C: Internal gap std={std_internal}"])
            if std_internal == 0:
                self._log_group('burstiness', ["Step D: Final Output = -1.0 (perfect regularity)"])
                return -1.0
        gaps = [positions[0]] + list(np.diff(positions))
        mean_gap = np.mean(gaps)
        std_gap = np.std(gaps, ddof=1) if len(gaps) >= 2 else 0
        self._log_group('burstiness_gaps', [f"Step B: Gaps={gaps}", f"Step C: mean_gap={mean_gap}, std_gap={std_gap}"])
        if mean_gap == 0:
            self._log_group('burstiness', ["Step D: Final Output = 0.0 (mean_gap=0)"])
            return 0.0
        cv = std_gap / mean_gap
        output = (cv - 1) / (cv + 1)
        self._log_group('burstiness', [f"Step D: Final Output = {output}"])
        return output

    # Override distributional measures for verbose tracing
    def _calc_distributional_measures(self, pos_map_lower_non_punct, feat_map_lower_non_punct, pos_map, feat_map, zipf_scores, tokens, doc_len, lang_code, lower_non_punct_tokens):
        self._log("\n_calc_distributional_measures called")
        self._log(f"Step A: Input tokens={tokens}, doc_len={doc_len}, lang_code={lang_code}")
        stats = {}
        def calc_concentration(positions, doc_len):
            self._log(f"  [calc_concentration] positions={positions}, doc_len={doc_len}")
            midpoint = doc_len / 2
            first_half = sum(1 for p in positions if p <= midpoint)
            second_half = len(positions) - first_half
            total = len(positions)
            self._log(f"  Step B: first_half={first_half}, second_half={second_half}, total={total}, midpoint={midpoint}")
            output = (second_half - first_half) / total if total > 0 else 0
            self._log(f"  Step D: Final Output = {output}")
            return output
        def calc_avg_position(positions, doc_len):
            self._log(f"  [calc_avg_position] positions={positions}, doc_len={doc_len}")
            output = ((np.mean(positions))-1) / (doc_len-1) if positions and doc_len > 1 else 0
            self._log(f"  Step D: Final Output = {output}")
            return output
        def calc_position_sd(positions, doc_len):
            self._log(f"  [calc_position_sd] positions={positions}, doc_len={doc_len}")
            sample_sd = np.std(positions, ddof=1) if positions and len(positions) >= 2 else 0
            output = sample_sd / (doc_len - 1) if doc_len > 1 else 0
            self._log(f"  Step C: sample_sd={sample_sd}")
            self._log(f"  Step D: Final Output = {output}")
            return output
        # Call original logic, but print for relevant tags/features
        # Only print for tags/features that are failing
        # (You can add more detailed logic here as needed)
        return super()._calc_distributional_measures(
            pos_map_lower_non_punct, feat_map_lower_non_punct, pos_map, feat_map,
            zipf_scores, tokens, doc_len, lang_code, lower_non_punct_tokens
        )

    # Override ratios for verbose tracing
    def _calc_ratios(self, pos_map_lower_non_punct, feat_map_lower_non_punct):
        self._log("\n_calc_ratios called")
        self._log(f"Step A: Input pos_map_lower_non_punct={pos_map_lower_non_punct}")
        stats = {}
        def safe_ratio(numerator, denominator):
            self._log(f"  [safe_ratio] numerator={numerator}, denominator={denominator}")
            output = numerator / denominator if denominator > 0 else 0
            self._log(f"  Step D: Final Output = {output}")
            return output
        def get_cnt(tags):
            if isinstance(tags, str): tags = {tags}
            cnt = sum(len(pos_map_lower_non_punct.get(t, [])) for t in tags)
            self._log(f"  [get_cnt] tags={tags}, count={cnt}")
            return cnt
        # Call original logic, but print for relevant ratios
        # (You can add more detailed logic here as needed)
        return super()._calc_ratios(pos_map_lower_non_punct, feat_map_lower_non_punct)

    # Override Zipf variants for verbose tracing
    def _calc_zipf_variants(self, zipf_scores, tokens, lang_code, doc_len):
        self._log("\n_calc_zipf_variants called")
        self._log(f"Step A: Input zipf_scores={zipf_scores}, tokens={tokens}, lang_code={lang_code}, doc_len={doc_len}")
        stats = {}
        word_counts = Counter(tokens)
        frequencies = np.array(sorted(word_counts.values(), reverse=True))
        self._log(f"Step B: frequencies={frequencies}")
        if len(frequencies) > 1:
            x_min = 1
            freq_above_min = frequencies[frequencies >= x_min]
            n = len(freq_above_min)
            self._log(f"Step B: freq_above_min={freq_above_min}, n={n}")
            if n > 1:
                logs = np.log(freq_above_min / (x_min - 0.5))
                sum_logs = np.sum(logs)
                self._log(f"Step C: logs={logs}, sum_logs={sum_logs}")
                alpha_mle = 1 + n / sum_logs
                self._log(f"Step D: Zipf curve steepness = {alpha_mle}")
                ranks = np.arange(1, len(freq_above_min) + 1)
                theoretical_freqs = 1 / (ranks ** alpha_mle)
                theoretical_freqs = theoretical_freqs * (np.sum(freq_above_min) / np.sum(theoretical_freqs))
                ss_res = np.sum((freq_above_min - theoretical_freqs) ** 2)
                ss_tot = np.sum((freq_above_min - np.mean(freq_above_min)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                self._log(f"Step D: Zipf goodness-of-fit = {max(0, r_squared)}")
        # Call original logic for final output
        return super()._calc_zipf_variants(zipf_scores, tokens, lang_code, doc_len)

# --- STEP 3: Run Debugging ---
def main():
    failed = get_failed_measures()
    if not failed:
        log("No failed measures found.")
        return

    profiler = DebugProfiler()
    nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma', verbose=False, use_gpu=profiler.use_gpu)

    for entry in failed:
        measure = entry['measure']
        sentence = entry['sentence']
        expected = entry['expected']
        actual = entry['actual']
        mapped_key = MEASURE_MAP.get(measure)
        if not mapped_key:
            log(f"\n[SKIP] No mapping for measure '{measure}'")
            continue
        # set current debug target and clear seen messages for fresh output
        profiler._debug_target = mapped_key
        SEEN_MESSAGES.clear()
        SEEN_GROUPS.clear()

        log("\n" + "="*60)
        log(f"DEBUGGING: {measure}")
        log(f"Sentence: {sentence}")
        log(f"Expected: {expected}, Actual: {actual}")
        doc = nlp(sentence)
        # Run the full extractor to get canonical outputs
        # Suppress global _log messages during full extraction to avoid unrelated Zipf/frequency noise
        profiler._suppress_global_logs = True
        stats = profiler._extract_measures(doc, 'en', sentence)
        profiler._suppress_global_logs = False

        # Focused debugging dispatch for different measure types
        dispatched = False
        # 1) Group counts (e.g., 'Grammatical item count')
        if mapped_key.endswith('count'):
            group_name = mapped_key.replace(' count', '')
            # Exact TAG_GROUP
            if group_name in profiler.TAG_GROUPS:
                dbg = profiler.debug_group_count(doc, 'en', group_name)
                dispatched = True
                if dbg is not None:
                    log(f"\n[FOCUSED DEBUG] {mapped_key}: {dbg}")
                else:
                    log(f"\n[ERROR] Could not debug group '{group_name}'")
            else:
                # Maybe it's a single PoS tag like 'NOUN count'
                tag = group_name.upper().split()[0]
                dbg = profiler.debug_pos_count(doc, tag)
                dispatched = True
                if dbg is not None:
                    log(f"\n[FOCUSED DEBUG] {mapped_key}: {dbg}")

        # 2) Burstiness measures
        if not dispatched and 'burstiness' in mapped_key.lower():
            tag_name = mapped_key.replace(' burstiness','')
            # prefer direct tag match
            tag = tag_name.upper()
            dbg = profiler.debug_burstiness_tag(doc, tag)
            dispatched = True
            log(f"\n[FOCUSED DEBUG] {mapped_key}: burstiness={dbg}")

        # 3) Distributional measures (concentration/average position/position SD)
        if not dispatched and (('concentration' in mapped_key.lower()) or ('average position' in mapped_key.lower()) or ('position sd' in mapped_key.lower())):
            tag_name = mapped_key.split()[0]
            tag = tag_name.upper()
            dbg = profiler.debug_distribution_for_tag(doc, tag)
            dispatched = True
            log(f"\n[FOCUSED DEBUG] {mapped_key}: {dbg}")

        # 4) Ratio measures
        if not dispatched and 'ratio' in mapped_key.lower():
            dbg = profiler.debug_ratio(doc, mapped_key)
            dispatched = True
            log(f"\n[FOCUSED DEBUG] {mapped_key}: {dbg}")

        # 5) Zipf / frequency measures
        if not dispatched and ('zipf' in mapped_key.lower() or 'frequency' in mapped_key.lower() or 'contextual diversity' in mapped_key.lower()):
            zipf_dbg = profiler._calc_zipf_variants([], [], 'en', len([w for s in doc.sentences for w in s.words if w.upos not in ('PUNCT','SYM','X')]))
            dispatched = True
            log(f"\n[FOCUSED DEBUG] {mapped_key}: {zipf_dbg}")

        if not dispatched:
            # No focused debug matched; fall back to full stats
            pass

        if mapped_key in stats:
            log(f"\n[RESULT] {mapped_key}: {stats[mapped_key]}")
        else:
            log(f"\n[ERROR] Profiler output does not contain key '{mapped_key}'")

if __name__ == "__main__":
    main()