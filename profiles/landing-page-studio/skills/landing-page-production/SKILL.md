---
name: landing-page-production
description: Use when creating or improving a landing page/website from product facts, client assets, discovery docs, or an existing website URL.
version: 1.0.0
created_by: agent
---

# Landing Page Production SOP

## Trigger
Use this skill whenever the task is to create, improve, critique, or plan a landing page or website page.

## Core rule
A landing page is not a converted BIP. It can use the same source-truth, but it must create its own conversion journey.

## Required workflow

### 0. Model routing and mode selection
Before producing any page, classify the job:

- **Reference / clone-inspired:** client provided a competitor, reference URL, screenshot, or “make it like X”. Use Capture → Deconstruct → Rebrand/Re-compose → Ship+QA. Never Capture → Ship. For the deconstruction step, use `references/reference-deconstruction-checklist.md`.
- **Greenfield:** no direct reference. Use Brief → Generate first 80% draft → Craft pass → Asset fan-out if needed → Ship+QA.

Use the Design Hermes NIM router before final production where useful:

```bash
# MiniMax M3: design taste, craft critique, distinctive move, anti-slop review
python3 factory/scripts/design_model_router.py --role design-critic --context-file clients/<client>/02-source-truth/client-facts.json --context-file clients/<client>/02-source-truth/DESIGN.md
python3 factory/scripts/design_model_router.py --role distinctive-move --context-file clients/<client>/02-source-truth/DESIGN.md
python3 factory/scripts/design_model_router.py --role anti-slop-review --context-file clients/<client>/06-deliverables/final-web/index.html

# Qwen: reference/screenshot/system-spec deconstruction
python3 factory/scripts/design_model_router.py --role reference-system-spec --context-file clients/<client>/01-extracted/website.md --out clients/<client>/02-source-truth/system-spec.md
```

Model roles:
- `minimaxai/minimax-m3` = free NIM design director / craft critic. Keep it source-truth constrained because it may otherwise suggest invented metrics/logos.
- `qwen/qwen3.5-122b-a10b` = free NIM multimodal/reference/system-spec reader.
- Cloudflare Kimi K2.6 remains the stable production model until NIM production quality is proven on multiple pilots.

### 1. Intake and source-truth
Use the shared source-truth when available. If missing, extract it from:
- assets folder
- Fathom transcript
- DOCX/PDF brief
- existing website URL
- current landing page

Minimum facts:
- audience
- product/service
- offer
- primary CTA
- proof
- objections
- brand notes

### 2. Conversion strategy
Define:
- one primary visitor
- one primary action
- hero promise
- problem framing
- solution mechanism
- proof plan
- CTA placement
- objection handling

### 3. Reference research and visual analysis
Before designing, collect 5–8 references and write a short reference-analysis note.

Required reference workflow:
1. Search Dribbble first for same-category inspiration, e.g. `AI automation landing page`, `AI agency website`, `voice agent SaaS`, `B2B AI platform`, `automation dashboard`.
2. Open promising shots and capture screenshots or use image URLs where available.
3. Use the image-analysis/vision tool on at least 2–3 visual references. Extract layout patterns, typography posture, colour/contrast, spacing, hero treatment, card style, motion implications, and what to avoid.
4. Also collect real competitor/client industry websites so the design is grounded in actual buying context, not only aesthetic shots.
5. Transform the references into an original design direction. Do not clone proprietary layouts or copy exact branded visuals.

When a client supplies a **specific reference URL** they want emulated, use `references/reference-deconstruction-checklist.md` to extract the structural system (typography, spacing, colour weights, card patterns, hero composition) and then rebrand/recompose with the client's assets and copy.

Reference sources:
- Dribbble shots for visual taste and composition
- 21st.dev hero components and other component libraries such as Sera UI, shadcn blocks, Magic UI, Aceternity UI, and MotionSites for proven section structure
- real competitor/client industry websites for market language and offer structure
- high-quality landing pages for conversion patterns
- design/interaction references for motion and UI polish

Hero composition gate before coding:
- Collect at least 3 hero-section references, including 1 from 21st.dev or a component library and 1 real SaaS/industry site.
- Choose a hero layout pattern explicitly: centered, split copy/media, full-background visual, dashboard mockup, or product screenshot.
- H1 should normally be 1–3 lines on desktop, never a tall 5–6 line block unless the brief intentionally asks for editorial poster typography.
- In split heroes, the media must align optically with the copy block. Avoid the common failure where text sits high-left and the dashboard/image starts low-right, creating a dead empty gap.
- Keep a clear relationship between eyebrow, H1, lede, CTA, proof cue, and visual. The hero should read as one composition, not two disconnected columns.
- Verify with desktop and mobile screenshots before delivery. If the hero feels unbalanced, revise spacing, grid columns, H1 length, or visual placement before moving on.

Use skills.sh-style references deliberately:
- `designing-beautiful-websites`: make next action obvious, build from user goals, systemise visuals, validate early.
- `gsap-framer-scroll-animation`: use GSAP for ScrollTrigger, pinning, horizontal scroll, complex timelines; use Motion/Framer Motion for React/Next declarative reveal/hover/tap/layout transitions.
- `nextjs-framer-motion-animations`: use small purposeful accessible animations in Next.js without breaking server/client boundaries.

### 4. Section flow
Default page flow:
1. Hero: sharp promise + CTA + proof cue
2. Problem / cost of inaction
3. Solution / product mechanism
4. Services/features/offers
5. How it works
6. Proof/case studies/testimonials
7. Differentiators
8. FAQ/objections
9. Final CTA

Adjust for the business. Do not overbuild.

### 5. Visual system
Define before coding:
- layout grid
- type scale
- colour palette
- image/illustration style
- card/section system
- motion principles
- responsive behaviour

### 6. Animation rules
Use animation only when it improves comprehension or perceived quality.
- Respect `prefers-reduced-motion`.
- Avoid scroll-jank and heavy effects.
- Use Motion/Framer Motion for most React/Next interactions.
- Use GSAP when there is a clear need for ScrollTrigger timelines, pinning, or complex choreography.
- Do not animate every section the same way.
- **Reveal-on-scroll pitfall (see Pitfalls):** if you gate visibility on `IntersectionObserver`, headless screenshots and slow-loading users will see empty content below the fold. Always include a viewport-on-load check + a 2–3 s safety-net timeout that adds `is-visible` to anything still hidden. The pattern is documented in the Animation pitfalls section below.

### 7. Build and export
Prefer:
- static HTML/CSS/JS for quick prototypes, or
- Next.js/React when the project needs components and Motion/Framer Motion.

Produce:
- source files
- desktop screenshot
- mobile screenshot
- QA report

## Multi-page site production
If the brief implies more than one page, treat the first page as the **design system proof**. Build its `styles.css`, nav, footer, and component vocabulary, then scale horizontally:

1. **Ship the system page first.** Resolve hero, type, colour, spacing, card language, and nav/footer on one page before delegating more.
2. **Write a shared-page contract.** Every child page must:
   - Link to the same `styles.css`.
   - Use the identical header/nav and footer markup, varying only the active/current page indicator.
   - Keep CTA destinations consistent (e.g. `contact.html#book`).
   - Reuse the same reveal-on-scroll script and `prefers-reduced-motion` guard.
3. **Delegate child pages in parallel** with the contract as context. Pass each agent the source docx, the canonical `styles.css` path, and the canonical page (the system page) as the component reference.
4. **Normalize after delegation.** Subagents rarely produce identical nav/footer link targets. Run a reconciliation pass that injects the canonical header and footer into every page and remaps active states. See `references/multi-page-normalize-script.py` for an example.
5. **Cross-page QA.** Verify every page links to every real HTML file, has no stray `#` anchors (except intentional in-page anchors), and has matching CSS variables. Generate desktop + mobile screenshots for every page before delivery.

### When to use subagents
Use parallel child agents when there are **3 or more distinct pages** with independent copy. For 1–2 pages, build sequentially so craft stays tight. For 3+, the coordination overhead of subagents is paid back by parallel output — but only if step 4 (normalization) is followed.

### 8. QA rubric
Score each 0–2:
1. Clear above-the-fold promise
2. Audience relevance
3. Conversion journey
4. CTA clarity
5. Proof placement
6. Visual hierarchy
7. Responsive design
8. Accessibility/contrast
9. Performance/lightweight motion
10. Brand fit
11. Interaction polish
12. Implementation handoff quality

Pass:
- 18/24 acceptable
- 21/24 client-ready
- Any 0 in hero clarity, CTA clarity, responsiveness, or accessibility requires revision.

---

## Pitfalls

### Reveal-on-scroll breaks static screenshots and slow loads
**Symptom:** the page looks correct in a normal browser, but in a Playwright/headless full-page screenshot, every section after the first viewport renders as empty whitespace. The browser tool's `browser_vision` snapshot may also capture the same blank state.

**Cause:** you set `.reveal { opacity: 0; transform: translateY(...) }` and rely on `IntersectionObserver` to add `.is-visible` on scroll. In a headless context that renders the whole page at once without a real scroll, the observer never fires for elements below the initial viewport — they stay at `opacity: 0` forever.

**Fix — always pair the observer with two safety nets:**

```js
(function () {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const els = document.querySelectorAll('.reveal');
  if (reduce) { els.forEach(el => el.classList.add('is-visible')); return; }

  // (1) Immediately reveal anything already in the viewport on load
  const vh = window.innerHeight || document.documentElement.clientHeight;
  els.forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.top < vh && r.bottom > 0) el.classList.add('is-visible');
  });

  if (!('IntersectionObserver' in window)) {
    els.forEach(el => el.classList.add('is-visible'));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.05, rootMargin: '0px 0px -20px 0px' });
  els.forEach(el => { if (!el.classList.contains('is-visible')) io.observe(el); });

  // (2) Safety net — guarantees content is visible even if observer never fires
  setTimeout(() => {
    document.querySelectorAll('.reveal:not(.is-visible)').forEach(el => el.classList.add('is-visible'));
  }, 2500);
})();
```

CSS should still respect `prefers-reduced-motion`:
```css
@media (prefers-reduced-motion: reduce) {
  .reveal { opacity: 1; transform: none; transition: none; }
}
```

**Verification step after building:** always run a full-page screenshot before declaring done. If any section is missing, the observer/safety-net pattern is the first place to look.

### Hero H1 wrapping to the wrong number of lines
**Symptom:** your H1 is meant to break into 3 lines on desktop, but the long middle phrase wraps onto a fourth line, breaking the optical balance.

**Fixes (try in order):**
1. Add `text-wrap: balance;` to the H1 — modern browsers will distribute text across 2–4 visually-balanced lines automatically.
2. Reduce the H1 font size by ~10% (e.g. `clamp(38px, 4.6vw, 58px)` instead of `clamp(40px, 5.4vw, 68px)`).
3. Widen the copy column in the grid (e.g. `grid-template-columns: 1.15fr 1fr` instead of `1.05fr 1fr`).
4. As a last resort, use explicit `<br/>` tags and accept the rigid structure.

### Capturing mobile screenshots when the browser tool can't resize
**Symptom:** the in-app browser tool loads the page at a fixed desktop viewport and there's no `set_viewport_size` call available. You need a mobile-width full-page screenshot for QA.

**Fix:** use Playwright via `python3 -c` through the terminal. Assumes `playwright` is installed (it usually is in Design Hermes — `~/.local/bin/playwright`):

```python
import subprocess
script = """
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.goto("file:///path/to/index.html")
        await page.wait_for_timeout(3500)  # let reveal-on-scroll safety net fire
        await page.screenshot(path="mobile.png", full_page=True)
        await browser.close()
asyncio.run(main())
"""
subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=60)
```

Save the screenshot into `06-deliverables/screenshots/` so it's part of the deliverable, not next to the source HTML.
