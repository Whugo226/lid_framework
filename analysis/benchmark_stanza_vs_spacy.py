"""Annotation throughput benchmark: stanza vs spaCy, both configured exactly as
the corresponding DeepProfiler implementations configure them.

- stanza:  logic/profiler.py      -> tokenize,mwt,pos,lemma (fallback without mwt),
                                     batch sizes 64, CPU
- spaCy:   profiler_knowledge_base.py -> spacy.load(model, disable=["ner"]) + senter fix

Identical inputs: 100 europarl evaluation-split segments per language,
languages en/nl/de/es/fi, seeded sample. Annotation only (no measure arithmetic).
Results appended to bench_results.json after every language so partial runs survive.
"""
import json
import pathlib
import time

import pandas as pd

SC = pathlib.Path(__file__).parent
EURO = pathlib.Path(r"c:/Users/User/OneDrive/Masters/LID_experiments/datasets/02_evaluation_15_cleaned/europarl")
OUT = SC / "bench_results.json"

LANGS = ["en", "nl", "de", "es", "fi"]
N = 100
SEED = 42

results = {"spacy": {}, "stanza": {}}
if OUT.exists():
    prev = json.loads(OUT.read_text())
    results["spacy"] = prev.get("spacy", {})

def save():
    OUT.write_text(json.dumps(results, indent=2))

texts = {}
for lang in LANGS:
    f = sorted(EURO.glob(f"{lang}_*.parquet"))[0]
    df = pd.read_parquet(f)
    texts[lang] = df["text"].dropna().astype(str).sample(N, random_state=SEED).tolist()
    print(f"loaded {lang}: {len(texts[lang])} segments, "
          f"{sum(len(t) for t in texts[lang])} chars", flush=True)

# ---------- spaCy, as in profiler_knowledge_base._make_pipeline ----------
import spacy

SPACY_MODELS = {"en": "en_core_web_sm", "nl": "nl_core_news_sm",
                "de": "de_core_news_sm", "es": "es_core_news_sm",
                "fi": "fi_core_news_sm"}

for lang in LANGS:
    if lang in results["spacy"]:
        print(f"spacy  {lang}: reusing previous result", flush=True)
        continue
    nlp = spacy.load(SPACY_MODELS[lang], disable=["ner"])
    if "senter" in nlp.disabled:
        nlp.enable_pipe("senter")
    elif "senter" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")
    _ = list(nlp.pipe(texts[lang][:5]))                      # warm-up
    t0 = time.perf_counter()
    docs = list(nlp.pipe(texts[lang]))
    dt = time.perf_counter() - t0
    ntok = sum(len(d) for d in docs)
    results["spacy"][lang] = {"seconds": dt, "tokens": ntok,
                              "tok_per_s": ntok / dt,
                              "components": nlp.pipe_names}
    save()
    print(f"spacy  {lang}: {dt:8.2f}s  {ntok:7d} tokens  {ntok/dt:9.0f} tok/s "
          f"{nlp.pipe_names}", flush=True)

sp_t = sum(r["seconds"] for r in results["spacy"].values())
sp_k = sum(r["tokens"] for r in results["spacy"].values())
print(f"spaCy TOTAL: {sp_t:.2f}s  {sp_k} tokens  {sp_k/sp_t:.0f} tok/s", flush=True)

# ---------- stanza, as in logic/profiler._make_pipeline ----------
import stanza

STANZA_DIR = r"C:\Users\User\stanza_resources"

def make_stanza(lang):
    kw = dict(tokenize_batch_size=64, pos_batch_size=64, batch_size=64,
              use_gpu=False, verbose=False, dir=STANZA_DIR)
    for procs in ("tokenize,mwt,pos,lemma", "tokenize,pos,lemma"):
        try:
            return stanza.Pipeline(lang=lang, processors=procs,
                                   download_method=None, **kw), procs
        except Exception as e:
            print(f"   [{lang}] offline load failed for '{procs}': {e}", flush=True)
    for procs in ("tokenize,mwt,pos,lemma", "tokenize,pos,lemma"):
        try:
            return stanza.Pipeline(lang=lang, processors=procs, **kw), procs
        except Exception as e:
            print(f"   [{lang}] download-mode load failed for '{procs}': {e}", flush=True)
    raise RuntimeError(f"could not build stanza pipeline for {lang}")

for lang in LANGS:
    pipe, procs = make_stanza(lang)
    _ = pipe([stanza.Document([], text=t) for t in texts[lang][:5]])   # warm-up
    t0 = time.perf_counter()
    out = pipe([stanza.Document([], text=t) for t in texts[lang]])
    dt = time.perf_counter() - t0
    ntok = sum(d.num_tokens for d in out)
    results["stanza"][lang] = {"seconds": dt, "tokens": ntok,
                               "tok_per_s": ntok / dt,
                               "components": procs}
    save()
    print(f"stanza {lang}: {dt:8.2f}s  {ntok:7d} tokens  {ntok/dt:9.0f} tok/s "
          f"[{procs}]", flush=True)

st_t = sum(r["seconds"] for r in results["stanza"].values())
st_k = sum(r["tokens"] for r in results["stanza"].values())
print(f"stanza TOTAL: {st_t:.2f}s  {st_k} tokens  {st_k/st_t:.0f} tok/s", flush=True)
print(f"\nspeed ratio (tok/s, spaCy / stanza): {(sp_k/sp_t)/(st_k/st_t):.1f}x", flush=True)
