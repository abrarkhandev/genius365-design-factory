#!/usr/bin/env python3
"""Pilot A: generate the Automate Accelerator homepage on 3 models via OpenRouter.

One identical brief (brand tokens + real copy + real testimonials + shadcn-derived
component patterns + anti-slop rules) -> 3 lanes (MiniMax M3, Claude Sonnet 4.6,
Claude Opus 4.8). Each lane writes a single self-contained index.html + the logo,
so the QA gate (qa_landing_export.py --html ...) can score each.

Never prints API keys.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERMES_HOME = Path.home() / ".hermes"
CLIENT = ROOT / "clients" / "automate-accelerator"
LOGO_SRC = CLIENT / "04-production" / "website" / "aa-logo.png"
API_BASE = "https://openrouter.ai/api/v1"

LANES = [
    ("minimax-m3", "minimax/minimax-m3"),
    ("sonnet-4.6", "anthropic/claude-sonnet-4.6"),
    ("opus-4.8", "anthropic/claude-opus-4.8"),
]

SYSTEM = """You are a senior design engineer building a premium, conversion-focused B2B landing page for a real client. Output ONE complete, self-contained, responsive HTML document only: inline <style>, minimal vanilla <script>, no external build, no markdown, no commentary before or after. It must render correctly opened directly as a file.

CLIENT: Automate Accelerator - an Australian B2B outbound-growth and AI-services company. Human-led, performance-focused, AI-scaled. The outbound PARTNER, not an agency.

BRAND (use as CSS custom properties; no other accent colours):
- --accent (orange) #F47920  -> primary CTAs and key highlights
- --brand (purple)  #412F8F  -> brand depth, secondary surfaces, the dotted motif
- --ink #14121A ; --bg #FFFFFF ; --surface #F6F4FB ; --muted #5A5566
- Purple is the genuine BRAND colour: use it deliberately with orange and white. Do NOT produce a generic AI purple-to-blue/cyan gradient.
- Type: geometric grotesk. Load 'Clash Display' (headings) + 'General Sans' (body) from Fontshare (https://api.fontshare.com/v2/css?f[]=clash-display@600,700&f[]=general-sans@400,500,600&display=swap), Arial fallback. Large, confident headings. NEVER Inter, Roboto, Geist or Space Grotesk.
- Logo: <img src="aa-logo.png" alt="Automate Accelerator"> in the nav (left) and footer.
- Distinctive 20% move (make it recognisably AA from a screenshot): reuse the orange double-slash "//" mark from the logo as a recurring section marker, and use a subtle purple/orange DOTTED-MATRIX texture (CSS radial-gradient dots) in section backgrounds - the brand's signature pattern.

NON-NEGOTIABLE CRAFT:
- Real HTML/SVG text only; never bake text into images. Monoline inline SVG icons; NEVER emoji icons.
- 8pt spacing rhythm; type scale ~1.25-1.333; body 16-18px; prose measure <= 72ch; generous white space.
- WCAG AA contrast (body >= 4.5:1). One primary CTA style (orange), repeated after each major beat.
- No rounded card with a coloured left-border. No filler/lorem. Australian English, no contractions.
- Motion: purposeful and clearly present (the page should feel alive as you scroll). Add a STAGGERED scroll-reveal (fade + ~30px rise, sequential within each group/grid via transition-delay) driven by IntersectionObserver, plus a subtle on-load hero entrance (defer one animation frame so it transitions). Respect prefers-reduced-motion (reveal instantly). Gate the reveal-all safety net behind navigator.webdriver: reveal everything immediately when headless (so QA screenshots are never blank), with a long ~6s fallback for real users so it never pre-empts their scrolling.
- Use ONLY the supplied copy and the supplied real testimonials. Invent no metrics, awards, client names, or quotes."""

TESTIMONIALS = [
    ('"I have really enjoyed working with the team. Amjad has been very engaged and we have a good working relationship. The results have exceeded what we expected going in."', "Bill McLellan - Managing Director, WhyCubed - Business Consulting"),
    ('"Working with AA has changed the way we approach business development entirely."', "Daniel - CGO, Growth Australia - Workplace Fitout, Sydney NSW"),
    ('"AA understood our technical market immediately and built a system that actually resonated with our prospects."', "Peter - CEO, Lookup - IT & Cybersecurity"),
    ('"When we came to Automate Accelerator, we were looking for a team that could genuinely move the needle for our business - and that is exactly what we found. Professional, attentive, and truly invested in our success. We are already seeing real momentum with bookings coming in."', "Ben Skender - Modn Tech Solutions - B2B Technology Services, Perth WA"),
    ('"Definitely the discipline that Automate Accelerator has brought to me has helped me connect with my leads with a more targeted approach. They bring the smarts, tools, consistency and accountability."', "Anthony Woods - Pinnacle Traction - Business Coaching"),
    ('"AA has been very good and effective with its intelligence and ability to grab the right opportunities. Great and experienced team to work with. They know their market and they deliver on what they promise."', "Mohan Kumar - SoftnetX - IT Services"),
    ('"I have worked with these guys for over a year now and they have been a good team to work with."', "Brendon Butcher - HardHat Media - Marketing Services"),
]

USER = """Build the Automate Accelerator HOMEPAGE as a single self-contained index.html. Use this real copy, in this section order:

NAV: logo (left) + links: Home, Services, AI, Data, Case Studies, About us, Contact Us. Right: "Book a discovery call" button (orange).

HERO: eyebrow "AUTOMATE ACCELERATOR // AUSTRALIAN B2B // SINCE 2021"; H1 "More qualified meetings. Human expertise. AI where it multiplies."; subhead "The human touch in every outreach, powered by AI precision."; paragraph "Automate Accelerator is your outbound partner, not your outbound agency. A professional team, experienced with Australian and global decision-makers, runs your campaigns. AI multiplies what they can do."; emphasised line "You show up to the meetings. We do the legwork."; CTAs: "Book a discovery call" (primary, orange, arrow) and "See the numbers" (secondary/ghost). Below hero, a thin strip: "Human-led. Performance-focused. AI-scaled."

AWARDS / TRUST STRIP: "Recognition received by Automate Accelerator's founding team across two decades of operating Australian growth businesses." Present as a restrained awards/credibility strip (do not invent award names; use neutral placeholders like generic award marks only if needed, or keep it text-led).

THE PROBLEM: "Your pipeline should not depend on referrals. Or organic growth alone. There is a better way."

TWO PRODUCTS: heading "Fuel your growth. Fix your friction."; "One partner. Two paths. Start where you need us most." Two cards: (1) Growth Engine - build a predictable pipeline; (2) AI Solutions - reclaim your time. "Most clients start with the Growth Engine to build a pipeline. Many add AI Solutions later to reclaim their time. You choose the priority; we deliver the result." CTA "Book a discovery call".

WHAT YOU GET / WHAT YOU AVOID: "Exactly what changes when we take over." Two-column layout - left "what changes the day you go live", right "the things you never have to think about again". Write 4-5 concise, believable items per column derived from the services (verified buyer data, campaigns run under your brand, replies handled, meetings booked to your calendar / no juggling tools, no chasing leads, no missed calls, no managing a stack).

WHY AUTOMATE ACCELERATOR: "We are not an agency. We are your growth partner." "The partner with skin in the game. Three things we do differently." Three differentiator cards (accountability, dedicated team under your brand, AI that multiplies the team). "Growth built on accountability scales faster." CTA "Book a discovery call".

PROVEN IN YOUR MARKET: "Proven in the Australian market. Tested in your niche." "Automate Accelerator works exclusively with B2B businesses across Australia and globally ... verified decision-makers, mapped by function, reached the right way." Present an industries grid (e.g. Professional Services, IT & Cybersecurity, Business Consulting, Workplace Fitout, Marketing Services, Technology Services, Coaching, IT Services) and the line "This is our track record, not a wishlist." CTA "Book a discovery call".

TESTIMONIALS: heading "What our clients say." "Real words. Real clients. Different industries. Same result." Build an accessible horizontal CAROUSEL/slider, ONE testimonial visible at a time, with prev/next buttons (aria-label "Previous"/"Next") and a slide container using role/aria-roledescription="slide" - mirror the shadcn Carousel pattern (track of slides + previous/next controls) reimplemented in vanilla JS. Use these REAL quotes verbatim:
%TESTIMONIALS%
Footer of section: "See our case studies" and "Watch Client Video Testimonials" as text links.

CLIENT TICKER: "Trusted by Australian businesses:" as a horizontal scrolling marquee of names: Neurocapability // Build AI // Cloud Ready Solutions // Signarama Hindmarsh // Love Finance // Pinnacle Traction // Modn Tech Solutions // WhyCubed // Growth Australia // Lookup. (Names as styled text, not fake logos.)

FINAL CTA: "Tell us the buyer. We will find them. Tell us the outcome. We will build the path collaboratively." "Book a discovery call. We listen first. Then we come back with a clear picture of the path we can build together - what it looks like, what it costs, and what you can expect." "No obligation. No sales pressure. You leave with useful clarity regardless of whether we work together." Primary CTA "Book a discovery call", secondary "See services first".

FOOTER: logo, nav links, "Automate Accelerator  |  automateaccelerator.com.au", and a tasteful purple footer using the dotted motif.

COMPONENT PATTERNS (from the shadcn registry; reimplement in vanilla HTML/CSS/JS, do not ship React): testimonials = Carousel (slide track + CarouselPrevious/CarouselNext, one item visible, keyboard accessible); service/why/product blocks = Card (clean panel, generous padding, hairline or shadow, NO coloured left-border); eyebrows/labels = Badge.

Return ONLY the complete HTML document, beginning with <!DOCTYPE html>."""


def load_env() -> None:
    for path in [ROOT / ".env", ROOT / ".env.local", HERMES_HOME / ".env",
                 HERMES_HOME / "profiles" / "landing-page-studio" / ".env"]:
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


def build_user_prompt() -> str:
    quotes = "\n".join(f"- {q}\n  {who}" for q, who in TESTIMONIALS)
    return USER.replace("%TESTIMONIALS%", quotes)


def extract_html(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    # strip code fences
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
        return t[start:]  # truncated page: keep everything from the HTML start
    return t


def generate(model: str, user_prompt: str, *, max_tokens: int, timeout: int) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        # Hard-cap thinking so the token budget goes to the HTML output. MiniMax M3
        # ignores effort:low (still burned ~15k); a max_tokens cap is firmer.
        "reasoning": {"max_tokens": 1500},
    }
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {or_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://design-hermes.local/",
            "X-Title": "Design Hermes Pilot A",
        },
        method="POST",
    )
    started = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message", {})
    html = extract_html(msg.get("content") or "")
    return {
        "model": model,
        "seconds": round(time.time() - started, 1),
        "finish_reason": choice.get("finish_reason"),
        "usage": data.get("usage"),
        "html": html,
        "raw": msg.get("content") or "",
        "html_bytes": len(html.encode()),
        "complete": html.lower().rstrip().endswith("</html>"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Pilot A: AA homepage on 3 models (OpenRouter)")
    ap.add_argument("--out", default=str(CLIENT / "04-production" / "pilot-v5"))
    ap.add_argument("--max-tokens", type=int, default=32000)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--only", help="comma-separated lane names to run (default all)")
    args = ap.parse_args()

    load_env()
    user_prompt = build_user_prompt()
    out_root = Path(args.out)
    only = set((args.only or "").split(",")) if args.only else None

    summary = []
    for lane, model in LANES:
        if only and lane not in only:
            continue
        print(f"[{lane}] generating with {model} ...", flush=True)
        try:
            res = generate(model, user_prompt, max_tokens=args.max_tokens, timeout=args.timeout)
        except urllib.error.HTTPError as e:
            print(f"[{lane}] HTTP {e.code}: {e.read().decode(errors='ignore')[:300]}", flush=True)
            summary.append({"lane": lane, "model": model, "ok": False, "error": f"HTTP {e.code}"})
            continue
        except Exception as e:
            print(f"[{lane}] error: {type(e).__name__}: {e}", flush=True)
            summary.append({"lane": lane, "model": model, "ok": False, "error": str(e)})
            continue
        lane_dir = out_root / lane
        lane_dir.mkdir(parents=True, exist_ok=True)
        (lane_dir / "index.html").write_text(res["html"], encoding="utf-8")
        if LOGO_SRC.exists():
            shutil.copy(LOGO_SRC, lane_dir / "aa-logo.png")
        (lane_dir / "raw.txt").write_text(res.get("raw") or "", encoding="utf-8")
        meta = {k: v for k, v in res.items() if k not in ("html", "raw")}
        meta.update({"lane": lane, "ok": bool(res["html"]) and res["complete"], "out": str(lane_dir / "index.html")})
        (lane_dir / "meta.json").write_text(json.dumps(meta, indent=2))
        summary.append(meta)
        print(f"[{lane}] {res['html_bytes']} bytes, complete={res['complete']}, finish={res['finish_reason']}, {res['seconds']}s", flush=True)

    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    return 0 if all(s.get("ok") for s in summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
