#!/usr/bin/env python3
"""Pilot (BIP, client 2): build the Inspra AI Business Information Pack.

Driven by the business-pack-studio soul, on Opus 4.8 via OpenRouter. 16:9 deck ->
self-contained HTML -> Playwright PDF. Embeds the image-lane cover
(assets/inspra-cover.png) and the real Inspra logo. Never prints API keys.
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
OUT_DIR = ROOT / "clients" / "inspra-ai" / "04-production" / "pilot-v5-bip"
API_BASE = "https://openrouter.ai/api/v1"

SYSTEM = """You are business-pack-studio, a senior editorial designer producing a premium Business Information Pack (BIP) - a client-ready sales/explainer PDF deck. Output ONE complete self-contained HTML document only (inline <style>, minimal vanilla <script> only if needed). No markdown, no commentary. It is rendered to a 16:9 landscape PDF via Playwright with prefer_css_page_size.

CLIENT: Inspra AI (by Genius365) - Voice AI agents for Australian businesses. We build, deploy and optimise Voice AI agents that handle phone calls 24/7 with natural, professional Australian conversations, so businesses scale without scaling headcount. ISO 27001 certified, Melbourne.

BIP BUILD RULES:
- 16:9 landscape deck. CSS: @page { size: 1280px 720px; margin: 0 }. Every slide is a <section class="page"> exactly 1280x720px, position:relative, overflow:hidden, break-after:page (no break on the last). Design each page as a complete composition; never overflow a page.
- Brand tokens (no other accents): --accent #39E100 (signature green - highlights, CTAs, the soundwave motif, key numbers), --ink #1A1A1A, --bg #FFFFFF, --dark #121212 (dark sections), --surface #F4F7F2, --muted #5A5F58. Green is the brand signal colour; use it deliberately on dark and white. Never a generic AI purple-to-blue gradient.
- Type: clean modern enterprise grotesk via Fontshare https://api.fontshare.com/v2/css?f[]=switzer@500,600,700&f[]=general-sans@400,500,600&display=swap - Switzer for headings, General Sans for body, Arial fallback. (Brand font is Calibri; this is the web-prototype substitute.) Large confident headings; one idea per page; headline states the takeaway.
- Brand motif: a green soundwave / waveform line and green signal dots (the voice-AI signature), used as section markers and dividers. Make it recognisably Inspra.
- COVER (page 1): full-bleed dark background <img src="assets/inspra-cover.png" alt=""> (decorative, object-fit:cover) with ALL text as real HTML overlaid in the clean left/lower area: the logo <img src="assets/inspra-logo-light.png" style="height:34px"> (light logo on the dark cover), eyebrow "Inspra AI // Voice AI for Australian business // ISO 27001", title "AI voice agents that handle your calls. Around the clock.", and "inspra.ai". The image is background ONLY - never bake text into it.
- ALL other text is real HTML/SVG. Monoline inline SVG icons, never emoji. WCAG AA contrast (green on dark and dark text on white both pass). Vary page rhythm: alternate full-bleed statement, 2-column, numbered process, big-stat, quote - no more than two card-grid pages in a row.
- Use ONLY the real proof supplied. Invent no metrics, logos, or quotes. Australian English, no contractions, no em-dashes.

12-PAGE IA: 1 Cover. 2 What we do (the voice-AI partner; scale without headcount). 3 The problem (missed calls, inconsistent quality, expensive phone staffing). 4 Ready-to-deploy industry agents (Real Estate, Legal, Dental, Plumbing). 5 The platform (Prospecting, Customer Support, Appointment Booking, Smart Dashboard, Call IQ, AI Chatbot, Data Bank). 6 How it works (Build, Test, Deploy, Optimise - numbered process). 7 The results (big-stat page: 40% conversion up, 15x call output, 40% cost reduction, 24/7, 350+ enterprises). 8 Why Inspra (ISO 27001; Australian voices; principle-based prompts; multi-platform VAPI/Retell/LiveKit; scales 10 to 10,000 calls/day). 9 Who it is for (SME and mid-market with high call volumes; the industries). 10 Capabilities (inbound, outbound, lead qualification, appointment setting, live transfer, follow-up). 11 Security & trust (ISO 27001, Australian-based, call recording + analytics). 12 Next step (Book a demo; 1300 467772; hello@inspra.ai; Melbourne; inspra.ai).

Return ONLY the complete HTML document, beginning with <!DOCTYPE html>."""

USER = """Build the Inspra AI BIP (12 pages, 16:9) using this real content.

POSITIONING: "AI voice agents for business." We build, deploy and optimise Voice AI agents that handle calls 24/7 with natural, professional Australian conversations. Scale without scaling headcount. You keep the human touch where it matters; the agents handle the volume.

THE PROBLEM: Missed calls, inconsistent call quality, and expensive staffing for phone-based workflows. Every missed call is a missed customer.

READY-TO-DEPLOY INDUSTRY AGENTS: Real Estate (24/7 lead capture, property details, virtual receptionist, calendar sync, CRM); Legal Services (compliant receptionist, lead qualification, case-status updates, secure answering); Dental Practice (reception, review follow-ups, patient history, insurance intake); Plumbing & Trades (service scheduling, emergency alerts, quote automation).

THE PLATFORM: Prospecting (outreach, lead qualification, appointment setting); Customer Support (FAQ, 24/7, issue resolution); Appointment Booking (virtual receptionist, real-time calendar sync); Smart Dashboard (call tracking, transcripts, booking management); Call IQ (auto summaries, sentiment analysis, call insights); AI Chatbot (website engagement, lead capture, CRM); Data Bank (targeted contact lists with LinkedIn profiling).

HOW IT WORKS (numbered): 1 Build - custom voice agents configured for your business, FAQs and flows. 2 Test - battle-tested with real scenarios before go-live. 3 Deploy - go-live with monitoring, call recording and analytics. 4 Optimise - continuous improvement from real call data.

THE RESULTS (big-stat page - use exactly): 40% increase in conversion; 15x more call outputs; 40% cost reduction in operations; 24/7 operation; 350+ enterprises on the platform; ISO 27001 certified.

WHY INSPRA (differentiators): ISO 27001 certified (enterprise-grade security for voice data); Australian-based with Australian voice profiles and local market knowledge; principle-based prompts (higher success than scripted flows); multi-platform (VAPI, Retell AI, LiveKit) - never locked to one provider; scales instantly from 10 to 10,000 calls per day, 24/7, no sick days.

WHO IT IS FOR: Australian SME and mid-market businesses with high call volumes - real estate, legal, dental, plumbing and trades, B2B sales teams, customer support operations, appointment-heavy businesses.

CAPABILITIES: inbound handling, outbound dialling, lead qualification, appointment setting, live transfer to a human when needed, follow-up management.

NEXT STEP: "Book a demo." 1300 467772 · hello@inspra.ai · Suite 1, Level 10/3 Bowen Crescent, Melbourne VIC 3004 · inspra.ai. Footer: "Inspra AI  //  inspra.ai".

Return ONLY the complete HTML document."""


def load_env() -> None:
    for path in [ROOT / ".env", ROOT / ".env.local", HERMES / ".env",
                 HERMES / "profiles" / "landing-page-studio" / ".env"]:
        if not path.exists():
            continue
        for line in path.read_text(errors="ignore").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Pilot BIP: Inspra AI (business-pack-studio soul)")
    ap.add_argument("--model", default="anthropic/claude-opus-4.8")
    ap.add_argument("--out", default=str(OUT_DIR))
    ap.add_argument("--max-tokens", type=int, default=40000)
    ap.add_argument("--timeout", type=int, default=700)
    a = ap.parse_args()

    load_env()
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": a.model,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER}],
        "max_tokens": a.max_tokens,
        "temperature": 0.6,
        "reasoning": {"max_tokens": 1500},
    }
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {or_key()}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://design-hermes.local/", "X-Title": "Design Hermes Pilot Inspra BIP"},
        method="POST",
    )
    print(f"building Inspra BIP with {a.model} ...", flush=True)
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=a.timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='ignore')[:400]}")
    choice = (data.get("choices") or [{}])[0]
    raw = (choice.get("message") or {}).get("content") or ""
    html = extract_html(raw)
    (out_dir / "bip.html").write_text(html, encoding="utf-8")
    (out_dir / "raw.txt").write_text(raw, encoding="utf-8")
    meta = {"model": a.model, "seconds": round(time.time() - started, 1),
            "finish_reason": choice.get("finish_reason"), "usage": data.get("usage"),
            "html_bytes": len(html.encode()), "complete": html.lower().rstrip().endswith("</html>"),
            "out": str(out_dir / "bip.html")}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps({k: v for k, v in meta.items() if k != "usage"}, indent=2))
    return 0 if meta["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
