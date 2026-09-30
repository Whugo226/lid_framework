"""
Resolves composite MKB variant names to trained model files and runs inference.

Variant naming convention used in the MKB:
    {architecture}_{training_dataset_name}
    e.g.  fasttext_subword_exorde-social-media-december-2024-week1

The zero-shot detectors are keyed per corpus (``lid.176_{dataset}``,
``cld3_{dataset}``) or bare (``xlm_v_base_language_id``); the dataset suffix names the
benchmark corpus, not a training corpus.

Where the model files come from, in order of preference:

1. A local copy of the experiments folder (``experiments_dir``), laid out as
       model_training/fasttext/{dataset}/{arch}/model.bin
       model_training/logistic_regression/{dataset}/{arch}/best_pipeline.pkl
       model_training/naive_bayes/{dataset}/{arch}/best_pipeline.pkl
       off_the_shelf_models/fasttext/lid.176.bin
2. The Hugging Face model repository ``models_repo``, which mirrors the
   ``model_training/`` layout above (``fasttext/{dataset}/{arch}/model.bin`` ...).
   Only the requested model is downloaded, and it is cached locally.
3. For lid.176, the official fastText download URL.

Environment variable overrides:
    LID_EXPERIMENTS_DIR    local experiments folder (optional)
    LID_MODELS_REPO        Hugging Face repo id (default below)
    LID_MODELS_REVISION    branch, tag or commit to download from (default: main)
"""
from __future__ import annotations

import os
import pickle
import warnings
from pathlib import Path
from typing import Any

from lid_toolkit.resources import lid176_is_local, lid176_path

DEFAULT_MODELS_REPO = "werner1hugo/lid-framework-models"

_LR_ARCHS: frozenset[str] = frozenset({
    "tfidf_lr_char_ngram_3_5",
    "bow_maxabs_lr_char_ngram_3_5",
})

_NB_ARCHS: frozenset[str] = frozenset({
    "tfidf_char_ngram_3_5",
    "bow_char_ngram_3_5",
})

# Zero-shot detectors the runner cannot execute itself.
_UNSUPPORTED: dict[str, str] = {
    "cld3": (
        "CLD3 is not bundled with the framework. Install the `gcld3` package "
        "and run Google's detector directly."
    ),
    "xlm_v_base_language_id": (
        "XLM-V Base is not bundled with the framework. Run the published "
        "checkpoint `juliensimon/xlm-v-base-language-id` with the Hugging Face "
        "`transformers` library."
    ),
}


def _family(arch: str) -> str:
    """Infer model family from architecture name."""
    if arch.startswith("fasttext"):
        return "fasttext"
    if arch.startswith("lid."):
        return "fasttext_ots"
    if arch in _UNSUPPORTED:
        return arch
    if arch in _LR_ARCHS:
        return "logistic_regression"
    if arch in _NB_ARCHS:
        return "naive_bayes"
    raise ValueError(f"Unknown model architecture {arch!r}")


class ModelRunner:
    """
    Resolves composite MKB variant names to trained model files and runs inference.

    Parameters
    ----------
    store_datasets :
        List of dataset names from MKBStore.datasets (used for longest-match suffix parsing).
    experiments_dir :
        Optional root of a local LID_experiments/ folder. Files found there are
        used directly; anything missing is downloaded instead.
    models_repo :
        Hugging Face repository holding the trained models.
    revision :
        Branch, tag or commit of ``models_repo`` to download from.
    """

    def __init__(
        self,
        store_datasets: list[str],
        experiments_dir: str | Path | None = None,
        models_repo: str | None = None,
        revision: str | None = None,
    ):
        env_dir = os.environ.get("LID_EXPERIMENTS_DIR")
        chosen = experiments_dir if experiments_dir else env_dir
        self.experiments_dir = Path(chosen) if chosen else None
        self.models_repo = models_repo or os.environ.get("LID_MODELS_REPO", DEFAULT_MODELS_REPO)
        self.revision = revision or os.environ.get("LID_MODELS_REVISION") or None
        self._datasets = sorted(store_datasets, key=len, reverse=True)
        self._cache: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Variant parsing
    # ------------------------------------------------------------------

    def resolve(self, variant: str) -> tuple[str, str, str]:
        """Parse a composite variant name → (architecture, dataset, family).

        Uses longest-match suffix search so dataset names that are substrings
        of other dataset names are handled correctly. Bare zero-shot names
        (``xlm_v_base_language_id``) return an empty dataset.
        """
        if variant in _UNSUPPORTED:
            return variant, "", variant
        for ds in self._datasets:
            if variant.endswith(f"_{ds}"):
                arch = variant[: -(len(ds) + 1)]
                return arch, ds, _family(arch)
        raise ValueError(
            f"Cannot resolve variant {variant!r} to a known dataset. "
            f"Known datasets (first 5): {self._datasets[:5]}"
        )

    def unsupported_reason(self, variant: str) -> str | None:
        """Return why the runner cannot execute this variant, or None if it can."""
        try:
            _, _, family = self.resolve(variant)
        except ValueError as exc:
            return str(exc)
        return _UNSUPPORTED.get(family)

    def relative_path(self, variant: str) -> str:
        """Path of the model file relative to ``model_training/`` (and to the HF repo root)."""
        arch, dataset, family = self.resolve(variant)
        if family == "fasttext":
            return f"fasttext/{dataset}/{arch}/model.bin"
        if family in ("logistic_regression", "naive_bayes"):
            return f"{family}/{dataset}/{arch}/best_pipeline.pkl"
        raise ValueError(f"{variant!r} has no trained-model file")

    def local_path(self, variant: str) -> Path | None:
        """Return the model file in the local experiments folder, if configured and present."""
        if self.experiments_dir is None:
            return None
        _, _, family = self.resolve(variant)
        if family == "fasttext_ots":
            path = self.experiments_dir / "off_the_shelf_models" / "fasttext" / "lid.176.bin"
        elif family in _UNSUPPORTED:
            return None
        else:
            path = self.experiments_dir / "model_training" / self.relative_path(variant)
        return path if path.exists() else None

    def is_cached(self, variant: str) -> bool:
        """Return True if the model is available without a download."""
        if self.unsupported_reason(variant):
            return False
        if self.local_path(variant) is not None:
            return True
        _, _, family = self.resolve(variant)
        if family == "fasttext_ots":
            return lid176_is_local()
        from huggingface_hub import try_to_load_from_cache
        hit = try_to_load_from_cache(
            self.models_repo, self.relative_path(variant), revision=self.revision
        )
        return isinstance(hit, str)

    def is_available(self, variant: str) -> bool:
        """Return True if the runner can execute this variant (locally or after a download)."""
        return self.unsupported_reason(variant) is None

    def fetch(self, variant: str) -> Path:
        """Return a local path to the model file, downloading it if necessary."""
        reason = self.unsupported_reason(variant)
        if reason:
            raise RuntimeError(reason)
        local = self.local_path(variant)
        if local is not None:
            return local
        _, _, family = self.resolve(variant)
        if family == "fasttext_ots":
            return lid176_path()
        from huggingface_hub import hf_hub_download
        return Path(hf_hub_download(
            repo_id=self.models_repo,
            filename=self.relative_path(variant),
            revision=self.revision,
        ))

    def model_path(self, variant: str) -> Path:
        """Backward-compatible alias for :meth:`fetch`."""
        return self.fetch(variant)

    # ------------------------------------------------------------------
    # Model loading (lazily cached)
    # ------------------------------------------------------------------

    def _load(self, variant: str) -> Any:
        if variant in self._cache:
            return self._cache[variant]
        path = self.fetch(variant)
        _, _, family = self.resolve(variant)
        if family in ("fasttext", "fasttext_ots"):
            import fasttext
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = fasttext.load_model(str(path))
        else:
            with open(path, "rb") as fh:
                model = pickle.load(fh)
        self._cache[variant] = model
        return model

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, variant: str, texts: list[str]) -> list[str]:
        """Return predicted ISO 639-1 language codes, one per input text."""
        model = self._load(variant)
        _, _, family = self.resolve(variant)
        if family in ("fasttext", "fasttext_ots"):
            clean = [" ".join(t.split()) for t in texts]
            labels, _ = model.predict(clean, k=1)
            return [lbl[0].replace("__label__", "") for lbl in labels]
        return list(model.predict(texts))

    def predict_with_confidence(
        self,
        variant: str,
        texts: list[str],
        top_k: int = 3,
    ) -> list[dict[str, float]]:
        """Return top-k (lang → confidence) dicts per input text."""
        model = self._load(variant)
        _, _, family = self.resolve(variant)
        results: list[dict[str, float]] = []
        if family in ("fasttext", "fasttext_ots"):
            clean = [" ".join(t.split()) for t in texts]
            all_labels, all_probs = model.predict(clean, k=top_k)
            for lbls, probs in zip(all_labels, all_probs):
                results.append(
                    {lbl.replace("__label__", ""): float(p)
                     for lbl, p in zip(lbls, probs)}
                )
        else:
            if hasattr(model, "predict_proba"):
                proba_matrix = model.predict_proba(texts)
                classes = model.classes_
                for row in proba_matrix:
                    idx = row.argsort()[-top_k:][::-1]
                    results.append({classes[i]: float(row[i]) for i in idx})
            else:
                preds = model.predict(texts)
                results = [{p: 1.0} for p in preds]
        return results

    def arch_label(self, variant: str) -> str:
        """Return a display-friendly label for the model family."""
        try:
            arch, _, family = self.resolve(variant)
        except ValueError:
            return variant
        labels = {
            "fasttext": "FastText (custom)",
            "fasttext_ots": "FastText lid.176 (off-the-shelf)",
            "logistic_regression": "Logistic Regression",
            "naive_bayes": "Naïve Bayes",
            "cld3": "CLD3 (off-the-shelf)",
            "xlm_v_base_language_id": "XLM-V Base (off-the-shelf)",
        }
        return labels.get(family, arch)
