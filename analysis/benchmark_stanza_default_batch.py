"""Fairness re-run of the annotation throughput benchmark (2026-08-05).

The original benchmark (benchmark_stanza_vs_spacy.py) ran stanza with the
DeepProfiler production overrides tokenize_batch_size=pos_batch_size=batch_size=64,
while spaCy ran at its own default batch size of 256. stanza's default lemma
batch size is 5000, so the production config handicapped its most
batch-sensitive component by ~78x. This script removes that asymmetry:
stanza is run at its library defaults (no batch-size kwargs at all), so the
remaining difference is architectural rather than a tuning choice.

Both frameworks are re-timed in the same process/session so that machine
thermal state is common to both arms. Everything else is identical to the
original: same corpus (100 europarl evaluation-split segments per language,
seed 42, langs en/nl/de/es/fi), CPU single-process, warm-up excluded, model
loading excluded from the timed region.

Component sets are recorded per language so the caption can state exactly what
each framework did (notably: spaCy runs a dependency parser, stanza does not;
stanza runs mwt, spaCy has no such stage).

Writes analysis/bench_results_default_batch_2026-08-05.json.
"""
import json
import pathlib
import platform
import time

import pandas as pd

SC = pathlib.Path(__file__).parent
EURO = pathlib.Path(r"c:/Users/User/OneDrive/Masters/LID_experiments/datasets/02_evaluation_15_cleaned/europarl")
OUT = SC / "bench_results_default_batch_2026-08-05.json"

LANGS = ["en", "nl", "de", "es", "fi"]
N = 100
SEED = 42

STANZA_DIR = r"C:\Users\User\stanza_resources"
SPACY_MODELS = {"en": "en_core_web_sm", "nl": "nl_core_news_sm",
                "de": "de_core_news_sm", "es": "es_core_news_sm",
                "fi": "fi_core_news_sm"}

results = {"meta": {}, "spacy": {}, "stanza_default_batch": {}}


def save():
    OUT.write_text(json.dumps(results, indent=2))


texts = {}
for lang in LANGS:
    f = sorted(EURO.glob(f"{lang}_*.parquet"))[0]
    df = pd.read_parquet(f)
    texts[lang] = df["text"].dropna().astype(str).sample(N, random_state=SEED).tolist()
    print(f"loaded {lang}: {len(texts[lang])} segments, "
          f"{sum(len(t) for t in texts[lang])} chars", flush=True)

# ---------- spaCy: unchanged, as in profiler_knowledge_base._make_pipeline ----------
import spacy

for lang in LANGS:
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
                              "components": nlp.pipe_names,
                              "batch_size": nlp.batch_size}
    save()
    print(f"spacy  {lang}: {dt:8.2f}s  {ntok:7d} tokens  {ntok/dt:9.0f} tok/s "
          f"{nlp.pipe_names} bs={nlp.batch_size}", flush=True)

sp_t = sum(r["seconds"] for r in results["spacy"].values())
sp_k = sum(r["tokens"] for r in results["spacy"].values())
print(f"spaCy TOTAL: {sp_t:.2f}s  {sp_k} tokens  {sp_k/sp_t:.0f} tok/s", flush=True)

# ---------- stanza at LIBRARY DEFAULT batch sizes (the fairness change) ----------
import stanza


def make_stanza(lang):
    """Same processor selection as logic/profiler._make_pipeline, but NO batch
    overrides -- stanza picks its own defaults for every processor."""
    kw = dict(use_gpu=False, verbose=False, dir=STANZA_DIR)
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
    eff = {name: pipe.processors[name].config.get("batch_size")
           for name in pipe.processors}
    _ = pipe([stanza.Document([], text=t) for t in texts[lang][:5]])   # warm-up
    t0 = time.perf_counter()
    out = pipe([stanza.Document([], text=t) for t in texts[lang]])
    dt = time.perf_counter() - t0
    ntok = sum(d.num_tokens for d in out)
    nwords = sum(d.num_words for d in out)
    results["stanza_default_batch"][lang] = {
        "seconds": dt, "tokens": ntok, "words_after_mwt": nwords,
        "tok_per_s": ntok / dt, "components": procs,
        "effective_batch_sizes": eff}
    save()
    print(f"stanza {lang}: {dt:8.2f}s  {ntok:7d} tokens ({nwords} words)  "
          f"{ntok/dt:9.0f} tok/s [{procs}] bs={eff}", flush=True)

st_t = sum(r["seconds"] for r in results["stanza_default_batch"].values())
st_k = sum(r["tokens"] for r in results["stanza_default_batch"].values())
print(f"stanza TOTAL: {st_t:.2f}s  {st_k} tokens  {st_k/st_t:.0f} tok/s", flush=True)

results["meta"] = {
    "date": "2026-08-05",
    "purpose": "fairness re-run: stanza at library-default batch sizes",
    "spacy_version": spacy.__version__,
    "stanza_version": stanza.__version__,
    "platform": platform.processor(),
    "n_segments_per_lang": N, "seed": SEED, "langs": LANGS,
    "spacy_total_seconds": sp_t, "spacy_total_tokens": sp_k,
    "spacy_tok_per_s": sp_k / sp_t,
    "stanza_total_seconds": st_t, "stanza_total_tokens": st_k,
    "stanza_tok_per_s": st_k / st_t,
    "speedup": st_t / sp_t,
}
save()
print(f"\nSPEEDUP (stanza time / spaCy time): {st_t / sp_t:.1f}x", flush=True)
