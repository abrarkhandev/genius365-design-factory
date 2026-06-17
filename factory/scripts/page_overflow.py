#!/usr/bin/env python3
"""Deterministic per-page overflow check for fixed-size print pages.

A magazine .page is a fixed A4 box; content that exceeds it is clipped by
overflow:hidden and silently lost (a clipped last process step, a colliding
folio). The anti-slop scanner cannot see this because it works on the HTML
string, not the laid-out box model. This module measures the RENDERED layout in
Chromium and flags any page where:

  * the page's own content overflows its box (scrollHeight > clientHeight + TOL,
    or scrollWidth > clientWidth + TOL), or
  * any descendant element's bounding rect extends beyond the page box on any
    edge by more than TOL pixels.

It returns structured findings shaped like qa_antislop findings so they roll
into the same report and the same gate of record.
"""
from __future__ import annotations

from typing import Any, Dict, List

# Sub-pixel rounding from layout/zoom is expected; only flag real overflow.
TOLERANCE_PX = 2.0

#: JS run in the page context. Returns one record per .page with its own
#: overflow plus the worst offending descendant on each edge.
PROBE_JS = """(tol) => {
  const pages = Array.from(document.querySelectorAll('.page'));
  return pages.map((page, i) => {
    const pr = page.getBoundingClientRect();
    const self_overflow_y = page.scrollHeight - page.clientHeight;
    const self_overflow_x = page.scrollWidth - page.clientWidth;
    let worst = { bottom: 0, right: 0, top: 0, left: 0 };
    let worst_el = { bottom: null, right: null };
    const all = page.querySelectorAll('*');
    for (const el of all) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      const overBottom = r.bottom - pr.bottom;
      const overRight = r.right - pr.right;
      const overTop = pr.top - r.top;
      const overLeft = pr.left - r.left;
      if (overBottom > worst.bottom) { worst.bottom = overBottom; worst_el.bottom = (el.className || el.tagName) + ' :: ' + (el.textContent || '').trim().slice(0, 60); }
      if (overRight > worst.right) { worst.right = overRight; worst_el.right = (el.className || el.tagName) + ' :: ' + (el.textContent || '').trim().slice(0, 60); }
      if (overTop > worst.top) worst.top = overTop;
      if (overLeft > worst.left) worst.left = overLeft;
    }
    return {
      index: i + 1,
      page_w: Math.round(pr.width), page_h: Math.round(pr.height),
      self_overflow_x: Math.round(self_overflow_x * 100) / 100,
      self_overflow_y: Math.round(self_overflow_y * 100) / 100,
      worst_bottom: Math.round(worst.bottom * 100) / 100,
      worst_right: Math.round(worst.right * 100) / 100,
      worst_top: Math.round(worst.top * 100) / 100,
      worst_left: Math.round(worst.left * 100) / 100,
      worst_bottom_el: worst_el.bottom,
      worst_right_el: worst_el.right,
    };
  });
}"""


async def measure_pages(page, tol: float = TOLERANCE_PX) -> List[Dict[str, Any]]:
    """Run the overflow probe against an already-loaded Playwright page."""
    return await page.evaluate(PROBE_JS, tol)


def findings_from_pages(
    pages: List[Dict[str, Any]], *, surface: str = "magazine", tol: float = TOLERANCE_PX
) -> List[Dict[str, Any]]:
    """Turn raw per-page measurements into P0 findings (qa_antislop shape)."""
    findings: List[Dict[str, Any]] = []
    for p in pages:
        breaches: List[str] = []
        if p["self_overflow_y"] > tol:
            breaches.append(f"content overflows page bottom by {p['self_overflow_y']}px (scrollHeight>clientHeight)")
        if p["self_overflow_x"] > tol:
            breaches.append(f"content overflows page right by {p['self_overflow_x']}px (scrollWidth>clientWidth)")
        if p["worst_bottom"] > tol:
            breaches.append(f"element extends {p['worst_bottom']}px below page box [{p.get('worst_bottom_el')}]")
        if p["worst_right"] > tol:
            breaches.append(f"element extends {p['worst_right']}px past page right [{p.get('worst_right_el')}]")
        if p["worst_top"] > tol:
            breaches.append(f"element extends {p['worst_top']}px above page top")
        if p["worst_left"] > tol:
            breaches.append(f"element extends {p['worst_left']}px past page left")
        if breaches:
            findings.append({
                "severity": "P0",
                "check": "page_overflow",
                "surface": surface,
                "line": None,
                "evidence": f"page {p['index']} ({p['page_w']}x{p['page_h']}): " + "; ".join(breaches),
                "fix": "Resize or move the offending module so the page does not overflow; keep at least 18mm clear at the bottom.",
            })
    return findings


def summarise(pages: List[Dict[str, Any]], tol: float = TOLERANCE_PX) -> Dict[str, Any]:
    """Compact per-page pass/fail summary for the report and machine output."""
    rows = []
    ok = True
    for p in pages:
        page_ok = (
            p["self_overflow_y"] <= tol and p["self_overflow_x"] <= tol
            and p["worst_bottom"] <= tol and p["worst_right"] <= tol
            and p["worst_top"] <= tol and p["worst_left"] <= tol
        )
        ok = ok and page_ok
        rows.append({
            "page": p["index"], "ok": page_ok,
            "overflow_y": p["self_overflow_y"], "worst_bottom": p["worst_bottom"],
            "worst_right": p["worst_right"],
        })
    return {"ok": ok, "tolerance_px": tol, "pages": rows}
