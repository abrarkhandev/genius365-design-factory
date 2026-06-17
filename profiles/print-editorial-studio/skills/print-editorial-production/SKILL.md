---
name: print-editorial-production
description: Use when creating or improving a catalogue, magazine, long-form article, report, or blog/print layout delivered as a PDF (with optional design elements for a client mock-up).
version: 1.0.0
created_by: agent
---

# Print and Editorial Production SOP

## Trigger
Use this skill whenever the task is to create, improve, critique, or plan an editorial print artifact: a catalogue, magazine or issue, long-form article or feature, annual/research report, white paper, brochure, or a blog post laid out for print. The unit is the page, the grid is law, and every output is an 80% draft finished with editorial taste. No InDesign: the build path is HTML/CSS to a PDF via Playwright/Chromium, or via paged.js / pagedjs-cli when the document needs running headers, page numbers, a TOC, recto/verso, or crop marks.

## Core rule
A spread is a composition, not a scrolling web page rescaled to a page size. Design the page as a complete unit, hold the grid and baseline rhythm across every page, and vary density across spreads. Monotony is the tell of a template.

## Required workflow

### 0. Inherit the constitution and read the client brief
Before producing anything:
- Read the per-client `clients/<client>/02-source-truth/DESIGN.md` (brand, fonts + licence + URL, tokens, the distinctive 20% move). It overrides defaults on brand only, never on the non-negotiables or honesty.
- Inherit `souls/DESIGN-OS.md` (the constitution). It is the floor: facts before layout, never invent proof, real text stays real, reference never copy, prototype free deliver licensed, accessibility required, the deterministic gate is the source of record.
- Confirm these source-truth files exist (create or update if missing):

```text
clients/<client>/02-source-truth/client-facts.json
clients/<client>/02-source-truth/DESIGN.md
clients/<client>/02-source-truth/system-spec.md   # required for reference/clone-inspired work
clients/<client>/02-source-truth/assumptions.md    # all missing proof logged here
```

### 1. Model routing
Route by stage. Draft and iterate cheaply, deliver client-grade, critique on a different model family than the builder.

- **Draft / iterate (content + layout HTML/CSS):** MiniMax M3 — free, via OpenRouter. Keep it source-truth constrained because a free model will otherwise suggest invented metrics, logos, or proof.
- **Deliver (client-grade build):** Claude Sonnet 4.6 (default) or Opus 4.8 for the hardest layouts:

```bash
-m anthropic/claude-sonnet-4.6 --provider openrouter
-m anthropic/claude-opus-4.8 --provider openrouter
```

- **Critique / QA (long-form structure, baseline rhythm, anti-slop):** a DIFFERENT family than the builder (for example GLM-5.1 or Qwen). Advisory only, evidence-cited; it never passes a deliverable on its own say-so.
- **Reference reading (multimodal):** a multimodal model (MiniMax M3 / Qwen 3.5 / Gemini 3 Flash) to read reference spreads, covers, and competitor PDFs.

### 2. Intake and source-truth
Classify the input and extract source-truth before any layout:
- **Mode A:** assets folder + transcript/DOCX/PDF/brief (the manuscript or copy deck).
- **Mode B:** existing website or article URL to set into print.
- **Mode C:** existing PDF/issue to improve or re-template.
- **Mode D:** mixed materials.

Pull the editorial source-truth: the manuscript/body copy, headline and standfirst candidates, byline and credits, real figures and their captions, pull-quote candidates (drawn only from real body text), the imagery brief, and brand notes. Never invent proof; log every gap to `assumptions.md`.

### 3. Page setup (decide up front)
- **Page size:** A4 for AU/UK/EU, US Letter for US. Pick one and design to it; never design a scrolling river rescaled between sizes.
- **Premium long-form margins (the golden canon):** margins roughly 1/9 and 2/9 of the page, with inner:top:outer:bottom = **2:3:4:6** (bottom largest, inner smallest). This alone makes a page look designed.
- **Orientation and binding:** decide portrait/landscape and whether the document is recto/verso (mirrored margins) before building.

### 4. Grid and baseline rhythm
- Define a Müller-Brockmann grid sized to communicative need (**8-32 fields**) and a **baseline grid**. Every margin, padding, and gutter is a multiple of one base unit.
- Emulate the baseline grid in CSS: set `line-height` as a multiple of a base rem and apply a `cap`-unit shift, since browsers ignore the font baseline.
- **Measure: 45-75 characters, target 66** (`max-width: 66ch`). Body type must be at least 12 pt in the PDF; author sizes in rem, editorial ratio 1.5/1.618.

### 5. Editorial component anatomy
Build every spread from named roles, not freeform blocks:
- masthead/kicker, headline, standfirst/intro, byline, body, subheads, pull quotes, captions, credits, folios (page numbers), running heads.
- **Pull quotes** quote real body text only (never invented copy), set large as a graphic element to break text-heavy pages.
- **Every figure gets a caption** in one consistent system (same size, weight, and position throughout).
- **Covers:** focal point in the upper half; masthead/title fixed in typeface and position (vary only the colour theme and hero image per issue); 2-3 fonts, 2-3 colours, one accent.

### 6. Pacing and the distinctive move
- **Pace the document:** vary density across spreads — full-bleed statement, then 2-column text, then an image spread, then a pull-quote page. Do not repeat one spread template.
- Carry ONE signature, ownable editorial move from `DESIGN.md` (a giant-numeral system, an opinionated serif/mono pairing, intentional asymmetry, marginalia, a custom motif from the logo geometry). HTML/CSS/SVG-feasible, no licensed imagery, no invented proof. Verify it survives to the final PDF.

### 7. Typography and colour (constitution, applied)
- Authored hierarchy from size + weight + colour, not size alone; three text colours max.
- ALL-CAPS labels track at least 0.06em; use curly quotes, a real ellipsis, and `tabular-nums` for figures.
- One dominant brand colour plus neutrals; accent at most 2 uses per screen/spread; pair one distinctive display face with one refined body (serif brand to serif display; avoid Inter/Roboto/Arial/Geist/Space Grotesk as the signature face).
- Derive the primary hue from the client's brand; never default to indigo/violet/blue. WCAG 2.2 AA contrast minimum (body at least 4.5:1).

### 8. HTML/CSS to PDF mechanics
Decision rule: simple decks or short docs with plain page numbers can use Chromium `page.pdf()`. Anything with running heads, "Page X of Y", a TOC with real page numbers, recto/verso, or crop marks must use paged.js / pagedjs-cli, because Chromium ignores CSS margin boxes and Playwright's footer template is buggy.

```css
@page { size: A4; margin: 20mm 18mm; }
@page :first { margin-top: 60mm; }
@page :left { margin-left: 24mm; }  @page :right { margin-right: 24mm; }
h1 { string-set: doctitle content(text); }
@page { @top-left { content: string(doctitle); } @bottom-right { content: "Page " counter(page) " of " counter(pages); } }
h2, figure, table, .pull-quote { break-inside: avoid; } h2 { break-after: avoid; }
section { break-before: page; } p { orphans: 3; widows: 3; }
```

### 9. Images and text
- One imagery language per document. Real text (headlines, titles, page numbers, body, captions) stays HTML/SVG, which also satisfies screen readers. Never bake a headline, title, or page number into a generated image (at most a 1-4 word decorative label).
- Imagery flows through `image-prompter` to `image-asset-lab`: prototype on free assets, deliver on a commercially licensed source with cost approval. No placeholder CDNs in delivery.

### 10. Honesty and copy (non-negotiable)
- **Australian English**, no US spellings, **no contractions**, no em/en dash punctuation in final body copy (restructure instead).
- No filler / lorem / placeholder copy in anything screenshot-able or delivered.
- Apply the banned-word list (revolutionary, game-changing, streamline, seamless, leverage, cutting-edge, world-class, delve, tapestry, testament, boasts, and the rest). Copy describes what the thing literally does.

### 11. Motion (only if a screen/interactive companion is produced)
If a screen companion or scroll preview ships alongside the PDF: animate only `transform`/`opacity`, ship 2-3 intentional motions, no bounce/spring, respect `prefers-reduced-motion` (provide the no-motion path), and give any reveal-on-scroll an in-viewport-on-load reveal plus a 2.5s timeout fallback so headless screenshots do not render blank. The PDF itself is static.

### 12. Commercial print (only if going to a real printer)
Author CMYK; rich black `C60 M40 Y40 K100` for large solids, **K100 only** for fine text and thin strokes; total ink under 300% (coated) / 260% (uncoated); export **PDF/X-1a**. For screen or office printing of our HTML PDFs, sRGB RGB is fine.

### 13. Build and export
Produce:
- source files (HTML/CSS, and the paged.js config if used)
- the exported PDF with fonts embedded and real, selectable text layers (self-host/embed fonts for print)
- a print-preview render at A4/Letter and a spread/mobile-equivalent inspection render
- the QA report and `assumptions.md` (missing proof)

## Quality bar
Client-ready only when ALL of the following hold.

Profile checklist:
- Consistent grid and baseline rhythm across every page; canon margins (2:3:4:6) applied.
- 66ch measure held; body at least 12 pt in the PDF.
- A caption on every figure, in one consistent system.
- Running heads and folios correct, including recto/verso where used; TOC page numbers real.
- Pull quotes quote real body text only; no invented metrics, proof, or logos.
- Density varies across spreads (no repeated template); the distinctive 20% move survived to the final PDF.
- Zero spelling errors in display type; the 7 anti-slop sins absent.
- Australian English, no contractions, no em/en dashes, no banned words, no filler copy.
- PDF exports clean: fonts embedded, real text layers, sRGB (or PDF/X-1a CMYK for a real printer).
- `asset-manifest.json` shows every delivered asset `approved-for-client: true`.

Deterministic QA gate (gate of record):
- Run the export QA gate before sign-off. The PDF/export gate is the source of record; an LLM critique is advisory and must cite evidence.

```bash
python3 factory/scripts/qa_bip_export.py clients/<client>/06-deliverables/<artifact>.pdf
# (use qa_landing_export.py instead only if delivering a screen/landing companion alongside the PDF)
```

Pass conditions:
- The deterministic export gate passes (`anti-slop-report.md` P0 = 0).
- Cross-family advisory critique has no unaddressed P0, each finding evidence-cited.
- Rubric at least 21/24 for client-ready (18/24 acceptable), no 0 in a critical category (grid/baseline rhythm, caption system, proof honesty, export quality).
- Print preview inspected at the chosen page size, plus a spread/mobile-equivalent render.

Final step:
- A **named human sign-off** is set in the deliverable record before the client sees anything. The bar is not "AI made it" — it is "a discerning client would pay for it."
