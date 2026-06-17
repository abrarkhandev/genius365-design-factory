---
name: email-newsletter-production
description: Use when creating, improving, critiquing, or planning an email newsletter or marketing email that must render in real inboxes (Outlook, Gmail, Apple Mail, dark mode) and as a matching PDF.
version: 1.0.0
created_by: agent
---

# Email Newsletter Production SOP

## Trigger
Use this skill whenever the task is to build, improve, critique, or plan an HTML email or newsletter that will be sent through a CRM/ESP, or its print/PDF counterpart. This covers campaign sends, recurring newsletters, announcements, and onboarding/lifecycle emails.

## Core rule
**Email is not web.** Inbox rendering is roughly ten years behind the browser. The factory's landing-page reflexes (flexbox, CSS grid, modern Tailwind, GSAP/Framer, WebP, freely-loaded web fonts) are mostly forbidden in the inbox. Code defensively for the lowest common denominator: the Microsoft Word engine inside Outlook for Windows. You maintain **one content source** and produce **two builds**: bulletproof inbox HTML, and a richer PDF rendered through Chromium.

## Required workflow

### 0. Inherit the constitution and the client brand
Before producing anything, read in this order:
1. `souls/DESIGN-OS.md` (the constitution; the floor, never overridden on non-negotiables or honesty).
2. This profile's `SOUL.md` (email domain craft).
3. The per-client `clients/<client>/02-source-truth/DESIGN.md` (brand tokens, fonts + licences, voice). Client instruction wins on brand only, never on §1 non-negotiables or §2 honesty.

Confirm these source-truth files exist (create/extract if missing):

```text
clients/<client>/02-source-truth/client-facts.json
clients/<client>/02-source-truth/DESIGN.md
clients/<client>/02-source-truth/assumptions.md   # where any missing proof is parked
```

Never re-extract or hard-code hex; read brand from the shared token layer (`dist/tokens.css`, semantic tier). Confirm fonts have a provable licence (Fontshare FFL / Google OFL-Apache) recorded in `DESIGN.md`; remember Outlook ignores web fonts anyway, so every stack ends in a web-safe fallback.

### 1. Model routing (draft free, deliver client-grade, critique on a different family)
- **Draft / iterate** content and MJML/HTML on **MiniMax M3** (free, OpenRouter). Keep it source-truth constrained because it will otherwise invent metrics, logos, and proof.
- **Deliver client-grade** on **Claude Sonnet 4.6** (or Opus 4.8 for the hardest layout/copy), invoked explicitly:

```bash
# client-grade build / final copy pass
-m anthropic/claude-sonnet-4.6 --provider openrouter
-m anthropic/claude-opus-4.8  --provider openrouter   # hardest layout or sensitive copy
```

- **Critique / anti-slop / QA** on a **different model family than the builder** (e.g. GLM-5.1 or Qwen). The LLM critique is advisory and must cite evidence; it never signs off a deliverable.
- Hero/section imagery flows through `image-prompter` -> `image-asset-lab`. Prototype on free assets; deliver only on licensed assets logged in `asset-manifest.json` with `approved-for-client: true`.

### 2. Intake and source-truth
Establish the content before any layout (facts before layout):
- audience and the single send context (who, why now)
- newsletter purpose / campaign goal
- one primary CTA and its destination URL
- sections/stories to include (and their priority order)
- proof points (real only) and brand voice notes
- sender identity, physical mailing address, and unsubscribe URL (mandatory for anti-spam compliance)
- target CRM/ESP (this dictates the paste/test path in step 8)

If proof, metrics, names, or logos are not in source-truth, they do not appear; park gaps in `assumptions.md`.

### 3. Content strategy and module plan
Define before building:
- **Preheader** (the hidden first body element, ~40-100 chars; the inbox-preview hook).
- **Module sequence** (single column only): header/logo -> hero -> story block(s) -> divider -> secondary blocks -> footer (unsubscribe + physical address).
- One **primary CTA** placed within the first ~300 px (above the fold). Secondary CTAs are subordinate.
- Voice per `DESIGN.md`: clear, scannable, warm-but-professional, written for a distracted reader in a crowded inbox.

### 4. Reference pass and the distinctive move
Gather 3-6 relevant references (newsletters in the same category, editorial layouts). Record what works and what to avoid. Then commit ONE ownable, table/inline-CSS-feasible signature move (a masthead motif from the logo geometry, an opinionated numeral or type pairing, an editorial divider system) and write it in one sentence. Verify it survives to the final render. Do not clone proprietary layouts.

### 5. Build the inbox HTML (the bulletproof skeleton)
Default build engine is **MJML** (`mj-section`/`mj-column`/`mj-text`/`mj-button`); it compiles to inlined, Outlook-safe, table-based HTML. Use **Maizzle** only when Tailwind parity is needed. **caniemail.com is a mandatory lookup before using any CSS feature.** Non-negotiable skeleton:

- `<!DOCTYPE html>`; `<html lang="en-AU" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">`.
- Layout = nested `<table role="presentation" cellpadding="0" cellspacing="0" border="0">`, never divs. Container **max-width 600px** (700 breaks on mobile). **Single column only.**
- **All critical CSS inline** ("inline for survival, internal for enhancement, external for nothing"). Embedded `<style>` only for progressive enhancement (media queries, dark mode). Longhand properties only; **no shorthand, no `position`/`float`/flexbox/grid.** Use `align`/`valign` attributes and explicit `width` on tables/cells; spacing via cells / `cellpadding` / spacer rows, never CSS `margin`.
- Hidden **preheader** as the first body element.
- **File size <100 KB** (Gmail clips ~102 KB); minify before delivery.

**Outlook (Word engine) survival kit:**
- MSO conditional comments `<!--[if mso]>...<![endif]-->` for ghost tables (fixed `width="600"` wrappers, since Outlook ignores `max-width`), Outlook-only spacing, and VML.
- End every font stack with a web-safe fallback (Arial, Georgia, Tahoma, "Times New Roman"); add `mso-generic-font-family` / `mso-font-alt`.
- `mso-line-height-rule:exactly;` to stop extra leading. A GIF shows only frame 1 in Outlook, so frame 1 must stand alone.

**Bulletproof buttons (never an image button):** real HTML text on a single-cell table; `background-color` + `border-radius` + padding on the `<td>`; link styles + `display:inline-block` + padding on the `<a>`. Outlook fallback = VML `<v:roundrect>` inside an `[if mso]` block using `rgb()` fill (so dark mode does not re-invert it). Tap target 42-72 px high; contrast >=4.5:1; meaningful label, never "Click here".

### 6. Type, images, and dark mode
- **Type:** body 14-16 px (14 px mobile floor), headings 20-24 px, line-height 1.4-1.6, short paragraphs, 20-30 px block padding. Three text colours max.
- **Images:** PNG/JPG only (**no WebP** — Outlook Windows has none). Retina = export 2x, constrain with `width`/`height` attributes; `display:block` to kill the gap bug; **mandatory descriptive `alt`** on every image (clients block images; the email must read fully with images off). Important text is **real HTML, never baked into an image** (at most a 1-4 word decorative label).
- **Dark mode:** add `<meta name="color-scheme" content="light dark">` + `supported-color-schemes`. Provide `@media (prefers-color-scheme: dark)` rules (Apple Mail) and `[data-ogsc]`/`[data-ogsb]` attribute rules (Outlook app). Protect transparent-PNG logos with a faint light halo, or ship a mid-tone logo that clears 4.5:1 on both white and black. Give Gmail an explicit `#ffffff` background.

### 7. Build the PDF variant
From the same content source, render HTML/CSS -> Chromium `page.pdf()` (Playwright). Here web fonts (self-hosted/embedded) and richer CSS are allowed because Chromium renders it.
- `@page { size: A4; margin: 20mm 15mm; }` (or Letter).
- `break-inside: avoid;` on story blocks; `break-before: page;` for sections.
- `printBackground: true`.

### 8. CRM delivery reality and the seed test (do not skip)
CRMs strip `<head>`/`<style>`/classes on paste, so the base table layout must work with **zero embedded styles** (media-query and dark-mode rules are enhancement only). Run the CSS inliner (htmlemail.io/inline) before pasting. **Never paste from Word/Docs/Notion.**

This is an SOP step, not an assumption:
1. Paste the fully-inlined HTML into the **actual target CRM/ESP**.
2. Send a **real seed test** to your seed inbox set.
3. Confirm it renders in Outlook (Windows), Gmail, Apple Mail, and at least one dark-mode client before sign-off.

### 9. Quality gate, rubric, and handoff
Run the deterministic gate, then the advisory critique (different family), then human sign-off (see Quality bar). Deliver:
- final inbox HTML (fully inlined) and the PDF
- editable MJML/source + content source-truth files
- `asset-manifest.json` (all `approved-for-client: true`) and screenshots
- QA report / rubric score, seed-test confirmation, and `assumptions.md` (missing proof noted)

## Quality bar

Client-ready only when ALL of the following hold.

**Non-negotiables (constitution §1-§2, never violated):**
- Real text in HTML (never baked into images); decorative image labels 1-4 words max.
- No invented metrics, percentages, dollar figures, client names, logos, testimonials, awards, or certifications; missing proof lives in `assumptions.md`.
- **Australian English; no US spellings; no contractions; no em/en dash punctuation** in final copy (restructure instead). No filler/lorem. Banned-word list respected (revolutionary, streamline, seamless, leverage, elevate, cutting-edge, world-class, all-in-one, "in today's fast-paced world", delve, tapestry, testament, boasts, etc.).
- `prefers-reduced-motion` respected (animated GIFs degrade to a standalone frame 1).
- Reference, never copy: no reproduced proprietary layout.
- Prototype on free assets; deliver only on licensed assets logged in `asset-manifest.json`.

**Email-specific checklist (the soul's concrete bar):**
- Renders correctly across Outlook (Windows) / Gmail / Apple Mail + at least one dark-mode client, seed-test or render-farm verified.
- File size **<100 KB**, minified.
- **Single primary CTA above the fold** (within ~300 px), bulletproof (HTML text + VML fallback), tap target 42-72 px, meaningful label.
- Preheader set as the first hidden body element.
- Descriptive `alt` on every image; the email reads fully with images off.
- Contrast **>=4.5:1** (body), >=3:1 (large/bold and UI), verified deterministically.
- Container max-width 600px, single column, table-based, fully inlined; base layout survives with zero embedded styles.
- The 7 anti-slop sins absent (default indigo/purple, AI two-stop gradient, emoji feature icons, wrong display font, coloured-left-border card, invented metrics, filler copy).
- The one distinctive signature move is present and ownable.

**Deterministic gate (the gate of record):** run the export QA on the PDF build (the email's print counterpart) before delivery:

```bash
python3 factory/scripts/qa_bip_export.py clients/<client>/06-deliverables/email/<name>.pdf
# (use factory/scripts/qa_landing_export.py if a web-hosted version of the email is also produced)
```

The deterministic gate is the source of record (`anti-slop-report.md` P0 = 0). An LLM critique is advisory only and must cite evidence. No deliverable passes on an LLM's say-so.

**Optional QA rubric (score each 0-2; mirrors the constitution's ">=21/24 client-ready, >=18/24 acceptable"):**
1. Inbox render fidelity (Outlook/Gmail/Apple Mail)
2. Dark-mode integrity
3. Above-the-fold promise and preheader
4. CTA clarity and bulletproofing
5. Proof placement (real proof only)
6. Visual hierarchy and scannability
7. Type/spacing for mobile (14 px floor)
8. Accessibility (alt text, contrast, semantic order)
9. File size / deliverability (<100 KB, inlined)
10. Brand fit (tokens, voice, distinctive move)
11. PDF variant quality (page breaks, fonts)
12. Handoff completeness (source, manifest, seed-test proof)

Any 0 in inbox render fidelity, CTA clarity, accessibility, or deliverability requires revision.

**Human sign-off:** a named human must approve after the seed test and the deterministic gate pass. Record the approver before delivery. Never ship an email you have not seen render in Outlook.
