#!/usr/bin/env python3
"""Model test: build the Sentra landing page with the landing-page-studio SOUL
on GLM-5.2 (z-ai/glm-5.2) via OpenRouter.

Mirrors the approved pilot generators: the profile SOUL + the inherited
constitution become the system prompt, a fixed brief becomes the user prompt,
and the model returns ONE self-contained HTML document. Never prints the key.
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
OUT_DIR = ROOT / "clients" / "sentra" / "04-production" / "glm-5.2"
API_BASE = "https://openrouter.ai/api/v1"

OUTPUT_CONTRACT = """OUTPUT CONTRACT (landing page):
- Output ONE complete, self-contained HTML document only: inline <style> and minimal vanilla <script>. No markdown, no commentary, no external files.
- This build uses NO external images: every visual is CSS or inline SVG. All real text stays HTML/SVG, never baked into a picture.
- Fully responsive: it must hold up at 1440px, 768px and 375px with no horizontal overflow.
- Land ONE ownable distinctive move - a single idea that makes this page unmistakably Sentra, not a template anyone could rebrand.
- Motion: any scroll-reveal must stagger in for real users, but (a) reveal ALL content immediately when navigator.webdriver is true (so headless screenshots are complete), (b) fall back to fully visible within 6 seconds, and (c) respect prefers-reduced-motion.
- WCAG 2.2 AA contrast on all text. Australian English, no contractions, no em-dashes or en-dashes in body copy.
- Use ONLY the facts supplied below. Invent no metrics, logos, customers or quotes.
- Return ONLY the complete HTML document, beginning with <!DOCTYPE html>."""

BRIEF = """Build the Sentra landing page (single long page) from this brief.

COMPANY: Sentra - AI incident response for engineering teams.
PROMISE: "Resolve incidents before your customers notice." An AI copilot that watches your systems, detects incidents, finds the likely root cause and drafts the fix, so on-call engineers go from paged to resolved in minutes, not hours.
AUDIENCE: platform, SRE and on-call engineers at fast-growing software companies.

FACT BANK (the only proof allowed on the page):
- Cuts mean time to resolution by 71%.
- Surfaces the likely root cause in under 30 seconds.
- Connects to 60+ tools (Datadog, PagerDuty, GitHub, Kubernetes, AWS, Sentry).
- Trusted by 400+ engineering teams.
- SOC 2 Type II certified; your logs are never used to train models.
- Pricing: Free (1 service), Team $30 per seat per month, Enterprise custom.

HOW IT WORKS: Detect -> Diagnose -> Draft fix -> Resolve. The drafted fix is always reviewed and approved by a human.
CAPABILITIES: always-on anomaly detection across logs, metrics and traces; root-cause analysis with the evidence trail shown; a drafted reviewable fix (PR or runbook step); auto-written incident timeline and post-incident summary; noise control that groups related alerts into one incident.

BRAND (build to this exactly):
- A dark "command center". Base near-black #0A0C10, off-white text, ONE electric signal-green accent #5EF38C (the "resolved / all clear" colour), with a restrained alert-amber #FFB020 as a secondary signal only. Glassy panels, precise grid, monospace for telemetry and code. Confident and technical, like a world-class observability product. NEVER a default indigo/violet or purple-blue gradient.
- Type: a strong modern grotesk for display via Fontshare (for example General Sans or Hanken Grotesk), with JetBrains Mono for telemetry, code and key numbers. Do not use Inter/Roboto/Arial as the signature face.
- Voice: precise, calm, credible.

SECTIONS (one long page): 1 Hero - the promise, a primary CTA, and a product visual built as inline SVG/HTML (for example a live incident-to-resolved timeline or a signal graph). 2 The problem - alert fatigue, slow MTTR, context-switching at 2am. 3 How it works - the four-step loop. 4 Capabilities - a bento-style grid. 5 Proof and trust - the metrics, SOC 2, "your logs never train models". 6 Pricing - the three tiers. 7 Final CTA.
PRIMARY CTA: "Start free". SECONDARY: "Book a demo".

Return ONLY the complete HTML document."""


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
    ap = argparse.ArgumentParser(description="Sentra landing built with the landing soul on GLM-5.2")
    ap.add_argument("--model", default="z-ai/glm-5.2")
    ap.add_argument("--out", default=str(OUT_DIR))
    ap.add_argument("--max-tokens", type=int, default=60000)
    ap.add_argument("--timeout", type=int, default=1200)
    a = ap.parse_args()

    load_env()
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": a.model,
        "messages": [
            {"role": "system", "content": build_system()},
            {"role": "user", "content": BRIEF},
        ],
        "max_tokens": a.max_tokens,
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {or_key()}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://design-hermes.local/", "X-Title": "GLM-5.2 landing test"},
        method="POST",
    )
    print(f"building Sentra landing with {a.model} ...", flush=True)
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=a.timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='ignore')[:400]}")
    choice = (data.get("choices") or [{}])[0]
    raw = (choice.get("message") or {}).get("content") or ""
    html = extract_html(raw)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    (out_dir / "raw.txt").write_text(raw, encoding="utf-8")
    meta = {"model": a.model, "seconds": round(time.time() - started, 1),
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
