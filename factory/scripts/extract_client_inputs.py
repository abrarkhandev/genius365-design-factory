#!/usr/bin/env python3
"""Extract client inputs into the design factory source-truth folder shape.

This is a deterministic first-pass extractor. It does not call an LLM and does
not invent claims. BIP and landing profiles use the output as source material.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {".txt", ".md", ".csv", ".json", ".rtf"}
DOC_SUFFIXES = {".docx", ".pdf", ".txt", ".md", ".rtf"}
ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".pdf", ".ai", ".eps", ".mp4", ".mov", ".pptx", ".fig", ".sketch"}

class TextHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip = True
        if tag in {"h1", "h2", "h3", "p", "li", "section", "article", "br"}:
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}:
            self.skip = False
        if tag in {"h1", "h2", "h3", "p", "li"}:
            self.parts.append("\n")
    def handle_data(self, data):
        if not self.skip:
            s = re.sub(r"\s+", " ", data).strip()
            if s:
                self.parts.append(s + " ")
    def text(self):
        return re.sub(r"\n{3,}", "\n\n", "".join(self.parts)).strip()

def safe_slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "client"

def read_docx(path: Path) -> str:
    try:
        with ZipFile(path) as z:
            xml = z.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        texts = [node.text for node in root.findall(".//w:t", ns) if node.text]
        return " ".join(texts)
    except Exception as e:
        return f"[DOCX extraction failed for {path.name}: {e}]"

def read_pdf(path: Path) -> str:
    try:
        out = subprocess.check_output(["pdftotext", "-layout", str(path), "-"], text=True, stderr=subprocess.DEVNULL, timeout=60)
        return out.strip()
    except Exception as e:
        return f"[PDF extraction failed for {path.name}: {e}]"

def read_text_file(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return read_docx(path)
    if path.suffix.lower() == ".pdf":
        return read_pdf(path)
    try:
        return path.read_text(errors="ignore")
    except Exception as e:
        return f"[Text extraction failed for {path.name}: {e}]"

def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "HermesDesignFactory/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode(errors="ignore")
    parser = TextHTMLParser()
    parser.feed(raw)
    return parser.text()

def inventory_assets(input_dir: Path) -> list[dict]:
    rows = []
    if not input_dir.exists():
        return rows
    for p in sorted(input_dir.rglob("*")):
        if p.is_file():
            try:
                rel = p.relative_to(input_dir).as_posix()
                rows.append({"path": rel, "suffix": p.suffix.lower(), "bytes": p.stat().st_size})
            except Exception:
                pass
    return rows

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True, help="Client/project name")
    ap.add_argument("--input", help="Path to assets/docs folder")
    ap.add_argument("--url", help="Existing website URL")
    ap.add_argument("--out-root", default="clients")
    args = ap.parse_args()

    slug = safe_slug(args.client)
    client_root = ROOT / args.out_root / slug
    dirs = {
        "input": client_root / "00-input",
        "extracted": client_root / "01-extracted",
        "truth": client_root / "02-source-truth",
        "strategy": client_root / "03-strategy",
        "prod_bip": client_root / "04-production/bip",
        "prod_landing": client_root / "04-production/landing-page",
        "qa": client_root / "05-qa",
        "deliver_pdf": client_root / "06-deliverables/final-pdf",
        "deliver_web": client_root / "06-deliverables/final-web",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    input_sources = []
    extracted_chunks = []
    asset_rows = []

    if args.input:
        in_path = Path(args.input).expanduser().resolve()
        input_sources.append(str(in_path))
        asset_rows = inventory_assets(in_path)
        inv_md = "# Asset Inventory\n\n" + "\n".join(f"- `{r['path']}` — {r['suffix'] or 'no-ext'}, {r['bytes']} bytes" for r in asset_rows)
        (dirs["extracted"] / "asset-inventory.md").write_text(inv_md + "\n")
        for p in sorted(in_path.rglob("*")):
            if p.is_file() and p.suffix.lower() in DOC_SUFFIXES:
                text = read_text_file(p)
                if text:
                    extracted_chunks.append(f"\n\n## {p.name}\n\n{text[:20000]}")
        (dirs["extracted"] / "docs-extracted.md").write_text("# Extracted Documents\n" + "\n".join(extracted_chunks) + "\n")

    website_text = ""
    if args.url:
        input_sources.append(args.url)
        try:
            website_text = fetch_url(args.url)
        except Exception as e:
            website_text = f"[Website extraction failed: {e}]"
        (dirs["extracted"] / "website.md").write_text(f"# Website Extract\n\nURL: {args.url}\n\n{website_text}\n")

    mode = "mixed" if args.input and args.url else "assets_docs" if args.input else "website_url" if args.url else "unknown"
    facts = {
        "client_name": args.client,
        "source_mode": mode,
        "input_sources": input_sources,
        "business_summary": "",
        "one_line_positioning": "",
        "audiences": [],
        "problems_solved": [],
        "services": [],
        "products": [],
        "process": [],
        "differentiators": [],
        "proof_points": [],
        "case_studies": [],
        "testimonials": [],
        "founder_team": [],
        "brand": {"tone": "", "colors": [], "fonts": [], "visual_style": "", "asset_notes": f"{len(asset_rows)} files inventoried."},
        "cta": {"primary": "", "secondary": "", "contact": {}},
        "unknowns": [
            "LLM/source-truth refinement required: deterministic extractor does not infer unstated business claims.",
            "Proof, testimonials, metrics, and client names must be verified from supplied materials before use."
        ]
    }
    (dirs["truth"] / "client-facts.json").write_text(json.dumps(facts, indent=2) + "\n")
    (dirs["truth"] / "client-facts.md").write_text(
        f"# Client Facts — {args.client}\n\n"
        f"Source mode: `{mode}`\n\n"
        f"Input sources:\n" + "\n".join(f"- {s}" for s in input_sources) + "\n\n"
        "This is a deterministic first pass. Have business-pack-studio or landing-page-studio refine it with Kimi K2.6 before production.\n"
    )
    (dirs["truth"] / "assumptions.md").write_text("# Assumptions / Unknowns\n\n- No proof or metrics may be used unless present in supplied material.\n- Refine this file during profile strategy.\n")
    (dirs["truth"] / "brand-kit.md").write_text(f"# Brand Kit — {args.client}\n\n- Asset files inventoried: {len(asset_rows)}\n- Website URL: {args.url or 'not supplied'}\n")
    (dirs["truth"] / "DESIGN.md").write_text(
        f"# DESIGN.md — {args.client}\n\n"
        "This is a first-pass design control file created by the deterministic intake extractor. "
        "Refine it with `factory/scripts/design_model_router.py --role design-md` before production.\n\n"
        "## 1. Brand essence\n[fill from source truth]\n\n"
        "## 2. Audience and conversion goal\n- Primary audience: [fill]\n- Primary action: [fill]\n- Main objection: [fill]\n\n"
        "## 3. Colour tokens\n- --accent: [fill; never default indigo unless brand-owned]\n- --bg: [fill]\n- --fg: [fill]\n- --muted: [fill]\n\n"
        "## 4. Typography\n- Display font: [fill]\n- Body font: [fill]\n\n"
        "## 5. Voice and copy\n- Australian English.\n- No contractions.\n- No filler copy.\n- No invented proof, metrics, testimonials, logos, certifications, or case studies.\n\n"
        "## 6. Iconography\n- Library: Lucide / Phosphor / Heroicons / custom\n- Stroke: 1.6–1.8px, currentColor unless brand requires otherwise\n- No emoji feature icons.\n\n"
        "## 7. Imagery and graphics\n- Prototype on free/internal models.\n- Deliver on commercially licensed sources only after approval.\n\n"
        "## 8. Motion\n- Motion must support comprehension or conversion.\n- Respect prefers-reduced-motion.\n\n"
        "## 9. The distinctive 20% move\n[fill]\n\n"
        "## 10. Do-not-cross list\n- No unverified claims.\n"
    )
    (dirs["truth"] / "system-spec.md").write_text(
        f"# System Spec — {args.client}\n\n"
        f"Source mode: `{mode}`\n\n"
        "This file is required for reference/clone-inspired work. It should be refined by "
        "`factory/scripts/design_model_router.py --role reference-system-spec` after reference screenshots or website extracts are available.\n\n"
        "## Reference summary\n[fill]\n\n"
        "## Type scale\n[fill]\n\n"
        "## Spacing scale\n[fill]\n\n"
        "## Grid and layout\n[fill]\n\n"
        "## Component patterns\n[fill]\n\n"
        "## Borrow list\n[abstract reusable patterns only]\n\n"
        "## Avoid list\n[anything too identifiable or risky to copy]\n"
    )

    print(json.dumps({"ok": True, "client_root": str(client_root), "source_mode": mode, "assets": len(asset_rows), "sources": input_sources, "created": ["client-facts.json", "client-facts.md", "assumptions.md", "brand-kit.md", "DESIGN.md", "system-spec.md"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
