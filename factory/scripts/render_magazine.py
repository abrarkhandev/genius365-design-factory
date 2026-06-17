#!/usr/bin/env python3
"""Render a magazine HTML to an A4 PDF and per-page PNG previews.

Mirrors the BIP export render path: Playwright/Chromium print-to-PDF with
prefer_css_page_size=True and print_background=True, plus one screenshot per
<section class="page"> for preview. Captures console messages and verifies the
PDF exists with the expected page count.

Usage:
    uv run --with playwright python render_magazine.py \\
        --html <magazine.html> --out <dir> [--pages 4]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import page_overflow

MIN_PDF_BYTES = 10000


async def render(html_path: Path, out_dir: Path, expected_pages: int) -> Dict[str, Any]:
    from playwright.async_api import async_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / "magazine.pdf"
    logs: List[Dict[str, Any]] = []
    result: Dict[str, Any] = {"html": str(html_path), "pdf": str(pdf_path), "pages": []}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        try:
            # A4 at 96dpi ~ 794x1123 px; viewport sized so screenshots clip cleanly.
            page = await browser.new_page(viewport={"width": 794, "height": 1123})
            page.on("console", lambda m: logs.append({"type": m.type, "text": m.text}))
            await page.goto(html_path.as_uri(), wait_until="networkidle")

            section_count = await page.evaluate("() => document.querySelectorAll('.page').length")
            result["section_count"] = section_count

            await page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
            )

            # One PNG per .page section.
            handles = await page.query_selector_all(".page")
            for i, handle in enumerate(handles, 1):
                png = out_dir / f"page-{i:02d}.png"
                await handle.screenshot(path=str(png))
                result["pages"].append(str(png))

            # Deterministic per-page overflow measurement (advisory here; the
            # gate of record is qa_magazine.py, which uses the same probe).
            measurements = await page_overflow.measure_pages(page)
        finally:
            await browser.close()

    result["console"] = logs
    result["console_error_count"] = sum(1 for m in logs if m.get("type") == "error")
    result["page_overflow"] = page_overflow.summarise(measurements)
    result["pdf_exists"] = pdf_path.exists() and pdf_path.stat().st_size > MIN_PDF_BYTES
    result["pdf_bytes"] = pdf_path.stat().st_size if pdf_path.exists() else 0
    result["expected_pages"] = expected_pages
    result["page_count_ok"] = result.get("section_count") == expected_pages
    result["ok"] = (
        result["pdf_exists"]
        and result["console_error_count"] == 0
        and result["page_count_ok"]
        and len(result["pages"]) == expected_pages
        and result["page_overflow"]["ok"]
    )
    return result


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render magazine HTML to A4 PDF + page PNGs.")
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pages", type=int, default=4)
    a = ap.parse_args(argv)

    html_path = Path(a.html).expanduser().resolve()
    if not html_path.is_file():
        raise SystemExit(f"error: HTML not found: {html_path}")
    out_dir = Path(a.out).expanduser().resolve()

    result = asyncio.run(render(html_path, out_dir, a.pages))
    (out_dir / "render-meta.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "console"}, indent=2))
    print(f"\nRender verdict: {'PASS' if result['ok'] else 'CHECK'}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
