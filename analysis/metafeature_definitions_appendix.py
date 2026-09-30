"""Regenerate the prose-normalised metafeature definition table.

The appendix retains the curated 327-row inventory and LaTeX structure. This
generator applies the thesis prose rules to those rows deterministically, then
validates the row count and prohibited terminology. The underlying catalogue
is documented in ``project_context/Lingualyzer_base_measures.txt``.

Run from the toolkit repository root::

    python analysis/metafeature_definitions_appendix.py
"""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_APPENDIX = (
    Path(__file__).resolve().parents[4]
    / "Thesis"
    / "Thesis Template Legit"
    / "appendices"
    / "metafeature_definitions_appendix.tex"
)
ROW_MARKER = " & "
ROW_END = "\\\\"
EXPECTED_ROWS = 327


def is_definition_row(line: str) -> bool:
    # A table row is "<measure> & <definition> \\"; the header row is bold and
    # excluded. (On 2026-09-26 the per-row \textbullet\quad marker and the
    # per-row \hline were dropped to shorten the table; rules now sit only
    # between the measure groups.)
    stripped = line.strip()
    return (
        ROW_MARKER in stripped
        and stripped.endswith(ROW_END)
        and not stripped.startswith(r"\textbf")
    )


def regenerate(text: str) -> str:
    lines = text.splitlines()
    row_indexes = [i for i, line in enumerate(lines) if is_definition_row(line)]
    if len(row_indexes) != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} metafeature rows, found {len(row_indexes)}"
        )

    for index in row_indexes:
        lines[index] = (
            lines[index]
            .replace("Operationalises", "Measures")
            .replace("operationalises", "measures")
            .replace("standardized frequency lists", "standardised frequency lists")
        )

    result = "\n".join(lines) + ("\n" if text.endswith(("\n", "\r")) else "")
    result = result.replace("deployed artifact", "deployed artefact")

    lowered = result.lower()
    for prohibited in ("operationalise", "operationalisation", "bespoke"):
        if prohibited in lowered:
            raise ValueError(f"Prohibited term remains: {prohibited}")
    if "standardized" in lowered:
        raise ValueError("American spelling remains: standardized")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appendix", type=Path, default=DEFAULT_APPENDIX)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source = args.appendix.read_text(encoding="utf-8")
    generated = regenerate(source)
    if args.check:
        if generated != source:
            raise SystemExit("Metafeature appendix is not up to date")
        print(f"Verified: {args.appendix} ({EXPECTED_ROWS} rows)")
        return

    args.appendix.write_text(generated, encoding="utf-8", newline="\r\n")
    print(f"Written: {args.appendix} ({EXPECTED_ROWS} rows)")


if __name__ == "__main__":
    main()
