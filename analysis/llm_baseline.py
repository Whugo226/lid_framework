"""llm_baseline.py — LLM-recommendation baseline for EQ3.

Simulates the practitioner who, instead of using the framework, asks a
general-purpose AI assistant which LID model to deploy. Fairness protocol:

  GIVEN to the LLM (what a practitioner cheaply has):
    - the candidate model inventory: 6 trained configurations x 17 training
      corpora (with one-line register descriptions) + 3 zero-shot detectors
    - a profile of the query corpus computed from the evaluation split only:
      ISO language list, text-length statistics, and N seeded sample texts
  WITHHELD from the LLM (the framework's actual evidence advantage):
    - all benchmark performance numbers
    - the query corpus's name/identity
    - the framework's linguistic fingerprints and MKB

The LLM must nominate exactly one candidate (structured output constrains the
answer to the candidate list). The choice is scored against the same ground
truth as the framework: gap = ground-truth best f1_weighted minus the chosen
variant's f1_weighted on the evaluation split.

Requires: ANTHROPIC_API_KEY (or an `ant auth login` profile) and internet
access — run LOCALLY, not on the HPC.

Usage:
    python analysis/llm_baseline.py [--report PATH] [--eval-dir PATH]
                                    [--n-samples 10] [--model claude-opus-4-8]
                                    [--dry-run]

--dry-run prints the prompts without calling the API.
"""
import argparse
import json
import random
import re
from pathlib import Path

import pandas as pd

TOOLKIT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = TOOLKIT / "validation_report.json"
DEFAULT_EVAL_DIR = Path(
    r"c:/Users/User/OneDrive/Masters/LID_experiments/datasets/02_evaluation_15_cleaned"
)
SEED = 42

# Canonical candidate space shown to the LLM: 6 trained configs x 17 corpora
# + 3 zero-shot detectors. Zero-shot keys in the benchmark records carry
# per-dataset suffixes (e.g. "lid.176_<dataset>"); we present the canonical
# name and map back to the dataset-local key when scoring.
TRAINED_CONFIGS = {
    "bow_char_ngram_3_5": "Multinomial Naive Bayes, bag-of-words counts of character 3-5-grams",
    "tfidf_char_ngram_3_5": "Multinomial Naive Bayes, TF-IDF-weighted character 3-5-grams",
    "bow_maxabs_lr_char_ngram_3_5": "Logistic Regression, MaxAbs-scaled bag-of-words character 3-5-grams",
    "tfidf_lr_char_ngram_3_5": "Logistic Regression, TF-IDF character 3-5-grams",
    "fasttext_word": "FastText classifier, word unigrams only (no subword information)",
    "fasttext_subword": "FastText classifier, character subwords (minn=2, maxn=4) + word bigrams",
}
TRAINING_CORPORA = {
    "OpenLID-v2": "large multi-domain LID benchmark, broad register coverage",
    "amazon_reviews_multi": "product reviews; short, informal consumer text",
    "europarl": "parliamentary proceedings; long, formal, structured sentences",
    "exorde-social-media-december-2024-week1": "social media posts; short, noisy, abbreviations",
    "flores_plus": "professional parallel translations; clean, balanced",
    "language-identification": "general LID evaluation corpus; diverse domains",
    "massive": "virtual-assistant utterances; short, imperative, spoken style",
    "mmarco": "machine-translated query-passage pairs; information-retrieval style",
    "multi_eurlex": "EU legal documents; long, highly technical, formal",
    "multilingual_cc_news": "CommonCrawl news articles; moderate length, formal register",
    "multilingual_toxicity_dataset": "online content with toxicity annotations; noisy",
    "stsb_multi_mt": "semantic-similarity sentence pairs; short, clean",
    "tweet_sentiment_multilingual": "tweets; very short, high noise, emoji-heavy",
    "tydiqa": "typologically diverse question-answering pairs; varied lengths",
    "wikipedia": "encyclopaedic article paragraphs; long, formal",
    "xlsum": "BBC news summaries; moderate length, formal",
    "xnli": "premise-hypothesis pairs; short, clean",
}
ZERO_SHOT = {
    "cld3": "Google Compact Language Detector 3, feed-forward network on byte n-grams (zero-shot, 100+ languages)",
    "lid.176": "pre-trained FastText lid.176 model, 176 languages (zero-shot)",
    "xlm_v_base": "XLM-V Base transformer fine-tuned for language identification (zero-shot; high accuracy, ~300x slower inference)",
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "top_choice": {
            "type": "string",
            "description": "Exactly one candidate ID from the inventory, e.g. "
                           "'fasttext_subword@europarl' or 'lid.176'",
        },
        "ranked_top3": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Top three candidate IDs in preference order (first = top_choice)",
        },
        "reasoning": {"type": "string"},
    },
    "required": ["top_choice", "ranked_top3", "reasoning"],
    "additionalProperties": False,
}


def canonical_candidates() -> list[str]:
    cands = [f"{cfg}@{corpus}" for cfg in TRAINED_CONFIGS for corpus in TRAINING_CORPORA]
    cands += list(ZERO_SHOT)
    return cands


def build_system_prompt() -> str:
    lines = [
        "You are advising an NLP practitioner who must deploy a language "
        "identification (LID) model for a new, unlabelled text corpus. They "
        "have the following inventory of candidate models available and no "
        "time or budget to benchmark them on the new corpus. Recommend the "
        "single candidate most likely to achieve the highest weighted F1 on "
        "the corpus described by the user.",
        "",
        "TRAINED CONFIGURATIONS (each exists trained on each of the 17 corpora below; "
        "candidate ID format: <configuration>@<training-corpus>):",
    ]
    for cfg, desc in TRAINED_CONFIGS.items():
        lines.append(f"  - {cfg}: {desc}")
    lines.append("")
    lines.append("TRAINING CORPORA (register descriptions):")
    for corpus, desc in TRAINING_CORPORA.items():
        lines.append(f"  - {corpus}: {desc}")
    lines.append("")
    lines.append("ZERO-SHOT DETECTORS (candidate ID is the bare name):")
    for name, desc in ZERO_SHOT.items():
        lines.append(f"  - {name}: {desc}")
    lines.append("")
    lines.append(
        "All trained configurations cover the same 24 high-resource languages. "
        "Respond with your single best candidate ID, your top-3 ranking, and "
        "brief reasoning."
    )
    return "\n".join(lines)


def profile_dataset(eval_dir: Path, dataset: str, n_samples: int, rng: random.Random):
    ds_dir = eval_dir / dataset
    files = sorted(ds_dir.glob("*.parquet"))
    langs = sorted({re.match(r"^([a-z]{2,3})_", f.stem).group(1)
                    for f in files if re.match(r"^([a-z]{2,3})_", f.stem)})
    texts, lengths = [], []
    for f in files:
        df = pd.read_parquet(f, columns=["text"])
        col = df["text"].dropna().astype(str)
        lengths.extend(col.str.len().sample(min(len(col), 2000), random_state=SEED).tolist())
        texts.extend(col.sample(min(len(col), 5), random_state=SEED).tolist())
    rng.shuffle(texts)
    samples = [t[:200] for t in texts[:n_samples]]
    s = pd.Series(lengths)
    return {
        "languages": langs,
        "char_len_median": float(s.median()),
        "char_len_q1": float(s.quantile(0.25)),
        "char_len_q3": float(s.quantile(0.75)),
        "samples": samples,
    }


def build_user_prompt(profile: dict) -> str:
    lines = [
        "Corpus profile (computed from an unlabelled sample of the target corpus):",
        f"- Languages detected: {', '.join(profile['languages'])} "
        f"({len(profile['languages'])} languages)",
        f"- Text length per document (characters): median {profile['char_len_median']:.0f}, "
        f"IQR [{profile['char_len_q1']:.0f}, {profile['char_len_q3']:.0f}]",
        "- Example documents (truncated to 200 chars):",
    ]
    for t in profile["samples"]:
        lines.append(f"    - {json.dumps(t, ensure_ascii=False)}")
    lines.append("")
    lines.append("Which candidate should the practitioner deploy?")
    return "\n".join(lines)


def resolve_score_key(choice: str, scores: dict) -> str | None:
    """Map a canonical candidate ID back to the dataset-local benchmark key."""
    if "@" in choice:
        cfg, corpus = choice.split("@", 1)
        for key in scores:
            if key.startswith(cfg) and key.endswith(corpus):
                return key
        return None
    # zero-shot: exact key, or per-dataset suffixed key (e.g. "lid.176_<ds>")
    if choice in scores:
        return choice
    matches = [k for k in scores if k == choice or k.startswith(choice + "_")]
    return matches[0] if len(matches) == 1 else (matches[0] if matches else None)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    ap.add_argument("--eval-dir", type=Path, default=DEFAULT_EVAL_DIR)
    ap.add_argument("--n-samples", type=int, default=10)
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    per = report["per_dataset"] if isinstance(report, dict) else report
    if isinstance(per, dict):
        per = list(per.values())

    system_prompt = build_system_prompt()
    valid = set(canonical_candidates())
    rng = random.Random(SEED)

    if not args.dry_run:
        import anthropic
        client = anthropic.Anthropic()

    results = []
    for d in per:
        dataset = d.get("dataset", d.get("name"))
        profile = profile_dataset(args.eval_dir, dataset, args.n_samples, rng)
        user_prompt = build_user_prompt(profile)

        if args.dry_run:
            print(f"\n===== {dataset} =====\n{user_prompt}")
            continue

        response = client.messages.create(
            model=args.model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=[{"type": "text", "text": system_prompt,
                     "cache_control": {"type": "ephemeral"}}],
            output_config={"format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
            messages=[{"role": "user", "content": user_prompt}],
        )
        if response.stop_reason == "refusal":
            print(f"{dataset}: request refused — skipping")
            continue
        text = next(b.text for b in response.content if b.type == "text")
        answer = json.loads(text)
        choice = answer["top_choice"]

        scores = d["all_benchmark_scores"]
        entry = {
            "dataset": dataset,
            "llm_choice": choice,
            "llm_ranked_top3": answer["ranked_top3"],
            "llm_reasoning": answer["reasoning"],
            "valid_candidate": choice in valid,
            "ground_truth_model": d["ground_truth_model"],
            "ground_truth_score": d["ground_truth_score"],
        }
        key = resolve_score_key(choice, scores)
        if key is None:
            entry["error"] = "choice not resolvable against benchmark scores"
            entry["gap"] = None
        else:
            entry["resolved_key"] = key
            entry["chosen_score"] = scores[key]
            entry["gap"] = d["ground_truth_score"] - scores[key]
            entry["exact_match"] = key == d["ground_truth_model"]
        results.append(entry)
        gap_str = f"{entry['gap']:.4f}" if entry.get("gap") is not None else "n/a"
        print(f"{dataset:45s} -> {choice:45s} gap={gap_str}")

    if args.dry_run:
        print("\n[dry run] no API calls made")
        return

    scored = [r for r in results if r.get("gap") is not None]
    summary = {
        "model": args.model,
        "n_datasets": len(results),
        "n_scored": len(scored),
        "exact_matches": sum(1 for r in scored if r.get("exact_match")),
        "mean_gap": sum(r["gap"] for r in scored) / len(scored) if scored else None,
        "max_gap": max((r["gap"] for r in scored), default=None),
        "median_gap": (sorted(r["gap"] for r in scored)[len(scored) // 2]
                       if scored else None),
        "per_dataset": results,
    }
    out = args.report.parent / "llm_baseline_results.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nexact {summary['exact_matches']}/{summary['n_scored']}  "
          f"mean gap {summary['mean_gap']:.4f}  max gap {summary['max_gap']:.4f}")
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
