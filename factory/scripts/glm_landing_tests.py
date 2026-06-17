#!/usr/bin/env python3
"""Model range test: build distinct landing pages with the landing-page-studio
SOUL on GLM-5.2 (z-ai/glm-5.2). Animation is allowed (GSAP via CDN); component
libraries (Aceternity / MagicUI / shadcn) are referenced as patterns to recreate
in vanilla HTML/CSS, not imported.

Each brief writes its own source-truth facts file (for the QA fact-trace) and one
self-contained HTML document. Never prints the key.

  uv run --no-project python factory/scripts/glm_landing_tests.py --brief sable
  uv run --no-project python factory/scripts/glm_landing_tests.py --brief lumora
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERMES = Path.home() / ".hermes"
PROFILE = HERMES / "profiles" / "landing-page-studio"
API_BASE = "https://openrouter.ai/api/v1"

OUTPUT_CONTRACT = """OUTPUT CONTRACT (animated landing page):
- Output ONE complete, self-contained HTML document only: inline <style> and vanilla <script>. No markdown, no commentary.
- You MAY load GSAP and ScrollTrigger from a CDN (https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js and the matching ScrollTrigger.min.js) for animation. No other external dependencies.
- NO external images: every visual is CSS or inline SVG. All real text stays HTML/SVG, never baked into a picture.
- Component libraries (Aceternity UI, MagicUI, shadcn) are REFERENCE ONLY: recreate their signature effects (aurora/gradient-mesh background, spotlight, bento grid, marquee, number ticker, animated gradient text, tilt/glare cards, accordion) in vanilla HTML/CSS/GSAP. Do not import React or Tailwind.
- Animations MUST be safe for static capture: respect prefers-reduced-motion (render ALL final content, no motion); AND if navigator.webdriver is true, reveal all content immediately. Never leave content invisible waiting on a scroll trigger without these fallbacks.
- Fully responsive: hold up at 1440px, 768px and 375px with no horizontal overflow.
- Land ONE ownable distinctive move. WCAG 2.2 AA contrast. Australian English, no contractions, no em-dashes or en-dashes in body copy.
- Use ONLY the facts supplied. Invent no metrics, logos, customers or quotes.
- Return ONLY the complete HTML document, beginning with <!DOCTYPE html>."""

BRIEFS = {
    "sable": {
        "facts": """# Sable - Source Truth (FICTIONAL sample brand, model test)
All facts below are the only proof permitted on the page. Invent nothing else.
- Sable - a wealth app that gives everyday investors one clear, calm view of all their money.
- Promise: "See all your money clearly. Decide with confidence."
- Connects 80+ banks, super funds and brokers into one view of your net worth.
- Tracks over $1.2 billion in assets for members.
- Bank-level encryption; read-only access, so Sable can never move your money.
- No ads, and your data is never sold.
- Pricing: Free, and Plus at $9 per month.
- Audience: everyday people whose savings, super, shares and crypto are scattered across apps.
""",
        "brief": """Build the Sable landing page (one long page).

COMPANY: Sable - a wealth app that gives everyday investors one clear, calm view of all their money in one place.
PROMISE: "See all your money clearly. Decide with confidence."
AUDIENCE: everyday people whose savings, super, shares and crypto are scattered across different apps.

FACT BANK (the only proof allowed):
- Connects 80+ banks, super funds and brokers into one view of your net worth.
- Tracks over $1.2 billion in assets for members.
- Bank-level encryption; read-only access, so Sable can never move your money.
- No ads, and your data is never sold.
- Pricing: Free, and Plus at $9 per month.

BRAND (build to this exactly - this is a LIGHT, editorial, premium look):
- Light and calm. Warm off-white base #FAF7F1, deep ink text #1A1A1A, a refined deep-green accent #1F5C3D (trust and growth) with a soft muted gold #C9A24B used sparingly. Generous whitespace, editorial restraint, a premium private-bank feel. NEVER dark, NEVER a default indigo/violet or purple-blue gradient.
- Type: a refined serif for display via Fontshare (for example Fraunces) with a clean grotesk for body and JetBrains Mono for figures. Large, confident, well-spaced headings.
- Voice: calm, plain, trustworthy.

ANIMATION (GSAP, restrained and tasteful - this brand is calm, not flashy):
- Gentle fade-and-rise reveals on scroll (staggered), an animated net-worth number that counts up once, a slow continuous marquee of supported institution names, and a light parallax on one hero element. Nothing loud.

SECTIONS: 1 Hero - the promise, a primary CTA, and a hero visual built in inline SVG/HTML (a clean "net worth over time" area chart or an account-aggregation diagram). 2 The problem - money scattered across apps, no single view. 3 One clear view - the core features as a calm bento. 4 Built on trust - encryption, read-only, no ads, data never sold. 5 Pricing - Free and Plus. 6 A short FAQ (accordion). 7 Final CTA.
PRIMARY CTA: "Get started free". SECONDARY: "See how it works".

Return ONLY the complete HTML document.""",
    },
    "lumora": {
        "facts": """# Lumora - Source Truth (FICTIONAL sample brand, model test)
All facts below are the only proof permitted on the page. Invent nothing else.
- Lumora - an AI studio that turns a brand brief into on-brand visuals, layouts and social assets in minutes.
- Promise: "Your brand, generated."
- Generates in 40+ formats, on-brand from your logo and colours.
- 12,000+ creators on the platform.
- Exports to Figma, Canva, PNG and SVG.
- Pricing: Free (20 generations a month), Pro $29 per month, Studio $99 per month.
- Audience: founders, marketers and small creative teams who need on-brand visuals fast.
""",
        "brief": """Build the Lumora landing page (one long page).

COMPANY: Lumora - an AI studio that turns a brand brief into on-brand visuals, layouts and social assets in minutes.
PROMISE: "Your brand, generated."
AUDIENCE: founders, marketers and small creative teams who need on-brand visuals fast.

FACT BANK (the only proof allowed):
- Generates in 40+ formats, on-brand from your logo and colours.
- 12,000+ creators on the platform.
- Exports to Figma, Canva, PNG and SVG.
- Pricing: Free (20 generations a month), Pro $29 per month, Studio $99 per month.

BRAND (build to this exactly - this is a BOLD, vibrant, maximalist, animated look):
- A bright, clean near-white base (#FBFBFD) with BOLD black display type, and a vivid CREATIVE-SPECTRUM accent used as an intentional multi-stop brand gradient: warm coral #FF6B4A into hot magenta #FF2D78 into violet #7C3AED (a warm-led sunset spectrum). This is deliberate brand identity, not a generic AI gradient - it must read warm and creative, and must NOT be a flat two-stop blue-to-purple. Use the gradient on the hero, on key headlines (animated gradient text), and on the primary CTA.
- Type: a big, characterful display grotesk via Fontshare (for example Clash Display or General Sans) with a clean body and JetBrains Mono for small labels.
- Voice: confident, energetic, plain.

ANIMATION (GSAP + ScrollTrigger, maximalist - lean into it):
- An animated aurora / gradient-mesh background that drifts slowly, a spotlight that follows the cursor on the hero, a kinetic animated headline (gradient-shimmer or word-by-word reveal), a fast logo/format marquee, number tickers that count up on scroll, a bento that animates in on scroll, and tilt/glare hover on the showcase cards. Recreate Aceternity / MagicUI style effects in vanilla CSS + GSAP.

SECTIONS: 1 Hero - the promise with kinetic gradient type, the aurora + spotlight, a primary CTA, and a "generated asset" mock built in CSS/SVG. 2 What it does. 3 How it works (brief -> generate -> export). 4 A showcase bento of what it can make. 5 Social proof - 12,000+ creators, a format/tool marquee. 6 Pricing - Free, Pro, Studio. 7 Final CTA.
PRIMARY CTA: "Generate your brand". SECONDARY: "See it work".

Return ONLY the complete HTML document.""",
    },
    "keel": {
        "facts": """# Keel - Source Truth (FICTIONAL sample brand, model test)
All facts below are the only proof permitted on the page. Invent nothing else.
- Keel - financial planning and forecasting that finance teams trust.
- Promise: "Forecasting your finance team can defend."
- Builds real-time forecasts from your actuals; no more stale spreadsheets.
- Connects to your ERP, accounting and CRM (NetSuite, Xero, QuickBooks, HubSpot, Salesforce).
- Scenario planning and live variance tracking against plan.
- Cuts the monthly forecast cycle from days to hours.
- SOC 2 Type II; bank-level encryption; read-only connections.
- Trusted by 300+ finance teams.
- Pricing: Starter free (1 entity), Growth $400 per month, Enterprise custom.
- Audience: finance leaders and FP&A teams at growing companies.
""",
        "brief": """Build the Keel landing page (one long page).

COMPANY: Keel - financial planning and forecasting that finance teams trust.
PROMISE: "Forecasting your finance team can defend."
AUDIENCE: finance leaders and FP&A teams at growing companies, tired of stale spreadsheet forecasts.

FACT BANK (the only proof allowed):
- Builds real-time forecasts from your actuals.
- Connects to your ERP, accounting and CRM (NetSuite, Xero, QuickBooks, HubSpot, Salesforce).
- Scenario planning and live variance tracking against plan.
- Cuts the monthly forecast cycle from days to hours.
- SOC 2 Type II; bank-level encryption; read-only connections.
- Trusted by 300+ finance teams.
- Pricing: Starter free (1 entity), Growth $400 per month, Enterprise custom.

ART DIRECTION - PREMIUM B2B SAAS. This grammar is deconstructed from best-in-class reference landing pages; recreate the GRAMMAR for Keel as an original page. Do not copy any real company's content, brand or layout.
- Hero, in this order: a slim top nav (wordmark left; short centre nav Product / Solutions / Pricing / Customers; right a text "Sign in" plus a FILLED primary button) -> a small rounded pill badge with one line of positioning microcopy -> a confident TWO-LINE headline framed as problem -> outcome -> one plain supporting sentence -> a primary FILLED button and a secondary OUTLINE button, with a tiny reassurance line beneath ("Free to start, no credit card") -> then the CENTREPIECE: a large, detailed, slightly 3D-angled PRODUCT-UI mock built entirely in HTML/CSS/SVG that looks like the real Keel app - a left sidebar, KPI tiles (forecast revenue, variance to plan, cash runway), a revenue-forecast area or line chart, a scenario toggle, and a small data table or category bars. It must read like a real finance dashboard, NOT abstract shapes or gradient tiles -> directly below, a quiet "Trusted by 300+ finance teams" line with a restrained monospace row of integration labels (NetSuite, Xero, QuickBooks, HubSpot, Salesforce).
- Then alternating sections, each with a small UPPERCASE kicker label, a confident headline, plain copy, and a relevant product-detail UI fragment or a tidy feature grid.

LOOK AND FEEL (this is the premium part - restraint, not decoration):
- LIGHT. Warm off-white base #FBFAF8, near-black ink #131417, generous whitespace, and exactly ONE accent: a deep considered teal #0E7C66 used sparingly (primary button, key numbers, one highlight). A soft neutral #ECE9E3 for surfaces and borders. NO decorative gradients, NO abstract blobs, NO default indigo/violet, NO purple-blue gradient. Premium comes from restraint, real product UI, type confidence and spacing.
- Type: a clean modern grotesk for display via Fontshare (for example General Sans or Hanken Grotesk) with JetBrains Mono for figures, labels and the dashboard. Large, tight headlines.
- Voice: precise, calm, credible.

ANIMATION (GSAP, restrained): gentle fade-and-rise reveals on scroll, one KPI number that counts up, a subtle build-in on the hero dashboard. Tasteful, never flashy.

SECTIONS: 1 Hero + product-UI mock + trust strip. 2 The problem (stale spreadsheets, forecasts out of date the day they ship). 3 The product (dashboard detail + features). 4 How it works (connect -> model -> decide). 5 Trust and security. 6 Pricing (three tiers, middle highlighted). 7 Final CTA.
PRIMARY CTA: "Start free". SECONDARY: "Book a demo".

Return ONLY the complete HTML document.""",
    },
}


def load_env() -> None:
    for path in [ROOT / ".env", ROOT / ".env.local", HERMES / ".env", PROFILE / ".env"]:
        if not path.exists():
            continue
        for line in path.read_text(errors="ignore").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


def or_key() -> str:
    k = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_KEY") or ""
    if not k.strip():
        raise SystemExit("Missing OPENROUTER_API_KEY")
    return k.strip()


def extract_html(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    if "```" in t:
        m = re.search(r"```(?:html)?\s*(.*?)```", t, re.S | re.I)
        if m:
            t = m.group(1).strip()
    low = t.lower()
    start = low.find("<!doctype")
    if start == -1:
        start = low.find("<html")
    end = low.rfind("</html>")
    if start != -1 and end != -1:
        return t[start:end + len("</html>")]
    if start != -1:
        return t[start:]
    return t


def build_system() -> str:
    soul = (PROFILE / "SOUL.md").read_text(errors="ignore")
    design_os = (PROFILE / "references" / "DESIGN-OS.md").read_text(errors="ignore")
    return (
        soul
        + "\n\n=== INHERITED CONSTITUTION (non-negotiable) ===\n" + design_os
        + "\n\n=== " + OUTPUT_CONTRACT
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="GLM-5.2 landing range tests")
    ap.add_argument("--brief", required=True, choices=sorted(BRIEFS))
    ap.add_argument("--model", default="z-ai/glm-5.2")
    ap.add_argument("--max-tokens", type=int, default=64000)
    ap.add_argument("--timeout", type=int, default=1200)
    a = ap.parse_args()

    spec = BRIEFS[a.brief]
    client_dir = ROOT / "clients" / a.brief
    (client_dir / "02-source-truth").mkdir(parents=True, exist_ok=True)
    (client_dir / "02-source-truth" / "facts.md").write_text(spec["facts"], encoding="utf-8")
    out_dir = client_dir / "04-production" / "glm-5.2"
    out_dir.mkdir(parents=True, exist_ok=True)

    load_env()
    payload = {
        "model": a.model,
        "messages": [
            {"role": "system", "content": build_system()},
            {"role": "user", "content": spec["brief"]},
        ],
        "max_tokens": a.max_tokens,
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {or_key()}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://design-hermes.local/", "X-Title": f"GLM-5.2 test {a.brief}"},
        method="POST",
    )
    print(f"building {a.brief} with {a.model} ...", flush=True)
    started = time.time()
    data = None
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(req, timeout=a.timeout) as resp:
                data = json.loads(resp.read().decode())
            break
        except urllib.error.HTTPError as e:
            raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='ignore')[:400]}")
        except (urllib.error.URLError, OSError) as e:  # transient reset/timeout
            print(f"network error (attempt {attempt}/4): {e}; retrying", flush=True)
            time.sleep(5)
    if data is None:
        raise SystemExit("network failed after 4 attempts")
    choice = (data.get("choices") or [{}])[0]
    raw = (choice.get("message") or {}).get("content") or ""
    html = extract_html(raw)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    (out_dir / "raw.txt").write_text(raw, encoding="utf-8")
    meta = {"brief": a.brief, "model": a.model, "seconds": round(time.time() - started, 1),
            "finish_reason": choice.get("finish_reason"), "usage": data.get("usage"),
            "html_bytes": len(html.encode()),
            "complete": html.lower().rstrip().endswith("</html>"),
            "out": str(out_dir / "index.html")}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps({k: v for k, v in meta.items() if k != "usage"}, indent=2))
    if meta["usage"]:
        u = meta["usage"]
        print(f"tokens: prompt={u.get('prompt_tokens')} completion={u.get('completion_tokens')} cost=${u.get('cost')}")
    return 0 if meta["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
