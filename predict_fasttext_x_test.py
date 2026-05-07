import fasttext
import pandas as pd
from pathlib import Path

# configuration copied from DeepProfiler for consistency
MAX_SAMPLES_PER_LANG = 300
SUPPORTED_SPACY_LANGS = {
    'ca', 'zh', 'hr', 'da', 'nl', 'en', 'fi', 'fr', 'de', 'el', 
    'it', 'ja', 'ko', 'lt', 'mk', 'nb', 'pl', 'pt', 'ro', 'ru', 
    'sl', 'es', 'sv', 'uk'
}


def main():
    # locate the fasttext language identification model relative to this file
    base_dir = Path(__file__).parent
    model_path = base_dir / "src" / "lid_toolkit" / "models" / "fasttext" / "lid.176.bin"
    if not model_path.exists():
        raise FileNotFoundError(f"Missing FastText LID model at {model_path}")

    print(f"Loading FastText model from {model_path}...")
    fasttext.FastText.eprint = lambda x: None  # suppress internal warnings
    model = fasttext.load_model(str(model_path))

    input_path = base_dir / "tests" / "data" / "x_test.txt"
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # read sentences (skip empty lines)
    sentences = []
    with input_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                sentences.append(line)

    print(f"Loaded {len(sentences)} sentences from x_test.txt")

    # --- THE FIX: BATCH PREDICTION ---
    # FastText is much happier (and won't crash) when you give it a list
    print("Predicting languages in batch...")
    labels, probs = model.predict(sentences) 
    
    # FastText returns a list of lists when batching
    records = []
    for i in range(len(sentences)):
        lang = labels[i][0].replace("__label__", "")
        conf = float(probs[i][0])
        records.append((sentences[i], lang, conf))

    df = pd.DataFrame(records, columns=["sentence", "predicted_lang_code", "confidence"])

    # filter to supported spaCy languages only
    df_supported = df[df["predicted_lang_code"].isin(SUPPORTED_SPACY_LANGS)].copy()
    # only keep high‑confidence predictions
    CONF_THRESHOLD = 0.95
    df_supported = df_supported[df_supported["confidence"] >= CONF_THRESHOLD]
    print(f"Keeping {len(df_supported)} rows for supported languages (out of {len(df)}) with confidence>={CONF_THRESHOLD}")

    sampled_parts = []
    for lang, group in df_supported.groupby("predicted_lang_code"):
        if len(group) > MAX_SAMPLES_PER_LANG:
            subset = group.sample(n=MAX_SAMPLES_PER_LANG, random_state=42)
            print(f"📊 Profiling '{lang}' (Sampled {MAX_SAMPLES_PER_LANG} of {len(group)} texts)...")
        else:
            subset = group
            print(f"📊 Profiling '{lang}' (100% of {len(group)} detected texts)...")
        sampled_parts.append(subset)

    if sampled_parts:
        final_df = pd.concat(sampled_parts, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=df.columns)

    output_path = base_dir / "fasttext_predictions_hpc.csv"
    final_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Exported sampled predictions to {output_path}")


if __name__ == "__main__":
    main()
