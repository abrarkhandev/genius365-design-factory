#!/usr/bin/env python3
"""Run the deterministic anti-slop gate against a rendered banner.

Renders the banner HTML to DOM via Playwright (so any client-side state resolves),
scans it with the shared qa_antislop scanner against the client's source-truth,
writes anti-slop-report.md + export-results.json to the QA dir, and exits non-zero
on any P0 finding. Mirrors how qa_landing_export.py uses the scanner.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_antislop as qa
from playwright.sync_api import sync_playwright

html_path = Path(sys.argv[1]).resolve()
source_truth_dir = Path(sys.argv[2]).resolve()
out_dir = Path(sys.argv[3]).resolve()
surface = sys.argv[4] if len(sys.argv) > 4 else "banner"
out_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1584, "height": 396}, device_scale_factor=2)
    console_errors = []
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.goto(html_path.as_uri())
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(800)
    dom = page.content()
    browser.close()

source_text, source_files = qa.load_source_truth_text(source_truth_dir)
report = qa.scan_surfaces({surface: dom}, source_text)
report["console_errors"] = console_errors

md = qa.render_markdown_report(
    report, title=f"LinkedIn Banner ({surface})", source_truth_files=source_files
)
(out_dir / "anti-slop-report.md").write_text(md, encoding="utf-8")
(out_dir / "export-results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps({
    "surface": surface,
    "ok": report["ok"],
    "p0_count": report["p0_count"],
    "p1_count": report["p1_count"],
    "console_errors": len(console_errors),
    "report": str(out_dir / "anti-slop-report.md"),
}, indent=2))
sys.exit(0 if report["ok"] and not console_errors else 1)
