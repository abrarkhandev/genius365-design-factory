#!/usr/bin/env python3
"""Render a LinkedIn carousel HTML to a PDF (the LinkedIn document) + slide PNGs.

LinkedIn document posts are PDFs. This renders the self-contained carousel.html
with Playwright/Chromium:
  * print-to-PDF with prefer_css_page_size=True and print_background=True so the
    document's @page { size: 1080px 1350px } is honoured -> carousel.pdf,
  * a screenshot of each <section class="slide"> element -> slide-01.png ...,
  * captures console messages and fails on any console error,
  * verifies the PDF exists and reports the page count.

No network is strictly required (fonts load from Fontshare if online; the page
is loaded via file:// and rendering waits for networkidle).

Example
-------
    uv run --with playwright python factory/scripts/pilot_linkedin_carousel_render.py \\
        --html clients/inspra-ai/04-production/pilot-linkedin-carousel/carousel.html
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

MIN_PDF_BYTES = 10000


def pdf_page_count(pdf_path: Path) -> int:
    """Best-effort PDF page count without a PDF library.

    Counts /Type /Page objects (not /Pages) in the raw bytes; falls back to
    counting /Count entries. Good enough to assert "8 pages" for our own render.
    """
    data = pdf_path.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page(?![sR])", data))
    if pages:
        return pages
    counts = [int(m) for m in re.findall(rb"/Count\s+(\d+)", data)]
    return max(counts) if counts else 0


async def run(html_path: Path, out_dir: Path) -> Dict[str, Any]:
    from playwright.async_api import async_playwright

    pdf_path = out_dir / "carousel.pdf"
    out_dir.mkdir(parents=True, exist_ok=True)

    result: Dict[str, Any] = {
        "ok": True,
        "html": str(html_path),
        "pdf": str(pdf_path),
        "slides": [],
        "console_errors": [],
    }

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        try:
            # Match a single slide's pixel box so element screenshots are crisp.
            page = await browser.new_page(
                viewport={"width": 1080, "height": 1350}, device_scale_factor=2
            )
            logs: List[Dict[str, str]] = []
            page.on("console", lambda m: logs.append({"type": m.type, "text": m.text}))
            page.on("pageerror", lambda e: logs.append({"type": "error", "text": str(e)}))

            await page.goto(html_path.as_uri(), wait_until="networkidle")
            # Give web fonts a beat to settle before screenshots/PDF.
            try:
                await page.evaluate("document.fonts && document.fonts.ready")
            except Exception:
                pass

            # PDF: honour the document @page size; print backgrounds.
            await page.pdf(
                path=str(pdf_path),
                print_background=True,
                prefer_css_page_size=True,
            )

            # Per-slide preview PNGs at 2x (device_scale_factor handles the 2x).
            slides = page.locator("section.slide")
            count = await slides.count()
            for i in range(count):
                name = f"slide-{i + 1:02d}.png"
                await slides.nth(i).screenshot(path=str(out_dir / name))
                result["slides"].append(name)

            result["slide_element_count"] = count
            result["console_errors"] = [e for e in logs if e["type"] == "error"]
        finally:
            await browser.close()

    pages = pdf_page_count(pdf_path) if pdf_path.exists() else 0
    result["pdf_exists"] = pdf_path.exists() and pdf_path.stat().st_size > MIN_PDF_BYTES
    result["pdf_bytes"] = pdf_path.stat().st_size if pdf_path.exists() else 0
    result["pdf_pages"] = pages
    result["ok"] = (
        result["pdf_exists"]
        and pages == 8
        and result.get("slide_element_count") == 8
        and not result["console_errors"]
    )
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Render LinkedIn carousel -> PDF + slide PNGs.")
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", default=None, help="Defaults to the HTML's directory.")
    a = ap.parse_args()

    html_path = Path(a.html).expanduser().resolve()
    if not html_path.is_file():
        raise SystemExit(f"missing carousel HTML: {html_path}")
    out_dir = Path(a.out).expanduser().resolve() if a.out else html_path.parent

    result = asyncio.run(run(html_path, out_dir))
    (out_dir / "render-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print(f"\ncarousel render: {'PASS' if result['ok'] else 'CHECK'}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
