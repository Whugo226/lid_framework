"""Capture the four Ch5 §5.7.2 figures from the running LID Toolkit dashboard.

Drives the real app in headless Edge: uploads the same 600-document WiLI-2018
sample used by analysis/walkthrough_demo.py, profiles it once, then captures
the panels the thesis section references.  Local filesystem paths are excluded
by hiding the sidebar before every capture.

Re-run this whenever the dashboard layout changes, otherwise the figures in
Chapter 5 stop matching the artefact they document.

Prerequisites
-------------
1. Start the dashboard **in a fresh process** (the profiling wall-clock the
   figures report is a cold-start number; a warm process profiles in ~55 s
   instead of ~100 s)::

       cd <repo root>
       python -m streamlit run src/lid_toolkit/explainer/dashboard.py \\
           --server.headless=true --server.port=8501

2. Playwright, in any interpreter (it does not need to be thesis_final)::

       python -m venv C:\\Users\\User\\AppData\\Local\\lidshot
       C:\\Users\\User\\AppData\\Local\\lidshot\\Scripts\\python -m pip install playwright

   The system Microsoft Edge is driven via ``channel="msedge"``, so no browser
   download is required.

3. Run this script with that interpreter. It writes
   fig1..fig4 into the thesis ``figures/dashboard/`` directory and a small
   ``capture_facts.json`` beside itself recording the on-screen timing banner.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"
CSV = Path(r"c:/Users/User/OneDrive/Masters/Python/toolkit_dev/lid_toolkit"
           r"/test_examples/wili2018_walkthrough_600.csv")
OUT = Path(r"c:/Users/User/OneDrive/Masters/Thesis/Thesis Template Legit/figures/dashboard")
OUT.mkdir(parents=True, exist_ok=True)

WIDTH = 1200

HIDE_CHROME = """
() => {
  const kill = sel => document.querySelectorAll(sel).forEach(e => e.remove());
  kill('[data-testid="stToolbar"]');
  kill('[data-testid="stDecoration"]');
  kill('[data-testid="stStatusWidget"]');
  kill('[data-testid="stSidebarCollapsedControl"]');
  const sb = document.querySelector('[data-testid="stSidebar"]');
  if (sb) sb.style.display = 'none';
  window.dispatchEvent(new Event('resize'));
}
"""


def log(*a):
    print(*a, flush=True)


def settle(page, ms=2000):
    page.wait_for_timeout(ms)
    page.evaluate(HIDE_CHROME)
    page.wait_for_timeout(900)


def resize(page, height):
    page.set_viewport_size({"width": WIDTH, "height": height})
    settle(page, 1600)


def click_tab(page, label):
    page.get_by_role("tab", name=label).click()
    page.wait_for_timeout(1600)


def shot(page, name, *, from_controls=False, from_title=False,
         stop_before=None, pad=28):
    """Screenshot the viewport.

    ``from_controls`` crops the title banner away (starting at the live priority
    -metric control); ``stop_before`` ends the crop just above the named heading
    so the figure closes on a section boundary rather than mid-widget.
    """
    vh = page.evaluate("() => window.innerHeight")
    top = 0.0
    if from_controls:
        box = page.get_by_text("Priority metric", exact=True).first.bounding_box()
        top = max(0.0, box["y"] - 16)
    elif from_title:
        box = page.locator(".lidf-title").first.bounding_box()
        top = max(0.0, box["y"] - 26)
    bottom = float(vh)
    if stop_before:
        heads = page.get_by_role("heading", name=stop_before, exact=False)
        loc = heads.first if heads.count() else \
            page.get_by_text(stop_before, exact=False).first
        b = loc.bounding_box()
        if b and top + 200 < b["y"] - pad < vh:
            bottom = b["y"] - pad
        else:
            log(f"     (stop_before {stop_before!r} not usable: {b})")
    clip = {"x": 0.0, "y": top, "width": float(WIDTH), "height": bottom - top}
    path = OUT / name
    page.screenshot(path=str(path), clip=clip)
    log(f"  -> {path.name}  ({int(clip['height'])} css px, "
        f"{path.stat().st_size // 1024} KB)")


def main():
    facts = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": WIDTH, "height": 1100},
                                device_scale_factor=2)
        page.set_default_timeout(60_000)

        log("opening", URL)
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(2500)

        log("uploading corpus")
        page.locator('input[type="file"]').set_input_files(str(CSV))
        page.wait_for_timeout(2000)

        log("clicking Profile Corpus")
        page.get_by_role("button", name="Profile Corpus").click()

        log("waiting for profiling (up to 12 min)…")
        page.get_by_role("tab", name="Corpus profile").wait_for(timeout=720_000)
        page.wait_for_timeout(4000)
        settle(page)

        facts["timing_banner"] = page.get_by_text(
            "Corpus profiled in", exact=False).first.inner_text()
        log("  ", facts["timing_banner"])

        # ── Figure 1 — corpus profile (title banner kept) ─────────────────────
        log("FIG 1 — Corpus Profile")
        click_tab(page, "Corpus profile")
        resize(page, 1260)
        shot(page, "fig1_corpus_profile.png", from_title=True,
             stop_before="Document-Length Summary")

        # ── Figure 2 — recommendation, quality priority ───────────────────────
        log("FIG 2 — Recommendation (f1_weighted)")
        click_tab(page, "Recommendation")
        resize(page, 1700)
        shot(page, "fig2_recommendation.png", from_controls=True,
             stop_before="Top-k Nearest Historical Datasets")

        # ── Figure 3 — per-stratum decomposition ──────────────────────────────
        log("FIG 3 — How It Works, Step 3")
        click_tab(page, "How it works")
        settle(page)
        page.get_by_text("Step 1 — Corpus Fingerprint", exact=False).first.click()
        page.wait_for_timeout(900)
        page.get_by_text("Step 3 — Per-Stratum Distance Breakdown",
                         exact=False).first.click()
        page.wait_for_timeout(2500)
        resize(page, 1900)
        shot(page, "fig3_stratum_decomposition.png", from_controls=True,
             stop_before="Step 4 —")

        # ── Figure 4 — latency re-query + coverage guard ──────────────────────
        log("FIG 4 — latency re-query")
        click_tab(page, "Recommendation")
        resize(page, 1420)
        page.locator('[data-testid="stSelectbox"]').first.click()
        page.wait_for_timeout(800)
        page.get_by_role("option", name="inference_time_ms_per_sample").click()
        log("  waiting for re-query…")
        page.get_by_text("COVERAGE WARNING", exact=False).first.wait_for(timeout=60_000)
        click_tab(page, "Recommendation")
        resize(page, 1420)
        facts["latency_banner"] = page.get_by_text(
            "Corpus profiled in", exact=False).first.inner_text()
        facts["coverage_warning"] = page.get_by_text(
            "COVERAGE WARNING", exact=False).first.inner_text()
        log("  ", facts["latency_banner"])
        log("  ", facts["coverage_warning"])
        shot(page, "fig4_latency_coverage_guard.png", from_controls=True,
             stop_before="Consensus Confidence")

        browser.close()

    Path(__file__).with_name("capture_facts.json").write_text(
        json.dumps(facts, indent=2, ensure_ascii=False), encoding="utf-8")
    log("done")


if __name__ == "__main__":
    sys.exit(main())
