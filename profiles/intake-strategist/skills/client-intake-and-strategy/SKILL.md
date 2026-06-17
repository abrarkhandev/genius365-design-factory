---
name: client-intake-and-strategy
description: Use when a new or messy client input (Fathom call transcript, assets folder, discovery doc/DOCX/PDF brief, or an existing website URL) needs to be turned into a source-truth fact bank, a per-client DESIGN.md control file, a reference pass, and a per-stream strategy before any deliverable is built.
version: 1.0.0
created_by: agent
---

# Client Intake and Strategy SOP

## Trigger
Use this skill whenever the task is the front-of-house job: take raw client inputs and produce the three things every downstream profile needs — a source-truth fact bank, a per-client `DESIGN.md`, and a per-stream strategy — plus a reference pass. Run this BEFORE any stream profile (landing-page-studio, business-pack-studio, linkedin-studio, email-newsletter-studio, print-editorial-studio) starts producing. You are read-mostly: you produce briefs, not deliverables.

## Core rule
Facts before layout, and never invent proof. You are the reason every downstream profile builds on truth instead of guesses. You would rather flag an unknown than fill it with a plausible lie. Missing metrics, logos, testimonials, certifications, awards, and results go to `assumptions.md` and the `unknowns` field — never into the brief.

## Required workflow

### 0. Inherit the constitution and seed the control file
Before producing anything:
- Read the shared constitution `souls/DESIGN-OS.md` (the floor for every stream: §1 non-negotiables, §2 honesty, §3 anti-slop, §4 tokens, §6 colour, §11 QA contract). It is inherited, not optional.
- Read this profile's `souls/intake-strategist.SOUL.md` for domain craft.
- Locate or create the per-client folder `clients/<client>/` and read any existing `clients/<client>/02-source-truth/DESIGN.md`. A per-client `DESIGN.md` overrides DESIGN-OS defaults on *brand* only — never on the §1 non-negotiables or §2 honesty.

Non-negotiables that bind every artifact you hand off (carry them into the brief explicitly):
- Real text stays real: headlines, body, CTAs, data, labels live in HTML/SVG; never bake real copy into a generated image (at most a 1–4 word decorative label).
- Never invent metrics, percentages, dollar figures, client names, logos, testimonials, certifications, awards, or results.
- Australian English; no US spellings; no contractions; no em/en dash punctuation in final body copy — restructure instead. Enforce the §2 banned-word list.
- Respect `prefers-reduced-motion` in every motion direction you specify.
- Prototype on free assets; deliver only on a provable licence (set by the model maker, not the prompter).

### 1. Intake mode detection (classify first, then extract accordingly)
- **Mode A:** assets folder + Fathom transcript / DOCX / PDF / discovery brief.
- **Mode B:** existing website URL.
- **Mode C:** existing BIP or asset to improve.
- **Mode D:** mixed materials.

Read raw inputs from `clients/<client>/00-input/` (`assets/`, `transcripts/`, `docs/`, `urls.md`) and write the extracted layer to `clients/<client>/01-extracted/` (`website.md`, `transcript.md`, `docx.md`, `asset-inventory.md`, `screenshots/`, `reference-captures/`).

### 2. Model routing
- Reference / screenshot / system-spec READING (vision): **Qwen 3.5** multimodal — `qwen/qwen3.5-122b-a10b`.
- Strategy / IA / fact-bank DRAFTING and iteration: **MiniMax M3** (free, OpenRouter) — `minimaxai/minimax-m3`. Advisory only: keep it source-truth constrained because it will otherwise invent proof, metrics, and logos. Treat every claim it returns as unverified until traced to source-truth.
- Throwaway extraction: free NIM.
- Client-grade drafting where it is warranted (the final brief language a client or director reads): deliver on **Claude Sonnet 4.6 / Opus 4.8** — `-m anthropic/claude-sonnet-4.6 --provider openrouter` or `-m anthropic/claude-opus-4.8 --provider openrouter`.
- Critique / QA must run on a DIFFERENT model family than the builder. If MiniMax M3 drafted the fact bank or strategy, have a Claude or Qwen pass scrutinise it for invented proof; if Claude drafted, critique on MiniMax or Qwen. Never let one model both write and bless its own output.

When the router is available, invoke it rather than calling models ad hoc:

```bash
# Qwen: read reference screenshots / a captured site into a deconstructed system-spec
python3 factory/scripts/design_model_router.py --role reference-system-spec \
  --context-file clients/<client>/01-extracted/website.md \
  --out clients/<client>/02-source-truth/system-spec.md

# MiniMax M3: draft strategy / IA (source-truth constrained, advisory)
python3 factory/scripts/design_model_router.py --role strategy-draft \
  --context-file clients/<client>/02-source-truth/client-facts.json \
  --context-file clients/<client>/02-source-truth/DESIGN.md

# Cross-family QA: scan the drafted fact bank / brief for invented proof (DIFFERENT family than the builder)
python3 factory/scripts/design_model_router.py --role fact-check \
  --context-file clients/<client>/02-source-truth/client-facts.json
```

### 3. Source-truth fact bank (`02-source-truth/client-facts.json`)
Extract and write structured facts. For each, record provenance; never fabricate. Fields:
- one-line positioning
- business summary
- audiences / segments
- problems solved
- services / offers / products, each with inclusions + outcomes
- process / how it works
- proof / testimonials / case studies (with the source quote)
- differentiators
- founder / team credibility
- CTA / contact
- brand notes
- **unknowns** (everything not stated in source)

From a Fathom transcript, map each quote to the claim it supports and keep the timestamp so any downstream profile can verify. Then write the companions:
- `client-facts.md` — the human-readable version.
- `assumptions.md` — everything inferred or missing, including all absent proof. This is where missing metrics/logos/testimonials/certifications go. Nothing in here is allowed to migrate into a brief as fact.
- `brand-kit.md` — raw brand observations (colours seen, fonts seen, logo, voice cues) feeding step 4.

### 4. `DESIGN.md` — the brand control file (seed fast, then curate)
Seed colour / type / spacing from the brand automatically, then have a human re-map to semantic tokens and remove any default indigo before it becomes truth.
- **Extractors (seed only):** `arvindrk/extract-design-system` (CLI + agent skill), Peel, FontOfWeb (DTCG export), Dembrandt (for deconstructing a reference site). These pull whatever the source used — often the banned indigo/purple — so treat all output as a draft, not truth.
- **Token shape:** author in **DTCG 2025.10** (`$value`/`$type`/`$description`; colour as `{colorSpace, components, hex}`; dimension as `{value, unit}`; aliases via `{group.token}`). Three tiers: primitive → semantic → component. Reference the semantic layer by purpose (`color.brand.primary`, `color.text.muted`), never raw hex. Build to `dist/tokens.css` via Style Dictionary so every stream reads one source.
- **Colour:** derive the primary hue from the client's logo/brand. Never default to indigo/violet/blue (banned hues ~250–280, and the AI two-stop purple/blue/cyan gradient). Verify **WCAG 2.2 AA** (body ≥4.5:1, large/bold ≥3:1, UI/icons/focus ≥3:1) and the **APCA target Lc ≥75 body / ≥60 large**. Generate tints/shades in **OKLCH** (Leonardo / Radix / tints) — never by sliding lightness alone. Use the Radix 12-step job mapping (1–2 bg, 3–5 component bg, 6–8 borders/focus, 9–10 solid, 11–12 text) or Tailwind 50–950. Accent appears ≤2 visible uses per screen.
- **Type:** pick a ratio (1.25 default, 1.333 marketing, 1.5/1.618 editorial only). Sizes in **rem**, fluid `clamp()` from Utopia. Body 16–18px-equiv, line-height 1.5–1.7, headings 1.0–1.2, measure 45–75ch, three text colours max, ALL-CAPS labels tracking ≥0.06em. Pair one distinctive display face with one refined body — avoid Inter/Roboto/Arial/Geist/Space Grotesk as the signature face; serif brand → serif display. Record font + **licence + URL** (Fontshare FFL — Satoshi, General Sans, Switzer, Clash Display — or Google OFL/Apache by default); self-host/embed for PDF/print.
- **Icons:** one family only (Lucide baseline; Phosphor for personality; Heroicons on Tailwind; Tabler for coverage; Radix for tight UI). Inline SVG, stroke 1.6–1.8px `currentColor`, sizes 16/20/24 only, decorative icons `aria-hidden`. Never mix libraries; never emoji feature icons.
- Fill all 13 sections of the `DESIGN.md` v2 template, including:
  - **the distinctive 20% move** — one ownable, HTML/CSS/SVG-feasible signature (logo-geometry motif, opinionated type decision, intentional asymmetry, editorial layout primitive) so an outsider can identify the brand from a screenshot. Document it in one sentence.
  - **the do-not-cross / negative-constraint list** — state explicitly what this design does NOT use (for example: no centred-stacked hero, no 3-up icon cards, no `rounded-full` pills, no coloured left-border cards, no gradient text, no dark-mode default, no AI gradient). The model acts on negatives.
  - the named **human sign-off owner** for the control file.

### 5. Reference pass (Capture → Deconstruct → Rebrand — never Capture → Ship)
- Pull 5–8 references per requested deliverable from Dribbble / Mobbin / component libraries plus real competitor sites for market language and buying context.
- Run vision (**Qwen 3.5**) on 2–3 of them to extract layout, type, colour, spacing, hero treatment, and card treatment, plus an explicit **avoid-list**. Save captures to `01-extracted/reference-captures/`.
- For clone-mode jobs, write `02-source-truth/system-spec.md` — the deconstructed system handed to the makers.
- **Legal gate:** study to build something original; never reproduce a near-identical copy of a proprietary layout. If the brief is "make it look exactly like X", STOP and flag it; do not proceed.

### 6. Per-stream strategy (`03-strategy/`)
Produce one strategy doc per requested deliverable, written from source-truth only:
- **Landing** (`landing-strategy.md`): conversion goal, ONE primary visitor + ONE primary action, hero promise, section flow, proof plan, objection handling.
- **BIP** (`bip-strategy.md`): information architecture + page plan.
- **LinkedIn** (`linkedin-strategy.md`): asset list + founder-vs-company routing.
- **Newsletter** (`newsletter-strategy.md`): module plan.
- **Print** (`print-strategy.md`): grid + page plan.

Every strategy carries the negative-constraint block from `DESIGN.md` and the distinctive-move sentence so the maker cannot regress to the median template.

### 7. Handoff to stream profiles
Hand the brief package to the makers via the orchestrator. The handoff is complete only when each requested stream has, in `clients/<client>/`:
- `02-source-truth/client-facts.json` + `client-facts.md` + `assumptions.md` + `brand-kit.md`
- `02-source-truth/DESIGN.md` (human-curated, default-indigo removed, sign-off owner named)
- `02-source-truth/system-spec.md` (clone-mode jobs only)
- `03-strategy/<stream>-strategy.md` for each requested deliverable
- `01-extracted/reference-captures/` populated, with avoid-list recorded

State clearly which stream profile owns each strategy and what is still in `unknowns` so the maker knows what cannot be claimed.

## Quality bar
Intake is not "done" until ALL of the following hold. This skill produces no client deliverable, so the deterministic export gates (`factory/scripts/qa_landing_export.py`, `factory/scripts/qa_bip_export.py`) run downstream in the stream profile's QA; intake's job is to make those gates pass on the first attempt by removing slop and invention at the source.

Concrete checklist:
1. **Mode detected** and recorded; extraction matches the mode.
2. **Provenance complete** — every fact in `client-facts.json` traces to a source (transcript timestamp, doc, or page); zero unsourced claims.
3. **No invented proof** — all missing metrics/logos/testimonials/certifications sit in `assumptions.md`, none in any brief. Verified by a cross-family fact-check pass (a DIFFERENT model than the drafter).
4. **`DESIGN.md` curated, not just seeded** — extractor defaults reviewed; no default indigo/violet/blue unless genuinely the brand; primary hue derived from the logo; all 13 sections filled.
5. **Contrast verified deterministically** — every text/background pair in the palette meets WCAG 2.2 AA (body ≥4.5:1) with the APCA Lc ≥75 body target noted; tokens authored in DTCG, referenced via the semantic tier, no raw hex/px outside the token layer.
6. **Tokens build** — `dist/tokens.css` generates cleanly via Style Dictionary; passes `@google/design.md lint` + `@lapidist/design-lint`.
7. **Distinctive 20% move** named in one sentence and the negative-constraint / do-not-cross list present in `DESIGN.md` and carried into every strategy.
8. **Reference pass legal-clean** — 5–8 references per deliverable, avoid-list recorded; no "make it exactly like X" job proceeded without a flag; clone jobs have `system-spec.md`.
9. **Fonts licensed for delivery** — font + licence + URL recorded; print/PDF fonts self-hostable.
10. **Honesty pass** — Australian English, no contractions, no em/en dashes, no §2 banned words, no filler/lorem in any brief.
11. **Handoff complete** — every required file present for each requested stream; `unknowns` surfaced to the maker.
12. **Named human sign-off** on `DESIGN.md` (and the fact bank) is set before any stream profile begins production. The single human gate later sits between `05-qa` and `06-deliverables`; intake's gate is the brand-truth sign-off that protects it.
