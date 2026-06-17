#!/usr/bin/env python3
"""Render a LinkedIn banner HTML to PNG via Playwright (viewport 1584x396, 2x)."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

html_path = Path(sys.argv[1]).resolve()
out_path = Path(sys.argv[2]).resolve()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1584, "height": 396}, device_scale_factor=2)
    page.goto(html_path.as_uri())
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.evaluate("document.fonts && document.fonts.ready")
    page.wait_for_timeout(1200)
    page.screenshot(path=str(out_path))
    browser.close()
print(f"rendered {out_path}")
