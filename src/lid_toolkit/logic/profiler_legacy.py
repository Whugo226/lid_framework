"""Data profiling utilities for analyzing DataFrames with linguistic feature extraction."""

import pandas as pd
import numpy as np
import re
from typing import Dict, Any, Optional, Set

class DataFrameProfiler:
    """A class that analyzes a DataFrame and returns profiling information as a dictionary."""
    
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe
    
    def profile(self, text_column: Optional[str] = None) -> Dict[str, Any]:
        # Green AI: Only scan relevant columns for missing values
        cols_to_scan = [text_column] if text_column else self.dataframe.columns

        profile_dict = {
            "shape": self.dataframe.shape,
            "columns": {col: str(dtype) for col, dtype in self.dataframe.dtypes.items()},
            # Optimization: Restrict missing value scan
            "missing_values": self._get_missing_values(cols_to_scan),
            "duplicate_rows": int(self.dataframe.duplicated().sum()),
            "memory_usage": self.dataframe.memory_usage(deep=True).to_dict(),
            "basic_stats": self.dataframe.describe().to_dict(),
        }

        if text_column and text_column in self.dataframe.columns:
            profile_dict["text_stats"] = self._get_text_surface_features(text_column)
            
        return profile_dict
    
    def _get_missing_values(self, columns: list) -> Dict[str, Dict[str, Any]]:
        """Calculate missing values only for the requested columns."""
        missing_dict = {}
        for column in columns:
            if column in self.dataframe.columns:
                missing_count = self.dataframe[column].isna().sum()
                missing_percent = (missing_count / len(self.dataframe)) * 100
                missing_dict[column] = {
                    "count": int(missing_count),
                    "percentage": round(missing_percent, 2)
                }
        return missing_dict
    
    def _get_sampling_subset(self, series: pd.Series, limit: int = 10000) -> pd.Series:
            """Helper to safely sample large datasets to ensure O(1) performance."""
            if len(series) > limit:
                return series.sample(limit, random_state=42)
            return series


    def _calculate_entropy_gini_features(self, text_series: pd.Series) -> dict:
        """
        Calculate Shannon entropy and Gini Impurity safely using sampling.
        """
        sample = self._get_sampling_subset(text_series)

        # Concatenate only the sample
        all_text = ''.join(sample.astype(str))
        
        if len(all_text) == 0:
            return {"character_entropy": 0.0, "gini_impurity": 0.0}
        
        # Calculate character frequency distribution
        # list() is still expensive but acceptable on a capped sample size
        char_counts = pd.Series(list(all_text)).value_counts()
        total_chars = char_counts.sum()
        char_probs = char_counts / total_chars
        
        # Shannon entropy
        entropy = -np.sum(char_probs * np.log2(char_probs))
        
        # Gini Impurity (Diversity Index): 1 - sum(p^2)
        # High Impurity = High Diversity (Randomness)
        gini_impurity = 1 - np.sum(char_probs ** 2)
        
        return {
            "character_entropy": round(float(entropy), 4),
            "gini_impurity": round(float(gini_impurity), 4)
        }
    
    def _get_script_features(self, text_series: pd.Series) -> dict:
        """
        Extract unicode script distribution, script mixing ratio, and emoji ratio.
        Uses Vectorized Regex for O(1) speed relative to row count.
        """
        sample = self._get_sampling_subset(text_series)

        total_rows = len(sample)
        if total_rows == 0:
            return {"script_mixing_ratio": 0.0, "emoji_ratio": 0.0}

        # Calculate total characters once for ratios
        # Note: We use str.len() which is vectorized
        char_lens = sample.str.len()
        total_chars = char_lens.sum()
        if total_chars == 0: return {}

        # 2. Define Regex Patterns for Major Scripts (The "Green" Way)
        # This replaces the massive _get_unicode_script checks
        patterns = {
            "latin_ratio": r'[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]',
            "cyrillic_ratio": r'[\u0400-\u04FF\u0500-\u052F]',
            "greek_ratio": r'[\u0370-\u03FF\u1F00-\u1FFF]',
            "arabic_ratio": r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]',
            "hebrew_ratio": r'[\u0590-\u05FF]',
            "armenian_ratio": r'[\u0530-\u058F]',
            "georgian_ratio": r'[\u10A0-\u10FF]',
            "devanagari_ratio": r'[\u0900-\u097F]',
            "bengali_ratio": r'[\u0980-\u09FF]',
            "gurmukhi_ratio": r'[\u0A00-\u0A7F]',
            "gujarati_ratio": r'[\u0A80-\u0AFF]',
            "oriya_ratio": r'[\u0B00-\u0B7F]',
            "tamil_ratio": r'[\u0B80-\u0BFF]',
            "telugu_ratio": r'[\u0C00-\u0C7F]',
            "kannada_ratio": r'[\u0C80-\u0CFF]',
            "malayalam_ratio": r'[\u0D00-\u0D7F]',
            "sinhala_ratio": r'[\u0D80-\u0DFF]',
            "thai_ratio": r'[\u0E00-\u0E7F]',
            "lao_ratio": r'[\u0E80-\u0EFF]',
            "tibetan_ratio": r'[\u0F00-\u0FFF]',
            "myanmar_ratio": r'[\u1000-\u109F]',
            "khmer_ratio": r'[\u1780-\u17FF]',
            "mongolian_ratio": r'[\u1800-\u18AF]',
            "cjk_ratio": r'[\u4E00-\u9FFF\u3400-\u4DBF]',
            "hiragana_ratio": r'[\u3040-\u309F]',
            "katakana_ratio": r'[\u30A0-\u30FF]',
            "hangul_ratio": r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]',
            "emoji_ratio": r'[\U0001F000-\U0001F9FF\U0001F600-\U0001F64F]'
        }
        
        script_stats = {}
        
        # Track mixing: Boolean DataFrame (Rows x Scripts)
        row_has_script = pd.DataFrame(index=sample.index)

        for stat_name, regex in patterns.items():
            # A. Global Ratio (Total script chars / Total chars)
            # This runs ONE check across the whole column instantly
            count = sample.str.count(regex).sum()
            script_stats[stat_name] = round(count / total_chars, 4)
            
            # B. Row Presence (For mixing ratio)
            if stat_name != "emoji_ratio":
                row_has_script[stat_name] = sample.str.contains(regex, regex=True)

        # 3. Calculate Script Mixing Ratio
        # Count how many distinct scripts appear in each row
        scripts_per_row = row_has_script.sum(axis=1)
        
        # A row is "Mixed" if it contains >1 script
        mixed_rows_count = (scripts_per_row > 1).sum()
        script_stats["script_mixing_ratio"] = round(mixed_rows_count / total_rows, 4)
        
        return script_stats
    

    def _get_lexical_features(self, text_series: pd.Series) -> dict:
        """Extract vocabulary richness (TTR, Hapax) and Web markers."""
        sample = self._get_sampling_subset(text_series)
        
        # Tokenize (split by whitespace)
        # We join and split to get a global bag of words for the sample
        all_text = ' '.join(sample.astype(str))
        tokens = all_text.split()
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return {"type_token_ratio": 0.0, "hapax_legomena_ratio": 0.0, "mean_word_length": 0.0}

        # 1. Type-Token Ratio (Vocabulary Diversity)
        # Using a Series for value_counts is fast enough for 10k rows of text
        token_series = pd.Series(tokens)
        token_counts = token_series.value_counts()
        unique_tokens = len(token_counts)
        ttr = unique_tokens / total_tokens

        # 2. Hapax Legomena (Words appearing exactly once)
        # These are "rare" words. High ratio = very complex/diverse text.
        hapax_count = (token_counts == 1).sum()
        hapax_ratio = hapax_count / total_tokens

        # 3. Mean Word Length (Morphology)
        char_count = sample.str.len().sum()
        whitespace_count = sample.str.count(r'\s').sum()
        avg_word_len = (char_count - whitespace_count) / total_tokens
        
        # 4. URL Ratio (Web Noise)
        url_count = sample.str.count(r'http[s]?://').sum()
        url_ratio = url_count / len(sample)

        # --- NEW: Rix / Long Word Metrics (Morphological Complexity) ---
        # We define a "Long Word" as having > 6 characters (Standard Rix definition)
        # Vectorized check on the token series
        token_series = pd.Series(tokens)
        token_lengths = token_series.str.len()
        
        long_word_count = (token_lengths > 6).sum()
        long_word_ratio = long_word_count / total_tokens

        return {
            "type_token_ratio": round(ttr, 4),
            "hapax_legomena_ratio": round(hapax_ratio, 4),
            "mean_word_length": round(avg_word_len, 2),
            "url_ratio": round(url_ratio, 4),
            "long_word_ratio": round(long_word_ratio, 4)
        }
    

    def _get_language_fingerprints(self, text_series: pd.Series) -> dict:
        """
        Estimate the presence of specific languages using lightweight stopword overlapping.
        This helps distinguish between languages with shared scripts (e.g. English vs Spanish).
        """
        sample = self._get_sampling_subset(text_series)
        
        # 2. Tokenize once (lowercase for matching)
        # Green AI: Simple regex split is faster than NLP library tokenizers
        all_text = ' '.join(sample.astype(str)).lower()
        tokens = re.findall(r'\b\w+\b', all_text)
        token_set = set(tokens) # Hashing for O(1) lookups
        
        if not token_set: return {}

        # 3. Knowledge Base: Top High-Frequency Words
        # PASTE YOUR GENERATED DICTIONARY BELOW
        # ---------------------------------------------------------
        fingerprints = {
        "lang_af": {'nie', 'in', 'van', 'jou', 'te', 'gaan', 'het', 'dit', 'my', 'ek', 'jy', 'vir', 'ons', 'hy', 'en', 'die', 'wat', 'sy', 'is', 'maar'},
        "lang_ar": {'أن', 'ما', 'إلى', 'هل', 'لقد', 'هنا', 'على', 'من', 'هو', 'لم', 'ماذا', 'ذلك', 'كان', 'هذه', 'أنا', 'لا', 'في', 'هذا', 'أنت', 'يا'},
        "lang_bg": {'за', 'да', 'от', 'ще', 'но', 'го', 'си', 'съм', 'ли', 'какво', 'трябва', 'те', 'на', 'аз', 'се', 'не', 'че', 'това', 'ти', 'ми'},
        "lang_bn": {'আর', 'সময়', 'সব', 'এখন', 'নয়', 'হল', 'এক', 'মত', 'এর', 'যখন', 'হয়', 'একজন', 'বছর', 'কর', 'ওহ', 'ওর', 'এমন', 'এই', 'উপর', 'বড়'},
        "lang_br": {'eus', 'ma', 'mat', 'eo', 'din', 'ya', 'petra', 'oa', 'da', 'an', 'ar', 'ket', 'ur', 'un', 'en', 'gant', 'ha', 'zo', 'bet', 'ne'},
        "lang_bs": {'nije', 'li', 'sam', 'je', 'ja', 'se', 'za', 'što', 'da', 'na', 'to', 'su', 'ali', 'ti', 'mi', 'si', 'sa', 'šta', 'ne', 'ovo'},
        "lang_ca": {'una', 'la', 'això', 'què', 'és', 'amb', 'el', 'per', 'que', 'les', 'ho', 'els', 'un', 'va', 'en', 'si', 'ha', 'de', 'no', 'com'},
        "lang_cs": {'jsi', 'jo', 'je', 'se', 'ty', 'že', 'na', 'to', 'tak', 'mě', 'do', 'jste', 'jsem', 'ale', 'co', 'mi', 'si', 'já', 'ne', 'jak'},
        "lang_da": {'han', 'der', 'dig', 'at', 'vi', 'det', 'til', 'på', 'er', 'mig', 'for', 'med', 'jeg', 'har', 'og', 'en', 'hvad', 'du', 'ikke', 'så'},
        "lang_de": {'nicht', 'in', 'der', 'das', 'sie', 'es', 'wie', 'er', 'ist', 'ja', 'mit', 'ein', 'zu', 'was', 'wir', 'und', 'die', 'ich', 'du', 'mir'},
        "lang_el": {'τον', 'του', 'και', 'τι', 'για', 'από', 'αυτό', 'ότι', 'μου', 'δεν', 'με', 'είναι', 'να', 'το', 'σε', 'θα', 'την', 'που', 'σου', 'τα'},
        "lang_en": {'he', 'me', 'of', 'in', 'on', 'you', 'that', 'for', 'we', 'my', 'your', 'to', 'do', 'and', 'have', 'is', 'the', 'this', 'what', 'it'},
        "lang_eo": {'ili', 'li', 'la', 'kiel', 'tio', 'vi', 'al', 'sed', 'kaj', 'vin', 'estas', 'en', 'mi', 'ni', 'por', 'ĉi', 'de', 'ne', 'ĉu', 'ke'},
        "lang_es": {'me', 'qué', 'una', 'la', 'es', 'el', 'te', 'se', 'que', 'los', 'con', 'un', 'está', 'en', 'mi', 'por', 'de', 'lo', 'no', 'para'},
        "lang_et": {'ta', 'me', 'on', 'ma', 'mida', 'mis', 'see', 'jah', 'ja', 'kas', 'oma', 'seda', 'ei', 'siis', 'pole', 'aga', 'sa', 'et', 'kui', 'nii'},
        "lang_eu": {'dut', 'baina', 'dago', 'hori', 'zer', 'zure', 'nire', 'behar', 'naiz', 'izan', 'da', 'duzu', 'ez', 'nahi', 'eta', 'bai', 'du', 'bat', 'esan', 'egin'},
        "lang_fa": {'در', 'ما', 'بود', 'با', 'از', 'تو', 'رو', 'اون', 'من', 'تا', 'ها', 'يه', 'نه', 'کنم', 'که', 'باشه', 'اين', 'به', 'هم', 'مي'},
        "lang_fi": {'että', 'on', 'hän', 'oli', 'ja', 'se', 'mutta', 'nyt', 'voi', 'minä', 'ei', 'jos', 'ole', 'vain', 'en', 'mitä', 'olen', 'tämä', 'sen', 'niin'},
        "lang_fr": {'il', 'vous', 'ça', 'une', 'on', 'la', 'je', 'ce', 'que', 'les', 'pour', 'le', 'un', 'en', 'est', 'et', 'pas', 'de', 'ne', 'tu'},
        "lang_gl": {'como', 'ao', 'as', 'ben', 'unha', 'se', 'que', 'da', 'máis', 'do', 'un', 'está', 'en', 'si', 'non', 'por', 'de', 'no', 'os', 'para'},
        "lang_he": {'יש', 'לי', 'של', 'בסדר', 'שלי', 'לך', 'שלך', 'לא', 'את', 'כל', 'כן', 'אני', 'זה', 'אבל', 'עם', 'היא', 'הוא', 'על', 'מה', 'אתה'},
        "lang_hi": {'मत', 'उस', 'और', 'समय', 'तरह', 'कर', 'एक', 'तक', 'वह', 'हम', 'जब', 'अगर', 'घर', 'सब', 'यह', 'आप', 'इस', 'पर', 'अब', 'बस'},
        "lang_hr": {'ga', 'me', 'nije', 'li', 'sam', 'je', 'ja', 'se', 'što', 'za', 'da', 'na', 'to', 'su', 'ali', 'samo', 'ti', 'mi', 'si', 'ne'},
        "lang_hu": {'van', 'vagy', 'csak', 'és', 'el', 'hogy', 'volt', 'igen', 'ez', 'én', 'egy', 'mi', 'meg', 'ha', 'nem', 'is', 'azt', 'de', 'kell', 'az'},
        "lang_hy": {'որ', 'ինձ', 'համար', 'են', 'եք', 'թե', 'այն', 'նչ', 'ու', 'քեզ', 'այդ', 'եմ', 'այս', 'ոչ', 'մի', 'դու', 'իմ', 'էլ', 'նա', 'ես'},
        "lang_id": {'kita', 'mereka', 'dengan', 'bisa', 'yang', 'akan', 'di', 'ada', 'itu', 'untuk', 'aku', 'apa', 'dia', 'tak', 'ini', 'tidak', 'anda', 'kau', 'dan', 'tahu'},
        "lang_is": {'hann', 'hvađ', 'ūetta', 'til', 'ađ', 'ekki', 'er', 'ūér', 'međ', 'ég', 'fyrir', 'af', 'ūađ', 'og', 'um', 'en', 'mér', 'viđ', 'ūú', 'sem'},
        "lang_it": {'il', 'in', 'che', 'ma', 'una', 'la', 'cosa', 'di', 'per', 'ho', 'le', 'con', 'un', 'mi', 'si', 'non', 'ha', 'lo', 'no', 'sono'},
        "lang_ja": {'仕事', '場所', '大丈夫', '時間', '出来', 'あなた', '電話', 'ありがとう', '同じ', '一緒', '本当', 'お前', '必要', 'あんた', 'あの', '自分', '分か', 'ああ', '彼女', '我々'},
        "lang_ka": {'რჲგა', 'ეა', 'ჟთ', 'კაკგჲ', 'ჟვ', 'ჟყმ', 'ნა', 'რთ', 'რვ', 'ჱა', 'ნჲ', 'დჲ', 'მთ', 'ლთ', 'ღვ', 'ნვ', 'ჲრ', 'ფვ', 'მვ', 'აჱ'},
        "lang_kk": {'бар', 'бұл', 'ма', 'оның', 'менің', 'емес', 'жақсы', 'маған', 'бе', 'керек', 'жоқ', 'иә', 'деп', 'ба', 'сен', 'ол', 'не', 'оны', 'сіз', 'мен'},
        "lang_ko": {'이제', '그게', '있어', '지금', '어떻게', '그래', '무슨', '정말', '거야', '있는', '그리고', '내가', '우리', '여기', '그럼', '그냥', '있어요', '제가', '우리가', '하지만'},
        "lang_lt": {'čia', 'kad', 'iš', 'taip', 'jis', 'kaip', 'mes', 'kas', 'mano', 'ar', 'su', 'ką', 'tai', 'man', 'ir', 'bet', 'ne', 'tu', 'gerai', 'aš'},
        "lang_lv": {'tev', 'es', 'jā', 'par', 'kas', 'viņš', 'to', 'ar', 'kā', 'un', 'ka', 'vai', 'man', 'ir', 'tas', 'ko', 'tā', 'tu', 'no', 'uz'},
        "lang_mk": {'за', 'да', 'го', 'ги', 'си', 'од', 'ќе', 'што', 'во', 'дека', 'на', 'јас', 'се', 'не', 'ја', 'како', 'со', 'ти', 'тоа', 'ми'},
        "lang_ms": {'kita', 'mereka', 'yang', 'akan', 'di', 'ada', 'itu', 'untuk', 'saya', 'kamu', 'aku', 'apa', 'dia', 'tak', 'ini', 'tidak', 'kau', 'awak', 'boleh', 'dan'},
        "lang_nl": {'in', 'van', 'ik', 'een', 'niet', 'je', 'te', 'er', 'dat', 'hij', 'het', 'we', 'zijn', 'en', 'wat', 'ze', 'is', 'maar', 'de', 'op'},
        "lang_no": {'han', 'at', 'vi', 'hva', 'det', 'på', 'til', 'er', 'deg', 'for', 'med', 'jeg', 'har', 'og', 'en', 'meg', 'du', 'ikke', 'som', 'så'},
        "lang_pl": {'nie', 'jest', 'go', 'mnie', 'że', 'ja', 'po', 'za', 'na', 'to', 'tego', 'tak', 'do', 'się', 'ale', 'co', 'tym', 'ci', 'mi', 'jak'},
        "lang_pt": {'como', 'bem', 'mas', 'se', 'que', 'da', 'eu', 'uma', 'não', 'em', 'ele', 'do', 'está', 'isso', 'um', 'por', 'de', 'os', 'com', 'para'},
        "lang_pt_br": {'me', 'como', 'bem', 'mas', 'se', 'que', 'você', 'eu', 'uma', 'não', 'em', 'ele', 'do', 'está', 'isso', 'um', 'por', 'de', 'com', 'para'},
        "lang_ro": {'sunt', 'şi', 'la', 'cu', 'ce', 'te', 'mai', 'că', 'asta', 'este', 'să', 'pe', 'nu', 'am', 'un', 'bine', 'ai', 'pentru', 'în', 'de'},
        "lang_ru": {'что', 'она', 'да', 'если', 'ты', 'так', 'как', 'все', 'мне', 'но', 'мы', 'тебя', 'это', 'на', 'нет', 'он', 'меня', 'вы', 'не', 'его'},
        "lang_si": {'එකට', 'ඕන', 'අද', 'අය', 'ඔබ', 'වල', 'වලට', 'ඒක', 'ඇය', 'කරන', 'ඔය', 'ඒකට', 'ඔබට', 'සහ', 'තව', 'මට', 'එක', 'උඹ', 'අර', 'මම'},
        "lang_sk": {'nie', 'čo', 'sme', 'je', 'ja', 'by', 'že', 'na', 'to', 'tak', 'do', 'ste', 'ale', 'mi', 'si', 'sa', 'ako', 'áno', 'tu', 'som'},
        "lang_sl": {'ga', 'in', 'bo', 'pa', 'lahko', 'je', 'se', 'kaj', 'za', 'da', 'na', 'to', 'ti', 'ni', 'si', 'mi', 'so', 'bi', 'ne', 'sem'},
        "lang_sq": {'me', 'ta', 'mirë', 'në', 'unë', 'jo', 'dhe', 'për', 'një', 'te', 'se', 'po', 'që', 'nuk', 'është', 'do', 'më', 'ka', 'ti', 'të'},
        "lang_sr": {'nije', 'li', 'sam', 'je', 'ja', 'se', 'za', 'što', 'da', 'na', 'to', 'su', 'ali', 'ti', 'mi', 'si', 'sa', 'šta', 'ne', 'ovo'},
        "lang_sv": {'är', 'han', 'inte', 'vi', 'vad', 'det', 'på', 'jag', 'mig', 'här', 'med', 'att', 'om', 'har', 'en', 'för', 'du', 'och', 'var', 'som'},
        "lang_tl": {'kung', 'ito', 'at', 'lang', 'mga', 'hindi', 'na', 'ba', 'mo', 'ka', 'ako', 'sa', 'si', 'isang', 'ang', 'ay', 'ng', 'ko', 'siya', 'para'},
        "lang_tr": {'bir', 'hayır', 'ben', 'çok', 'daha', 'da', 'evet', 'değil', 'için', 'mi', 've', 'ama', 'bu', 'şey', 'kadar', 'de', 'ne', 'var', 'sen', 'mı'},
        "lang_uk": {'что', 'за', 'ты', 'так', 'він', 'все', 'це', 'як', 'ви', 'это', 'мене', 'що', 'тебе', 'на', 'мені', 'он', 'до', 'не', 'ти', 'ми'},
        "lang_ur": {'آپ', 'سے', 'کو', 'ہے', 'ہم', 'ہیں', 'کیا', 'وہ', 'میں', 'یہ', 'تم', 'کر', 'اور', 'ہو', 'نے', 'ایک', 'کی', 'اس', 'نہیں', 'کے'},
        "lang_vi": {'ta', 'rồi', 'chúng', 'và', 'của', 'đã', 'sẽ', 'tôi', 'đi', 'làm', 'có', 'phải', 'một', 'gì', 'là', 'cô', 'không', 'được', 'anh', 'đó'},
        "lang_zh_cn": {'现在', '可以', '没有', '就是', 'you', '我们', '怎么', '他们', '你们', '如果', '自己', '这样', 'to', '什么', '这个', '一个', 'the', '不是', '这里', '知道'},
        "lang_zh_tw": {'可以', '就是', '我們', '怎麼', '一個', '你們', '這是', '如果', '自己', '現在', '什么', '什麼', '真的', '不會', '這個', '他們', '這樣', '不是', '知道', '因為'},
        }

        # ---------------------------------------------------------

        lang_stats = {}

        # 4. Calculate Overlap (Jaccard-ish proxy)
        for lang, stopwords in fingerprints.items():
            # Count how many of this language's top words appear in the dataset
            overlap_count = len(token_set.intersection(stopwords))
            
            # Normalize: What % of the "fingerprint" was found?
            # 1.0 = Strong signal (All top words present)
            if overlap_count > 0:
                lang_stats[f"{lang}_signal"] = round(overlap_count / len(stopwords), 2)

        return lang_stats    

    
    def _get_text_surface_features(self, column: str) -> Dict[str, float]:
        """Extract statistical surface features from a specific text column."""
        series = self.dataframe[column].dropna().astype(str)
        total_rows = len(series)
        
        if total_rows == 0:
            return {}

        # --- Basic Vectorized Metrics ---
        char_counts = series.str.len()
        safe_char_counts = char_counts.replace(0, 1)

        mean_char_len = float(char_counts.mean())
        len_variance = float(char_counts.std())
        
        token_counts = series.str.split().str.len()
        mean_token_count = float(token_counts.mean())
        
        whitespace_counts = series.str.count(r'\s')
        whitespace_ratio = float((whitespace_counts / safe_char_counts).mean())
        
        digit_counts = series.str.count(r'\d')
        digit_density = float((digit_counts / safe_char_counts).mean())
        
        symbol_counts = series.str.count(r'[^\w\s]')
        alpha_counts = series.str.count(r'\w')
        safe_alpha_counts = alpha_counts.replace(0, 1)
        symbol_density = float((symbol_counts / safe_alpha_counts).mean())

        # --- Information Theoretic Features ---
        entropy_stats = self._calculate_entropy_gini_features(series)
        
        # --- Script and Unicode Features ---
        script_stats = self._get_script_features(series)


        # --- Lexical Features ---
        lexical_stats = self._get_lexical_features(series)

        return {
            "num_rows": total_rows,   # <--- Added critical feature
            "mean_char_length": round(mean_char_len, 2),
            "length_variance": round(len_variance, 2),
            "mean_token_count": round(mean_token_count, 2),
            "symbol_density": round(symbol_density, 4),
            "digit_density": round(digit_density, 4),
            "whitespace_ratio": round(whitespace_ratio, 4),
            **entropy_stats,  # Unpack dictionary directly
            **script_stats,  # Unpack script statistics
            **lexical_stats   # Unpack lexical statistics
        }