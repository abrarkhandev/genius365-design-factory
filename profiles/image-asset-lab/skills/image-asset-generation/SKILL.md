---
name: image-asset-generation
description: Use when a prompt package from image-prompter must be executed into a finished image, vector, or short motion asset with full provenance for a Hermes deliverable.
version: 1.0.0
created_by: agent
---

# Image Asset Generation SOP

## Trigger
Use this skill whenever you receive a prompt package from `image-prompter` and must execute it: generate the asset, iterate on it, and return it with full provenance. You execute prompts; you do not write them (that is `image-prompter`) and you do not build deliverables (that is the stream profiles). If no prompt package exists, stop and route back to `image-prompter`.

## Core rule
The licence on an output is set by the model maker, not by who wrote the prompt. Prototype on free, deliver on licensed. Real, load-bearing text (headlines, prices, labels, CTAs, logos) is never baked into a raster; it stays HTML/SVG in the deliverable. No asset reaches a client artifact unless it is licensed, on brand, and logged `approved_for_client: true`.

## Required workflow

### 0. Read the design contract before generating anything
Read in this order and do not generate until you have:
1. The per-client `clients/<client>/02-source-truth/DESIGN.md` (brand: hue derived from the logo, fonts and licences, the distinctive 20% move, the mandatory negative-constraint block).
2. The inherited constitution `souls/DESIGN-OS.md` (the floor: non-negotiables, anti-slop bans, imagery policy, the QA contract).
3. Your own `souls/image-asset-lab.SOUL.md` (the licence chain, the model menu, execution rules, the provenance schema).

Client instruction wins on brand, never on the non-negotiables (§1) or honesty (§2). If the prompt package contradicts any non-negotiable, do not ship it; send it back to `image-prompter` for a corrected prompt.

### 1. Intake the prompt package
The package from `image-prompter` MUST carry: `model` (intended target), `prompt`, `refs` (reference images for multi-ref or composite work), `aspect`, `seed`, and `licence_class`. Confirm all six fields are present and unambiguous. Then classify the job so you pick the right lane and model:
- **Photoreal hero / multi-ref brand / composite** (default).
- **Hex-exact brand colour / photoreal alt.**
- **Typography-heavy or non-Latin lettering.**
- **Readable decorative lettering, poster, thumbnail.**
- **Vector / SVG icon, logotype, flat illustration** (output native SVG, never a flattened PNG).
- **IP-indemnified / provenance-clean** (client demands a clean chain).
- **Short motion loop or hero accent** (video = short loops only, no load-bearing text in the clip).

Record the intended deliverable resolution. Generate at the lowest resolution that meets it; upscale only if needed.

### 2. Model routing (drafting brains vs delivery brains vs the image model)
Two separate routing decisions run in parallel: which language model reasons about the work, and which image model renders it.

Language-model routing for any planning, prompt-repair notes, self-critique, or manifest reasoning:
- **Draft and iterate** on MiniMax M3 (free, OpenRouter) while you are still resolving composition and cost:
  ```bash
  llm -m openrouter/minimax/minimax-m3 --provider openrouter "<draft reasoning prompt>"
  ```
- **Client-grade reasoning** (final provenance notes, disclosure wording, the asset-manifest write-up that ships) on Claude Sonnet 4.6 or Opus 4.8:
  ```bash
  llm -m anthropic/claude-sonnet-4.6 --provider openrouter "<delivery reasoning prompt>"
  llm -m anthropic/claude-opus-4.8 --provider openrouter "<delivery reasoning prompt>"
  ```
- **Critique / QA on a DIFFERENT model family than the builder.** If MiniMax M3 drafted the plan, run the anti-slop and brand-fit critique on Claude (or vice versa). Never let one model family both build and bless its own output.

Image-model routing (verified June 2026 — confirm price at point of use, in plain $/image or $/second, never tokens/credits):

| Use case | Model | ~Price | Licence note |
|---|---|---|---|
| Photoreal hero / multi-ref / composite (default) | Nano Banana Pro (`gemini-3-pro-image-preview`) | ~$0.13/2K, ~$0.24/4K | commercial OK; invisible SynthID on every image (disclose) |
| Photoreal alt / hex-exact brand colour | FLUX.2 [pro] | ~$0.03/img | [pro]/[flex] commercial OK; [dev] non-commercial without paid BFL self-host licence |
| Typography-heavy / non-Latin / cheap photoreal | Seedream 4.5 | provider-priced | commercial via provider — confirm terms |
| Readable decorative lettering / poster / thumbnail | Ideogram 3 | $0.03 turbo / $0.09 quality | paid plans grant commercial rights |
| Vector / SVG icons / logotype / flat illustration | Recraft V3 (SVG) | $0.04 raster / $0.08 vector | commercial on paid/Replicate; hand off SVG, not PNG |
| IP-indemnified / provenance-clean | Adobe Firefly | ~$0.02–0.10/img; API ~$1k/mo min | trained on licensed data; indemnified on paid plans |
| Open-source, commercial-clean, self-host | Qwen-Image (Apache 2.0) / FLUX schnell/klein | self-host | Apache — commercial-safe |
| Short motion loop / hero accent | Kling 3.0 (~$0.10/s) / Veo 3.1 Fast (~$0.15/s, audio) | per second | short loops only; no load-bearing text in clips |

Midjourney is excluded from automation (no official API) — manual-only, out of scope.

### 3. Prototype lane (free) — resolve composition first
Iterate composition, crop, and layout at near-zero cost on Cloudflare Workers AI (10,000 neurons/day free). The factory executor is `factory/scripts/image_gen_cloudflare.py`, which now defaults to **FLUX.2 [dev]** (`@cf/black-forest-labs/flux-2-dev`) — the current best free prototype model and a clear step up from schnell:
```bash
uv run --no-project python factory/scripts/image_gen_cloudflare.py \
  --prompt "<background / illustration only, no baked text>" \
  --out clients/<client>/04-production/<asset>/assets/<name>.jpg \
  --width 1280 --height 720 \
  [--reference clients/<client>/02-source-truth/<logo-or-swatch>.png]
```
FLUX.2 [dev] uses a multipart request (prompt/steps/width/height + an optional `--reference` image for on-brand consistency) and returns JPEG. Pass `--model @cf/black-forest-labs/flux-1-schnell` for the faster legacy 8-step lane (which also honours `--seed` for exact regeneration); SDXL-Lightning and Leonardo Lucid Origin remain available as alternates. Reuse the seed `image-prompter` supplied where the model supports it so QA can regenerate a near-identical frame. Generate many candidates, then curate to the best ~5%; you are the art director, the model is a junior supplying raw material.

Stop and reject any candidate that violates the anti-slop bans before it goes further:
- default indigo/purple accents (`#6366f1 #4f46e5 #8b5cf6 #7c3aed`, hues ~250–280) where it is not genuinely the brand;
- the two-stop purple/blue/cyan "AI gradient", or cyan accent text on dark;
- emoji used as feature icons;
- AI-stock look (team-round-a-laptop, floating 3D blobs, plastic skin, off hands);
- a decorative gradient passed off as the main visual.

A banned-aesthetic candidate is not a render problem; it is a prompt problem — send it back to `image-prompter` for a corrected prompt rather than re-rolling blindly.

### 4. Cost approval gate (before any paid render)
Paid generation requires explicit cost approval first, stated in plain $/image or $/second. Present the chosen frame, the target model, the resolution, and the per-unit cost (for example "Nano Banana Pro, 1 image at 2K, ~$0.13" or "Veo 3.1 Fast, 4-second loop, ~$0.60"). Use Batch/Flex mode to roughly halve cost on non-urgent bulk renders. Do not proceed to the delivery lane until approval is recorded.

### 5. Delivery lane (licensed) — re-render the chosen frame
Re-render the approved composition on the Tier-1 model selected in step 2, reusing the supplied seed so the licensed frame matches the prototyped one. Confirm the output's licence class against the client agreement:
- Does this asset ship in something the client pays for? If yes, it MUST come from a commercially licensed source — verify before delivery.
- For icons, logotype, and flat illustration, hand off the native SVG, never a flattened PNG.
- For motion, deliver a short loop only, with no load-bearing text inside the clip and a reduced-motion still or fallback path so `prefers-reduced-motion` users are served.
- Generated imagery is supporting, never a substitute for clarity; prefer real client assets and vector/SVG diagrams over decorative generation.

Re-confirm the non-negotiables on the delivered asset: real text stays HTML/SVG (a generated raster carries at most a 1–4 word decorative label); never invent or imply metrics, proof, logos, certifications, or awards inside the image; any copy in or around the asset is Australian English, no US spellings, no contractions, no em/en dash punctuation, and free of the banned-word list.

### 6. Write provenance — `05-qa/asset-manifest.json`
Append one row per delivered asset, exactly:
```json
{ "path": "", "purpose": "", "model": "", "prompt": "", "seed": "", "licence_class": "", "approved_for_client": false, "est_cost": "" }
```
Set `approved_for_client: true` only once the licence is verified and the asset has cleared QA. Record `est_cost` in plain dollars. Note the disclosure mechanism where the model embeds provenance (SynthID on Nano Banana Pro is the disclosure mechanism per the client agreement, not a block on shipping).

### 7. Critique and QA (different family than the builder)
Run the advisory critique on a model family different from whatever built the asset (step 2). The critique is advisory and must cite evidence; it cannot pass an asset on its own say-so. Inspect the asset placed in context at desktop and mobile widths (1440 / 768 / 375) and confirm:
- no anti-slop ban is present (re-run the step 3 checklist on the final render);
- the asset supports, and does not replace, the deliverable's distinctive 20% move;
- contrast of any overlaid real text meets WCAG 2.2 AA (body ≥4.5:1, large/bold ≥3:1, UI/icons ≥3:1);
- the licence class on the manifest row is correct for where the asset ships.

### 8. Handoff
Return to the requesting stream profile:
- the delivered asset(s) at the agreed resolution (SVG for vector/icon/logotype work);
- the reduced-motion still or fallback for any motion loop;
- the updated `05-qa/asset-manifest.json` with every delivered row `approved_for_client: true`;
- a one-line provenance note per asset (model, seed, licence class, est cost, disclosure flag);
- any rejected-and-returned items flagged back to `image-prompter` with the reason.

## Quality bar
An asset is client-ready only when ALL of the following hold:

1. **Design contract read.** `DESIGN.md` and `DESIGN-OS.md` were read before generation (step 0); brand hue is derived from the client logo, never a default indigo/violet/blue.
2. **Licence chain intact.** Prototyped on a free model, delivered on a commercially licensed source; the licence is set by the model maker and verified against where the asset ships.
3. **No baked text, no invented proof.** Load-bearing text stays HTML/SVG (≤1–4 word decorative label in a raster); no invented metrics, logos, certifications, testimonials, or awards anywhere in the image.
4. **Anti-slop clean.** None of the cardinal sins present: default indigo/purple, two-stop AI gradient, emoji feature icons, AI-stock look, decorative-gradient-as-main-visual. Off-brand or banned-aesthetic output is returned to `image-prompter`, not shipped.
5. **Copy discipline.** Australian English, no contractions, no em/en dash punctuation, no banned words in any copy in or around the asset.
6. **Format correct.** Icons/logotype/flat illustration handed off as native SVG; motion is a short loop with no load-bearing text and a reduced-motion fallback; resolution is the lowest that meets the deliverable.
7. **Cost approved and logged.** Every paid render had explicit cost approval (plain $/image or $/second) before generation; `est_cost` recorded.
8. **Provenance complete.** `05-qa/asset-manifest.json` has one row per delivered asset, every delivered row `approved_for_client: true`, disclosure noted where applicable (e.g. SynthID).
9. **Cross-family critique.** Advisory critique run on a different model family than the builder, evidence-cited, no unaddressed P0; asset inspected in context at 1440 / 768 / 375 with WCAG 2.2 AA contrast on any overlaid real text.

Deterministic export gate: when the asset is embedded into a delivered HTML or PDF artifact, that artifact is the source of record and must clear its stream's deterministic gate before delivery — `factory/scripts/qa_landing_export.py` for landing-page artifacts, `factory/scripts/qa_bip_export.py` for Business Information Pack artifacts (`anti-slop-report.md` P0 = 0). An LLM critique never overrides the deterministic gate.

Human sign-off: a named human gate checks every delivered asset is `approved_for_client: true` and confirms the licence chain and disclosure before the client sees anything. No asset ships on a model's say-so.
