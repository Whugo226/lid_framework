"""Publish the 102 trained candidate models to the Hugging Face Hub.

Uploads only the model folders that the Meta-Knowledge Base refers to, from a
local LID_experiments/model_training/ folder, together with the model card in
docs/model_card.md. The upload is resumable: rerun the script after an
interruption and it continues where it stopped.

Requires a Hugging Face token with write access (`hf auth login`).

Usage (from the repository root):
    python scripts/upload_models_to_hf.py --model-training <path to LID_experiments/model_training>
    python scripts/upload_models_to_hf.py --model-training ... --dry-run
"""
from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lid_toolkit.explainer.model_runner import DEFAULT_MODELS_REPO, ModelRunner  # noqa: E402

TRAINED_FAMILIES = ("fasttext", "naive_bayes", "logistic_regression")


def model_folders(store_path: Path) -> list[str]:
    """Return the repo-relative folder of every trained variant in the MKB."""
    with open(store_path, "rb") as fh:
        store = pickle.load(fh)
    names: set[str] = set()
    for entry in store._entries.values():
        names.update(entry.performances)
    runner = ModelRunner(list(store.datasets))
    folders = {
        str(Path(runner.relative_path(n)).parent).replace("\\", "/")
        for n in names
        if runner.resolve(n)[2] in TRAINED_FAMILIES
    }
    return sorted(folders)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-training", required=True, type=Path,
                    help="Path to LID_experiments/model_training")
    ap.add_argument("--store", type=Path, default=ROOT / "mkb.pkl")
    ap.add_argument("--repo", default=DEFAULT_MODELS_REPO)
    ap.add_argument("--dry-run", action="store_true", help="List what would be uploaded")
    args = ap.parse_args()

    folders = model_folders(args.store)
    missing = [f for f in folders if not (args.model_training / f).is_dir()]
    if missing:
        sys.exit(f"{len(missing)} model folders missing locally, e.g. {missing[:3]}")
    total = sum(p.stat().st_size for f in folders for p in (args.model_training / f).iterdir())
    print(f"{len(folders)} model folders, {total / 1e9:.1f} GB -> {args.repo}")
    if args.dry_run:
        for f in folders:
            print("  ", f)
        return

    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(args.repo, repo_type="model", private=False, exist_ok=True)
    api.upload_file(
        path_or_fileobj=str(ROOT / "docs" / "model_card.md"),
        path_in_repo="README.md",
        repo_id=args.repo,
        commit_message="Add model card",
    )
    api.upload_large_folder(
        repo_id=args.repo,
        repo_type="model",
        folder_path=str(args.model_training),
        allow_patterns=[f"{f}/*" for f in folders],
    )
    head = api.list_repo_commits(args.repo)[0].commit_id
    print(f"Done. Pin this revision for the thesis release: LID_MODELS_REVISION={head}")


if __name__ == "__main__":
    main()
