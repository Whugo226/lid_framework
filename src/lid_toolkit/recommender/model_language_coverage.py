"""
Language inventories for the zero-shot (off-the-shelf) LID models.

The coverage guard in :mod:`mkb_similarity` needs to know which languages a
candidate model can identify.  For the six *trained* configurations this is
correctly inferred from the training corpus suffix in the variant name
(e.g. ``fasttext_subword_europarl`` knows europarl's languages).  For the
three *zero-shot* models, however, that inference is wrong: ``lid.176_massive``
is merely lid.176 *evaluated on* massive — the model itself identifies 176
languages regardless of which benchmark corpus the record came from.

This module holds the authoritative label inventories for the three zero-shot
models, sourced from their official documentation:

* fastText ``lid.176.bin`` — 176 languages (fasttext.cc/docs/en/language-identification)
* CLD3 — 107 output classes; script-variant labels (``bg-Latn`` etc.) collapse
  to their base code, giving the base-language set below
  (github.com/google/cld3#supported-languages)
* ``juliensimon/xlm-v-base-language-id`` — fine-tuned on google/fleurs,
  102 languages (model card + FLEURS dataset card)

Normalisation notes
-------------------
* Codes are ISO 639-1 where one exists, otherwise the ISO 639-2/3 code used
  by the model's own label set (e.g. ``ceb``, ``yue``, ``ckb``).
* Deprecated codes in CLD3's label set are mapped to their modern equivalents
  (``iw`` → ``he``); ``fil`` is kept alongside its 639-1 alias ``tl``.
* Macrolanguage expansion: models that label Norwegian as ``no`` are credited
  with ``nb`` (Bokmål) — the code used throughout this toolkit — since Bokmål
  text is identified (as ``no``) by those models.  lid.176 additionally lists
  ``nn`` (Nynorsk) explicitly.
"""

from __future__ import annotations

from typing import Optional

# fastText lid.176.bin — 176 labels as published, plus nb via the `no` macrolanguage.
LID176_LANGUAGES: frozenset[str] = frozenset(
    """af als am an ar arz as ast av az azb ba bar bcl be bg bh bn bo bpy br bs
    bxr ca cbk ce ceb ckb co cs cv cy da de diq dsb dty dv el eml en eo es et
    eu fa fi fr frr fy ga gd gl gn gom gu gv he hi hif hr hsb ht hu hy ia id
    ie ilo io is it ja jbo jv ka kk km kn ko krc ku kv kw ky la lb lez li lmo
    lo lrc lt lv mai mg mhr min mk ml mn mr mrj ms mt mwl my myv mzn nah nap
    nds ne new nl nn no oc or os pa pam pfl pl pms pnb ps pt qu rm ro ru rue
    sa sah sc scn sco sd sh si sk sl so sq sr su sv sw ta te tg th tk tl tr
    tt tyv ug uk ur uz vec vep vi vls vo wa war wuu xal xmf yi yo yue zh
    nb""".split()
)

# CLD3 — base-language codes (script variants like `bg-Latn` collapsed;
# `iw` → `he`; `fil` kept with alias `tl`; `no` expanded with `nb`).
CLD3_LANGUAGES: frozenset[str] = frozenset(
    """af am ar bg bn bs ca ceb co cs cy da de el en eo es et eu fa fi fil fr
    fy ga gd gl gu ha haw he hi hmn hr ht hu hy id ig is it ja jv ka kk km kn ko
    ku ky la lb lo lt lv mg mi mk ml mn mr ms mt my ne nl no ny pa pl ps pt
    ro ru sd si sk sl sm sn so sq sr st su sv sw ta te tg th tr uk ur uz vi
    xh yi yo zh zu
    tl nb""".split()
)

# juliensimon/xlm-v-base-language-id — the 102 FLEURS languages
# (FLEURS dataset card, grouped by geographical area; `fil` aliased to `tl`).
XLM_V_LANGUAGE_ID_LANGUAGES: frozenset[str] = frozenset(
    """ast bs ca hr da nl en fi fr gl de el hu is ga it kea lb mt nb oc pt es
    sv cy
    hy be bg cs et ka lv lt mk pl ro ru sr sk sl uk
    ar az he kk ky mn ps fa ckb tg tr uz
    af am ff lg ha ig kam ln luo nso ny om sn so sw umb wo xh yo zu
    as bn gu hi kn ml mr ne or pa sd ta te ur
    my ceb fil id jv km lo ms mi th vi
    yue zh ja ko
    tl""".split()
)

# Variant-name prefix → inventory.  Zero-shot variants appear in the MKB as
# `lid.176_<dataset>`, `cld3_<dataset>`, or bare `xlm_v_base_language_id`.
_ZERO_SHOT_INVENTORIES: dict[str, frozenset[str]] = {
    "lid.176": LID176_LANGUAGES,
    "cld3": CLD3_LANGUAGES,
    "xlm_v_base_language_id": XLM_V_LANGUAGE_ID_LANGUAGES,
}


def zero_shot_inventory(variant: str) -> Optional[frozenset[str]]:
    """
    Return the full language inventory for a zero-shot model variant, or
    ``None`` if `variant` is not a zero-shot model (i.e. it is one of the
    trained configurations, whose coverage is corpus-specific).
    """
    for prefix, langs in _ZERO_SHOT_INVENTORIES.items():
        if variant == prefix or variant.startswith(prefix + "_"):
            return langs
    return None
