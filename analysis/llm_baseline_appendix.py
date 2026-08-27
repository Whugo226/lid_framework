"""
llm_baseline_appendix.py

GENERATES THE REPRODUCIBILITY APPENDIX FOR THE LLM RECOMMENDATION BASELINE.

The LLM row of Table `tab:baseline_comparison` is the one baseline a later
reader cannot re-derive from a committed artifact alone, because it depends on
prompts that live in code and on a remote inference endpoint.  This script
emits the material that closes that gap: the run configuration actually used,
the system prompt verbatim, a worked example of a user prompt, and the
per-corpus outcome of every draw.

Emits a .tex fragment for pasting between the AUTO-GENERATED markers of
    Thesis Template Legit/appendices/llm_baseline_appendix.tex
exactly as analysis/stratum_audit.py does for the stratum audit. (A superseded
pre-promotion snapshot also exists at drafts/llm_baseline_appendix.tex; it is
archived and must not be updated.)

TWO FIDELITY NOTES
------------------
1. The system prompt is pure ASCII and is reproduced byte-for-byte.  Its long
   lines are wrapped by `listings` for the page; no characters are altered.

2. The user prompt embeds ten sample documents drawn from the query corpus.
   These span Greek and Cyrillic script among others, which pdflatex cannot
   typeset without additional font support.  Samples that are ASCII-safe are
   reproduced verbatim; the remainder are replaced by a marked placeholder
   that records the script involved.  The full prompts for all 17 corpora can
   be regenerated in one command with no API key and no network call:

       python analysis/llm_baseline.py --dry-run

Reads only committed artifacts; writes one .tex fragment. Modifies nothing else.

Run (repo root, thesis_final):
    python analysis/llm_baseline_appendix.py
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "analysis"))

import llm_baseline as lb  # noqa: E402

RESULTS = REPO / "llm_baseline_gptoss.json"
DEFAULT_OUT = REPO / "analysis" / "llm_baseline_appendix_tables.tex"
LST_OPTS = (
    "basicstyle=\\ttfamily\\scriptsize,breaklines=true,breakindent=0pt,"
    "columns=fullflexible,frame=single,framesep=4pt,xleftmargin=0pt"
)


def tex(s: str) -> str:
    """Escape a plain string for a LaTeX tabular cell."""
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"),
                 ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def breakable(s: str) -> str:
    """
    Escape for a tabular cell and permit line breaks inside long identifiers.
    Candidate IDs run to 55 characters and will not wrap on their own, which
    overflows the page by ~200pt in a plain tabular.
    """
    out = tex(s)
    for sep in (r"\_", "@", "-"):
        out = out.replace(sep, sep + r"\allowbreak{}")
    return out


def script_of(text: str) -> str:
    """
    Describe why a line cannot be printed: the script of its first non-ASCII
    character. Accented Latin is called out as such, since unaccented Latin
    samples ARE reproduced and the distinction would otherwise look arbitrary.
    """
    for ch in text:
        if ord(ch) > 127:
            try:
                script = unicodedata.name(ch).split()[0].title()
            except ValueError:
                break
            return "accented Latin" if script == "Latin" else f"{script} script"
    return "non-ASCII"


def safe_prompt_lines(prompt: str) -> list[str]:
    """User prompt with non-ASCII sample lines replaced by a marked placeholder."""
    out = []
    for line in prompt.split("\n"):
        if any(ord(c) > 127 for c in line):
            stripped = line.strip()
            n = len(stripped) - len("- ") if stripped.startswith("- ") else len(stripped)
            out.append(
                f"    - [sample of {n} chars in {script_of(line)}, "
                f"omitted from print; see --dry-run]"
            )
        else:
            out.append(line)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=RESULTS)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    res = json.loads(args.results.read_text(encoding="utf-8"))
    report = json.loads((REPO / "validation_report.json").read_text(encoding="utf-8"))

    # Regenerate the prompts exactly as the recorded run built them: one RNG
    # seeded once, datasets consumed in report order, so the first dataset's
    # profile is reproduced bit-for-bit.
    system_prompt = lb.build_system_prompt()
    example_dataset = report["per_dataset"][0]["dataset"]
    rng = random.Random(lb.SEED)
    profile = lb.profile_dataset(lb.DEFAULT_EVAL_DIR, example_dataset, 10, rng)
    user_prompt = lb.build_user_prompt(profile)

    L: list[str] = []
    L.append("% ── AUTO-GENERATED by analysis/llm_baseline_appendix.py — do not edit by hand ──")
    L.append(f"% Source artifact: {args.results.name}")
    L.append(f"% Prompts regenerated from analysis/llm_baseline.py (seed {lb.SEED})")
    L.append("")

    # ── Run configuration ────────────────────────────────────────────────
    L.append(r"\begin{table}[H]")
    L.append(r"    \mytable")
    L.append(r"    \caption{Run configuration for the language-model recommendation "
             r"baseline, as recorded in the results artifact.}")
    L.append(r"    \label{tab:llm_run_config}")
    L.append(r"    \begin{tabular}{|l|l|}")
    L.append(r"        \hline")
    L.append(r"        \textbf{Setting} & \textbf{Value} \\")
    L.append(r"        \hline")
    for label, value in [
        ("Model", f"\\texttt{{{tex(res['model'])}}}"),
        ("Weights", "Open, publicly versioned" if res["open_weights"] else "Proprietary"),
        ("Inference host", f"\\texttt{{{tex(res['provider'])}}}"),
        ("Endpoint", f"\\texttt{{{tex(res['base_url'])}}}"),
        ("Temperature", f"{res['temperature']}"),
        ("Draws per corpus", f"{res['repeats_per_dataset']}"),
        ("Corpora queried", f"{res['n_datasets']}"),
        ("Total API calls", f"{res['total_api_calls']}"),
        ("Sampling seed", f"{res['seed']}"),
        ("Candidates offered", "105"),
        ("Sample documents per prompt", "10, truncated to 200 characters"),
    ]:
        L.append(f"        {label} & {value} \\\\")
        L.append(r"        \hline")
    L.append(r"    \end{tabular}")
    L.append(r"\end{table}")
    L.append("")

    # ── System prompt ────────────────────────────────────────────────────
    L.append(r"\subsection*{System prompt}")
    L.append("")
    L.append(r"The system prompt is identical for all 17 corpora and all 51 calls. It "
             r"is reproduced verbatim; long lines are wrapped for the page.")
    L.append("")
    L.append(f"\\begin{{lstlisting}}[{LST_OPTS}]")
    L.extend(system_prompt.split("\n"))
    L.append(r"\end{lstlisting}")
    L.append("")

    # ── Example user prompt ──────────────────────────────────────────────
    L.append(r"\subsection*{Example user prompt}")
    L.append("")
    L.append(r"One user prompt is built per corpus from its evaluation split alone. "
             r"The example below is the prompt for \texttt{" + tex(example_dataset) +
             r"}, regenerated from the same seed as the recorded run.")
    L.append("")
    L.append(f"\\begin{{lstlisting}}[{LST_OPTS}]")
    L.extend(safe_prompt_lines(user_prompt))
    L.append(r"\end{lstlisting}")
    L.append("")

    # ── Per-corpus outcomes ──────────────────────────────────────────────
    L.append(r"\begin{table}[H]")
    L.append(r"    \mytable")
    L.append(r"    \caption{Per-corpus outcome of the language-model baseline. The "
             r"modal choice is the most frequent recommendation across the three "
             r"draws; self-consistency is the proportion of draws agreeing with it; "
             r"the gap is the mean over the draws.}")
    L.append(r"    \label{tab:llm_per_corpus}")
    # Escape tier 1: at the house \small this 17-row table overruns its page
    # box, so it drops one step. \resizebox is deliberately not used.
    L.append(r"    \footnotesize")
    # \raggedright on the wrapping columns: justified text plus \allowbreak in
    # 55-character identifiers produces badness-10000 underfull lines.
    L.append(r"    \begin{tabular}{|>{\raggedright\arraybackslash}p{0.26\textwidth}"
             r"|>{\raggedright\arraybackslash}p{0.34\textwidth}|r|r|}")
    L.append(r"        \hline")
    L.append(r"        \textbf{Corpus} & \textbf{Modal choice} & "
             r"\textbf{Self-cons.} & \textbf{Gap} \\")
    L.append(r"        \hline")
    for row in sorted(res["per_dataset"], key=lambda r: r["dataset"]):
        L.append(
            f"        {breakable(row['dataset'])} & "
            f"\\texttt{{{breakable(row['modal_choice'])}}} & "
            f"{row['self_consistency']:.2f} & {row['gap']:.4f} \\\\"
        )
        L.append(r"        \hline")
    L.append(f"        \\textbf{{Mean}} & --- & "
             f"\\textbf{{{res['mean_self_consistency']:.3f}}} & "
             f"\\textbf{{{res['mean_gap']:.4f}}} \\\\")
    L.append(r"        \hline")
    L.append(r"    \end{tabular}")
    L.append(r"\end{table}")
    L.append("")
    L.append(r"% ── END AUTO-GENERATED ──")

    args.out.write_text("\n".join(L) + "\n", encoding="utf-8")

    n_omitted = sum(1 for line in safe_prompt_lines(user_prompt) if "omitted from print" in line)
    print(f"model              : {res['model']}")
    print(f"mean gap / max gap : {res['mean_gap']:.4f} / {res['max_gap']:.4f}")
    print(f"self-consistency   : {res['mean_self_consistency']:.3f}")
    print(f"system prompt      : {len(system_prompt)} chars, "
          f"{system_prompt.count(chr(10)) + 1} lines, ASCII-only "
          f"{all(ord(c) < 128 for c in system_prompt)}")
    print(f"example prompt     : {example_dataset}, "
          f"{n_omitted}/10 samples placeheld for script reasons")
    print(f"\nWrote {args.out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
