---
name: linkedin-asset-production
description: Use when creating or improving LinkedIn visual assets (personal/company banners, carousels/document posts, single infographics, image posts, newsletter or event art) for a B2B founder or company.
version: 1.0.0
created_by: agent
---

# LinkedIn Asset Production SOP

## Trigger
Use this skill whenever the task is to create, improve, critique, or plan a LinkedIn visual asset: a personal banner, company logo/cover, carousel (document post), single image/infographic, image post, newsletter logo/cover, link-share OG image, or event banner. Every output is an 80% draft finished with taste; it must be legible thumb-first on a phone (~80% of views are mobile) and unmistakably on-brand.

## Core rule
The asset is invisible if the dimensions or safe zones are wrong. Get the exact specs right first, then design. Generate only backgrounds/illustration via `image-prompter` -> `image-asset-lab`; lay every headline, stat, logo and CTA as real HTML/SVG text (never baked into the image); export at 2x, then downscale.

## Required workflow

### 0. Inherit the constitution and read the client brief
Before producing anything:
1. Read `DESIGN-OS.md` (the constitution) — the non-negotiables (§1), honesty/banned-words (§2), the 7 anti-slop sins (§3), tokens (§4), type (§5), colour (§6), the distinctive-move test (§9), and the QA contract (§11) are the floor and are NOT overridable by a brief.
2. Read the per-client `clients/<client>/02-source-truth/DESIGN.md`. It wins on *brand* (palette, fonts, logo geometry, voice), never on the non-negotiables or honesty. If it is missing, build it before designing — output quality depends more on a tight `DESIGN.md` than on the model.
3. Confirm these source-truth files exist; create any that are missing:

```text
clients/<client>/02-source-truth/client-facts.json   # the fact bank (real stats, proof, claims)
clients/<client>/02-source-truth/DESIGN.md           # brand palette, fonts + licence + URL, logo, voice
clients/<client>/02-source-truth/assumptions.md      # where missing proof is logged, never invented
```

**Build rule (non-negotiable):** real text stays real HTML/SVG. The image layer carries only background/texture/illustration and at most a 1-4 word decorative label. Headlines, stats, logos, CTAs, page numbers and chart numerals are always overlaid as live text.

**Honesty (non-negotiable):** never invent metrics, percentages, dollar figures, client names, logos, testimonials, awards or results. If a stat is not in `client-facts.json` it does not appear; missing proof goes to `assumptions.md`. Australian English, no US spellings, no contractions, no em/en-dash punctuation in final copy. Avoid the banned-word list (revolutionary, game-changing, streamline, empower, seamless, unlock, elevate, leverage, cutting-edge, world-class, best-in-class, all-in-one, delve, tapestry, testament, boasts, etc.).

### 1. Intake and asset-type routing
Classify the request and lock the exact specs from the soul before anything else. These dimensions are the law:

- **Personal banner:** 1584x396 px (4:1), JPG/PNG <=8 MB. The round avatar covers the LOWER-LEFT on BOTH desktop and mobile (mobile overlap ~568x264 px since Jan 2025). Keep ALL text/logo >=400 px from the left edge, above the midline, and >=150 px from the bottom. The lower-left quadrant is DEAD; the far-left third is hidden on mobile.
- **Company logo:** 400x400 (1:1, <=3 MB). **Company cover:** 1128x191 (design master 4200x700, 6:1) — keep lower-left clear for the logo overlap. Life tab: main 1128x376 (3:1), modules 502x282, photos 900x600.
- **Newsletter:** logo 300x300; cover art designed at 1280x720 (16:9) but all critical content inside the 1128x650 live-render safe rectangle.
- **Carousel / document post:** pick ONE ratio — 1080x1080 (square, default) or 1080x1350 (portrait, max reach) — and use it on EVERY slide (LinkedIn locks the doc to slide 1's ratio). 8-12 slides. Export a font-embedded PDF, <3 MB. Never upload a JPG/PNG sequence (recompression blurs text).
- **Single image / infographic:** 1080x1350 (4:5) for max mobile reach, or 1080x1080 (1:1) safe. Never taller than 4:5 (LinkedIn centre-crops it). PNG for text/infographics, JPG for photos.
- **Link-share OG image:** 1200x627 (1.91:1). **Event banner:** 1600x900 (16:9).

### 2. Surface and channel strategy (founder vs company)
Decide who the asset speaks as before designing:
- **Personal profiles out-reach Pages dramatically** (~5-7x reach; carousels ~63% higher engagement). Route carousels and thought-leadership through the FOUNDER profile. Founder assets read as a credible human: first-person voice, real headshot, one borrowed brand colour, banner = name + one-line value proposition kept entirely out of the avatar/lower-left zone.
- The **Company Page** carries the strict brand system: logo lockup, product clarity, life-tab culture imagery.
- Define the single idea for the asset (one idea per slide for carousels), the one action you want, and the one real proof point that earns it.

### 3. Mobile-feed legibility constraints (hard floor)
Bake these in before laying any text. ~80% of views are mobile.
- Body text >=24 pt, headings >=48 pt (design-file sizes).
- <=6-8 lines and <=60 words per slide; one idea per slide.
- Contrast >=4.5:1 (WCAG 2.2 AA; APCA target Lc>=75 body / Lc>=60 large).
- Safe margins >=50-80 px; logos/CTAs >=60 px from edges.
- Palette <=3-4 colours; treat white space as a design asset.
- Derive the primary hue from the client logo/brand (never default indigo/violet/blue); accent appears <=2 visible uses per surface.
- Pair one distinctive display font with one refined body font — never Inter/Roboto/Arial/Geist/Space Grotesk as the signature face. A serif brand needs a serif display.

### 4. Carousel anatomy (when the asset is a document post)
- **Slide 1 — HOOK:** a bold specific claim OR a single REAL stat (never invented), brand logo, high contrast, and a swipe cue ("Swipe ->" / arrow). No generic "Tips for X" or "Did you know?".
- **Body slides:** one point each; alternate text-led and visual-led; identical grid/fonts/colours across every slide; a persistent progress cue ("3/9") and bridging phrases ("Here's why", "The result").
- **Last slide — CTA:** restate the one takeaway + one action (comment prompt / follow / "link in post") + brand mark. A question lifts comments, which lifts reach.

### 5. Model routing (draft free, deliver client-grade, critique cross-family)
Layout and copy are an 80% draft on a free model, finished to client grade on a paid model, then critiqued by a DIFFERENT model family than the builder (a vision LLM caught only 24% of real UX issues, so critique is advisory and must cite evidence).

- **Draft / iterate (free):** MiniMax M3 on OpenRouter — layout options, hook/copy variants, slide structure, the distinctive move. Keep it source-truth constrained or it will suggest invented metrics/logos.
- **Deliver (client-grade, paid):** Claude Sonnet 4.6 or Opus 4.8 via OpenRouter, e.g. `-m anthropic/claude-sonnet-4.6 --provider openrouter` (or `anthropic/claude-opus-4.8`). Kimi K2.6 / Qwen 3.7 Max as A/B options.
- **Critique / anti-slop (different family from the builder):** GLM-5.1 or Qwen — advisory, evidence-cited only.

The factory router wraps these roles:

```bash
# MiniMax M3 (free): hook/copy variants, slide structure, distinctive move
python3 factory/scripts/design_model_router.py --role distinctive-move \
  --context-file clients/<client>/02-source-truth/DESIGN.md

# Anti-slop / craft critique on a DIFFERENT family than the builder (advisory, evidence-cited)
python3 factory/scripts/design_model_router.py --role anti-slop-review \
  --context-file clients/<client>/04-production/<asset>/index.html
```

### 6. Image-prompter slot briefs (background/illustration only)
Hand a background brief to `image-prompter` -> `image-asset-lab`. Every brief MUST carry a negative-constraint block. Prototype on free assets; deliver only on licensed assets (the licence is set by the model maker, recorded in `asset-manifest.json`). No baked text, numbers, logos or faces in the generated layer.

- **Personal banner:** "1584x396 background, [brand] palette, abstract/professional texture, intentional empty negative space across the LOWER-LEFT quadrant and far-left third, focal interest centre-right, no text/logos/faces, no purple-blue-cyan gradient." Then overlay name + value proposition centre-right, above the midline, as real text.
- **Carousel:** "1080x1080 (or 1080x1350) consistent template, [brand] palette, generous white space, 80 px safe margin, no text." Then overlay hook/body/CTA + page number as real text.
- **Infographic:** "1080x1350 scaffold, clean grid, 3-4 colours, space for one chart + 3-5 labelled points, 50 px padding, no baked numbers." Then overlay verified data and render the chart as SVG.

Mandatory negatives on every brief: no centred-stacked AI hero, no default indigo/purple accents, no two-stop purple/blue/cyan gradient, no emoji icons, no rounded card with coloured left-border, no AI-stock look (team-round-a-laptop, floating 3D blobs, plastic skin).

### 7. Build, distinctive move, and export at 2x
1. Lay out the asset as HTML/SVG (real text layer) over the generated background. Author colour/size from the shared token layer in rem; no raw hex/px outside the token layer.
2. Land the ONE ownable, distinctive move (DESIGN-OS §9): a motif from the logo geometry, an opinionated type decision, intentional asymmetry, an editorial primitive. If an outsider could not tell which brand a slide belongs to, it is a template — rework it. Document the move in one sentence in the brief.
3. If the asset uses any motion (animated preview, GIF), animate only `transform`/`opacity`, no bounce/spring, and provide a `prefers-reduced-motion` no-motion path.
4. Render at 2x, then downscale. Export per type:
   - Carousel/document post -> font-embedded PDF, 8-12 slides, <3 MB. Never a JPG/PNG sequence.
   - Single image/infographic -> PNG for text/infographics, JPG for photos, within the locked ratio.
   - Banners/covers -> JPG/PNG within the file-size cap, critical content inside the safe rectangle.

### 8. QA gate (deterministic gate of record + cross-family critique)
Run the deterministic gate — it is the source of record; no asset ships on an LLM's say-so. Both gates run the shared `qa_antislop` scanner on the rendered DOM and exit non-zero on any P0 finding or console error.

```bash
# Carousels / document posts / single infographics that export to PDF:
python3 factory/scripts/qa_bip_export.py \
  --html clients/<client>/04-production/<asset>/index.html \
  --source-truth clients/<client>/02-source-truth \
  --out clients/<client>/05-qa

# Banners, covers, single image posts, OG/event art rendered as a web surface:
python3 factory/scripts/qa_landing_export.py \
  --html clients/<client>/04-production/<asset>/index.html \
  --source-truth clients/<client>/02-source-truth \
  --out clients/<client>/05-qa
```

Then run the advisory cross-family vision critique (step 5) and resolve every P0 with cited evidence. The gate is authoritative; the critique is advisory.

## Quality bar
Client-ready only when ALL of the following hold:

- **Specs and safe zones correct** for the asset type (exact dimensions, file-size cap, locked carousel ratio identical on every slide). Banner/cover keeps the lower-left avatar/logo zone clear; carousel kept inside the safe margins; nothing taller than 4:5 for single images.
- **Legibility floor met:** body >=24 pt, headings >=48 pt; <=6-8 lines / <=60 words per slide; contrast >=4.5:1; <=3-4 colours; one idea per slide.
- **Carousel structure present:** hook (real claim or real stat) + swipe cue on slide 1; persistent progress cue and identical grid/fonts/colours on body slides; takeaway + one action + brand mark on the last slide.
- **The 7 anti-slop sins absent:** no default indigo/purple accents; no two-stop purple/blue/cyan gradient; no emoji feature icons; no wrong/generic display font; no rounded coloured-left-border cards; no invented metrics; no filler/lorem copy.
- **Honesty held:** every stat traceable to `client-facts.json`; nothing invented; Australian English, no contractions, no dash punctuation, no banned words.
- **Real text stays real:** all headlines/stats/logos/CTAs/page numbers/chart numerals are live HTML/SVG, not baked into the image. Chart numerals come from verified data.
- **Distinctive move present and survived to the final export** (the soul test), documented in one sentence.
- **Deterministic gate passes** (`qa_bip_export.py` for PDF assets, `qa_landing_export.py` for web-surface assets): `anti-slop-report.md` P0 = 0, no console errors. Advisory cross-family critique has no unaddressed P0, each finding evidence-cited.
- **Export correct:** carousel is a font-embedded PDF <3 MB (never a JPG/PNG sequence); other assets in the right format and ratio; rendered at 2x then downscaled.
- **Inspected at mobile and desktop** (the asset is designed for the thumb, not the desktop), including the avatar/logo overlap on banners.
- **Licensing logged:** every delivered asset in `asset-manifest.json` with `approved-for-client: true`; prototype was on free assets, delivery on licensed.
- **Named human sign-off set** before the client sees anything. The bar is not "AI made it" — it is "a discerning client would pay for it."
