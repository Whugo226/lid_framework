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

PROVIDER
--------
Uses an OPEN-WEIGHTS model served over an OpenAI-compatible chat-completions
endpoint. Any such host works — Groq, OpenRouter, Together, or a local Ollama
server — selected with --provider. Only `requests` is required; no vendor SDK.

Open weights are the better choice for a thesis baseline regardless of cost: the
model is named, versioned and publicly downloadable, so the comparison is
reproducible by an examiner. A proprietary endpoint can be silently updated,
which would make this row of the baseline table unreproducible.

Set the API key in the environment variable named by --api-key-env (default
follows the chosen provider). Free tiers sufficient for a 17-call run exist for
Groq and OpenRouter; `--provider ollama` needs no key at all.

Usage:
    # free hosted (recommended): get a key at console.groq.com
    set GROQ_API_KEY=...
    python analysis/llm_baseline.py --provider groq

    # fully local, no key, no network
    ollama serve && ollama pull llama3.3:70b
    python analysis/llm_baseline.py --provider ollama

    # any other OpenAI-compatible host
    python analysis/llm_baseline.py --provider custom \
        --base-url https://... --model <id> --api-key-env MY_KEY

--dry-run prints the prompts without calling the API.
"""
import argparse
import json
import os
import random
import re
import time
from pathlib import Path

import pandas as pd
import requests

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

# OpenAI-compatible hosts. `model` is a sensible default that exists on that
# host at the time of writing; override with --model.
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        # gpt-oss-120b: open-weights, 200K tokens/day on the free tier (2x
        # llama-3.3-70b's 100K), which is what a full 17-corpus run needs.
        # This is the PRIMARY baseline: open-weights, versioned, reproducible.
        "model": "openai/gpt-oss-120b",
        "api_key_env": "GROQ_API_KEY",
    },
    "gemini": {
        # Google's OpenAI-compatibility layer — same chat/completions shape, so
        # no new code. SECONDARY robustness check only: Gemini is proprietary and
        # vendor-versioned (and this is a *preview* model), so it is NOT
        # reproducible the way gpt-oss is; report it as a supplementary data
        # point, never as the citable baseline row.
        #
        # A frontier proprietary model, the strongest the account has access to:
        # the check exists to answer "would a stronger model close the gap?", so
        # it uses the best available adversary. gemini-3.5-flash is a STABLE
        # release (not preview), which is marginally better for reproducibility.
        # If even this loses to the framework, the result is about information
        # access (the withheld benchmark records), not model capability.
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-3.5-flash",  # override with --model if the ID 404s
        "api_key_env": "GEMINI_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "api_key_env": "TOGETHER_API_KEY",
    },
    "ollama": {  # local; no key required
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.3:70b",
        "api_key_env": "",
    },
    "custom": {"base_url": "", "model": "", "api_key_env": ""},
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
        "All trained configurations cover the same 24 high-resource languages."
    )
    lines.append("")
    # The literal word "json" must appear in the messages: OpenAI-compatible
    # hosts (Groq among them) reject response_format=json_object without it.
    lines.append(
        "Reply with ONLY a json object, no prose and no code fences, in exactly "
        "this form:"
    )
    lines.append(
        '  {"top_choice": "<candidate ID>", '
        '"ranked_top3": ["<candidate ID>", "<candidate ID>", "<candidate ID>"], '
        '"reasoning": "<one or two sentences>"}'
    )
    lines.append(
        'Each candidate ID must be copied exactly from the inventory above: '
        'either "<configuration>@<training-corpus>" for a trained model '
        '(for example "fasttext_subword@europarl"), or the bare name for a '
        'zero-shot detector (for example "lid.176"). '
        'The first entry of ranked_top3 must equal top_choice.'
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


def call_llm(
    base_url: str,
    model: str,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    valid: set[str],
    temperature: float = 0.0,
    max_attempts: int = 3,
    rate_limit_retries: int = 8,
) -> dict:
    """
    One recommendation from an OpenAI-compatible chat-completions endpoint.

    Open-weights models follow a JSON schema less reliably than a vendor's
    constrained-decoding mode, so validity is enforced here instead: the reply
    must parse as JSON, carry the required keys, and name a candidate that
    exists in the inventory. A failed attempt is fed back to the model as a
    correction turn rather than silently discarded, so a malformed reply costs
    a retry rather than a missing data point.

    Rate-limit (HTTP 429) waits are handled separately from validity retries and
    do NOT consume the validity budget: a per-minute token limit should only ever
    cost time, never a data point. The endpoint's Retry-After header is honoured
    when present. A per-DAY limit cannot be waited out and eventually raises, so
    the caller can record the gap and stop rather than spin forever.
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    def post_with_backoff() -> requests.Response:
        for rl in range(1, rate_limit_retries + 1):
            resp = requests.post(url, headers=headers, json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"},
            }, timeout=180)
            if resp.status_code != 429:
                return resp
            retry_after = resp.headers.get("retry-after")
            wait = float(retry_after) if retry_after else min(2 ** rl * 5, 60)
            print(f"    rate-limited ({rl}/{rate_limit_retries}); waiting {wait:.0f}s")
            time.sleep(wait)
        raise RuntimeError(
            f"still rate-limited after {rate_limit_retries} waits — this is likely "
            f"the daily token cap, which cannot be waited out. Re-run later with "
            f"--resume, or switch --model / --provider."
        )

    last_error = None
    for attempt in range(1, max_attempts + 1):
        resp = post_with_backoff()
        if resp.status_code >= 400:
            raise RuntimeError(f"{resp.status_code} from {url}: {resp.text[:300]}")

        text = resp.json()["choices"][0]["message"]["content"]

        try:
            answer = json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", text, re.S)  # some models fence the JSON
            if not m:
                last_error = "reply was not JSON"
                messages += [
                    {"role": "assistant", "content": text},
                    {"role": "user", "content":
                        "That was not valid JSON. Reply with ONLY a JSON object "
                        'with keys "top_choice", "ranked_top3", "reasoning".'},
                ]
                continue
            answer = json.loads(m.group(0))

        missing = {"top_choice", "ranked_top3", "reasoning"} - set(answer)
        if missing:
            last_error = f"missing keys: {sorted(missing)}"
        elif answer["top_choice"] not in valid:
            last_error = f"'{answer['top_choice']}' is not a candidate ID"
        else:
            answer["_attempts"] = attempt
            return answer

        messages += [
            {"role": "assistant", "content": text},
            {"role": "user", "content":
                f"Invalid response: {last_error}. The candidate ID must appear "
                "exactly as listed in the inventory — either "
                "'<configuration>@<training-corpus>' or a bare zero-shot name. "
                "Reply with ONLY the JSON object."},
        ]

    raise RuntimeError(f"no valid response after {max_attempts} attempts: {last_error}")


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
    ap.add_argument("--provider", choices=sorted(PROVIDERS), default="groq")
    ap.add_argument("--repeats", type=int, default=5,
                    help="draws per dataset; >1 measures the LLM's own variability")
    ap.add_argument("--temperature", type=float, default=0.7,
                    help="use 0.0 with --repeats 1 for a deterministic single-shot run")
    ap.add_argument("--resume", action="store_true",
                    help="skip datasets already complete (n_draws == repeats) in the "
                         "existing results file; only query the missing ones. Lets a "
                         "rate-limited partial run be finished without re-spending calls.")
    ap.add_argument("--model", default=None, help="override the provider default")
    ap.add_argument("--base-url", default=None, help="required for --provider custom")
    ap.add_argument("--api-key-env", default=None, help="env var holding the API key")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    prov = PROVIDERS[args.provider]
    base_url = args.base_url or prov["base_url"]
    model = args.model or prov["model"]
    api_key_env = args.api_key_env if args.api_key_env is not None else prov["api_key_env"]
    api_key = os.environ.get(api_key_env, "") if api_key_env else ""

    if not args.dry_run:
        if not base_url or not model:
            ap.error("--provider custom requires --base-url and --model")
        if api_key_env and not api_key:
            ap.error(
                f"environment variable {api_key_env} is not set. "
                f"Set it, or use --provider ollama to run locally without a key."
            )

    report = json.loads(args.report.read_text(encoding="utf-8"))
    per = report["per_dataset"] if isinstance(report, dict) else report
    if isinstance(per, dict):
        per = list(per.values())

    system_prompt = build_system_prompt()
    valid = set(canonical_candidates())
    rng = random.Random(SEED)

    out = args.report.parent / "llm_baseline_results.json"

    # Resume: carry forward any dataset already complete (full set of draws).
    # A baseline is one model at one draw count; refuse to mix. Carrying draws
    # from a different model or a different --repeats silently contaminates the
    # aggregate, so both must match before anything is reused.
    completed: dict[str, dict] = {}
    if args.resume and out.exists():
        prev = json.loads(out.read_text(encoding="utf-8"))
        prev_model = prev.get("model")
        prev_repeats = prev.get("repeats_per_dataset")
        if prev_model not in (None, model):
            ap.error(
                f"--resume refused: existing results are from model '{prev_model}', "
                f"but this run uses '{model}'. A baseline must be a single model. "
                f"Start fresh (omit --resume; it overwrites), or match --model."
            )
        if prev_repeats not in (None, args.repeats):
            ap.error(
                f"--resume refused: existing results used repeats={prev_repeats}, "
                f"this run uses repeats={args.repeats}. Match --repeats or start fresh."
            )
        for r in prev.get("per_dataset", []):
            if r.get("n_draws", 0) >= args.repeats:
                completed[r["dataset"]] = r
        print(f"resume: {len(completed)} datasets already complete, "
              f"{len(per) - len(completed)} to query")

    if not args.dry_run:
        print(f"provider={args.provider}  model={model}  endpoint={base_url}")

    results = []
    for d in per:
        dataset = d.get("dataset", d.get("name"))

        if dataset in completed:
            results.append(completed[dataset])
            continue

        profile = profile_dataset(args.eval_dir, dataset, args.n_samples, rng)
        user_prompt = build_user_prompt(profile)

        if args.dry_run:
            print(f"\n===== {dataset} =====\n{user_prompt}")
            continue

        scores = d["all_benchmark_scores"]
        draws = []
        for r in range(args.repeats):
            try:
                answer = call_llm(base_url, model, api_key, system_prompt,
                                  user_prompt, valid, temperature=args.temperature)
            except RuntimeError as exc:
                print(f"  {dataset} draw {r + 1}: {exc}")
                continue
            choice = answer["top_choice"]
            key = resolve_score_key(choice, scores)
            draws.append({
                "choice": choice,
                "ranked_top3": answer["ranked_top3"],
                "reasoning": answer["reasoning"],
                "attempts": answer.get("_attempts", 1),
                "resolved_key": key,
                "chosen_score": scores[key] if key else None,
                "gap": (d["ground_truth_score"] - scores[key]) if key else None,
                "exact_match": (key == d["ground_truth_model"]) if key else False,
            })

        scored = [x for x in draws if x["gap"] is not None]
        choices = [x["choice"] for x in draws]
        modal = max(set(choices), key=choices.count) if choices else None
        entry = {
            "dataset": dataset,
            "n_draws": len(draws),
            "n_scored": len(scored),
            # Self-consistency: share of draws landing on the most common choice.
            # 1.0 means the model always gave the same answer.
            "self_consistency": round(choices.count(modal) / len(choices), 3) if choices else None,
            "modal_choice": modal,
            "distinct_choices": sorted(set(choices)),
            # Per-dataset gap is the MEAN over draws: the expected cost of asking
            # an assistant once, not the cost of its luckiest answer.
            "gap": (sum(x["gap"] for x in scored) / len(scored)) if scored else None,
            "gap_min": min((x["gap"] for x in scored), default=None),
            "gap_max": max((x["gap"] for x in scored), default=None),
            "exact_match_rate": (sum(x["exact_match"] for x in scored) / len(scored)) if scored else None,
            "ground_truth_model": d["ground_truth_model"],
            "ground_truth_score": d["ground_truth_score"],
            "draws": draws,
        }
        results.append(entry)
        gap_str = f"{entry['gap']:.4f}" if entry.get("gap") is not None else "n/a"
        print(f"{dataset:45s} -> {str(modal):40s} gap={gap_str} "
              f"consistency={entry['self_consistency']}")

    if args.dry_run:
        print("\n[dry run] no API calls made")
        return

    scored = [r for r in results if r.get("gap") is not None]
    cons = [r["self_consistency"] for r in results if r.get("self_consistency") is not None]
    summary = {
        "provider": args.provider,
        "model": model,
        "base_url": base_url,
        "open_weights": args.provider != "custom",
        "temperature": args.temperature,
        "repeats_per_dataset": args.repeats,
        "total_api_calls": sum(r.get("n_draws", 0) for r in results),
        "seed": SEED,
        "n_datasets": len(results),
        "n_scored": len(scored),
        # Expected exact-match rate over draws, not a count of lucky datasets.
        "mean_exact_match_rate": (
            sum(r["exact_match_rate"] for r in scored) / len(scored) if scored else None
        ),
        "mean_gap": sum(r["gap"] for r in scored) / len(scored) if scored else None,
        "max_gap": max((r["gap"] for r in scored), default=None),
        "median_gap": (sorted(r["gap"] for r in scored)[len(scored) // 2]
                       if scored else None),
        "mean_self_consistency": round(sum(cons) / len(cons), 3) if cons else None,
        "per_dataset": results,
    }
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{summary['total_api_calls']} calls over {summary['n_scored']} datasets "
          f"({args.repeats} draws each, temperature {args.temperature})")
    if summary["mean_gap"] is None:
        print("NO DATASET PRODUCED A SCOREABLE ANSWER — the report below is empty. "
              "Check the errors above before interpreting anything.")
    else:
        print(f"mean gap {summary['mean_gap']:.4f}  max gap {summary['max_gap']:.4f}  "
              f"exact-match rate {summary['mean_exact_match_rate']:.3f}  "
              f"self-consistency {summary['mean_self_consistency']}")
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
