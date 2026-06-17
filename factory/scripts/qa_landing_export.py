#!/usr/bin/env python3
"""Client-agnostic landing-page QA + export for the Hermes Design Factory.

This is the deterministic QA gate ("gate of record") for a client's landing
page. Given either a ``--client`` slug or an explicit ``--html`` path it will:

* render a full-page desktop (1440 wide) and mobile (390 wide) screenshot,
* capture console messages on every surface,
* detect mobile horizontal overflow,
* run the shared deterministic anti-slop scanner on the *rendered* DOM,
* write ``anti-slop-report.md`` (human) + ``export-results.json`` (machine), and
* exit non-zero if there is any P0 anti-slop finding or any console error.

No check from the original Inspra pilot is weakened. P1 findings are reported
but do not fail the gate; P0 findings and console errors do.

Examples
--------
Resolve everything from a client slug::

    python3 factory/scripts/qa_landing_export.py --client inspra-ai-australia

Run against an arbitrary HTML file with explicit source truth and output dir::

    python3 factory/scripts/qa_landing_export.py \\
        --html /path/to/index.html \\
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

import qa_antislop

# Repository root: .../design-hermes (this file lives in factory/scripts/).
ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Path resolution.
# ---------------------------------------------------------------------------

def client_dir(slug: str) -> Path:
    """Absolute path to a client's working folder."""
    return ROOT / "clients" / slug


def resolve_paths(args: argparse.Namespace) -> Dict[str, Path]:
    """Resolve the HTML, source-truth, and output paths from CLI arguments.

    ``--html`` takes precedence over ``--client`` for the page location, but a
    ``--client`` is still required to derive defaults for source-truth and out
    unless those are given explicitly.
    """
    slug = args.client

    if args.html:
        html = Path(args.html).expanduser().resolve()
    else:
        if not slug:
            raise SystemExit("error: provide --client <slug> or --html <path>.")
        html = client_dir(slug) / "04-production/landing-page/index.html"

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

    return {"html": html, "source_truth": source_truth, "out": out}


def source_truth_inputs(source_truth: Path) -> List[Path]:
    """Decide what to feed the source-truth loader.

    If the path is a directory we hand the whole directory to the loader (it
    walks for .md/.txt/.json, matching the original pilot). If it is a file we
    also include its parent directory so sibling brand/spec files still count as
    source-truth backing for proof claims.
    """
    if source_truth.is_dir():
        return [source_truth]
    if source_truth.is_file():
        return [source_truth.parent]
    # Missing: still pass it through so the loader yields an empty corpus.
    return [source_truth]


# ---------------------------------------------------------------------------
# Browser-side helpers.
# ---------------------------------------------------------------------------

REVEAL_SCRIPT = """() => {
  const style = document.createElement('style');
  style.id = 'qa-force-visible';
  style.textContent = `.reveal{opacity:1!important;transform:none!important;transition:none!important} *{animation-duration:0s!important;transition-duration:0s!important;transition-delay:0s!important}`;
  document.head.appendChild(style);
  document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
}"""

OVERFLOW_SCRIPT = """() => {
  const w = document.documentElement.clientWidth;
  const offenders = [...document.querySelectorAll('body *')]
    .filter(el => el.scrollWidth > w + 2 || el.getBoundingClientRect().right > w + 2)
    .slice(0, 8)
    .map(el => ({tag: el.tagName, cls: el.className, right: el.getBoundingClientRect().right, sw: el.scrollWidth}));
  return {viewport: w, scrollWidth: document.documentElement.scrollWidth, offenders};
}"""


async def _reveal_all(page) -> None:
    """Force scroll-reveal sections visible and kill transitions for screenshots.

    The live page keeps its scroll-triggered animation; this only affects the
    deliverable capture so screenshots never catch a mid-fade frame.
    """
    await page.evaluate(REVEAL_SCRIPT)
    await page.wait_for_timeout(120)


def _attach_console(page, sink: List[Dict[str, Any]]) -> None:
    """Record every console message on ``page`` into ``sink``."""
    page.on("console", lambda msg: sink.append({"type": msg.type, "text": msg.text}))


def _probe_landing_dom_script() -> str:
    """JS that gathers generic, non-fatal landing DOM stats.

    Everything here is best-effort: a client whose markup differs simply reports
    zeros. None of these values gate the build (the original's hard asserts were
    Inspra-specific); the gate is console errors, overflow, and anti-slop.
    """
    return """() => {
      const q = (sel) => document.querySelectorAll(sel).length;
      const h1El = document.querySelector('h1');
      return {
        title: document.title || null,
        h1: h1El ? (h1El.textContent || '').trim() : null,
        h1_count: q('h1'),
        article_count: q('article'),
        section_count: q('section'),
        link_count: q('a'),
        image_count: q('img'),
      };
    }"""


# ---------------------------------------------------------------------------
# Main render + scan flow.
# ---------------------------------------------------------------------------

async def run(paths: Dict[str, Path], label: str) -> Dict[str, Any]:
    """Render screenshots, capture diagnostics, and scan the rendered DOM."""
    html_path = paths["html"]
    out = paths["out"]
    screen = out / "screenshots"
    screen.mkdir(parents=True, exist_ok=True)

    result: Dict[str, Any] = {
        "ok": True,
        "surface": "landing",
        "client_label": label,
        "inputs": {k: str(v) for k, v in paths.items()},
        "console": {},
        "screenshots": {},
        "checks": {},
    }

    if not html_path.is_file():
        # Cannot render a page that does not exist. Record a P0 and bail before
        # touching Playwright so the gate fails deterministically even on hosts
        # without a browser toolchain installed.
        report = {
            "ok": False,
            "p0_count": 1,
            "p1_count": 0,
            "findings": [qa_antislop.missing_surface_finding("landing", html_path)],
        }
        result["ok"] = False
        result["checks"]["anti_slop"] = report
        result["checks"]["console_error_count"] = 0
        result["checks"]["console_errors"] = []
        result["checks"]["screenshots_exist"] = False
        return result

    # Imported lazily and only once we have a real surface to render, so the
    # missing-surface path above never requires Playwright to be installed.
    from playwright.async_api import async_playwright

    source_text, source_files = qa_antislop.load_source_truth_text(
        source_truth_inputs(paths["source_truth"])
    )
    result["checks"]["source_truth_files"] = source_files

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        try:
            # --- Desktop (1440 wide) ---
            desktop = await browser.new_page(
                viewport={"width": 1440, "height": 1200}, device_scale_factor=1
            )
            desktop_logs: List[Dict[str, Any]] = []
            _attach_console(desktop, desktop_logs)
            await desktop.goto(html_path.as_uri(), wait_until="networkidle")
            await _reveal_all(desktop)
            await desktop.screenshot(
                path=str(screen / "landing-desktop.png"), full_page=True
            )
            # Scan the RENDERED DOM (resolved templating + inline <style>).
            rendered_html = await desktop.content()
            result["screenshots"]["landing_desktop"] = str(screen / "landing-desktop.png")
            result["console"]["landing_desktop"] = desktop_logs
            result["checks"]["landing_dom"] = await desktop.evaluate(
                _probe_landing_dom_script()
            )

            # --- Mobile (390 wide) ---
            mobile = await browser.new_page(
                viewport={"width": 390, "height": 900}, is_mobile=True
            )
            mobile_logs: List[Dict[str, Any]] = []
            _attach_console(mobile, mobile_logs)
            await mobile.goto(html_path.as_uri(), wait_until="networkidle")
            await _reveal_all(mobile)
            await mobile.screenshot(
                path=str(screen / "landing-mobile.png"), full_page=True
            )
            result["screenshots"]["landing_mobile"] = str(screen / "landing-mobile.png")
            result["console"]["landing_mobile"] = mobile_logs
            result["checks"]["mobile_overflow"] = await mobile.evaluate(OVERFLOW_SCRIPT)
        finally:
            await browser.close()

    # --- Deterministic anti-slop on the rendered DOM ---
    report = qa_antislop.scan_surfaces({"landing": rendered_html}, source_text)
    result["checks"]["anti_slop"] = report

    # --- Roll up gating diagnostics ---
    error_logs: List[Dict[str, Any]] = []
    for surface_name, logs in result["console"].items():
        error_logs.extend(
            {"surface": surface_name, **entry}
            for entry in logs
            if entry.get("type") == "error"
        )
    result["checks"]["console_error_count"] = len(error_logs)
    result["checks"]["console_errors"] = error_logs
    result["checks"]["screenshots_exist"] = all(
        Path(p).exists() and Path(p).stat().st_size > 10000
        for p in result["screenshots"].values()
    )

    overflow = result["checks"].get("mobile_overflow", {})
    overflow_ok = overflow.get("scrollWidth", 0) <= overflow.get("viewport", 0) + 2
    result["checks"]["mobile_overflow_ok"] = overflow_ok

    result["ok"] = (
        report["ok"]
        and result["checks"]["console_error_count"] == 0
        and result["checks"]["screenshots_exist"]
        and overflow_ok
    )
    return result


def write_reports(result: Dict[str, Any], out: Path, label: str) -> None:
    """Write ``anti-slop-report.md`` and ``export-results.json`` into ``out``."""
    out.mkdir(parents=True, exist_ok=True)
    report = result["checks"]["anti_slop"]
    source_files = result["checks"].get("source_truth_files", [])
    md = qa_antislop.render_markdown_report(
        report, title=f"{label} - Landing", source_truth_files=source_files
    )
    (out / "anti-slop-report.md").write_text(md)
    (out / "export-results.json").write_text(json.dumps(result, indent=2) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qa_landing_export.py",
        description="Render + deterministic anti-slop QA gate for a client's landing page.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exit status:\n"
            "  0  PASS  - no P0 anti-slop findings, no console errors, no mobile overflow.\n"
            "  1  FAIL  - one or more P0 findings or console errors (the gate of record).\n"
        ),
    )
    parser.add_argument(
        "--client",
        help="Client slug; resolves clients/<slug>/04-production/landing-page/index.html.",
    )
    parser.add_argument(
        "--html",
        help="Explicit path to the landing HTML (overrides --client for the page).",
    )
    parser.add_argument(
        "--source-truth",
        help="Source-truth file or directory (default clients/<slug>/02-source-truth/client-facts.json).",
    )
    parser.add_argument(
        "--out",
        help="Output directory for reports + screenshots (default clients/<slug>/05-qa).",
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
    print(f"\nLanding QA verdict: {verdict}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
