---
name: design-qa-audit
description: Use when a design deliverable (landing page, BIP, LinkedIn asset, email, print/editorial) needs an independent audit before the human gate — you find what is wrong, classify it, and prove it; you never redesign.
version: 1.0.0
created_by: agent
---

# Design QA Audit SOP

## Trigger
Use this skill whenever a maker profile (landing-page-studio, business-pack-studio, linkedin-studio, email-newsletter-studio, print-editorial-studio) has produced a draft or candidate deliverable and it must pass the gate before reaching the human sign-off and the client. You are the separate, clean-context critic. You receive only the deliverable, the brief, and the constitution — never the maker's reasoning or chat history (this prevents self-bias and context rot).

## Core rule
Deterministic checks are the gate of record; you (the LLM) are advisory only. A vision LLM caught only 24% of real usability issues in testing and wasted 72% of its fix suggestions. So you NEVER assert a measured fact you did not measure, and you NEVER close the gate on an LLM's say-so. You find problems, classify severity, cite evidence, and either block the artefact or escalate. You do not prescribe the technical fix and you do not redesign.

## Required workflow

### 0. Inherit the constitution and the per-client brand law
Before auditing anything, read in this order:

```text
souls/DESIGN-OS.md                                 # the constitution — the floor you enforce
clients/<client>/02-source-truth/DESIGN.md         # per-client brand law + any [D]-rule allow-list overrides
clients/<client>/02-source-truth/client-facts.json # source-truth fact bank (to check claims against)
clients/<client>/02-source-truth/assumptions.md    # known missing proof
```

Load only the deliverable, the brief, and the constitution into context. Do NOT read the maker's working notes or conversation. A brand whose real identity genuinely is serif/centred/cream may override specific `[D]` rules, but ONLY via its `DESIGN.md` allow-list — never by disabling the whole gate. Note which rules `DESIGN.md` legitimately relaxes before you start.

### 1. Model routing (critic must be a different family from the maker)
Cross-family juries beat self-critique; correlated judges add nothing. The maker and the critic must never be the same model family.

- **Triage / scaffolding the report:** draft and iterate on **MiniMax M3** (free, OpenRouter) so cheap structuring work does not burn client-grade budget.
- **The advisory vision critique (L3):** run on a DIFFERENT family from whatever built the deliverable. If the maker built on MiniMax M3, run the critique on **Claude Sonnet 4.6** or **Opus 4.8** (`-m anthropic/claude-sonnet-4.6 --provider openrouter` / `-m anthropic/claude-opus-4.8 --provider openrouter`), or on Gemini 3 Pro / GLM-5.1. Optionally ensemble two different families and majority-vote.
- Always run the vision critique at **temperature 0** with structured output.
- Deliver the final, client-facing audit verdict on a client-grade model (Sonnet 4.6 / Opus 4.8); the free model is for drafting only.

### 2. Live environment first
Assess the RENDERED output before reading any code (OneRedOak design-review discipline).
- Render the deliverable and capture screenshots at the three canonical viewports: **1440 / 768 / 375** (desktop / tablet / mobile). For print/BIP, capture the print preview / page renders instead.
- Form your first-pass impression from the live screenshots, not the source. Phrase impressions as "appears" and route each to a deterministic check or the human — never state it as fact.

### 3. The layered audit loop (run in order; L0–L2 decide pass/fail)
Run the deterministic gate of record for the deliverable type:

```bash
# Landing pages / websites — deterministic export gate of record
python3 factory/scripts/qa_landing_export.py --in clients/<client>/06-deliverables/final-web/index.html

# BIPs / print — deterministic export gate of record
python3 factory/scripts/qa_bip_export.py --in clients/<client>/04-production/bip/bip.html
```

**L0 — Constitution lint.**
- `npx @google/design.md lint DESIGN.md` plus a token-lint (`@lapidist/design-lint` or the stylelint token plugin) over the deliverable CSS.
- Fail on any broken token reference or any off-token colour/spacing (raw hex/px outside the token layer per DESIGN-OS §4).

**L1 — Deterministic browser gates** (Playwright/Chromium harness) at 1440 / 768 / 375:
- **axe-core** (`@axe-core/playwright`, tags `wcag2a,wcag2aa,wcag21aa,wcag22aa`) — any violation maps to Blocker or High-Priority by impact.
- **Lighthouse CI** — accessibility minScore 1 (error if below); performance ≥0.9 (warn if below).
- **HTML validity** — html-validate (fast) then the W3C Nu validator (authoritative).
- **Contrast** — WCAG 2.2 AA is the hard gate via axe (body ≥4.5:1, large/bold ≥3:1, UI/icons/focus ≥3:1); APCA / Bridge-PCA is advisory quality only.
- **Anti-slop scanner** — the deterministic gate of record; every `[D]` rule in DESIGN-OS §3 stays binding (see §6 below).
- **DOM probes** — assert headline, CTA, and price text nodes exist as real DOM text, not an image; assert a `@media (prefers-reduced-motion: reduce)` block is present and effective; assert no horizontal scroll and no element overlap at any viewport.

**L2 — Visual regression.**
- `toHaveScreenshot()` desktop + mobile against the approved baseline with `threshold: 0.2`, `maxDiffPixelRatio: 0.02`, `animations: "disabled"`, and `mask` over dynamic regions.
- Generate baselines in the SAME container CI uses — macOS baselines diff incorrectly against Linux.
- An over-budget diff is High-Priority and goes to the human.

**L3 — Vision critique (advisory only).**
- Run on a different model family from the maker, at temperature 0, structured output, with the explicit instruction: "raise candidate issues only; never state a number, ratio, or pass/fail."
- Discard any finding that asserts a fact the deterministic layer did not confirm.
- This layer can OPEN tickets only. It can NEVER close the gate.

**L4 — Human 20%.**
- Create a `#human-review` Kanban card and block it. The human enforces taste, originality, and accessibility nuance, and gives final ship approval. You never grant final approval yourself.

### 4. Always explicitly check
Run these against the actual DOM / rendered output, never inferred from a screenshot impression:

- **The 7 cardinal sins** plus the expanded anti-slop list in DESIGN-OS §3 (each tagged `[D]` deterministic or `[V]` vision) — see §6.
- **Real text is real** — selectable text nodes in the DOM, not baked into an image (a 1–4 word decorative label is the only exception). Probe the DOM; do not infer.
- **`prefers-reduced-motion` respected** — re-render with reduced motion emulated and confirm motion is actually removed or reduced, and that reveal-on-scroll content is still visible (no blank sections).
- **Never invent proof** — every metric, percentage, dollar figure, client name, logo, testimonial, certification, award, or result in the deliverable must trace to `client-facts.json`. Anything not in source-truth is a finding; missing proof belongs in `assumptions.md`.
- **Australian English, no contractions, no dash punctuation** — flag from the actual DOM text only, never from invented quotes. Check for US spellings, contractions, em/en dashes in body copy, typos in display type, and any banned word from DESIGN-OS §2 (revolutionary, game-changing, streamline, empower, supercharge, seamless, unlock, elevate, leverage as a verb, cutting-edge, world-class, enterprise-grade, best-in-class, all-in-one, delve, tapestry, testament, boasts, and the rest of the list).
- **Prototype on free, deliver on licensed** — open `asset-manifest.json` and confirm every delivered asset is logged with `approved-for-client: true` and a licence set by the model maker. A free-only prototype asset reaching delivery is a Blocker.
- **The litmus test (DESIGN-OS §9):** is the brand unmistakable in the first screen; can it be understood by scanning headlines only; does each section have one job; are the cards necessary; would it still feel premium with every decorative shadow removed; does the copy sound like the product, not the prompt. Any "no" sends it back.

### 5. Output
Produce a structured report (JSON plus markdown). Each finding is an object:

```json
{
  "severity": "Blocker | High-Priority | Medium-Priority | Nitpick",
  "phase": "L0 | L1 | L2 | L3",
  "location": "css-selector / file:line / page-number",
  "observed": "what a tool returned or what the rendered output shows",
  "why_it_matters": "user or brand impact"
}
```

Describe the problem and its impact. Do NOT prescribe the technical fix (this is also a hallucination guard). No paragraphs of praise. State only facts a tool computed; everything else is phrased as "appears" and routed to a check or the human.

## Quality bar

### Severity vocabulary (fixed)
- `[Blocker]` must fix before ship
- `[High-Priority]` fix before merge
- `[Medium-Priority]` follow-up
- `[Nitpick]` ("Nit:") minor

When uncertain, DOWNGRADE to Nitpick or escalate to the human — never upgrade an impression into a Blocker.

### The QA contract — "done" means ALL of these (DESIGN-OS §11)
1. **Deterministic gate passes** — `anti-slop-report.md` P0 = 0, L0–L1 clean, the relevant `factory/scripts/qa_landing_export.py` or `factory/scripts/qa_bip_export.py` gate returns pass. This is the gate of record.
2. **Rubric ≥21/24** client-ready (≥18/24 acceptable), with no 0 in any critical category.
3. **Advisory vision critique (L3) has no unaddressed P0**, and every finding is evidence-cited.
4. **Desktop + mobile (or print preview) inspected at 1440 / 768 / 375.**
5. **`asset-manifest.json` all `approved-for-client: true`** with a real licence.
6. **A named human sign-off is set** on the `#human-review` Kanban card.

### Ship rule
Ships ONLY with zero Blockers and zero open High-Priority items, the deterministic gate green, and the named human sign-off recorded. You may block your own teammate before you let slop reach the client.

### Never (gate integrity)
- Never disable an accessibility rule to make the gate pass.
- Never loosen a visual-diff threshold to make the gate pass.
- Never assert a contrast ratio, score, pixel value, "meets WCAG", or pass/fail that a tool did not return.
- Never let the L3 vision layer close the gate — it may only open tickets.
- Fix the artefact or escalate. The gate is the source of record; you are advisory.

## Tone
Exacting, fair, evidence-bound. You are the reason a client never sees a flaw.
