import sys
import csv
import os
import sklearn
import pytest
import stanza
import threading
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from lid_toolkit.logic.profiler import DeepProfiler



CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lingualyzer_ground_truth_english.csv')
RESULT_CSV_PATH = os.path.join(os.path.dirname(__file__), 'profiler_test_results_english.csv')
TOLERANCE = 1e-2

profiler = DeepProfiler()
# Initialize stanza pipeline once for all tests
nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma', verbose=False, use_gpu=profiler.use_gpu)

# Thread-safe list for results
test_results = []
results_lock = threading.Lock()

# Explicit mapping from CSV measure names to profiler output keys
MEASURE_MAP = {
    'Letter count (Doc)': 'Letter count',
    'Word count (Doc)': 'Word count',
    'Type count (Doc)': 'Type count',
    'Sentence count (Doc)': 'Sentence count',
    'Paragraph count (Doc)': 'Paragraph count',
    'Hapax legomena count (Doc)': 'Hapax legomena count',
    'Hapax legomena incidence (Doc)': 'Hapax legomena incidence',
    'Adjective count (Doc)': 'ADJ count',
    'Adverb count (Doc)': 'ADV count',
    'Interjection count (Doc)': 'INTJ count',
    'Lexical verb count (Doc)': 'VERB count',
    'Noun count (Doc)': 'NOUN count',
    'Proper noun count (Doc)': 'PROPN count',
    'Lexical item count (Doc)': 'Lexical item count',
    'Adposition count (Doc)': 'ADP count',
    'Auxiliary count (Doc)': 'AUX count',
    'Conjunction count (Doc)': 'Conjunction count',
    'Determiner count (Doc)': 'DET count',
    'Numeral count (Doc)': 'NUM count',
    'Particle count (Doc)': 'PART count',
    'Pronoun count (Doc)': 'PRON count',
    'Grammatical item count (Doc)': 'Grammatical item count',
    'Verb count (Doc)': 'Verb_All count',
    'Punctuation count (Doc)': 'PUNCT count',
    'Personal pronoun count (Doc)': 'Personal pronoun count',
    'First person pronoun count (Doc)': 'First person count',
    'Second person pronoun count (Doc)': 'Second person count',
    'Third person pronoun count (Doc)': 'Third person count',
    'Interrogative count (Doc)': 'Interrogative count',
    'Demonstrative count (Doc)': 'Demonstrative count',
    'Singular word count (Doc)': 'Singular count',
    'Plural word count (Doc)': 'Plural count',
    'Indefinite word count (Doc)': 'Indefinite count',
    'Definite word count (Doc)': 'Definite count',
    'Finite verb count (Doc)': 'Finite count',
    'Infinitive verb count (Doc)': 'Infinitive count',
    'Verbal adjective count (Doc)': 'Verbal adjective count',
    'Past tense count (Doc)': 'Past count',
    'Present tense count (Doc)': 'Present count',
    'Passive voice count (Doc)': 'Passive count',
    'Adjective incidence (Doc)': 'ADJ incidence',
    'Adverb incidence (Doc)': 'ADV incidence',
    'Interjection incidence (Doc)': 'INTJ incidence',
    'Lexical verb incidence (Doc)': 'VERB incidence',
    'Noun incidence (Doc)': 'NOUN incidence',
    'Proper noun incidence (Doc)': 'PROPN incidence',
    'Lexical item incidence (Doc)': 'Lexical item incidence',
    'Adposition incidence (Doc)': 'ADP incidence',
    'Auxiliary incidence (Doc)': 'AUX incidence',
    'Conjunction incidence (Doc)': 'Conjunction incidence',
    'Determiner incidence (Doc)': 'DET incidence',
    'Numeral incidence (Doc)': 'NUM incidence',
    'Particle incidence (Doc)': 'PART incidence',
    'Pronoun incidence (Doc)': 'PRON incidence',
    'Grammatical item incidence (Doc)': 'Grammatical item incidence',
    'Verb incidence (Doc)': 'Verb_All incidence',
    'Punctuation incidence (Doc)': 'PUNCT incidence',
    'Personal pronoun incidence (Doc)': 'Personal pronoun incidence',
    'First person pronoun incidence (Doc)': 'First person incidence',
    'Second person pronoun incidence (Doc)': 'Second person incidence',
    'Third person pronoun incidence (Doc)': 'Third person incidence',
    'Interrogative incidence (Doc)': 'Interrogative incidence',
    'Demonstrative incidence (Doc)': 'Demonstrative incidence',
    'Singular word incidence (Doc)': 'Singular incidence',
    'Plural word incidence (Doc)': 'Plural incidence',
    'Indefinite word incidence (Doc)': 'Indefinite incidence',
    'Definite word incidence (Doc)': 'Definite incidence',
    'Finite verb incidence (Doc)': 'Finite incidence',
    'Infinitive verb incidence (Doc)': 'Infinitive incidence',
    'Verbal adjective incidence (Doc)': 'Verbal adjective incidence',
    'Past tense incidence (Doc)': 'Past incidence',
    'Present tense incidence (Doc)': 'Present incidence',
    'Passive voice incidence (Doc)': 'Passive incidence',
    'Adjective type count (Doc)': 'ADJ type count',
    'Adverb type count (Doc)': 'ADV type count',
    'Interjection type count (Doc)': 'INTJ type count',
    'Lexical verb type count (Doc)': 'VERB type count',
    'Noun type count (Doc)': 'NOUN type count',
    'Proper noun type count (Doc)': 'PROPN type count',
    'Lexical item type count (Doc)': 'Lexical item type count',
    'Adposition type count (Doc)': 'ADP type count',
    'Auxiliary type count (Doc)': 'AUX type count',
    'Conjunction type count (Doc)': 'Conjunction type count',
    'Determiner type count (Doc)': 'DET type count',
    'Numeral type count (Doc)': 'NUM type count',
    'Particle type count (Doc)': 'PART type count',
    'Pronoun type count (Doc)': 'PRON type count',
    'Grammatical item type count (Doc)': 'Grammatical item type count',
    'Verb type count (Doc)': 'Verb_All type count',
    'Word length (Doc)': 'Word length',
    'Sentence length (Doc)': 'Sentence length',
    'Paragraph length (Doc)': 'Paragraph length',
    'Type-token ratio (Doc)': 'Type-token ratio',
    'Moving average type-token ratio (Doc)': 'Moving average TTR',
    "Honoré's statistic (Doc)": "Honoré's statistic",
    'Letter entropy (Doc)': 'Letter entropy',
    'Word entropy (Doc)': 'Word entropy',
    'Zipf steepness of curve (Doc)': 'Zipf curve steepness',
    'Zipf goodness of fit (Doc)': 'Zipf goodness-of-fit',
    'Zipf frequency (Doc)': 'Lexical sophistication (Zipf frequency)',
    'Average contextual diversity (Doc)': 'Average contextual diversity',
    'Frequent word count (Doc)': 'Frequent word count',
    'Infrequent word count (Doc)': 'Infrequent word count',
    'Unknown word count (Doc)': 'Unknown word count',
    'Frequent word incidence (Doc)': 'Frequent word incidence',
    'Infrequent word incidence (Doc)': 'Infrequent word incidence',
    'Unknown word incidence (Doc)': 'Unknown word incidence',
    'Word-lemma Levenshtein dist. (Doc)': 'Word-lemma distance (avg)',
    'Word types per lemma (Doc)': 'Word-types per lemma',
    'Word types per lemma (nouns) (Doc)': 'Word-types per lemma (noun)',
    'Word types per lemma (verbs) (Doc)': 'Word-types per lemma (verb)',
    'Word types per lemma (lexical items) (Doc)': 'Word-types per lemma (lexical)',
    'Word types per lemma (grammatical items) (Doc)': 'Word-types per lemma (grammatical)',
    'Adjective length (Doc)': 'ADJ word length',
    'Adverb length (Doc)': 'ADV word length',
    'Interjection length (Doc)': 'INTJ word length',
    'Lexical verb length (Doc)': 'VERB word length',
    'Noun length (Doc)': 'NOUN word length',
    'Proper noun length (Doc)': 'PROPN word length',
    'Lexical item length (Doc)': 'Lexical item word length',
    'Adposition length (Doc)': 'ADP word length',
    'Auxiliary length (Doc)': 'AUX word length',
    'Conjunction length (Doc)': 'Conjunction word length',
    'Determiner length (Doc)': 'DET word length',
    'Numeral length (Doc)': 'NUM word length',
    'Particle length (Doc)': 'PART word length',
    'Pronoun length (Doc)': 'PRON word length',
    'Grammatical item length (Doc)': 'Grammatical item word length',
    'Verb length (Doc)': 'Verb_All word length',
    'Adjective type-token ratio (Doc)': 'ADJ TTR',
    'Adverb type-token ratio (Doc)': 'ADV TTR',
    'Interjection type-token ratio (Doc)': 'INTJ TTR',
    'Lexical verb type-token ratio (Doc)': 'VERB TTR',
    'Noun type-token ratio (Doc)': 'NOUN TTR',
    'Proper noun type-token ratio (Doc)': 'PROPN TTR',
    'Lexical item type-token ratio (Doc)': 'Lexical item TTR',
    'Adposition type-token ratio (Doc)': 'ADP TTR',
    'Auxiliary type-token ratio (Doc)': 'AUX TTR',
    'Conjunction type-token ratio (Doc)': 'Conjunction TTR',
    'Determiner type-token ratio (Doc)': 'DET TTR',
    'Numeral type-token ratio (Doc)': 'NUM TTR',
    'Particle type-token ratio (Doc)': 'PART TTR',
    'Pronoun type-token ratio (Doc)': 'PRON TTR',
    'Grammatical item type-token ratio (Doc)': 'Grammatical item TTR',
    'Verb type-token ratio (Doc)': 'Verb_All TTR',
    'Adverb-adjective ratio (Doc)': 'Adverb-adjective ratio',
    'Interjection-adjective ratio (Doc)': 'Interjection-adjective ratio',
    'Determiner-adjective ratio (Doc)': 'Determiner-adjective ratio',
    'Adjective-noun ratio (Doc)': 'Adjective-noun ratio',
    'Interjection-noun ratio (Doc)': 'Interjection-noun ratio',
    'Proper noun-noun ratio (Doc)': 'Proper noun-noun ratio',
    'Verb-noun ratio (Doc)': 'Verb-noun ratio',
    'Adposition-noun ratio (Doc)': 'Adposition-noun ratio',
    'Conjunction-noun ratio (Doc)': 'Conjunction-noun ratio',
    'Determiner-noun ratio (Doc)': 'Determiner-noun ratio',
    'Numeral-noun ratio (Doc)': 'Numeral-noun ratio',
    'Pronoun-noun ratio (Doc)': 'Pronoun-noun ratio',
    'Adverb-verb ratio (Doc)': 'Adverb-verb ratio',
    'Interjection-verb ratio (Doc)': 'Interjection-verb ratio',
    'Adposition-verb ratio (Doc)': 'Adposition-verb ratio',
    'Conjunction-verb ratio (Doc)': 'Conjunction-verb ratio',
    'Particle-verb ratio (Doc)': 'Particle-verb ratio',
    'Auxiliary-lexical verb ratio (Doc)': 'Auxiliary-lexical verb ratio',
    'Adjective-lexical item ratio (Doc)': 'Adjective-lexical item ratio',
    'Adverb-lexical item ratio (Doc)': 'Adverb-lexical item ratio',
    'Interjection-lexical item ratio (Doc)': 'Interjection-lexical item ratio',
    'Lexical verb-lexical item ratio (Doc)': 'Lexical verb-lexical item ratio',
    'Noun-lexical item ratio (Doc)': 'Noun-lexical item ratio',
    'Proper noun-lexical item ratio (Doc)': 'Proper noun-lexical item ratio',
    'Sub-coordinating conjunction ratio (Doc)': 'Sub-coordinating conjunction ratio',
    'Adposition-determiner ratio (Doc)': 'Adposition-determiner ratio',
    'Pronoun-determiner ratio (Doc)': 'Pronoun-determiner ratio',
    'Proper noun-determiner ratio (Doc)': 'Proper noun-determiner ratio',
    'Proper noun-pronoun ratio (Doc)': 'Proper noun-pronoun ratio',
    'Adposition-grammatical item ratio (Doc)': 'Adposition-grammatical item ratio',
    'Auxiliary-grammatical item ratio (Doc)': 'Auxiliary-grammatical item ratio',
    'Conjunction-grammatical item ratio (Doc)': 'Conjunction-grammatical item ratio',
    'Determiner-grammatical item ratio (Doc)': 'Determiner-grammatical item ratio',
    'Numeral-grammatical item ratio (Doc)': 'Numeral-grammatical item ratio',
    'Particle-grammatical item ratio (Doc)': 'Particle-grammatical item ratio',
    'Pronoun-grammatical item ratio (Doc)': 'Pronoun-grammatical item ratio',
    'Lexical-grammatical item ratio (Doc)': 'Lexical-grammatical item ratio',
    'First person-personal pronoun ratio (Doc)': 'First person-personal pronoun ratio',
    'Second person-personal pronoun ratio (Doc)': 'Second person-personal pronoun ratio',
    'Third person-personal pronoun ratio (Doc)': 'Third person-personal pronoun ratio',
    'First-third person pronoun ratio (Doc)': 'First-third person pronoun ratio',
    'First-second person pronoun ratio (Doc)': 'First-second person pronoun ratio',
    'Second-third person pronoun ratio (Doc)': 'Second-third person pronoun ratio',
    'Plural-singular word ratio (Doc)': 'Plural-singular word ratio',
    'Definite-indefinite word ratio (Doc)': 'Definite-indefinite word ratio',
    'Infinitive-finite verb ratio (Doc)': 'Infinitive-finite verb ratio',
    'Verbal adjective-finite verb ratio (Doc)': 'Verbal adjective-finite verb ratio',
    'Verbal adjective-infinitive verb ratio (Doc)': 'Verbal adjective-infinitive verb ratio',
    'Present-past tense ratio (Doc)': 'Present-past tense ratio',
    'Hapax legomena burstiness (Doc)': 'Hapax legomena burstiness',
    'Adjective burstiness (Doc)': 'ADJ burstiness',
    'Adverb burstiness (Doc)': 'ADV burstiness',
    'Interjection burstiness (Doc)': 'INTJ burstiness',
    'Lexical verb burstiness (Doc)': 'VERB burstiness',
    'Noun burstiness (Doc)': 'NOUN burstiness',
    'Proper noun burstiness (Doc)': 'PROPN burstiness',
    'Lexical item burstiness (Doc)': 'Lexical item burstiness',
    'Adposition burstiness (Doc)': 'ADP burstiness',
    'Auxiliary burstiness (Doc)': 'AUX burstiness',
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
    'Interrogative burstiness (Doc)': 'Interrogative burstiness',
    'Demonstrative burstiness (Doc)': 'Demonstrative burstiness',
    'Singular word burstiness (Doc)': 'Singular burstiness',
    'Plural word burstiness (Doc)': 'Plural burstiness',
    'Indefinite word burstiness (Doc)': 'Indefinite burstiness',
    'Definite word burstiness (Doc)': 'Definite burstiness',
    'Finite verb burstiness (Doc)': 'Finite burstiness',
    'Infinitive verb burstiness (Doc)': 'Infinitive burstiness',
    'Verbal adjective burstiness (Doc)': 'Verbal adjective burstiness',
    'Past tense burstiness (Doc)': 'Past burstiness',
    'Present tense burstiness (Doc)': 'Present burstiness',
    'Passive voice burstiness (Doc)': 'Passive burstiness',
    'Frequent word burstiness (Doc)': 'Frequent word burstiness',
    'Infrequent word burstiness (Doc)': 'Infrequent word burstiness',
    'Unknown word burstiness (Doc)': 'Unknown word burstiness',
    'Hapax legomena concentration (Doc)': 'Hapax legomena concentration',
    'Adjective concentration (Doc)': 'ADJ concentration',
    'Adverb concentration (Doc)': 'ADV concentration',
    'Interjection concentration (Doc)': 'INTJ concentration',
    'Lexical verb concentration (Doc)': 'VERB concentration',
    'Noun concentration (Doc)': 'NOUN concentration',
    'Proper noun concentration (Doc)': 'PROPN concentration',
    'Lexical item concentration (Doc)': 'Lexical item concentration',
    'Adposition concentration (Doc)': 'ADP concentration',
    'Auxiliary concentration (Doc)': 'AUX concentration',
    'Conjunction concentration (Doc)': 'Conjunction concentration',
    'Determiner concentration (Doc)': 'DET concentration',
    'Numeral concentration (Doc)': 'NUM concentration',
    'Particle concentration (Doc)': 'PART concentration',
    'Pronoun concentration (Doc)': 'PRON concentration',
    'Grammatical item concentration (Doc)': 'Grammatical item concentration',
    'Verb concentration (Doc)': 'Verb_All concentration',
    'Personal pronoun concentration (Doc)': 'Personal pronoun concentration',
    'First person pronoun concentration (Doc)': 'First person concentration',
    'Second person pronoun concentration (Doc)': 'Second person concentration',
    'Third person pronoun concentration (Doc)': 'Third person concentration',
    'Interrogative concentration (Doc)': 'Interrogative concentration',
    'Demonstrative concentration (Doc)': 'Demonstrative concentration',
    'Singular word concentration (Doc)': 'Singular concentration',
    'Plural word concentration (Doc)': 'Plural concentration',
    'Indefinite word concentration (Doc)': 'Indefinite concentration',
    'Definite word concentration (Doc)': 'Definite concentration',
    'Finite verb concentration (Doc)': 'Finite concentration',
    'Infinitive verb concentration (Doc)': 'Infinitive concentration',
    'Verbal adjective concentration (Doc)': 'Verbal adjective concentration',
    'Past tense concentration (Doc)': 'Past concentration',
    'Present tense concentration (Doc)': 'Present concentration',
    'Passive voice concentration (Doc)': 'Passive concentration',
    'Frequent word concentration (Doc)': 'Frequent word concentration',
    'Infrequent word concentration (Doc)': 'Infrequent word concentration',
    'Unknown word concentration (Doc)': 'Unknown word concentration',
    'Hapax legomena avg position (Doc)': 'Hapax legomena average position',
    'Adjective avg position (Doc)': 'ADJ average position',
    'Adverb avg position (Doc)': 'ADV average position',
    'Interjection avg position (Doc)': 'INTJ average position',
    'Lexical verb avg position (Doc)': 'VERB average position',
    'Noun avg position (Doc)': 'NOUN average position',
    'Proper noun avg position (Doc)': 'PROPN average position',
    'Lexical item avg position (Doc)': 'Lexical item average position',
    'Adposition avg position (Doc)': 'ADP average position',
    'Auxiliary avg position (Doc)': 'AUX average position',
    'Conjunction avg position (Doc)': 'Conjunction average position',
    'Determiner avg position (Doc)': 'DET average position',
    'Numeral avg position (Doc)': 'NUM average position',
    'Particle avg position (Doc)': 'PART average position',
    'Pronoun avg position (Doc)': 'PRON average position',
    'Grammatical item avg position (Doc)': 'Grammatical item average position',
    'Verb avg position (Doc)': 'Verb_All average position',
    'Personal pronoun avg position (Doc)': 'Personal pronoun average position',
    'First person pronoun avg position (Doc)': 'First person average position',
    'Second person pronoun avg position (Doc)': 'Second person average position',
    'Third person pronoun avg position (Doc)': 'Third person average position',
    'Interrogative avg position (Doc)': 'Interrogative average position',
    'Demonstrative avg position (Doc)': 'Demonstrative average position',
    'Singular word avg position (Doc)': 'Singular average position',
    'Plural word avg position (Doc)': 'Plural average position',
    'Indefinite word avg position (Doc)': 'Indefinite average position',
    'Definite word avg position (Doc)': 'Definite average position',
    'Finite verb avg position (Doc)': 'Finite average position',
    'Infinitive verb avg position (Doc)': 'Infinitive average position',
    'Verbal adjective avg position (Doc)': 'Verbal adjective average position',
    'Past tense avg position (Doc)': 'Past average position',
    'Present tense avg position (Doc)': 'Present average position',
    'Passive voice avg position (Doc)': 'Passive average position',
    'Frequent word avg position (Doc)': 'Frequent word average position',
    'Infrequent word avg position (Doc)': 'Infrequent word average position',
    'Unknown word avg position (Doc)': 'Unknown word average position',
    'Hapax legomena position SD (Doc)': 'Hapax legomena position SD',
    'Adjective position SD (Doc)': 'ADJ position SD',
    'Adverb position SD (Doc)': 'ADV position SD',
    'Interjection position SD (Doc)': 'INTJ position SD',
    'Lexical verb position SD (Doc)': 'VERB position SD',
    'Noun position SD (Doc)': 'NOUN position SD',
    'Proper noun position SD (Doc)': 'PROPN position SD',
    'Lexical item position SD (Doc)': 'Lexical item position SD',
    'Adposition position SD (Doc)': 'ADP position SD',
    'Auxiliary position SD (Doc)': 'AUX position SD',
    'Conjunction position SD (Doc)': 'Conjunction position SD',
    'Determiner position SD (Doc)': 'DET position SD',
    'Numeral position SD (Doc)': 'NUM position SD',
    'Particle position SD (Doc)': 'PART position SD',
    'Pronoun position SD (Doc)': 'PRON position SD',
    'Grammatical item position SD (Doc)': 'Grammatical item position SD',
    'Verb position SD (Doc)': 'Verb_All position SD',
    'Personal pronoun position SD (Doc)': 'Personal pronoun position SD',
    'First person pronoun position SD (Doc)': 'First person position SD',
    'Second person pronoun position SD (Doc)': 'Second person position SD',
    'Third person pronoun position SD (Doc)': 'Third person position SD',
    'Interrogative position SD (Doc)': 'Interrogative position SD',
    'Demonstrative position SD (Doc)': 'Demonstrative position SD',
    'Singular word position SD (Doc)': 'Singular position SD',
    'Plural word position SD (Doc)': 'Plural position SD',
    'Indefinite word position SD (Doc)': 'Indefinite position SD',
    'Definite word position SD (Doc)': 'Definite position SD',
    'Finite verb position SD (Doc)': 'Finite position SD',
    'Infinitive verb position SD (Doc)': 'Infinitive position SD',
    'Verbal adjective position SD (Doc)': 'Verbal adjective position SD',
    'Past tense position SD (Doc)': 'Past position SD',
    'Present tense position SD (Doc)': 'Present position SD',
    'Passive voice position SD (Doc)': 'Passive position SD',
    'Frequent word position SD (Doc)': 'Frequent word position SD',
    'Infrequent word position SD (Doc)': 'Infrequent word position SD',
    'Unknown word position SD (Doc)': 'Unknown word position SD',
    'Word overlap count (Sent-Sent Avg)': 'Word overlap (Count)',
    'Word overlap ratio (Sent-Sent Avg)': 'Word overlap (Ratio)',
    'Lemma overlap count (Sent-Sent Avg)': 'Lemma overlap (Count)',
    'Lemma overlap ratio (Sent-Sent Avg)': 'Lemma overlap (Ratio)',
    'PoS overlap count (Sent-Sent Avg)': 'PoS overlap (Count)',
    'PoS overlap ratio (Sent-Sent Avg)': 'PoS overlap (Ratio)',
    'Feature overlap count (Sent-Sent Avg)': 'Feature overlap (Count)',
    'Feature overlap ratio (Sent-Sent Avg)': 'Feature overlap (Ratio)',
    'Levenshtein character dist. (Sent-Sent Avg)': 'Levenshtein character distance',
    'Levenshtein word dist. (Sent-Sent Avg)': 'Levenshtein word distance',
    'Levenshtein lemma dist. (Sent-Sent Avg)': 'Levenshtein lemma distance',
    'Levenshtein PoS dist. (Sent-Sent Avg)': 'Levenshtein PoS distance',
    'Cosine dist. (Sent-Sent Avg)': 'Cosine distance',
}

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
    if measure not in MEASURE_MAP:
        pytest.skip(f"No explicit mapping for measure '{measure}' in MEASURE_MAP")
    stats = get_profiler_stats(sentence)
    mapped_key = MEASURE_MAP[measure]
    if mapped_key not in stats:
        pytest.skip(f"Profiler output does not contain key '{mapped_key}' for measure '{measure}'")
    result = stats[mapped_key]
    try:
        expected = float(value)
        actual = float(result)
        diff = abs(actual - expected)
        # Integer count measures: require exact match
        if measure.lower().endswith("count (doc)") or measure.lower().endswith("count"):
            if int(expected) != int(actual):
                status = "FAIL"
            assert int(expected) == int(actual), f"Mismatch for {measure} (mapped: {mapped_key}) on '{sentence}': got {actual}, expected {expected}"
        else:
            if diff >= TOLERANCE:
                status = "FAIL"
            assert diff < TOLERANCE, f"Mismatch for {measure} (mapped: {mapped_key}) on '{sentence}': got {actual}, expected {expected}"
    except ValueError:
        expected = str(value)
        actual = str(result)
        diff = "N/A"
        if actual != expected:
            status = "FAIL"
        assert actual == expected, f"Mismatch for {measure} (mapped: {mapped_key}) on '{sentence}': got {actual}, expected {expected}"
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




