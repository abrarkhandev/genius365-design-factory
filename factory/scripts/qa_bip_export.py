#!/usr/bin/env python3
"""Client-agnostic BIP (Business Information Pack) QA + export.

This is the deterministic QA gate ("gate of record") for a client's BIP. Given
either a ``--client`` slug or an explicit ``--html`` path it will:

* render the BIP to an A4 PDF with ``print_background`` on (and
  ``prefer_css_page_size`` so the document's ``@page { size: A4 }`` is honoured),
* render a preview PNG of the first page,
* capture console messages,
* run the shared deterministic anti-slop scanner on the *rendered* DOM,
* write ``anti-slop-report.md`` (human) + ``export-results.json`` (machine), and
* exit non-zero if there is any P0 anti-slop finding or any console error.

The final PDF is written to ``clients/<slug>/06-deliverables/final-pdf/
<slug>-bip.pdf`` (the deliverable of record). Reports are written to ``--out``
(default ``clients/<slug>/05-qa``). No check from the original Inspra pilot is
weakened.

Examples
--------
Resolve everything from a client slug::

    python3 factory/scripts/qa_bip_export.py --client inspra-ai-australia

Run against an arbitrary BIP HTML (PDF lands under <out>/final-pdf/)::

    python3 factory/scripts/qa_bip_export.py \\
        --html /path/to/bip.html \\
        --source-truth /path/to/02-source-truth \\
        --out /path/to/05-qa

No network access is required; the page is loaded via a ``file://`` URI.
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

# Repository root: .../design-hermes (this file lives in factory/scripts/).
ROOT = Path(__file__).resolve().parents[2]

# A4 PDF must clear this size (bytes) to count as a real render, not a blank page.
MIN_PDF_BYTES = 10000
MIN_PNG_BYTES = 10000


# ---------------------------------------------------------------------------
# Path resolution.
# ---------------------------------------------------------------------------

def client_dir(slug: str) -> Path:
    """Absolute path to a client's working folder."""
    return ROOT / "clients" / slug


def resolve_paths(args: argparse.Namespace) -> Dict[str, Path]:
    """Resolve HTML, source-truth, output, and PDF paths from CLI arguments.

    The PDF deliverable path is derived from the slug when available
    (``06-deliverables/final-pdf/<slug>-bip.pdf``); with a bare ``--html`` it
    falls back to ``<out>/final-pdf/<stem>-bip.pdf``.
    """
    slug = args.client

    if args.html:
        html = Path(args.html).expanduser().resolve()
    else:
        if not slug:
            raise SystemExit("error: provide --client <slug> or --html <path>.")
        html = client_dir(slug) / "04-production/bip/bip.html"

    if args.source_truth:
        source_truth = Path(args.source_truth).expanduser().resolve()
    else:
        if not slug:
            raise SystemExit("error: --source-truth is required when --client is omitted.")
        source_truth = client_dir(slug) / "02-source-truth/client-facts.json"

    if args.out:
        out = Path(args.out).expanduser().resolve()
    else:
        if not slug:
            raise SystemExit("error: --out is required when --client is omitted.")
        out = client_dir(slug) / "05-qa"

    if slug:
        pdf = client_dir(slug) / "06-deliverables/final-pdf" / f"{slug}-bip.pdf"
    else:
        pdf = out / "final-pdf" / f"{html.stem}-bip.pdf"

    return {"html": html, "source_truth": source_truth, "out": out, "pdf": pdf}


def source_truth_inputs(source_truth: Path) -> List[Path]:
    """Decide what to feed the source-truth loader (mirrors the landing script)."""
    if source_truth.is_dir():
        return [source_truth]
    if source_truth.is_file():
        return [source_truth.parent]
    return [source_truth]


# ---------------------------------------------------------------------------
# Browser-side helpers.
# ---------------------------------------------------------------------------

def _attach_console(page, sink: List[Dict[str, Any]]) -> None:
    """Record every console message on ``page`` into ``sink``."""
    page.on("console", lambda msg: sink.append({"type": msg.type, "text": msg.text}))


def _probe_bip_dom_script() -> str:
    """JS that gathers generic, non-fatal BIP DOM stats (best-effort, never gates)."""
    return """() => {
      const q = (sel) => document.querySelectorAll(sel).length;
      return {
        title: document.title || null,
        page_count: q('.page'),
        section_count: q('section'),
        image_count: q('img'),
      };
    }"""


# ---------------------------------------------------------------------------
# Main render + scan flow.
# ---------------------------------------------------------------------------

async def run(paths: Dict[str, Path], label: str) -> Dict[str, Any]:
    """Render the A4 PDF + preview PNG, capture diagnostics, scan rendered DOM."""
    html_path = paths["html"]
    out = paths["out"]
    pdf_path = paths["pdf"]
    screen = out / "screenshots"
    screen.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    result: Dict[str, Any] = {
        "ok": True,
        "surface": "bip",
        "client_label": label,
        "inputs": {k: str(v) for k, v in paths.items()},
        "console": {},
        "screenshots": {},
        "pdf": str(pdf_path),
        "checks": {},
    }

    if not html_path.is_file():
        # Fail deterministically before launching the browser, so the
        # missing-surface path never requires Playwright to be installed.
        report = {
            "ok": False,
            "p0_count": 1,
            "p1_count": 0,
            "findings": [qa_antislop.missing_surface_finding("bip", html_path)],
        }
        result["ok"] = False
        result["checks"]["anti_slop"] = report
        result["checks"]["console_error_count"] = 0
        result["checks"]["console_errors"] = []
        result["checks"]["pdf_exists"] = False
        result["checks"]["preview_exists"] = False
        return result

    # Imported lazily and only once we have a real surface to render.
    from playwright.async_api import async_playwright

    source_text, source_files = qa_antislop.load_source_truth_text(
        source_truth_inputs(paths["source_truth"])
    )
    result["checks"]["source_truth_files"] = source_files

    preview_path = screen / "bip-preview.png"

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        try:
            page = await browser.new_page(viewport={"width": 1000, "height": 1400})
            logs: List[Dict[str, Any]] = []
            _attach_console(page, logs)
            await page.goto(html_path.as_uri(), wait_until="networkidle")

            # Preview PNG of the first page (above the fold).
            await page.screenshot(path=str(preview_path), full_page=False)

            # A4 PDF: print backgrounds and honour the document's @page size.
            await page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
            )

            rendered_html = await page.content()
            result["screenshots"]["bip_preview"] = str(preview_path)
            result["console"]["bip"] = logs
            result["checks"]["bip_dom"] = await page.evaluate(_probe_bip_dom_script())
            # Measure the laid-out box model for per-page overflow (gate of record).
            overflow_pages = await page_overflow.measure_pages(page)
        finally:
            await browser.close()

    # --- Deterministic anti-slop on the rendered DOM ---
    report = qa_antislop.scan_surfaces({"bip": rendered_html}, source_text)

    # --- Deterministic page-overflow on the rendered layout (gate of record) ---
    # A fixed-size .page whose content overflows its box is silently clipped;
    # the anti-slop string scan cannot see this, so fold it into the same gate.
    overflow_findings = page_overflow.findings_from_pages(overflow_pages, surface="bip")
    if overflow_findings:
        report["findings"].extend(overflow_findings)
        report["p0_count"] = report.get("p0_count", 0) + len(overflow_findings)
        report["ok"] = report["ok"] and not overflow_findings
    result["checks"]["anti_slop"] = report
    result["checks"]["page_overflow"] = page_overflow.summarise(overflow_pages)

    # --- Roll up gating diagnostics ---
    error_logs: List[Dict[str, Any]] = []
    for surface_name, surface_logs in result["console"].items():
        error_logs.extend(
            {"surface": surface_name, **entry}
            for entry in surface_logs
            if entry.get("type") == "error"
        )
    result["checks"]["console_error_count"] = len(error_logs)
    result["checks"]["console_errors"] = error_logs
    result["checks"]["pdf_exists"] = (
        pdf_path.exists() and pdf_path.stat().st_size > MIN_PDF_BYTES
    )
    result["checks"]["preview_exists"] = (
        preview_path.exists() and preview_path.stat().st_size > MIN_PNG_BYTES
    )

    result["ok"] = (
        report["ok"]
        and result["checks"]["console_error_count"] == 0
        and result["checks"]["pdf_exists"]
        and result["checks"]["preview_exists"]
    )
    return result


def write_reports(result: Dict[str, Any], out: Path, label: str) -> None:
    """Write ``anti-slop-report.md`` and ``export-results.json`` into ``out``."""
    out.mkdir(parents=True, exist_ok=True)
    report = result["checks"]["anti_slop"]
    source_files = result["checks"].get("source_truth_files", [])
    md = qa_antislop.render_markdown_report(
        report, title=f"{label} - BIP", source_truth_files=source_files
    )
    (out / "anti-slop-report.md").write_text(md)
    (out / "export-results.json").write_text(json.dumps(result, indent=2) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qa_bip_export.py",
        description="Render A4 PDF + deterministic anti-slop QA gate for a client's BIP.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Output:\n"
            "  PDF      clients/<slug>/06-deliverables/final-pdf/<slug>-bip.pdf\n"
            "  reports  <out>/anti-slop-report.md + <out>/export-results.json\n\n"
            "Exit status:\n"
            "  0  PASS  - no P0 anti-slop findings, no console errors, PDF + preview rendered.\n"
            "  1  FAIL  - one or more P0 findings or console errors (the gate of record).\n"
        ),
    )
    parser.add_argument(
        "--client",
        help="Client slug; resolves clients/<slug>/04-production/bip/bip.html.",
    )
    parser.add_argument(
        "--html",
        help="Explicit path to the BIP HTML (overrides --client for the page).",
    )
    parser.add_argument(
        "--source-truth",
        help="Source-truth file or directory (default clients/<slug>/02-source-truth/client-facts.json).",
    )
    parser.add_argument(
        "--out",
        help="Output directory for reports + preview (default clients/<slug>/05-qa).",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = resolve_paths(args)
    label = args.client or paths["html"].stem

    result = asyncio.run(run(paths, label))
    write_reports(result, paths["out"], label)

    print(json.dumps(result, indent=2))
    verdict = "PASS" if result["ok"] else "FAIL"
    print(f"\nBIP QA verdict: {verdict}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
