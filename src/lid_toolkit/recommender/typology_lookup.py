"""
Typological property lookup for the 24 languages supported by DeepProfiler.

Each language is described by four categorical properties that are *never*
compressed by PCA (Stratum S6). They capture linguistic nuances — tonal
phonology, writing system, morphological type, language family — that are
predictive of LID model performance but cannot be expressed as a continuous
gradient.

Sources: WALS (World Atlas of Language Structures), Ethnologue, Glottolog.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, FrozenSet


ScriptType   = Literal["latin", "cyrillic", "greek", "cjk", "hangul"]
MorphType    = Literal["fusional", "agglutinative", "isolating", "mixed"]
LangFamily   = Literal[
    "germanic", "romance", "slavic", "baltic", "hellenic",
    "sino-tibetan", "japonic", "koreanic", "uralic"
]


@dataclass(frozen=True)
class LanguageTypology:
    iso: str
    tonal: bool
    scripts: FrozenSet[ScriptType]
    morph_type: MorphType
    family: LangFamily
    agglutinative: bool   # True if prominent agglutinative morphology
    polysyllabic: bool    # False for predominantly monosyllabic (CJK isolating)


# ---------------------------------------------------------------------------
# Catalogue — one entry per ISO 639-1 code recognised by DeepProfiler
# ---------------------------------------------------------------------------

_CATALOGUE: list[LanguageTypology] = [
    # ── Germanic ────────────────────────────────────────────────────────────
    LanguageTypology("en", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="germanic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("da", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="germanic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("nl", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="germanic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("de", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="germanic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("nb", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="germanic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("sv", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="germanic",
                     agglutinative=False, polysyllabic=True),

    # ── Romance ─────────────────────────────────────────────────────────────
    LanguageTypology("ca", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="romance",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("fr", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="romance",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("it", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="romance",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("pt", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="romance",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("ro", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="romance",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("es", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="romance",
                     agglutinative=False, polysyllabic=True),

    # ── Slavic ──────────────────────────────────────────────────────────────
    LanguageTypology("hr", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="slavic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("mk", tonal=False, scripts=frozenset({"cyrillic"}),
                     morph_type="fusional",    family="slavic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("pl", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="slavic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("ru", tonal=False, scripts=frozenset({"cyrillic"}),
                     morph_type="fusional",    family="slavic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("sl", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="slavic",
                     agglutinative=False, polysyllabic=True),
    LanguageTypology("uk", tonal=False, scripts=frozenset({"cyrillic"}),
                     morph_type="fusional",    family="slavic",
                     agglutinative=False, polysyllabic=True),

    # ── Baltic ──────────────────────────────────────────────────────────────
    LanguageTypology("lt", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="fusional",    family="baltic",
                     agglutinative=False, polysyllabic=True),

    # ── Hellenic ────────────────────────────────────────────────────────────
    LanguageTypology("el", tonal=False, scripts=frozenset({"greek"}),
                     morph_type="fusional",    family="hellenic",
                     agglutinative=False, polysyllabic=True),

    # ── Sino-Tibetan ────────────────────────────────────────────────────────
    LanguageTypology("zh", tonal=True,  scripts=frozenset({"cjk"}),
                     morph_type="isolating",   family="sino-tibetan",
                     agglutinative=False, polysyllabic=False),

    # ── Japonic ─────────────────────────────────────────────────────────────
    LanguageTypology("ja", tonal=False, scripts=frozenset({"cjk"}),
                     morph_type="agglutinative", family="japonic",
                     agglutinative=True, polysyllabic=True),

    # ── Koreanic ────────────────────────────────────────────────────────────
    LanguageTypology("ko", tonal=False, scripts=frozenset({"hangul"}),
                     morph_type="agglutinative", family="koreanic",
                     agglutinative=True, polysyllabic=True),

    # ── Uralic ──────────────────────────────────────────────────────────────
    LanguageTypology("fi", tonal=False, scripts=frozenset({"latin"}),
                     morph_type="agglutinative", family="uralic",
                     agglutinative=True, polysyllabic=True),
]

# Quick lookup by ISO code
TYPOLOGY: dict[str, LanguageTypology] = {t.iso: t for t in _CATALOGUE}


# ---------------------------------------------------------------------------
# Dataset-level summary helpers
# ---------------------------------------------------------------------------

def dataset_typology_flags(iso_codes: list[str]) -> dict:
    """
    Aggregate typological properties across all languages in a dataset.

    Returns a flat dict suitable for concatenation into a fingerprint vector.
    Keys prefixed with ``cat__`` so the fingerprint builder can separate them
    from the continuous PCA features.
    """
    entries = [TYPOLOGY[c] for c in iso_codes if c in TYPOLOGY]
    if not entries:
        return {}

    all_scripts  = set().union(*(e.scripts for e in entries))
    all_families = {e.family for e in entries}

    return {
        "cat__n_languages":       len(iso_codes),
        "cat__n_tonal":           sum(e.tonal for e in entries),
        "cat__has_tonal":         int(any(e.tonal for e in entries)),
        "cat__n_script_types":    len(all_scripts),
        "cat__has_cjk":           int("cjk" in all_scripts),
        "cat__has_cyrillic":      int("cyrillic" in all_scripts),
        "cat__has_greek":         int("greek" in all_scripts),
        "cat__has_hangul":        int("hangul" in all_scripts),
        "cat__has_latin":         int("latin" in all_scripts),
        "cat__n_agglutinative":   sum(e.agglutinative for e in entries),
        "cat__frac_agglutinative":sum(e.agglutinative for e in entries) / len(entries),
        "cat__n_isolating":       sum(e.morph_type == "isolating" for e in entries),
        "cat__n_polysyllabic":    sum(e.polysyllabic for e in entries),
        "cat__n_language_families": len(all_families),
        "cat__frac_germanic":     sum(e.family == "germanic" for e in entries) / len(entries),
        "cat__frac_romance":      sum(e.family == "romance"  for e in entries) / len(entries),
        "cat__frac_slavic":       sum(e.family == "slavic"   for e in entries) / len(entries),
    }
