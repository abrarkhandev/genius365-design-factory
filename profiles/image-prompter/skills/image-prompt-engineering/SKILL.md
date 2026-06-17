---
name: image-prompt-engineering
description: Use when a deliverable needs a generated image, illustration, icon, or background and you must choose the right model and write the optimal, brand-obedient prompt for a single slot.
version: 1.0.0
created_by: agent
---

# Image Prompt Engineering SOP

## Trigger
Use this skill whenever a stream profile (landing page, BIP, LinkedIn, email, print) hands you a single slot brief for a generated visual: a hero background, a section illustration, a personal-banner background, a feature icon set, a product mockup, a typographic poster, or a recurring brand character. You write the prompt package and route the model. You do NOT run the model (that is `image-asset-lab`) and you do NOT build the deliverable (that is the stream profile).

## Core rule
You are the art director and prompt engineer, not the renderer or the layout author. Your output is a reproducible prompt package plus a manifest caption. The one rule above all others: important text — headlines, body, CTAs, prices, metrics, logos, legal — stays as real HTML/SVG in the deliverable. Image-baked text is for short decorative labels only (1 to 4 words). Never bake a metric, claim, or logo into a raster.

## Required workflow

### 0. Inherit the constitution and read the per-client brand
Before writing a single prompt:

- Read the per-client `DESIGN.md` for this client (brand tokens, mood, style, font + licence, primary hue derived from the logo). It overrides defaults on brand.
- Inherit `DESIGN-OS.md` (the constitution) — it is the floor, not the ceiling. Client instruction wins on brand, never on the non-negotiables (§1) or honesty (§2).

```text
clients/<client>/02-source-truth/DESIGN.md          # brand tokens, mood, font + licence, primary hue
clients/<client>/02-source-truth/client-facts.json  # source-truth — the only place real proof exists
souls/DESIGN-OS.md                                   # inherited constitution
```

Never re-extract or hard-code hex. Reference the semantic token layer from `DESIGN.md` (`color.brand.primary`, `color.text.muted`); feed the literal hex into a prompt only where the model supports hex control (see step 3).

### 1. Intake the slot brief
For each slot, pin down before routing:

- **Host artifact and channel** (web hero / BIP section / LinkedIn banner / email header / print plate) — sets aspect ratio, resolution, and crispness needs.
- **Role of the asset:** background, supporting illustration, feature icon, product mockup, typographic poster, or recurring character.
- **Is it overlay-heavy?** (banner, carousel, infographic). If yes, you generate background/illustration ONLY, with intentional negative space where text will overlay. The stream profile lays headlines, stats, and logos as real HTML/SVG.
- **Prototype or client delivery?** Prototype slots route to free models. Client-delivery slots route to licensed models and are flagged for cost approval.
- **Any real proof needed in the frame?** If the brief implies a metric, logo, testimonial, or client name baked into the image — stop. It does not go in the raster; it goes to the stream profile as real text, and any missing proof goes to `assumptions.md`.

### 2. Reference and brand strategy
- Pull brand tokens straight from `DESIGN.md`: derive the primary hue from the client logo, never default to indigo/violet/blue.
- For a set or a recurring subject, decide the consistency mechanism up front: a Midjourney `--sref` or Ideogram style code for campaign style; a role-assigned style-reference image with high reference weight for a recurring character; repeat exact identifying details every prompt.
- Triangulate references from different domains for the distinctive move (the soul test, §9): e.g. botanical plates × Swiss editorial × data-density. Anchor to one aesthetic family and stay disciplined.
- Always plan a seed where the model supports it, so QA can regenerate after a tweak.

### 3. Choose the image model (the decision rule)
Route by the dominant requirement of the slot:

- **Accurate multi-line text / typographic poster** → **Ideogram 3/4** (or Nano Banana Pro). Keep each string ≤6 words, each in its own non-overlapping zone; describe type visually (no font-family names in Ideogram); palette as uppercase hex.
- **Brand-accurate hero / mockup / infographic / needs grounding or many refs** → **Nano Banana Pro** (Gemini 3 Pro Image). Up to 14 role-assigned refs; you may quote text and name fonts; state aspect ratio in-prompt.
- **Photoreal product/lifestyle, hex-exact brand colour, JSON templating** → **FLUX 2**: `[dev]` to prototype, `[pro]`/`[max]` to deliver, `[flex]` for any text. No negative prompts — reframe to positive states ("sharp focus throughout", never "no blur"). Hex control: `an apple in color #0047AB` (colour name + code + bound object; ≤3 to 5 colours). Name camera/lens/film for realism. Set a seed for QA reproducibility.
- **Vector icons / scalable brand illustration / locked palette / SVG** → **Recraft V3** (the sanctioned replacement for emoji feature icons; upload brand refs to lock the palette).
- **Distinctive art-directed atmosphere / recurring character** → **Midjourney v7** (manual, no API — top-tier brand work, weakest at text). `--sref` for campaign style, `--oref --ow 600–1000` to hold a subject.
- **Fast multi-ref blend / non-Latin text** → **Seedream 4.5**.

Then bind the licence class: prototype slots → free models; client-delivery slots → licensed models. The licence is set by the model maker, not by you. Flag client-delivery cost for approval.

### 4. Write the prompt (universal anatomy)
Lead with the subject; write descriptive prose, not keyword soup; front-load the most important element (models attend to first tokens). Skeleton:

`[Subject] + [Action/Pose] + [Style/Medium] + [Context/Setting] + [Lighting] + [Camera/Lens/Technical] + ["quoted text" if any] + [aspect ratio]`

- **Lighting has the single greatest impact on quality — always specify it.**
- Target 30 to 80 words. Use 10 to 30 words to explore; 80+ only for complex scenes.
- Feed brand tokens per model: FLUX hex-in-prompt, Recraft locked palette from refs, Ideogram uppercase-hex palette, Nano Banana role-assigned refs.
- For overlay-heavy slots, describe the composition with deliberate empty negative space where the headline/stat/logo will sit; render no real copy in the frame.

### 5. Anti-slop pass (design the banned sins around the image)
Before finalising the prompt, engineer the cardinal sins OUT of the frame, never into it (DESIGN-OS §3):

- No default indigo/purple accents; no two-stop purple/blue/cyan "AI gradient"; no cyan accent text on dark.
- No emoji as feature icons — use Recraft vector icons.
- Correct brand display font for any short overlay label (and only where the model can name fonts).
- Add one authentic imperfection (visible skin pores, slight asymmetry, real wear).
- Replace "cinematic / 8k / hyperdetailed" with real optics: "Sony A7IV, 50mm f/1.8, soft window light from the left." Lower guidance/stylize for realism.
- Avoid the AI-stock look: team-round-a-laptop, floating 3D blobs, plastic skin, off hands.

### 6. Honesty and copy gate (any short label in-frame)
Any 1 to 4 word decorative label baked into the image must obey DESIGN-OS §2:

- **Australian English; no US spellings; no contractions; no em/en dash punctuation.**
- No filler, lorem, or placeholder copy in anything screenshot-able or delivered.
- No banned words (revolutionary, game-changing, streamline, empower, supercharge, seamless, unlock, elevate, leverage, cutting-edge, world-class, enterprise-grade, best-in-class, all-in-one, delve, tapestry, testament, boasts, and the rest of the §2 list).
- Never invent a metric, claim, logo, or client name in the frame.

### 7. Assemble the prompt package and manifest caption
Output, per slot:

```json
{
  "model": "<flux-pro | nano-banana-pro | ideogram-4 | recraft-v3 | midjourney-v7 | seedream-4.5>",
  "prompt": "<prose prompt, 30-80 words>",
  "negatives": "<only if the model supports them; FLUX gets none>",
  "aspect_ratio": "<e.g. 16:9, 4:5, 1:1>",
  "resolution": "<2x target where the channel needs crispness, then downscale>",
  "reference_images": [{ "path": "...", "role": "style | subject | palette" }],
  "seed": <int where supported>,
  "expected_cost": "$<per image, plain dollars>",
  "licence_class": "free-prototype | licensed-delivery"
}
```

Plus a one-line caption for `asset-manifest.json` recording model + prompt for reproducibility. State cost in plain $/image. Resolution rule: output at 2x then downscale where the channel needs crispness.

### 8. Handoff to image-asset-lab and the stream profile
- Hand the prompt package to `image-asset-lab` to render (prototype on free assets, deliver on licensed).
- Tell the stream profile explicitly: which strings stay as real HTML/SVG, where the negative space sits, and which model + seed produced the asset.
- Every delivered asset is logged in `asset-manifest.json` with `approved-for-client: true`; record the licence class. Prototype renders may use free assets; final delivery must be on a licensed source with cost approved.

## Quality bar

Before a generated asset is cleared for delivery, verify the checklist:

1. **Brand fit** — primary hue derived from the logo; no default indigo/violet/blue; brand tokens fed per model.
2. **Text policy** — no headline/body/CTA/metric/logo/legal baked into the raster; at most a 1 to 4 word decorative label.
3. **Anti-slop** — none of the 7 cardinal sins present; no AI-stock look; one authentic imperfection; real optics over "cinematic/8k".
4. **Copy honesty** — any in-frame label is Australian English, no contractions, no dashes, no banned words, no invented proof.
5. **Distinctive move** — the asset carries or supports the deliverable's one ownable signature; an outsider could tell whose brand it is.
6. **Reproducibility** — seed set where supported; model + prompt captioned in `asset-manifest.json`.
7. **Composition** — for overlay slots, intentional negative space where text will overlay; aspect ratio and resolution match the channel; 2x then downscaled where crispness is needed.
8. **Licence** — prototype on free; delivery on a licensed source with cost approval; `approved-for-client: true` set.

### Critique on a different model family
Run the craft/anti-slop critique on a DIFFERENT model family than the one that drafted the prompt, so the reviewer does not rubber-stamp its own grammar. Iterate prompt drafts on **MiniMax M3** (free, OpenRouter); take the package to client-grade on **Claude Sonnet 4.6 / Opus 4.8** (`-m anthropic/claude-sonnet-4.6` or `-m anthropic/claude-opus-4.8 --provider openrouter`); critique on the opposing family. An LLM critique is advisory only and must cite evidence.

### Deterministic gate of record
The image-prompter ships an asset INTO a host deliverable; the deterministic gate runs on that rendered host, not on the raw image. When the asset lands in a page or BIP, the host must pass its gate with the asset embedded:

```bash
# Landing page / web host
python3 factory/scripts/qa_landing_export.py --client <client>
# Business Information Pack host
python3 factory/scripts/qa_bip_export.py --client <client>
```

The gate renders the deliverable, runs the shared anti-slop scanner on the rendered DOM, and exits non-zero on any P0 finding or console error. An asset that reintroduces a cardinal sin (an AI gradient bleeding into the hero, a baked metric, an emoji icon) fails the host gate and must be reprompted. The gate is the source of record; the LLM critique never overrides it.

### Human sign-off
No generated asset is delivered to a client until: the checklist passes, the host deterministic gate is green with the asset embedded, the cross-family critique has no unaddressed P0, the licence is cleared with cost approved, and a named human sign-off is set on the `asset-manifest.json` entry. The bar is not "AI made it" — it is "a discerning client would pay for it."
