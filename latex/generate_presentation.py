"""
generate_presentation.py
Generates the LID Toolkit Master's Thesis presentation as a .pptx file.
Run: python generate_presentation.py
Output: lid_toolkit_presentation.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
import pptx.oxml.ns as nsmap
from lxml import etree
import copy

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
C_BG        = RGBColor(0x1A, 0x1A, 0x2E)   # near-black navy
C_ACCENT    = RGBColor(0x16, 0x21, 0x3E)   # dark blue panel
C_HIGHLIGHT = RGBColor(0xE9, 0x4F, 0x37)   # red-orange accent
C_GOLD      = RGBColor(0xF5, 0xA6, 0x23)   # gold for equations
C_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
C_LIGHT     = RGBColor(0xCC, 0xD6, 0xE8)   # light blue-grey text
C_GREEN     = RGBColor(0x4C, 0xAF, 0x50)
C_STRATUM   = [
    RGBColor(0x42, 0x8B, 0xCA),  # S1 – blue
    RGBColor(0x5C, 0xB8, 0x5C),  # S2 – green
    RGBColor(0xF0, 0xAD, 0x4E),  # S3 – orange
    RGBColor(0xD9, 0x53, 0x4F),  # S4 – red
    RGBColor(0x9B, 0x59, 0xB6),  # S5 – purple
    RGBColor(0x1A, 0xBC, 0x9C),  # S6 – teal
]

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _set_bg(slide, colour: RGBColor):
    """Fill slide background with a solid colour."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = colour


def _add_textbox(slide, left, top, width, height,
                 text, font_size=18, bold=False, italic=False,
                 colour=C_WHITE, align=PP_ALIGN.LEFT,
                 word_wrap=True, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = word_wrap
    tf.auto_size = None
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = colour
    run.font.name = font_name
    return txBox


def _add_multiline_textbox(slide, left, top, width, height,
                            lines, base_font_size=16,
                            colour=C_LIGHT, font_name="Calibri",
                            line_spacing_pt=None):
    """
    lines: list of (text, font_size, bold, italic, colour, align)
           Omit trailing fields to use defaults.
    """
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, entry in enumerate(lines):
        if isinstance(entry, str):
            entry = (entry,)
        text   = entry[0] if len(entry) > 0 else ""
        fsize  = entry[1] if len(entry) > 1 else base_font_size
        fbold  = entry[2] if len(entry) > 2 else False
        fital  = entry[3] if len(entry) > 3 else False
        fcol   = entry[4] if len(entry) > 4 else colour
        falign = entry[5] if len(entry) > 5 else PP_ALIGN.LEFT

        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = falign

        if line_spacing_pt:
            from pptx.util import Pt as _Pt
            from pptx.oxml.ns import qn
            pPr = p._p.get_or_add_pPr()
            lnSpc = etree.SubElement(pPr, qn('a:lnSpc'))
            spcPts = etree.SubElement(lnSpc, qn('a:spcPts'))
            spcPts.set('val', str(int(line_spacing_pt * 100)))

        run = p.add_run()
        run.text = text
        run.font.size = Pt(fsize)
        run.font.bold = fbold
        run.font.italic = fital
        run.font.color.rgb = fcol
        run.font.name = font_name

    return txBox


def _add_rect(slide, left, top, width, height, fill_colour, line_colour=None):
    shape = slide.shapes.add_shape(
        pptx.enum.shapes.MSO_SHAPE_TYPE.AUTO_SHAPE if False else 1,  # MSO_SHAPE_TYPE.RECTANGLE = 1
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_colour
    if line_colour:
        shape.line.color.rgb = line_colour
    else:
        shape.line.fill.background()
    return shape


def _add_notes(slide, text: str):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text


def _add_divider(slide, top, colour=C_HIGHLIGHT):
    _add_rect(slide,
              Inches(0.5), top,
              Inches(12.33), Inches(0.04),
              colour)


def _section_label(slide, left, top, label: str, colour):
    _add_rect(slide, left, top, Inches(0.18), Inches(0.28), colour)
    _add_textbox(slide, left + Inches(0.25), top - Inches(0.02),
                 Inches(2), Inches(0.32),
                 label, font_size=11, bold=True, colour=colour)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_title(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    _set_bg(slide, C_BG)

    # Left accent bar
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    # Main title
    _add_multiline_textbox(slide,
        Inches(0.6), Inches(0.6), Inches(12.5), Inches(1.4),
        [
            ("The Interactive LID Model Selection Toolkit", 32, True, False, C_WHITE, PP_ALIGN.LEFT),
        ]
    )
    _add_divider(slide, Inches(2.05), C_HIGHLIGHT)

    _add_multiline_textbox(slide,
        Inches(0.6), Inches(2.2), Inches(12.5), Inches(0.5),
        [("A Meta-Knowledge Approach to Recommending Language Identification Models",
          20, False, True, C_GOLD, PP_ALIGN.LEFT)]
    )

    # Key facts box
    _add_rect(slide, Inches(0.6), Inches(3.0), Inches(5.8), Inches(3.8),
              RGBColor(0x0D, 0x0D, 0x1E))

    facts = [
        ("Thesis Metadata", 14, True, False, C_HIGHLIGHT),
        ("", 8),
        ("Scope:  18 benchmark datasets  |  24 languages", 13, False, False, C_LIGHT),
        ("Models:  FastText & spaCy variant families", 13, False, False, C_LIGHT),
        ("Output:  Python CLI / API toolkit (HPC + laptop)", 13, False, False, C_LIGHT),
        ("Novelty:  Zero manual tuning  —  query the MKB", 13, False, False, C_LIGHT),
        ("", 6),
        ("Key Pipeline Stages:", 13, True, False, C_WHITE),
        ("  Raw text  →  DeepProfiler  →  277-dim fingerprint", 12, False, False, C_LIGHT),
        ("  →  k-NN similarity  →  IDW vote  →  Recommendation", 12, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.8), Inches(3.1), Inches(5.4), Inches(3.5),
                            facts, base_font_size=13)

    # Equation box
    _add_rect(slide, Inches(6.8), Inches(3.0), Inches(6.1), Inches(3.8),
              RGBColor(0x0D, 0x0D, 0x1E))

    eq_lines = [
        ("Core Recommendation Equation", 13, True, False, C_GOLD),
        ("", 7),
        ("m* = arg max_m   Σᵢ∈𝒩ₖ(f̂)  Acc(m, 𝒟ᵢ) · γᵢ(m)", 12, False, True, C_WHITE),
        ("                 ——————————————————————————————", 11, False, False, C_LIGHT),
        ("                          dᵢ  +  ε", 12, False, True, C_WHITE),
        ("", 6),
        ("where:", 11, True, False, C_LIGHT),
        ("  dᵢ        =  Euclidean distance in 277-dim PCA fingerprint space", 11, False, False, C_LIGHT),
        ("  γᵢ(m) ∈ (0, 1]  =  language coverage factor for model m at neighbour i", 11, False, False, C_LIGHT),
        ("  ε = 10⁻⁹  (regularisation; prevents division by zero)", 11, False, False, C_LIGHT),
        ("  k = 3  nearest neighbours  |  𝒩ₖ(f̂) = k-NN set of query fingerprint f̂ ∈ ℝ²⁷⁷", 11, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(7.0), Inches(3.1), Inches(5.7), Inches(3.6),
                            eq_lines, base_font_size=12)

    _add_notes(slide,
        "Good morning. The central premise of this thesis is straightforward: selecting the right "
        "language identification model for a dataset should not be a matter of trial-and-error — it "
        "should be a query. We pre-compute linguistic profiles of 18 benchmark datasets, compress them "
        "into 277-dimensional fingerprints, and when a practitioner brings a new dataset we find the "
        "nearest historical neighbours and let their benchmark performance vote on a recommendation. "
        "The engineering novelty is in how we define 'nearest': we compare distilled linguistic "
        "structure, not raw text, and that is what I will defend today."
    )
    return slide


def slide_02_problem(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, C_BG)
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    _add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.7),
                 "Why LID Model Selection Is a Non-Trivial Engineering Problem",
                 font_size=26, bold=True, colour=C_WHITE)
    _add_divider(slide, Inches(1.1))

    # Three columns
    cols = [
        ("The User's Situation", C_STRATUM[0], [
            "New multilingual dataset arrives",
            "Dozens of model variants exist",
            "No principled selection method",
            "Result: ad-hoc trial-and-error",
            "Cost: hours of GPU evaluation time",
        ]),
        ("Current State of Practice", C_STRATUM[3], [
            "Run all models on new data",
            "Pick the winner manually",
            "Domain shift = silent failure",
            "Wikipedia-trained model fails",
            "  on social-media corpora",
            "No transferable knowledge",
        ]),
        ("The Proposed Solution", C_GREEN, [
            "Query the Meta-Knowledge Base",
            "Sub-second recommendation",
            "Interpretable explanation",
            "Coverage gap warnings",
            "Zero model evaluations needed",
        ]),
    ]

    for i, (title, colour, bullets) in enumerate(cols):
        left = Inches(0.55 + i * 4.2)
        _add_rect(slide, left, Inches(1.25), Inches(4.0), Inches(3.8),
                  RGBColor(0x0D, 0x0D, 0x1E))
        _add_rect(slide, left, Inches(1.25), Inches(4.0), Inches(0.38), colour)
        _add_textbox(slide, left + Inches(0.1), Inches(1.28), Inches(3.8), Inches(0.35),
                     title, font_size=13, bold=True, colour=C_WHITE)
        bullet_lines = [("  •  " + b, 12, False, False, C_LIGHT) for b in bullets]
        bullet_lines.insert(0, ("", 6))
        _add_multiline_textbox(slide, left + Inches(0.1), Inches(1.65),
                                Inches(3.8), Inches(3.2), bullet_lines)

    # Equation
    _add_rect(slide, Inches(0.55), Inches(5.2), Inches(12.33), Inches(2.0),
              RGBColor(0x0D, 0x0D, 0x1E))
    eq = [
        ("Surrogate Modelling Formulation", 13, True, False, C_GOLD),
        ("", 5),
        ("True objective (intractable):   m* = arg max_m  𝔼[ Acc(m, 𝒟_new) ]", 13, False, True, C_WHITE),
        ("", 3),
        ("MKB approximation:              m* ≈ arg max_m  Σᵢ∈𝒩ₖ(f̂)  wᵢ · Acc(m, 𝒟ᵢ)", 13, False, True, C_WHITE),
        ("", 3),
        ("where  𝒩ₖ(f̂)  is the k-nearest-neighbour set of the query fingerprint  f̂ ∈ ℝ²⁷⁷", 11, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.75), Inches(5.28), Inches(12.0), Inches(1.8), eq)

    _add_notes(slide,
        "The problem reduces to a form Industrial Engineers will recognise immediately: surrogate "
        "modelling. We cannot afford to evaluate the objective function — running all models on every "
        "new dataset — so we build a surrogate from historical evaluations and query the surrogate "
        "instead. The key engineering contribution is the design of the feature space — the fingerprint — "
        "that makes historical similarity predictive of future performance. That design constitutes the "
        "bulk of this thesis."
    )
    return slide


def slide_03_architecture(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, C_BG)
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    _add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6),
                 "End-to-End Pipeline: From Raw Parquet to Ranked Recommendations",
                 font_size=24, bold=True, colour=C_WHITE)
    _add_divider(slide, Inches(1.0))

    # -- OFFLINE PHASE LABEL
    _add_rect(slide, Inches(0.55), Inches(1.1), Inches(12.33), Inches(0.32),
              RGBColor(0x2C, 0x2C, 0x44))
    _add_textbox(slide, Inches(0.65), Inches(1.12), Inches(4), Inches(0.28),
                 "OFFLINE BUILD PHASE  (executed once on HPC)",
                 font_size=11, bold=True, colour=C_GOLD)

    offline_boxes = [
        ("18 Dataset Dirs\n(.parquet files)", C_STRATUM[2]),
        ("DeepProfiler\n2,726 raw features\nper language", C_STRATUM[0]),
        ("FeatureStratifier\nS1–S5 PCA fit\n(95% variance)", C_STRATUM[1]),
        ("FingerprintBuilder\n277-dim OrderedDict\nper dataset", C_STRATUM[4]),
        ("MKBStore\n+ benchmark\nperformance → mkb.pkl", C_STRATUM[5]),
    ]

    arrow = "→"
    box_w = Inches(2.2)
    box_h = Inches(1.15)
    top = Inches(1.5)
    gap = Inches(0.22)
    for i, (label, colour) in enumerate(offline_boxes):
        left = Inches(0.55) + i * (box_w + gap)
        _add_rect(slide, left, top, box_w, box_h, colour)
        _add_multiline_textbox(slide, left + Inches(0.08), top + Inches(0.08),
                                box_w - Inches(0.16), box_h - Inches(0.1),
                                [(label, 11, True, False, C_WHITE, PP_ALIGN.CENTER)])
        if i < len(offline_boxes) - 1:
            _add_textbox(slide,
                         left + box_w, top + Inches(0.44),
                         gap, Inches(0.3),
                         arrow, font_size=18, bold=True, colour=C_WHITE,
                         align=PP_ALIGN.CENTER)

    # -- ONLINE PHASE LABEL
    _add_rect(slide, Inches(0.55), Inches(2.85), Inches(12.33), Inches(0.32),
              RGBColor(0x1A, 0x2E, 0x1A))
    _add_textbox(slide, Inches(0.65), Inches(2.87), Inches(6), Inches(0.28),
                 "ONLINE QUERY PHASE  (sub-second, at recommendation time)",
                 font_size=11, bold=True, colour=C_GREEN)

    query_boxes = [
        ("User\ntext_series", C_STRATUM[2]),
        ("DeepProfiler\nget_multilingual\n_profile()", C_STRATUM[0]),
        ("Fitted\nFeatureStratifier\n(from mkb.pkl)", C_STRATUM[1]),
        ("Query\nFingerprint\nf̂ ∈ ℝ²⁷⁷", C_STRATUM[4]),
        ("SimilarityEngine\nk-NN + IDW\n+ CoverageGuard", C_STRATUM[3]),
        ("Ranked\nModels +\nConfidence", C_GREEN),
    ]
    top2 = Inches(3.25)
    box_w2 = Inches(2.0)
    gap2 = Inches(0.1)
    for i, (label, colour) in enumerate(query_boxes):
        left = Inches(0.55) + i * (box_w2 + gap2)
        _add_rect(slide, left, top2, box_w2, box_h, colour)
        _add_multiline_textbox(slide, left + Inches(0.08), top2 + Inches(0.08),
                                box_w2 - Inches(0.16), box_h - Inches(0.1),
                                [(label, 11, True, False, C_WHITE, PP_ALIGN.CENTER)])
        if i < len(query_boxes) - 1:
            _add_textbox(slide,
                         left + box_w2, top2 + Inches(0.44),
                         gap2, Inches(0.3),
                         arrow, font_size=16, bold=True, colour=C_WHITE,
                         align=PP_ALIGN.CENTER)

    # Math formulation
    _add_rect(slide, Inches(0.55), Inches(4.55), Inches(12.33), Inches(2.7),
              RGBColor(0x0D, 0x0D, 0x1E))
    math_lines = [
        ("Two-Phase Mathematical Formulation", 13, True, False, C_GOLD),
        ("", 5),
        ("Phase 1  —  Profiling:    Φ : 𝒟  →  𝐏 ∈ ℝᶠˣᴸ       F = 2,726 raw features,  L = |Λⱼ| languages in dataset", 12, False, True, C_WHITE),
        ("", 3),
        ("Phase 2  —  Fingerprint:  Ψ : 𝐏  →  f ∈ ℝ²⁷⁷       Ψ = Agg ∘ PCAₛ ∘ Std    (per stratum s)", 12, False, True, C_WHITE),
        ("", 3),
        ("Query:                    f̂   →  [SimilarityEngine]  →  m* ∈ ℳ           (< 100 ms on laptop)", 12, False, True, C_WHITE),
        ("", 5),
        ("Critical constraint:  The FITTED FeatureStratifier (StandardScaler + PCA) serialised in mkb.pkl must be", 11, False, False, C_LIGHT),
        ("reused at query time — never refit.  Refitting destroys comparability with MKB fingerprints.", 11, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.75), Inches(4.63), Inches(12.0), Inches(2.55),
                            math_lines)

    _add_notes(slide,
        "The two-phase architecture is the key to computational tractability. Phase 1 — profiling and MKB "
        "assembly — is expensive and runs once on HPC infrastructure. Phase 2 — query and recommendation — "
        "is a nearest-neighbour lookup in a 277-dimensional space with 18 data points. That query runs in "
        "under 100 milliseconds on a laptop. The discipline of 'fit once, transform many' is fundamental: "
        "reusing the fitted PCA from build time at query time ensures query fingerprints live in the same "
        "coordinate system as the MKB fingerprints. Training-serving skew — where the transform at serving "
        "time differs from training — is a classic ML engineering bug, and the mkb.pkl serialisation pattern "
        "explicitly prevents it."
    )
    return slide


def slide_04_datasets(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, C_BG)
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    _add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6),
                 "The 18 Knowledge Benchmark Datasets: Diversity by Design",
                 font_size=24, bold=True, colour=C_WHITE)
    _add_divider(slide, Inches(1.0))

    # Dataset table — left panel
    _add_rect(slide, Inches(0.55), Inches(1.1), Inches(7.6), Inches(6.15),
              RGBColor(0x0D, 0x0D, 0x1E))

    datasets = [
        ("Dataset", "Domain", "# Lang", True),
        ("OpenLID-v2", "Curated LID benchmark", "23", False),
        ("wikipedia", "Encyclopaedic", "24", False),
        ("exorde", "Social media", "24", False),
        ("flores_plus", "Low-resource NLP", "23", False),
        ("europarl", "Parliamentary proceedings", "13", False),
        ("amazon_reviews_multi", "E-commerce reviews", "6", False),
        ("multilingual_cc_news", "News articles", "21", False),
        ("tweet_sentiment_multi", "Twitter sentiment", "6", False),
        ("massive", "Virtual assistant utterances", "18", False),
        ("mmarco", "Machine-translated MS MARCO", "10", False),
        ("multi_eurlex", "EU legislation", "16", False),
        ("multilingual_toxicity", "Toxicity detection", "9", False),
        ("stsb_multi_mt", "Sentence similarity", "10", False),
        ("tydiqa", "Information-seeking QA", "5", False),
        ("xlsum", "News summarisation", "9", False),
        ("xnli", "Natural language inference", "7", False),
        ("librispeech_asr", "Audiobook transcripts (en)", "1", False),
    ]

    row_h = Inches(0.305)
    col_w = [Inches(2.55), Inches(3.2), Inches(0.9)]
    for r, (name, domain, n_lang, header) in enumerate(datasets):
        top_r = Inches(1.1) + r * row_h
        bg_col = RGBColor(0x1C, 0x2A, 0x40) if header else (
            RGBColor(0x12, 0x1A, 0x2E) if r % 2 == 0 else RGBColor(0x0D, 0x12, 0x22))
        for c, (val, w) in enumerate(zip([name, domain, n_lang], col_w)):
            left_c = Inches(0.55) + sum(col_w[:c])
            _add_rect(slide, left_c, top_r, w, row_h, bg_col)
            col_r = C_GOLD if header else (C_WHITE if c == 0 else C_LIGHT)
            _add_textbox(slide, left_c + Inches(0.07), top_r + Inches(0.04),
                         w - Inches(0.08), row_h - Inches(0.04),
                         val, font_size=10 if not header else 11,
                         bold=header, colour=col_r)

    # Right panel: language codes + file format
    right_lines = [
        ("24 Supported ISO 639-1 Codes", 13, True, False, C_GOLD),
        ("", 5),
        ("en  ca  zh  hr  da  nl  fi  fr  de  el", 11, False, True, C_WHITE),
        ("it  ja  ko  lt  mk  nb  pl  pt  ro  ru", 11, False, True, C_WHITE),
        ("sl  es  sv  uk", 11, False, True, C_WHITE),
        ("", 8),
        ("File Formats", 13, True, False, C_GOLD),
        ("", 4),
        ("Raw datasets:   Apache Parquet (.parquet)", 11, False, False, C_LIGHT),
        ("  Filename:  {iso_code}_{shard_id}.parquet", 11, False, True, C_WHITE),
        ("Profiles:       Python pickle (.pkl)", 11, False, False, C_LIGHT),
        ("  One file per dataset in profiles/", 11, False, False, C_LIGHT),
        ("MKB store:      mkb.pkl  (pickle, HIGHEST_PROTOCOL)", 11, False, False, C_LIGHT),
        ("Benchmarks:     benchmark_metadata.json  per model", 11, False, False, C_LIGHT),
        ("Config:         config.yaml", 11, False, False, C_LIGHT),
        ("", 8),
        ("Benchmark Metrics per Model Variant", 13, True, False, C_GOLD),
        ("", 4),
        ("accuracy  |  f1_macro  |  f1_weighted", 11, False, False, C_LIGHT),
        ("precision_macro  |  recall_macro", 11, False, False, C_LIGHT),
        ("inference_time_total_s", 11, False, False, C_LIGHT),
        ("", 8),
        ("MKB Formula", 13, True, False, C_GOLD),
        ("", 4),
        ("𝒦 = {𝒟₁, …, 𝒟₁₈}     |Λ_global| = 24", 11, False, True, C_WHITE),
        ("Nⱼ,ₗ ≤ 100  per language per dataset", 11, False, True, C_WHITE),
        ("Total language-dataset pairs: 340", 11, False, False, C_LIGHT),
    ]
    _add_rect(slide, Inches(8.35), Inches(1.1), Inches(4.55), Inches(6.15),
              RGBColor(0x0D, 0x0D, 0x1E))
    _add_multiline_textbox(slide, Inches(8.5), Inches(1.18), Inches(4.25), Inches(6.0),
                            right_lines)

    _add_notes(slide,
        "Dataset diversity was not accidental. We deliberately selected corpora that vary along three "
        "independent axes: domain (formal/informal, long-form/short-form), language coverage (from "
        "monolingual English to 24-language mixtures), and register (parliamentary, social media, "
        "encyclopaedic). This variation is what gives the MKB its discriminative power. The Parquet "
        "format was chosen because HuggingFace Hub delivers datasets as sharded Parquet files — we "
        "consume them directly without format conversion. The filename convention {iso}_{shard}.parquet "
        "allows the profiler to infer language identity from the path without parsing file contents."
    )
    return slide


def slide_05_snapshot_census(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, C_BG)
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    _add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6),
                 "CONF_THRESHOLD = 0.0: The Case Against Linguistic Suppression",
                 font_size=24, bold=True, colour=C_WHITE)
    _add_divider(slide, Inches(1.0))

    # Constants panel
    _add_rect(slide, Inches(0.55), Inches(1.1), Inches(4.0), Inches(3.6),
              RGBColor(0x0D, 0x0D, 0x1E))
    const_lines = [
        ("Key Constants", 14, True, False, C_GOLD),
        ("", 8),
        ("SNAPSHOT_SIZE  = 10,000", 14, True, True, C_WHITE),
        ("  Max texts for language census", 11, False, False, C_LIGHT),
        ("", 5),
        ("MAX_SAMPLES  = 100", 14, True, True, C_WHITE),
        ("  Cap per language per dataset", 11, False, False, C_LIGHT),
        ("", 5),
        ("CONF_THRESHOLD  = 0.0", 14, True, True, C_HIGHLIGHT),
        ("  FastText confidence threshold", 11, False, False, C_LIGHT),
        ("  Accept ALL detected tokens", 11, False, False, C_LIGHT),
        ("", 8),
        ("Source: profiler_knowledge_base.py", 10, False, True, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.7), Inches(1.2), Inches(3.7), Inches(3.4),
                            const_lines)

    # Comparison panel
    for i, (tau, title, colour, effect) in enumerate([
        ("tau = 0.7  (filtered)", "BIASED PROFILE", C_STRATUM[3],
         ["Minority-language samples discarded", "Ambiguous code-switched text lost",
          "Social-media noise removed silently", "Profile looks 'clean' but misleading",
          "Recommendation tuned to easy data"]),
        ("tau = 0.0  (unfiltered)", "HONEST PROFILE", C_GREEN,
         ["All detected tokens accepted", "Noisy, ambiguous samples retained",
          "Profile reflects real-world distribution", "Hard datasets look hard",
          "Recommendation accounts for complexity"]),
    ]):
        left = Inches(4.75 + i * 4.3)
        _add_rect(slide, left, Inches(1.1), Inches(4.05), Inches(3.6),
                  RGBColor(0x0D, 0x0D, 0x1E))
        _add_rect(slide, left, Inches(1.1), Inches(4.05), Inches(0.38), colour)
        _add_textbox(slide, left + Inches(0.1), Inches(1.13), Inches(3.85), Inches(0.35),
                     f"{tau}  —  {title}",
                     font_size=11, bold=True, colour=C_WHITE)
        eff_lines = [("  •  " + e, 11, False, False, C_LIGHT) for e in effect]
        eff_lines.insert(0, ("", 5))
        _add_multiline_textbox(slide, left + Inches(0.1), Inches(1.5),
                                Inches(3.85), Inches(3.0), eff_lines)

    # Equation
    _add_rect(slide, Inches(0.55), Inches(4.85), Inches(12.33), Inches(2.4),
              RGBColor(0x0D, 0x0D, 0x1E))
    eq_lines = [
        ("Bias Analysis of Confidence-Filtered Census", 13, True, False, C_GOLD),
        ("", 5),
        ("Standard (biased) filtered census:   𝒮ₗ = { t ∈ 𝒯 : l̂(t) = l  ∧  conf(t) ≥ τ }", 13, False, True, C_WHITE),
        ("  Selection bias:   𝒮ₗ ⊊ 𝒯ₗ  —  overrepresents prototypical (easy) samples; minority texts discarded", 11, False, False, C_LIGHT),
        ("", 4),
        ("Our unfiltered approach (τ = 0.0):    𝒮ₗ* = { t ∈ 𝒯 : l̂(t) = l }", 13, False, True, C_WHITE),
        ("  Unbiased:   𝔼[φ̄(𝒮ₗ*)] = φ̄(𝒯ₗ)    vs.    𝔼[φ̄(𝒮ₗ)] ≠ φ̄(𝒯ₗ)  when τ > 0", 11, False, False, C_LIGHT),
        ("", 4),
        ("100-sample convergence:  SE(φ̄ₙ) = σ/√n  →  at n=100,  SE = σ/10  (knee of effort–accuracy curve)", 11, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.75), Inches(4.93), Inches(12.0), Inches(2.25),
                            eq_lines)

    _add_notes(slide,
        "This is a subtle but important point about measurement validity — a concept at the heart of "
        "Industrial Engineering's Six Sigma quality frameworks. If we filter samples by FastText "
        "confidence, we are not measuring the corpus as it is; we are measuring an idealised version "
        "that discards the noisy edge cases. But those edge cases are precisely what distinguishes a "
        "social-media corpus from a parliamentary one. The 100-sample cap per language is a "
        "computational compromise: spaCy's deep linguistic analysis is expensive, and profiling more "
        "than 100 samples yields diminishing returns on the feature means while dramatically increasing "
        "processing time. We validated this: feature mean convergence is stable at n=50 and essentially "
        "flat by n=100. The knee of the SE curve sits squarely at n=100."
    )
    return slide


def slide_06_deepProfiler(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, C_BG)
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    _add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6),
                 "2,726 Features, 5 Semantic Domains: What We Measure and Why",
                 font_size=24, bold=True, colour=C_WHITE)
    _add_divider(slide, Inches(1.0))

    strata = [
        ("S1", "Morphological\nRichness", 917, C_STRATUM[0],
         "Person, number, definiteness,\ntense, voice, lemma distance,\ntypes per lemma, verbal forms"),
        ("S2", "Lexical\nDiversity", 441, C_STRATUM[1],
         "Type-token ratio, hapax\nlegomena, Honore statistic,\nZipf frequency scores"),
        ("S3", "Structural /\nSyntactic", 1288, C_STRATUM[2],
         "PoS incidence, PoS ratios,\nword/sentence length stats,\ndependency structure"),
        ("S4", "Information-\nTheoretic", 20, C_STRATUM[3],
         "Shannon entropy, Zipf curve\nsteepness (MLE slope alpha),\nZipf goodness-of-fit (R^2)"),
        ("S5", "Cross-Level\nCohesion", 260, C_STRATUM[4],
         "Par-doc, sent-doc overlap,\ncosine / Levenshtein distance\nacross text unit pairs"),
    ]

    box_w = Inches(2.38)
    box_h = Inches(3.5)
    top = Inches(1.15)
    for i, (code, name, n_feat, colour, details) in enumerate(strata):
        left = Inches(0.55) + i * (box_w + Inches(0.1))
        _add_rect(slide, left, top, box_w, box_h, RGBColor(0x0D, 0x0D, 0x1E))
        _add_rect(slide, left, top, box_w, Inches(0.38), colour)

        # stratum code + name
        _add_textbox(slide, left + Inches(0.07), top + Inches(0.04),
                     box_w - Inches(0.1), Inches(0.3),
                     f"{code}  {name}", font_size=12, bold=True, colour=C_WHITE)

        # feature count badge
        _add_rect(slide, left + Inches(0.07), top + Inches(0.5),
                  box_w - Inches(0.14), Inches(0.5), colour)
        _add_textbox(slide, left + Inches(0.07), top + Inches(0.52),
                     box_w - Inches(0.14), Inches(0.46),
                     f"{n_feat:,}  raw features",
                     font_size=14, bold=True, colour=C_WHITE, align=PP_ALIGN.CENTER)

        _add_multiline_textbox(slide, left + Inches(0.1), top + Inches(1.1),
                                box_w - Inches(0.15), Inches(2.2),
                                [(details, 10, False, False, C_LIGHT)])

    # formula panel
    _add_rect(slide, Inches(0.55), Inches(4.8), Inches(12.33), Inches(2.45),
              RGBColor(0x0D, 0x0D, 0x1E))
    eq_lines = [
        ("Profile Extraction Formula", 13, True, False, C_GOLD),
        ("", 5),
        ("For dataset 𝒟ⱼ and language l,  the raw profile is the feature-wise mean across Nⱼ,ₗ sampled texts:", 12, False, False, C_LIGHT),
        ("", 3),
        ("  p_{j,l}  =  (1 / Nⱼ,ₗ) · Σₙ₌₁^{Nⱼ,ₗ}  φ(tⱼ,ₗ,ₙ)     ∈ ℝᶠ,    F ∈ {2726, 2926}", 13, False, True, C_WHITE),
        ("", 3),
        ("Full dataset profile matrix:   𝐏ⱼ  =  [ pⱼ,ₗ₁ | pⱼ,ₗ₂ | … | pⱼ,ₗ|Λⱼ| ]   ∈ ℝᶠˣ|Λⱼ|", 13, False, True, C_WHITE),
        ("", 3),
        ("Serialised to:   profiles/{dataset_name}.pkl   as pd.DataFrame  (F rows × Lⱼ language columns)", 11, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.75), Inches(4.88), Inches(12.0), Inches(2.3),
                            eq_lines)

    _add_notes(slide,
        "Why 2,726 features? This is not a magic number — it is the union of all features that spaCy's "
        "linguistic annotation pipeline can produce for the 24 languages in our benchmark. Some features "
        "are universal (every language has token counts), while others are language-specific — case "
        "morphology features are zero for isolating languages like Mandarin. We preserve this sparsity "
        "rather than imputing it, because the pattern of zeros is itself linguistically informative: a "
        "dataset with many zero morphological features is likely rich in isolating languages. A skeptic "
        "might ask: why not use transformer embeddings? The answer is interpretability. I cannot explain "
        "to a practitioner why their dataset is similar to Wikipedia using a 768-dim BERT embedding. I "
        "can explain it using morphological richness scores and lexical diversity metrics."
    )
    return slide


def slide_07_pca(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, C_BG)
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    _add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6),
                 "Stratum-Wise PCA: 2,926  →  52 Principal Components",
                 font_size=24, bold=True, colour=C_WHITE)
    _add_divider(slide, Inches(1.0))

    # Table
    _add_rect(slide, Inches(0.55), Inches(1.1), Inches(6.9), Inches(3.5),
              RGBColor(0x0D, 0x0D, 0x1E))

    headers = ("Stratum", "Raw Features", "PCs Retained", "Variance %")
    rows = [
        ("S1  Morphological",  "917",   "14", "95.0%", C_STRATUM[0]),
        ("S2  Lexical Diversity", "441", "12", "95.5%", C_STRATUM[1]),
        ("S3  Structural",   "1,288",   "13", "95.5%", C_STRATUM[2]),
        ("S4  Info-Theoretic",  "20",    "4", "98.6%", C_STRATUM[3]),
        ("S5  Cross-Level",    "260",    "9", "96.1%", C_STRATUM[4]),
        ("TOTAL",           "2,926",   "52",  "—",    C_GOLD),
    ]
    col_w2 = [Inches(2.2), Inches(1.6), Inches(1.6), Inches(1.4)]
    row_h2 = Inches(0.42)

    # header row
    for c, (h, w) in enumerate(zip(headers, col_w2)):
        left_c = Inches(0.55) + sum(col_w2[:c])
        _add_rect(slide, left_c, Inches(1.1), w, row_h2, RGBColor(0x1C, 0x2A, 0x40))
        _add_textbox(slide, left_c + Inches(0.07), Inches(1.14), w, row_h2 - Inches(0.05),
                     h, font_size=11, bold=True, colour=C_GOLD)

    for r, (name, raw, pcs, var, colour) in enumerate(rows):
        top_r = Inches(1.1) + (r + 1) * row_h2
        bg = RGBColor(0x12, 0x1A, 0x2E) if r % 2 == 0 else RGBColor(0x0D, 0x12, 0x22)
        for c, (val, w) in enumerate(zip([name, raw, pcs, var], col_w2)):
            left_c = Inches(0.55) + sum(col_w2[:c])
            _add_rect(slide, left_c, top_r, w, row_h2, bg)
            col_val = colour if c == 0 else C_WHITE
            _add_textbox(slide, left_c + Inches(0.07), top_r + Inches(0.05),
                         w, row_h2 - Inches(0.05),
                         val, font_size=11, bold=(r == len(rows) - 1), colour=col_val)

    # Design rationale
    _add_rect(slide, Inches(7.65), Inches(1.1), Inches(5.25), Inches(3.5),
              RGBColor(0x0D, 0x0D, 0x1E))
    rat_lines = [
        ("Design Rationale", 13, True, False, C_GOLD),
        ("", 6),
        ("  Why stratum-wise?  NOT global PCA:", 12, True, False, C_WHITE),
        ("", 3),
        (" •  F ≫ N_obs  globally (2,926 features vs. 24 samples)", 11, False, False, C_LIGHT),
        ("    Global PCA is rank-23 at best: degenerate", 11, False, False, C_LIGHT),
        (" •  Each stratum = coherent semantic domain", 11, False, False, C_LIGHT),
        ("    PCs remain linguistically interpretable", 11, False, False, C_LIGHT),
        (" •  S4: 20 features → 4 PCs (98.6% variance)", 11, False, False, C_LIGHT),
        ("    Entropy + Zipf are highly correlated", 11, False, False, C_LIGHT),
        ("", 5),
        ("  config.yaml settings:", 12, True, False, C_WHITE),
        ("  variance_threshold: 0.95", 11, False, True, C_LIGHT),
        ("  max_pca_components: 20  (hard cap)", 11, False, True, C_LIGHT),
        ("  N_obs = 24 language samples for PCA fit", 11, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(7.8), Inches(1.18), Inches(4.95), Inches(3.3),
                            rat_lines)

    # Math panel
    _add_rect(slide, Inches(0.55), Inches(4.75), Inches(12.33), Inches(2.5),
              RGBColor(0x0D, 0x0D, 0x1E))
    math_lines = [
        ("Stratum-Wise PCA Algorithm", 13, True, False, C_GOLD),
        ("", 5),
        ("Step 1  Standardise:   X̃ₛ = StandardScaler(Xₛ)    ⟹    X̃ₛ,ᵢⱼ = (Xₛ,ᵢⱼ − μₛ,ⱼ) / σₛ,ⱼ", 12, False, True, C_WHITE),
        ("         Where:  X̃ₛ ∈ ℝⁿˣᶠˢ,  n = N_obs = 24,  fₛ = raw features in stratum s", 11, False, False, C_LIGHT),
        ("", 3),
        ("Step 2  PCA:           𝐙ₛ = X̃ₛ𝐕ₛ        where  𝐕ₛ = top-Kₛ eigenvectors of  X̃ₛᵀX̃ₛ", 12, False, True, C_WHITE),
        ("         Where:  𝐕ₛ ∈ ℝᶠˢˣᴷˢ (PC loadings),  𝐙ₛ ∈ ℝⁿˣᴷˢ (score matrix)", 11, False, False, C_LIGHT),
        ("", 3),
        ("         Kₛ = min(Kₛ*, 20)     Kₛ* = min{ k : Σᵢ₌₁ᵏ λₛ,ᵢ / Σᵢ λₛ,ᵢ  ≥  0.95 }", 12, False, True, C_WHITE),
        ("", 3),
        ("Rank check:   F_S4 = 20  <  N_obs = 24  ≪  F_S3 = 1,288   ⟹  stratum partitioning is statistically necessary", 11, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.75), Inches(4.83), Inches(12.0), Inches(2.35),
                            math_lines)

    _add_notes(slide,
        "The stratum-wise design is the key methodological decision in this thesis. A naive approach "
        "would run a single PCA on all 2,926 features. That would be statistically invalid: with 24 "
        "observations and 2,926 features you have a rank-23 matrix at best. More importantly, it would "
        "mix morphological signals with syntactic signals, creating principal components that are "
        "linguistically uninterpretable. By keeping the strata separate, each PC has a coherent "
        "semantic interpretation. The S4 stratum is the clearest case: 20 information-theoretic features "
        "compressed to just 4 PCs that explain 98.6% of variance — a near-perfect compression because "
        "entropy and Zipf statistics are highly correlated across languages."
    )
    return slide


def slide_08_fingerprint(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, C_BG)
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    _add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6),
                 "277-Dimensional Fingerprint: The Linguistic DNA of a Dataset",
                 font_size=24, bold=True, colour=C_WHITE)
    _add_divider(slide, Inches(1.0))

    # DNA strand visualisation (stacked bars)
    stratum_info = [
        ("S1", "Morphological", 70, 14, C_STRATUM[0]),
        ("S2", "Lexical", 60, 12, C_STRATUM[1]),
        ("S3", "Structural", 65, 13, C_STRATUM[2]),
        ("S4", "Info-Theoretic", 20, 4, C_STRATUM[3]),
        ("S5", "Cross-Level", 45, 9, C_STRATUM[4]),
        ("S6", "Typological", 17, 17, C_STRATUM[5]),
    ]
    total_dims = sum(d for _, _, d, _, _ in stratum_info)  # 277

    bar_left = Inches(0.55)
    bar_top = Inches(1.15)
    bar_total_w = Inches(8.5)
    bar_h = Inches(0.7)

    cur_left = bar_left
    for code, name, dims, n_pc, colour in stratum_info:
        w = bar_total_w * dims / total_dims
        _add_rect(slide, cur_left, bar_top, w, bar_h, colour)
        if w > Inches(0.8):
            _add_textbox(slide, cur_left + Inches(0.05), bar_top + Inches(0.08),
                         w - Inches(0.07), Inches(0.55),
                         f"{code}\n{dims}d", font_size=9, bold=True,
                         colour=C_WHITE, align=PP_ALIGN.CENTER)
        cur_left += w

    # Label under bar
    _add_textbox(slide, bar_left, bar_top + bar_h + Inches(0.05),
                 bar_total_w, Inches(0.25),
                 f"Total: {total_dims} dimensions   (OrderedDict[str, float]   —   keys are ordered by stratum)",
                 font_size=10, colour=C_LIGHT, italic=True)

    # Detail table on right
    _add_rect(slide, Inches(9.2), Inches(1.1), Inches(3.7), Inches(2.1),
              RGBColor(0x0D, 0x0D, 0x1E))
    dim_table = [
        ("Stratum", "PCs", "x5 stats", "=Dims", True),
        ("S1 Morphological", "14", "5", "70", False),
        ("S2 Lexical", "12", "5", "60", False),
        ("S3 Structural", "13", "5", "65", False),
        ("S4 Info-Theoretic", "4", "5", "20", False),
        ("S5 Cross-Level", "9", "5", "45", False),
        ("S6 Typological", "—", "17 flags", "17", False),
        ("TOTAL", "52", "", "277", True),
    ]
    rh = Inches(0.233)
    cw = [Inches(1.6), Inches(0.5), Inches(0.8), Inches(0.6)]
    for ri, row in enumerate(dim_table):
        *vals, hdr = row
        for ci, (val, cw_) in enumerate(zip(vals, cw)):
            left_c = Inches(9.2) + sum(cw[:ci])
            bg = RGBColor(0x1C, 0x2A, 0x40) if hdr else (
                RGBColor(0x12, 0x1A, 0x2E) if ri % 2 == 0 else RGBColor(0x0D, 0x12, 0x22))
            _add_rect(slide, left_c, Inches(1.1) + ri * rh, cw_, rh, bg)
            c_col = C_GOLD if hdr else C_LIGHT
            _add_textbox(slide, left_c + Inches(0.05), Inches(1.12) + ri * rh,
                         cw_ - Inches(0.05), rh,
                         val, font_size=9, bold=hdr, colour=c_col)

    # Five statistics explanation
    _add_rect(slide, Inches(0.55), Inches(2.2), Inches(8.5), Inches(2.3),
              RGBColor(0x0D, 0x0D, 0x1E))
    stats_lines = [
        ("Five Statistics per Principal Component  (S1–S5)", 13, True, False, C_GOLD),
        ("", 4),
        ("For stratum s, PC r, let  zₛ,ᵣ ∈ ℝ|Λⱼ|  be the vector of PC-r scores across all languages:", 11, False, False, C_LIGHT),
        ("", 3),
        ("  {s}_PC{r}_mean  =  z̄ₛ,ᵣ          mean of PC scores across languages     (central tendency)", 11, False, True, C_WHITE),
        ("  {s}_PC{r}_std   =  σ(zₛ,ᵣ)       std across languages                   (spread)", 11, False, True, C_WHITE),
        ("  {s}_PC{r}_min   =  min(zₛ,ᵣ)     minimum PC score across languages", 11, False, True, C_WHITE),
        ("  {s}_PC{r}_max   =  max(zₛ,ᵣ)     maximum PC score across languages", 11, False, True, C_WHITE),
        ("  {s}_PC{r}_het   =  s(zₛ,ᵣ, δ=1)  intra-dataset heterogeneity  (= 0 if monolingual)", 11, False, True, C_WHITE),
    ]
    _add_multiline_textbox(slide, Inches(0.7), Inches(2.28), Inches(8.3), Inches(2.15),
                            stats_lines)

    # S6 flags
    _add_rect(slide, Inches(0.55), Inches(4.63), Inches(12.33), Inches(2.62),
              RGBColor(0x0D, 0x0D, 0x1E))
    eq_lines = [
        ("Fingerprint Construction Formula  (FingerprintBuilder.build)", 13, True, False, C_GOLD),
        ("", 4),
        ("For stratum s, PC index r,  let  zₛ,ᵣ ∈ ℝ|Λⱼ|  be the PC-r scores across all languages in 𝒟ⱼ:", 11, False, False, C_LIGHT),
        ("", 3),
        ("  𝐟ₛ,ᵣ  =  ( z̄ₛ,ᵣ,  σ(zₛ,ᵣ),  min(zₛ,ᵣ),  max(zₛ,ᵣ),  s(zₛ,ᵣ) )    ∈ ℝ⁵", 13, False, True, C_WHITE),
        ("", 3),
        ("Full fingerprint:   𝐟ⱼ  =  [ 𝐟_{S1,0} ‖ … ‖ 𝐟_{S1,13} ‖ 𝐟_{S2,0} ‖ … ‖ 𝐟_{S5,8} ‖ cⱼ ]   ∈ ℝ²⁷⁷", 13, False, True, C_WHITE),
        ("", 3),
        ("S6 categorical vector  cⱼ ∈ ℝ¹⁷:  cat__has_cjk, cat__has_cyrillic, cat__frac_germanic, cat__n_tonal, …", 11, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.75), Inches(4.71), Inches(12.0), Inches(2.5),
                            eq_lines)

    _add_notes(slide,
        "The five statistics per PC are not arbitrary — they are a minimal sufficient statistic for the "
        "distribution of that PC across the dataset's languages. The mean tells you where the dataset "
        "sits on average, the std and min/max tell you its spread, and the het — which emphasises "
        "within-dataset heterogeneity as a first-class feature — captures whether a dataset's languages "
        "are clustered or dispersed in this linguistic dimension. A dataset with high mean and low het "
        "is linguistically uniform. A dataset with high mean and high het is diverse and challenging. "
        "These two datasets need different models even if their averages match. The OrderedDict type "
        "guarantees key order — critical when we serialise to numpy arrays for distance computation."
    )
    return slide


def slide_09_knn_idw(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, C_BG)
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    _add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6),
                 "Weighted k-NN & Inverse-Distance Weighting: The Similarity Engine",
                 font_size=24, bold=True, colour=C_WHITE)
    _add_divider(slide, Inches(1.0))

    # Step-by-step left panel
    _add_rect(slide, Inches(0.55), Inches(1.1), Inches(6.2), Inches(5.9),
              RGBColor(0x0D, 0x0D, 0x1E))
    steps = [
        ("Step 1  —  Per-Stratum Euclidean Distance", C_STRATUM[0]),
        ("Step 2  —  S6 Normalised Hamming Distance", C_STRATUM[5]),
        ("Step 3  —  Weighted Composite Distance", C_GOLD),
        ("Step 4  —  k-NN Retrieval  (k = 3)", C_STRATUM[2]),
        ("Step 5  —  IDW Vote per Model Variant", C_STRATUM[4]),
        ("Step 6  —  Confidence Score", C_GREEN),
    ]
    step_detail = [
        "dₛ(f̂, fⱼ) = ‖f̂⁽ˢ⁾ − fⱼ⁽ˢ⁾‖₂\nfor s ∈ {S1, S2, S3, S4, S5}",
        "d_S6 = (1/17) · Σᵣ 𝟙[f̂ᵣᶜᵃᵗ ≠ fⱼ,ᵣᶜᵃᵗ]\nnormalised Hamming over 17 boolean flags",
        "d(f̂, fⱼ) = Σₛ(wₛ · dₛ) / Σₛ(wₛ)\ndefault: wₛ = 1.0 for all strata",
        "Sort candidates by d ascending\nReturn top-k NeighbourResult objects  (k=3 default)",
        "score(m) = Σᵢ [Acc(m,𝒟ᵢ)·γᵢ / (dᵢ+ε)]\n           ————————————————————————\n           Σᵢ [1 / (dᵢ + ε)]",
        "conf = |{i ∈ 𝒩ₖ : m̂ᵢ* = m*}| / k\nFraction of neighbours agreeing with recommendation",
    ]
    for i, ((label, colour), detail) in enumerate(zip(steps, step_detail)):
        top_s = Inches(1.15) + i * Inches(0.93)
        _add_rect(slide, Inches(0.6), top_s, Inches(0.38), Inches(0.75), colour)
        _add_textbox(slide, Inches(0.6), top_s + Inches(0.22),
                     Inches(0.38), Inches(0.3),
                     str(i + 1), font_size=13, bold=True, colour=C_WHITE,
                     align=PP_ALIGN.CENTER)
        lines = [
            (label, 11, True, False, colour),
            (detail, 10, False, True, C_WHITE),
        ]
        _add_multiline_textbox(slide, Inches(1.07), top_s + Inches(0.04),
                                Inches(5.55), Inches(0.85), lines)

    # Right panel: worked example
    _add_rect(slide, Inches(7.0), Inches(1.1), Inches(6.0), Inches(5.9),
              RGBColor(0x0D, 0x0D, 0x1E))
    example = [
        ("Worked IDW Vote Example", 13, True, False, C_GOLD),
        ("", 6),
        ("Query fingerprint f̂ retrieved k=3 nearest neighbours:", 11, False, False, C_LIGHT),
        ("", 4),
        ("  Neighbour 1:  wikipedia    d₁ = 0.12   Acc(ft-large) = 0.94", 11, False, True, C_WHITE),
        ("  Neighbour 2:  europarl     d₂ = 0.21   Acc(ft-large) = 0.91", 11, False, True, C_WHITE),
        ("  Neighbour 3:  flores_plus  d₃ = 0.35   Acc(ft-small) = 0.88", 11, False, True, C_WHITE),
        ("", 5),
        ("IDW weights  wᵢ = 1/(dᵢ + ε),   ε = 10⁻⁹:", 11, True, False, C_WHITE),
        ("  w₁ = 1/0.12 = 8.33    w₂ = 1/0.21 = 4.76    w₃ = 1/0.35 = 2.86", 11, False, True, C_LIGHT),
        ("", 5),
        ("score(ft-large)  =  (8.33·0.94 + 4.76·0.91) / (8.33+4.76)  =  0.927", 11, False, True, C_WHITE),
        ("score(ft-small)  =  (2.86·0.88) / 2.86  =  0.880", 11, False, True, C_WHITE),
        ("", 5),
        ("  ⟹  Recommendation:  ft-large", 13, True, False, C_GREEN),
        ("  ⟹  Confidence:  2/3 ≈ 0.67  (neighbours 1 and 2 agree)", 12, False, False, C_LIGHT),
        ("", 5),
        ("Why Euclidean in PCA space (not cosine)?", 11, True, False, C_GOLD),
        ("  PCA ensures orthogonality  (no multicollinearity)", 10, False, False, C_LIGHT),
        ("  StandardScaler ensures equal-scale dimensions", 10, False, False, C_LIGHT),
        ("  Magnitude matters: extreme PC scores = extreme domain", 10, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(7.15), Inches(1.18), Inches(5.7), Inches(5.75),
                            example)

    _add_notes(slide,
        "Why Euclidean distance in PCA space rather than cosine similarity on raw features? Three "
        "reasons. First, PCA ensures the dimensions are orthogonal — there is no multicollinearity to "
        "distort Euclidean distances. Second, we standardised before PCA, so all features are on the "
        "same scale. Third, cosine similarity ignores magnitude, which matters here: a dataset with "
        "large PC scores is more extreme in that linguistic dimension, and we want that extremity to "
        "count. The k=3 default is conservative given our N=18 knowledge base — increasing k risks "
        "pulling in linguistically dissimilar datasets that dilute the vote. The IDW formula is a "
        "continuous generalisation of majority vote where nearer neighbour = stronger vote."
    )
    return slide


def slide_10_coverage_conclusions(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, C_BG)
    _add_rect(slide, Inches(0), Inches(0), Inches(0.3), SLIDE_H, C_HIGHLIGHT)

    _add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6),
                 "Coverage Guard & Conclusions: Principled Degradation + What We Built",
                 font_size=24, bold=True, colour=C_WHITE)
    _add_divider(slide, Inches(1.0))

    # Coverage guard
    _add_rect(slide, Inches(0.55), Inches(1.1), Inches(6.2), Inches(3.8),
              RGBColor(0x0D, 0x0D, 0x1E))
    cov_lines = [
        ("Coverage Guard  (SimilarityEngine.query)", 13, True, False, C_GOLD),
        ("", 5),
        ("Purpose: soft-penalise models with language coverage gaps", 11, False, False, C_LIGHT),
        ("", 4),
        ("Δᵢ(m)  =  Λ_user  ∖  Λ_m", 12, False, True, C_WHITE),
        ("  (languages in user corpus that model m was not trained on)", 10, False, False, C_LIGHT),
        ("", 3),
        ("γᵢ(m)  =  1  −  |Δᵢ(m)| / |Λ_user|", 12, False, True, C_WHITE),
        ("", 3),
        ("  γ = 1.0   ⟹  Δ = ∅  (full coverage)   ⟹  no penalty", 10, False, False, C_GREEN),
        ("  γ = 0.75  ⟹  25% gap              ⟹  vote weight × 0.75", 10, False, False, C_GOLD),
        ("  γ = 0.0   ⟹  zero coverage        ⟹  effectively excluded", 10, False, False, C_HIGHLIGHT),
        ("", 5),
        ("Truly uncoverable languages  (∉ any 𝒟ⱼ ∈ 𝒦):", 11, True, False, C_WHITE),
        ("  ⟹  Flagged with ⚠ warning in RecommendationResult", 10, False, False, C_LIGHT),
        ("  ⟹  Transparent communication of epistemic limits", 10, False, False, C_LIGHT),
        ("", 4),
        ("Preference ordering per neighbour:", 11, True, False, C_WHITE),
        ("  1. Fully-covering variants  (Δ = ∅)", 10, False, False, C_LIGHT),
        ("  2. Smallest |Δ| variant  (if none fully covers)", 10, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.7), Inches(1.18), Inches(5.9), Inches(3.65),
                            cov_lines)

    # Conclusions + future work
    _add_rect(slide, Inches(6.95), Inches(1.1), Inches(6.1), Inches(3.8),
              RGBColor(0x0D, 0x0D, 0x1E))
    conc_lines = [
        ("What Was Built  ✓", 13, True, False, C_GREEN),
        ("", 4),
        ("  ✓  277-dim Linguistic DNA fingerprint", 11, False, False, C_LIGHT),
        ("  ✓  Stratum-wise PCA (5 semantic domains)", 11, False, False, C_LIGHT),
        ("  ✓  IDW vote with coverage guard", 11, False, False, C_LIGHT),
        ("  ✓  Sub-second CLI/API toolkit (HPC + laptop)", 11, False, False, C_LIGHT),
        ("  ✓  18 datasets  x  24 languages  x  8 metrics", 11, False, False, C_LIGHT),
        ("", 6),
        ("Future Work", 13, True, False, C_GOLD),
        ("", 4),
        ("  1.  MKB expansion: more datasets, low-resource langs", 11, False, False, C_LIGHT),
        ("  2.  Stratum weight optimisation via Bayesian opt.", 11, False, False, C_LIGHT),
        ("     Learn optimal {w_s} from LOO feedback", 10, False, False, C_LIGHT),
        ("  3.  Portable serialisation: ONNX / joblib", 11, False, False, C_LIGHT),
        ("     Replace pickle for cross-environment deploy", 10, False, False, C_LIGHT),
        ("", 5),
        ("Leave-One-Out Validation", 13, True, False, C_GOLD),
        ("  Acc_LOO = (1/18) · Σⱼ 𝟙[m̂ⱼ = m*ⱼ]", 11, False, True, C_WHITE),
        ("  N=18 folds  |  k=3  |  honest uncertainty estimates", 10, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(7.1), Inches(1.18), Inches(5.8), Inches(3.65),
                            conc_lines)

    # Full closed-form equation at bottom
    _add_rect(slide, Inches(0.55), Inches(5.05), Inches(12.33), Inches(2.2),
              RGBColor(0x0D, 0x0D, 0x1E))
    full_eq = [
        ("Complete Recommendation Formula (closed form)", 13, True, False, C_GOLD),
        ("", 5),
        ("m* = arg max_m   Σᵢ∈𝒩ₖ(f̂)   Acc(m, 𝒟ᵢ) · (1 − |Λ_user ∖ Λ_m| / |Λ_user|)", 13, False, True, C_WHITE),
        ("                 ————————————————————————————————————————————————————————————", 11, False, False, C_LIGHT),
        ("                                    d(f̂, fᵢ)  +  ε", 13, False, True, C_WHITE),
        ("", 4),
        ("where   d = Σₛ(wₛ · ‖·‖₂⁽ˢ⁾) / Σₛ(wₛ)    𝐟ⱼ ∈ ℝ²⁷⁷    𝒩ₖ = top-k by d    k=3    ε = 10⁻⁹", 11, False, False, C_LIGHT),
    ]
    _add_multiline_textbox(slide, Inches(0.75), Inches(5.13), Inches(12.0), Inches(2.05),
                            full_eq)

    _add_notes(slide,
        "The coverage guard embodies a quality principle from operations research: when you cannot "
        "satisfy a hard constraint, degrade gracefully rather than fail silently. A hard exclusion "
        "rule would often return no recommendation at all, because our 24-language benchmark cannot "
        "anticipate every possible language a user might bring. The soft penalty says: this model is "
        "probably suboptimal for your full language set, but here is our best estimate of its "
        "performance weighted by how much of your data it actually handles.\n\n"
        "The thesis delivers on its core promise: a practitioner with a new multilingual dataset can "
        "query the MKB and receive an interpretable, justified model recommendation in under a second, "
        "without running a single model evaluation. The system does not pretend to omniscience — the "
        "coverage guard and uncertainty estimates are explicit about what the system does not know. "
        "This is the hallmark of responsible engineering: a system that fails gracefully and "
        "communicates its own limitations. The foundation is solid enough that improvements are "
        "incremental, not foundational."
    )
    return slide


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_presentation(output_path: str = "lid_toolkit_presentation.pptx"):
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    builders = [
        slide_01_title,
        slide_02_problem,
        slide_03_architecture,
        slide_04_datasets,
        slide_05_snapshot_census,
        slide_06_deepProfiler,
        slide_07_pca,
        slide_08_fingerprint,
        slide_09_knn_idw,
        slide_10_coverage_conclusions,
    ]

    print(f"Building {len(builders)}-slide presentation...")
    for i, builder in enumerate(builders, 1):
        builder(prs)
        print(f"  Slide {i:02d} done: {builder.__name__}")

    prs.save(output_path)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    build_presentation()
