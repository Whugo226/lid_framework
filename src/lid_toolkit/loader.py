from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_text(
    source: str | Path | pd.Series,
    text_column: str | None = None,
    sample: int | None = None,
) -> pd.Series:
    """
    Load text from a .txt file, .csv/.tsv file, folder of .txt files, or pass pd.Series through.

    Args:
        source: One of:
            - pd.Series of strings (returned as-is after cleaning)
            - Path/str to a .txt file (read line-by-line, blanks dropped)
            - Path/str to a .csv or .tsv file (requires text_column)
            - Path/str to a directory (each .txt file becomes one Series element)
        text_column: Column name to read from CSV/TSV files.
        sample: If set, randomly sample this many rows (reproducible, random_state=42).

    Returns:
        pd.Series of str with a clean integer index.
    """
    if isinstance(source, pd.Series):
        result = source.dropna().astype(str).reset_index(drop=True)
        if sample is not None:
            n = min(sample, len(result))
            result = result.sample(n=n, random_state=42).reset_index(drop=True)
        return result

    path = Path(source)

    if path.is_dir():
        files = sorted(path.glob("*.txt"))
        if not files:
            raise ValueError(f"No .txt files found in directory: {path}")
        series = pd.Series([f.read_text(encoding="utf-8") for f in files], dtype=str)

    elif path.suffix.lower() == ".txt":
        lines = path.read_text(encoding="utf-8").splitlines()
        series = pd.Series([line.strip() for line in lines if line.strip()], dtype=str)

    elif path.suffix.lower() in (".csv", ".tsv"):
        if text_column is None:
            raise ValueError("text_column must be provided when loading a CSV or TSV file.")
        sep = "\t" if path.suffix.lower() == ".tsv" else ","
        df = pd.read_csv(path, sep=sep, dtype=str)
        if text_column not in df.columns:
            raise ValueError(
                f"Column '{text_column}' not found in {path}. "
                f"Available columns: {list(df.columns)}"
            )
        series = df[text_column].dropna()

    else:
        raise ValueError(
            f"Unsupported file type '{path.suffix}'. Expected .txt, .csv, .tsv, or a directory."
        )

    series = series.reset_index(drop=True)
    if sample is not None:
        n = min(sample, len(series))
        series = series.sample(n=n, random_state=42).reset_index(drop=True)
    return series
