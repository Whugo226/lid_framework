"""Locating external model files that are too large to ship inside the package."""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

LID176_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

# Where a development checkout keeps its copy (gitignored, so absent from a clone).
_PACKAGE_LID176 = Path(__file__).parent / "models" / "fasttext" / "lid.176.bin"


def cache_dir() -> Path:
    """Directory for downloaded resources (``LID_CACHE_DIR`` overrides it)."""
    override = os.environ.get("LID_CACHE_DIR")
    if override:
        return Path(override)
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "lid_toolkit"


def lid176_is_local() -> bool:
    """Return True if lid.176 is available without a download."""
    return _PACKAGE_LID176.exists() or (cache_dir() / "lid.176.bin").exists()


def lid176_path() -> Path:
    """Return a local path to the pre-trained fastText lid.176 model.

    Uses a copy inside the package if one exists, otherwise the cached download,
    downloading it (about 126 MB) from the official fastText URL on first use.
    The model is distributed by the fastText project under CC BY-SA 3.0.
    """
    if _PACKAGE_LID176.exists():
        return _PACKAGE_LID176
    target = cache_dir() / "lid.176.bin"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading fastText lid.176 (about 126 MB) to {target} ...")
        tmp = target.with_suffix(".part")
        urllib.request.urlretrieve(LID176_URL, tmp)
        tmp.replace(target)
    return target
