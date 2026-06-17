"""
Normalize nav and footer across a static multi-page site.

Use after delegating child pages to subagents. Each subagent tends to invent slightly
different nav link targets or active-state markup, so this script injects a canonical
header/footer block and remaps the active page indicator.

Usage:
  python3 multi-page-normalize-script.py \
      --base /Users/mc/Desktop/aa-test/website \
      --canonical services.html \
      --pages index.html services.html ai.html data.html case-studies.html about.html contact.html

Expectations:
- The canonical page must contain a <header class="navbar"> and a <footer class="footer">.
- The canonical header nav links should point to real HTML files, not # placeholders.
- Active-state patterns supported: aria-current="page", inline style color override,
  or an `active` class. The script strips whichever was used and applies aria-current
  to the page currently being processed.
"""
import argparse
import re
from pathlib import Path


def extract_canonical(base: Path, canonical: str):
    txt = (base / canonical).read_text()
    nav = re.search(r'<header class="navbar">.*?</header>', txt, re.S)
    footer = re.search(r'<footer class="footer">.*?</footer>", txt, re.S)
    if not nav or not footer:
        raise ValueError("Canonical page must contain a navbar header and a footer.")
    return nav.group(0), footer.group(0)


def make_active(nav: str, page_name: str):
    # Reset existing active markers
    nav = re.sub(r' aria-current="page"', '', nav)
    nav = re.sub(r' style="color:\s*var\(--aa-purple\);"', '', nav)
    nav = re.sub(r' class="([^"]*)active([^"]*)"', lambda m: f' class="{m.group(1)}{m.group(2)}"'.strip(), nav)

    # Set aria-current on the matching link
    page_map = {
        'index.html': 'href="index.html">Home',
        'services.html': 'href="services.html">Services',
        'ai.html': 'href="ai.html">AI',
        'data.html': 'href="data.html">Data',
        'case-studies.html': 'href="case-studies.html">Case Studies',
        'about.html': 'href="about.html">About Us',
    }
    key = page_map.get(page_name)
    if key and key in nav:
        nav = nav.replace(key, key.replace('>', ' aria-current="page">'))
    return nav


def fix_booking_ctas(txt: str, contact: str = 'contact.html#book'):
    # Remap any leftover placeholder CTAs to the canonical booking destination
    txt = txt.replace('href="#book" class="btn btn-primary">Book a Demo</a>', f'href="{contact}" class="btn btn-primary">Book a Demo</a>')
    txt = txt.replace('href="#book" class="btn btn-primary">Book a discovery call</a>', f'href="{contact}" class="btn btn-primary">Book a discovery call</a>')
    txt = txt.replace('href="#" class="nav__agent"><span>☎</span> Test the Agent</a>', f'href="{contact}" class="nav__agent"><span>☎</span> Test the Agent</a>')
    return txt


def normalize_page(base: Path, page: str, canonical_nav: str, canonical_footer: str):
    path = base / page
    if not path.exists():
        print(f"SKIPPED {page}: file not found")
        return
    txt = path.read_text()
    txt = re.sub(r'<header class="navbar">.*?</header>', make_active(canonical_nav, page), txt, flags=re.S)
    txt = re.sub(r'<footer class="footer">.*?</footer>', canonical_footer, txt, flags=re.S)
    txt = fix_booking_ctas(txt)
    path.write_text(txt)
    print(f"NORMALIZED {page}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--canonical', default='services.html')
    parser.add_argument('--pages', nargs='+', required=True)
    args = parser.parse_args()

    nav, footer = extract_canonical(args.base, args.canonical)
    for page in args.pages:
        normalize_page(args.base, page, nav, footer)


if __name__ == '__main__':
    main()
