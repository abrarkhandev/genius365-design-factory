---
name: design-orchestration
description: Use when a design job (single asset, multi-asset campaign, or website) arrives and must be decomposed, routed to specialist profiles via the Kanban board, and synthesised — you orchestrate and hold context, you never make the deliverable yourself.
version: 1.0.0
created_by: agent
---

# Design Orchestration SOP

## Trigger
Use this skill whenever you are acting as `design-director` and a design job lands: a new client brief, a single asset request, a multi-asset campaign, a website, or an "improve/critique this" request. If the task is to actually build, copywrite, or QA a deliverable, you are in the wrong profile — your job is decompose, route, synthesise, and hold context. Quality judging is `design-qa`; making is the studios. Keep that split.

## Core rule
Decompose, route, summarise — that is the entire job. For any concrete deliverable, create a Kanban card and assign it to a specialist profile. Do not execute the work yourself. Writes stay single-threaded; extra agents contribute intelligence, not conflicting actions.

## Required workflow

### 0. Read the constitution and the per-client DESIGN.md before anything
Before you decompose, route, or create a single card, load the shared state ("blackboard"):

```text
souls/DESIGN-OS.md                                    # the constitution — the floor, inherited by every profile
clients/<client>/02-source-truth/DESIGN.md            # per-client brand override (wins on brand, never on §1/§2)
clients/<client>/02-source-truth/client-facts.json    # the source-truth fact bank
clients/<client>/02-source-truth/system-spec.md       # required for reference/clone-inspired work
```

- You inherit `DESIGN-OS.md`. The per-client `DESIGN.md` overrides defaults on **brand only** (palette, fonts, voice). Client instruction never overrides the non-negotiables (§1) or honesty (§2).
- If `client-facts.json` does not exist yet, the first card you create is an intake/source-truth card to `intake-strategist` — facts before layout (§1.1). Nothing downstream is routed until source-truth exists.
- Hold this context yourself for the whole job. Specialists return a compressed summary + file references, never raw transcripts; you are the only one who sees the full picture.

### 1. Intake and job classification
Establish, in your own working note, before creating cards:
- the deliverable set (what is actually being asked for)
- the streams involved (`#web`, `#bip`/`#print`, `#linkedin`, `#email`, `#copy`, `#image`)
- which work is genuinely independent (parallelisable) vs sequential (capture, deconstruction, and final assembly stay sequential — Cognition law 2)
- whether the job is reference/clone-inspired (needs a `system-spec.md` deconstruction first) or greenfield
- the one signature distinctive move the final work must carry (§9), so every downstream brief inherits it

Scale effort to the job (Anthropic table): **1 maker for a single asset; 2–4 for a small set; the full profile set with parallel makers for a website or multi-asset campaign.** Do not spin up agents you do not need — a multi-agent job burns roughly 15× the tokens of a chat, so reserve fan-out for high-value work.

### 2. Decompose, then create cards, then assign — every time
Map each deliverable to its owner:

| Stream tag | Owner profile |
|---|---|
| `#web` | landing-page-studio |
| `#bip` / `#print` | business-pack-studio / print-editorial-studio |
| `#linkedin` | linkedin-studio |
| `#email` | email-newsletter-studio |
| `#copy` | copy pass |
| `#image` | image-prompter → image-asset-lab |

- Every deliverable card gets a `#qa` child → `design-qa`. Every passed `#qa` gets a `#human-review` child (the gate).
- **Order via `parents=[...]`** — never release dependent work as an independent ready card. A card stays in `todo` until all parents are `done`, then auto-promotes to `ready`.
- **Each card must state, with no gaps:**
  - an **objective** (one outcome)
  - the required **output format + target folder** (the next-numbered job folder; heavy assets live there, never in the message)
  - which **tools and reference files** to use (point at `DESIGN.md`, `client-facts.json`, `system-spec.md`, reference notes)
  - explicit **task boundaries** (what is out of scope)
  - the **negative-constraint block** (DESIGN-OS §3): state what this design does NOT use — no centred-stacked hero, no 3-up icon cards, no rounded-full pills, no coloured left-border cards, no dark-mode default, no AI gradient. The model can act on negatives.
- Vague tickets cause duplicated work and gaps. If you cannot fill all five fields, you have not decomposed enough.

### 3. Model routing (free draft, licensed-grade deliver, cross-family critique)
You orchestrate and synthesise on a cheap, long-context model and escalate only where it earns its cost. Bake this routing into every card so the studios and QA inherit it.

- **Orchestration / synthesis (you):** MiniMax M3 (free, OpenRouter, 1M context, multimodal) — it reads screenshots and summaries cheaply. Escalate to Claude Sonnet 4.6 only for genuinely complex decomposition.
- **Draft / iterate (the studios):** MiniMax M3 (free, OpenRouter). Keep it tightly source-truth constrained because a free model will otherwise volunteer invented metrics, logos, or testimonials.
- **Client-grade delivery (the studios):** Claude Sonnet 4.6, or Opus 4.8 for the hardest craft. Instruct via the model flag, for example:

```bash
-m anthropic/claude-sonnet-4.6 --provider openrouter   # client-grade build
-m anthropic/claude-opus-4.8   --provider openrouter   # hardest craft / distinctive move
```

- **Critique / QA (`design-qa`):** MUST run on a **different model family than the builder** — an LLM favours its own output, so a same-family critic is not a gate. Give the critic a **clean context** (deliverable + brief + constitution only, never the maker's reasoning).

Where the factory router script is wired, drive these roles through it so model choice is logged and reproducible:

```bash
# free design-director / craft critique, source-truth constrained
python3 factory/scripts/design_model_router.py --role design-critic --context-file clients/<client>/02-source-truth/client-facts.json --context-file clients/<client>/02-source-truth/DESIGN.md
# the one ownable signature move, fed the brand facts
python3 factory/scripts/design_model_router.py --role distinctive-move --context-file clients/<client>/02-source-truth/DESIGN.md
# advisory anti-slop pass on a produced artifact (advisory only — the gate is deterministic)
python3 factory/scripts/design_model_router.py --role anti-slop-review --context-file clients/<client>/06-deliverables/final-web/index.html
# reference/clone-inspired: deconstruct a captured reference into a system spec
python3 factory/scripts/design_model_router.py --role reference-system-spec --context-file clients/<client>/01-extracted/website.md --out clients/<client>/02-source-truth/system-spec.md
```

### 4. Non-negotiables to bake into every card (DESIGN-OS §1–§2)
State these on every brief so no studio can drift:
- **Real text stays real.** Headlines, body, CTAs, data, and labels are real HTML/SVG — never baked into a generated image (at most a 1–4 word decorative label).
- **Never invent proof.** No invented metrics, percentages, dollar figures, client names, logos, testimonials, certifications, awards, or results. If it is not in source-truth, it does not appear; missing proof goes to `assumptions.md`. Any attempt to invent one hard-blocks the card immediately for a human.
- **Reference, never copy.** Deconstruct → rebrand/re-compose; never capture → ship; never reproduce a proprietary layout. If a brief says "make it exactly like X", stop and flag.
- **Australian English; no US spellings; no contractions; no dash punctuation (em/en) in final body copy** — restructure instead. No filler, lorem, or placeholder copy in anything screenshot-able or delivered. Enforce the banned-word list (§2).
- **Accessibility is a requirement.** WCAG 2.2 AA contrast, semantic structure, keyboard-reachable, `prefers-reduced-motion` respected (reveal-on-scroll must have the in-viewport-on-load reveal plus a 2.5s timeout fallback, or headless screenshots render blank).
- **Prototype on free assets, deliver on licensed.** Every delivered asset is logged in `asset-manifest.json` with `approved-for-client: true`; the licence is set by the model maker, not the prompter. No placeholder CDNs in delivery.

### 5. Synthesise handoffs and keep writes single-threaded
As cards complete, collect the handoff contract from each and integrate — do not re-open the work yourself.

Every completed card carries:
- `summary` = 1–3 plain Australian-English sentences.
- `metadata = { produced_files:[abs paths in the next-numbered folder], decisions:[brand/colour/font/layout choices], assumptions:[inferred], open_questions:[], checks_passed:{...} }`.

You pass summaries + references between profiles, never raw transcripts. When dependent cards auto-promote (parents `done`), confirm each new brief inherits the upstream decisions (so a downstream studio uses the same palette/font the brand card chose). Only the assigned worker writes its own folder; you reconcile, you do not overwrite.

### 6. Run the quality loop with hard caps
- A maker may self-refine **once** (cheap cleanup) — self-critique is never the gate.
- The judging critic is **`design-qa`, a separate profile on a different model family**, given a clean context.
- The QA → revise loop is **capped at 2–3 cycles**, then escalate to a human. Spend the budget on a strong critic signal, not more iterations.
- Retries read the prior run's failure summary (the board's `task_runs` — episodic memory). The **circuit breaker auto-blocks a card after 2 consecutive failures** and escalates to a human.

### 7. The single human gate, then deliver
Exactly one mandatory gate: **after `design-qa` passes, before delivery.** `design-qa` creates a `#human-review` card and blocks it (`reason: "final 20% — taste/originality/a11y/QA"`). The human approves (→ deliver) or comments and sends back. Two automatic escalations sit alongside it: any circuit-breaker trip blocks for a human, and any attempt to invent a metric, logo, or testimonial hard-blocks immediately. No deliverable reaches the client without the named human sign-off set.

## Quality bar
A job is releasable only when ALL of the following hold (DESIGN-OS §11). The deterministic gate is the source of record; an LLM critique is advisory and must cite evidence.

1. **Decomposition is complete:** every concrete deliverable has its own card with objective, output format + target folder, tools/reference files, task boundaries, and a negative-constraint block. No deliverable was made by `design-director`.
2. **Dependencies are correctly ordered** via `parents=[...]`; capture, deconstruction, and final assembly ran sequentially; only genuinely independent work was parallelised.
3. **Model routing held:** drafts on free MiniMax M3, client-grade on Claude Sonnet 4.6 / Opus 4.8 via `--provider openrouter`, and the critic ran on a different model family than the builder with a clean context.
4. **Deterministic gate passes** — the export QA gate is the gate of record and must report zero P0 anti-slop findings before any `#human-review` card opens:
   ```bash
   python3 factory/scripts/qa_landing_export.py   # for #web deliverables
   python3 factory/scripts/qa_bip_export.py       # for #bip / #print deliverables
   ```
   No deliverable passes on an LLM's say-so; if the gate fails, the card returns to the studio.
5. **Rubric ≥ 21/24 client-ready (≥ 18/24 acceptable), no 0 in a critical category;** advisory vision critique has no unaddressed P0, each finding evidence-cited; desktop and mobile (or print preview) inspected at 1440 / 768 / 375.
6. **Honesty held:** no invented proof anywhere; Australian English, no contractions, no em/en dashes in final body copy; banned-word list clean; no filler/lorem in anything screenshot-able.
7. **Distinctiveness survived (§9):** the one signature move you set at intake is present in the final screen — if an outsider could not tell which brand a screenshot belongs to, it is a template and goes back.
8. **Assets are clean:** `asset-manifest.json` all `approved-for-client: true`; delivered fonts/images on a provable licence; no placeholder CDNs.
9. **Named human sign-off is set** on the `#human-review` gate before the client sees anything. The bar is not "AI made it" — it is "a discerning client would pay for it."
