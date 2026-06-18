"""
Resolves composite MKB variant names to trained model files and runs inference.

Variant naming convention used in the MKB:
    {architecture}_{training_dataset_name}
    e.g.  fasttext_subword_exorde-social-media-december-2024-week1

Model file layout under LID_experiments/:
    model_training/fasttext/{dataset}/{arch}/model.bin          (FastText custom)
    model_training/logistic_regression/{dataset}/{arch}/best_pipeline.pkl
    model_training/naive_bayes/{dataset}/{arch}/best_pipeline.pkl
    off_the_shelf_models/fasttext/lid.176.bin                  (lid.176 OTS)
"""
from __future__ import annotations

import pickle
import warnings
from pathlib import Path
from typing import Any

_LR_ARCHS: frozenset[str] = frozenset({
    "tfidf_lr_char_ngram_3_5",
    "bow_maxabs_lr_char_ngram_3_5",
})

_NB_ARCHS: frozenset[str] = frozenset({
    "tfidf_char_ngram_3_5",
    "bow_char_ngram_3_5",
})


def _family(arch: str) -> str:
    """Infer model family from architecture name."""
    if arch.startswith("fasttext"):
        return "fasttext"
    if arch.startswith("lid."):
        return "fasttext_ots"
    if arch in _LR_ARCHS:
        return "logistic_regression"
    return "naive_bayes"


class ModelRunner:
    """
    Resolves composite MKB variant names to trained model files and runs inference.

    Parameters
    ----------
    experiments_dir :
        Root of the LID_experiments/ directory.
    store_datasets :
        List of dataset names from MKBStore.datasets (used for longest-match suffix parsing).
    """

    def __init__(self, experiments_dir: str | Path, store_datasets: list[str]):
        self.experiments_dir = Path(experiments_dir)
        self._datasets = sorted(store_datasets, key=len, reverse=True)
        self._cache: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Variant parsing
    # ------------------------------------------------------------------

    def resolve(self, variant: str) -> tuple[str, str, str]:
        """Parse a composite variant name → (architecture, training_dataset, family).

        Uses longest-match suffix search so dataset names that are substrings
        of other dataset names are handled correctly.
        """
        for ds in self._datasets:
            if variant.endswith(f"_{ds}"):
                arch = variant[: -(len(ds) + 1)]
                return arch, ds, _family(arch)
        raise ValueError(
            f"Cannot resolve variant {variant!r} to a known dataset. "
            f"Known datasets (first 5): {self._datasets[:5]}"
        )

    def model_path(self, variant: str) -> Path:
        """Return the absolute path to the model file for this variant."""
        arch, dataset, family = self.resolve(variant)
        base = self.experiments_dir
        if family == "fasttext_ots":
            return base / "off_the_shelf_models" / "fasttext" / "lid.176.bin"
        if family == "fasttext":
            return base / "model_training" / "fasttext" / dataset / arch / "model.bin"
        if family == "logistic_regression":
            return (base / "model_training" / "logistic_regression"
                    / dataset / arch / "best_pipeline.pkl")
        # naive_bayes
        return base / "model_training" / "naive_bayes" / dataset / arch / "best_pipeline.pkl"

    def is_available(self, variant: str) -> bool:
        """Return True if the model file exists on disk."""
        try:
            return self.model_path(variant).exists()
        except ValueError:
            return False

    # ------------------------------------------------------------------
    # Model loading (lazily cached)
    # ------------------------------------------------------------------

    def _load(self, variant: str) -> Any:
        if variant in self._cache:
            return self._cache[variant]
        path = self.model_path(variant)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
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
        }
        return labels.get(family, arch)
