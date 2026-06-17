#!/usr/bin/env python3
"""Deterministic QA gate for a magazine editorial feature.

Renders the magazine HTML in Chromium (so any computed CSS is resolved), then
runs TWO deterministic checks against the RENDERED layout and rolls both into a
single gate of record:

  1. the shared qa_antislop scanner (the 7 sins + unverified proof), and
  2. a per-page OVERFLOW check (page_overflow): no .page may overflow its fixed
     box and no descendant may extend beyond it.

Writes anti-slop-report.md + qa-results.json and exits non-zero on any P0
finding (anti-slop OR overflow) or any console error.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import page_overflow
import qa_antislop


async def scan(html_path: Path, source_truth: Path) -> Dict[str, Any]:
    from playwright.async_api import async_playwright

    source_text, source_files = qa_antislop.load_source_truth_text([source_truth])
    logs: List[Dict[str, Any]] = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        try:
            page = await browser.new_page(viewport={"width": 794, "height": 1123})
            page.on("console", lambda m: logs.append({"type": m.type, "text": m.text}))
            await page.goto(html_path.as_uri(), wait_until="networkidle")
            rendered = await page.content()
            page_measurements = await page_overflow.measure_pages(page)
        finally:
            await browser.close()

    report = qa_antislop.scan_surfaces({"magazine": rendered}, source_text)
    # Fold the deterministic overflow findings into the same report/gate.
    overflow_findings = page_overflow.findings_from_pages(page_measurements, surface="magazine")
    overflow_summary = page_overflow.summarise(page_measurements)
    report["findings"].extend(overflow_findings)
    report["p0_count"] += sum(1 for f in overflow_findings if f["severity"] == "P0")
    report["ok"] = report["p0_count"] == 0

    error_logs = [m for m in logs if m.get("type") == "error"]
    return {
        "html": str(html_path),
        "source_truth_files": source_files,
        "anti_slop": report,
        "page_overflow": overflow_summary,
        "console_error_count": len(error_logs),
        "console_errors": error_logs,
        "ok": report["ok"] and len(error_logs) == 0,
    }


def _overflow_section(summary: Dict[str, Any]) -> str:
    """Render the per-page overflow table appended to the report."""
    lines = [
        "",
        "## Per-page overflow check",
        "",
        f"Verdict: **{'PASS' if summary['ok'] else 'REWORK'}** (tolerance {summary['tolerance_px']}px)",
        "",
        "| Page | Result | Overflow Y (px) | Worst below box (px) | Worst past right (px) |",
        "|---:|---|---:|---:|---:|",
    ]
    for row in summary["pages"]:
        lines.append(
            f"| {row['page']} | {'PASS' if row['ok'] else 'OVERFLOW'} | "
            f"{row['overflow_y']} | {row['worst_bottom']} | {row['worst_right']} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Anti-slop + overflow QA gate for a magazine HTML.")
    ap.add_argument("--html", required=True)
    ap.add_argument("--source-truth", required=True, help="Source-truth file or directory.")
    ap.add_argument("--out", required=True, help="Output dir for report + json.")
    ap.add_argument("--label", default="Magazine")
    a = ap.parse_args(argv)

    html_path = Path(a.html).expanduser().resolve()
    source_truth = Path(a.source_truth).expanduser().resolve()
    out = Path(a.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not html_path.is_file():
        raise SystemExit(f"error: HTML not found: {html_path}")

    result = asyncio.run(scan(html_path, source_truth))
    md = qa_antislop.render_markdown_report(
        result["anti_slop"], title=f"{a.label} - Magazine",
        source_truth_files=result["source_truth_files"],
    )
    md += _overflow_section(result["page_overflow"])
    (out / "anti-slop-report.md").write_text(md)
    (out / "qa-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "console_errors"}, indent=2))
    print(f"\nMagazine QA verdict: {'PASS' if result['ok'] else 'FAIL'}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
