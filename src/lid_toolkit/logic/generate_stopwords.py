import requests
import re

def generate_fingerprints():
    # 1. Map Language Codes to the raw text URLs (standardized to HermitDave)
    # I replaced your Wiktionary links with HermitDave raw links for automation ease.
    sources = {
        "af": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/af/af_full.txt",
            "ar": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ar/ar_50k.txt",
            "bg": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/bg/bg_50k.txt",
            "bn": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/bn/bn_50k.txt",
            "br": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/br/br_full.txt",
            "bs": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/bs/bs_50k.txt",
            "ca": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ca/ca_50k.txt",
            "cs": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/cs/cs_50k.txt",
            "da": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/da/da_50k.txt",
            "de": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/de/de_50k.txt",
            "el": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/el/el_50k.txt",
            "en": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_50k.txt",
            "eo": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/eo/eo_full.txt",
            "es": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/es/es_50k.txt",
            "et": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/et/et_50k.txt",
            "eu": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/eu/eu_50k.txt",
            "fa": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/fa/fa_50k.txt",
            "fi": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/fi/fi_50k.txt",
            "fr": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/fr/fr_50k.txt",
            "gl": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/gl/gl_50k.txt",
            "he": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/he/he_50k.txt",
            "hi": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/hi/hi_full.txt",
            "hr": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/hr/hr_50k.txt",
            "hu": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/hu/hu_50k.txt",
            "hy": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/hy/hy_full.txt",
            "id": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/id/id_50k.txt",
            "is": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/is/is_50k.txt",
            "it": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/it/it_50k.txt",
            "ja": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ja/ja_full.txt",
            "ka": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ka/ka_50k.txt",
            "kk": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/kk/kk_full.txt",
            "ko": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ko/ko_50k.txt",
            "lt": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/lt/lt_50k.txt",
            "lv": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/lv/lv_50k.txt",
            "mk": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/mk/mk_50k.txt",
            "ml": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ml/ml_50k.txt",
            "ms": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ms/ms_50k.txt",
            "nl": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/nl/nl_50k.txt",
            "no": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/no/no_50k.txt",
            "pl": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/pl/pl_50k.txt",
            "pt": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/pt/pt_50k.txt",
            "pt_br": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/pt_br/pt_br_50k.txt",
            "ro": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ro/ro_50k.txt",
            "ru": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ru/ru_50k.txt",
            "si": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/si/si_full.txt",
            "sk": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/sk/sk_50k.txt",
            "sl": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/sl/sl_50k.txt",
            "sq": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/sq/sq_50k.txt",
            "sr": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/sr/sr_50k.txt",
            "sv": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/sv/sv_50k.txt",
            "ta": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ta/ta_full.txt",
            "te": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/te/te_full.txt",
            "th": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/th/th_50k.txt",
            "tl": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/tl/tl_full.txt",
            "tr": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/tr/tr_50k.txt",
            "uk": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/uk/uk_50k.txt",
            "ur": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ur/ur_full.txt",
            "vi": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/vi/vi_50k.txt",
            "ze_en": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ze_en/ze_en_50k.txt",
            "ze_zh": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ze_zh/ze_zh_50k.txt",
            "zh_cn": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/zh_cn/zh_cn_50k.txt",
            "zh_tw": "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/zh_tw/zh_tw_50k.txt",
    }

    output_file = "language_fingerprints.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("fingerprints = {\n")
        
        for lang_code, url in sources.items():
            try:
                # Download the file
                response = requests.get(url)
                content = response.text.splitlines()
                
                top_words = set()
                count = 0
                
                # Extract Top 20 valid words
                for line in content:
                    if count >= 20: break
                    
                    parts = line.strip().split(' ')
                    word = parts[0]
                    
                    # Filter out numbers, punctuation, and single letters (except 'a', 'y', etc.)
                    # We want robust "Function Words"
                    if len(word) > 1 and word.isalpha():
                        top_words.add(word.lower())
                        count += 1
                
                # Write formatted Python code to file
                f.write(f'    "lang_{lang_code}": {str(top_words)},\n')
                print(f"Processed {lang_code}")
                
            except Exception as e:
                f.write(f"    # Error processing {lang_code}: {e}\n")
                print(f"Error processing {lang_code}: {e}")

        f.write("}\n")
    
    print(f"\nOutput saved to {output_file}")

if __name__ == "__main__":
    generate_fingerprints()