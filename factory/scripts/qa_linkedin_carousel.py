#!/usr/bin/env python3
"""Deterministic anti-slop QA gate for a LinkedIn carousel (gate of record).

Renders the carousel HTML in Chromium, runs the shared qa_antislop scanner on
the *rendered* DOM against the client's full source-truth directory, captures
console errors, and writes anti-slop-report.md + qa-results.json. Exits non-zero
on any P0 finding or console error.

Example
-------
    uv run --with playwright python factory/scripts/qa_linkedin_carousel.py \\
        --html clients/inspra-ai/04-production/pilot-linkedin-carousel/carousel.html \\
        --source-truth clients/inspra-ai/02-source-truth \\
        --out clients/inspra-ai/05-qa/pilot-linkedin-carousel \\
        --label "Inspra AI"
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import qa_antislop


async def render_dom(html_path: Path) -> tuple[str, List[Dict[str, str]]]:
    from playwright.async_api import async_playwright

    logs: List[Dict[str, str]] = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        try:
            page = await browser.new_page(viewport={"width": 1080, "height": 1350})
            page.on("console", lambda m: logs.append({"type": m.type, "text": m.text}))
            page.on("pageerror", lambda e: logs.append({"type": "error", "text": str(e)}))
            await page.goto(html_path.as_uri(), wait_until="networkidle")
            dom = await page.content()
        finally:
            await browser.close()
    return dom, logs


def main() -> int:
    ap = argparse.ArgumentParser(description="Anti-slop QA gate for a LinkedIn carousel.")
    ap.add_argument("--html", required=True)
    ap.add_argument("--source-truth", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default=None)
    a = ap.parse_args()

    html_path = Path(a.html).expanduser().resolve()
    source_truth = Path(a.source_truth).expanduser().resolve()
    out = Path(a.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    label = a.label or html_path.parent.parent.parent.name

    if not html_path.is_file():
        raise SystemExit(f"missing carousel HTML: {html_path}")

    source_text, source_files = qa_antislop.load_source_truth_text([source_truth])
    dom, logs = asyncio.run(render_dom(html_path))
    report = qa_antislop.scan_surfaces({"carousel": dom}, source_text)
    console_errors = [e for e in logs if e["type"] == "error"]

    result: Dict[str, Any] = {
        "ok": report["ok"] and not console_errors,
        "label": label,
        "html": str(html_path),
        "source_truth_files": source_files,
        "anti_slop": report,
        "console_error_count": len(console_errors),
        "console_errors": console_errors,
    }

    md = qa_antislop.render_markdown_report(
        report, title=f"{label} - LinkedIn carousel", source_truth_files=source_files
    )
    (out / "anti-slop-report.md").write_text(md)
    (out / "qa-results.json").write_text(json.dumps(result, indent=2) + "\n")

    print(json.dumps(result, indent=2))
    verdict = "PASS" if result["ok"] else "REWORK"
    print(
        f"\ncarousel QA verdict: {verdict} "
        f"(P0={report['p0_count']} P1={report['p1_count']} "
        f"console_errors={len(console_errors)})",
        file=sys.stderr,
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
