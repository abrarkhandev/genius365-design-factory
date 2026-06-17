# Hermes Design Factory — Master Plan v5

**Status:** v5 complete — architecture, 10 souls, constitution, audit loop, model routing, and resource library all written. **Awaiting human review** (the one gate). The consolidated research dossier (`research/dossier/`) + verification reports (`research/raw/V*.md`) finalise from background workflow `wndkltbgf`; §7/§8 facts were sourced from already-URL-verified research and will be reconciled against the verify reports on completion.
**Date:** 2026-06-15
**Supersedes:** `design-hermes/design-factory-locked-pilot-v4.md` (extends, does not discard)

---

## 0. What this is, in one paragraph

The Hermes Design Factory is an AI-run design studio that takes messy client inputs (a Fathom call, an assets folder, a discovery doc, or a reference URL) and produces client-ready design deliverables across five streams — LinkedIn assets, BIPs, websites/landing pages, email newsletters, and print/editorial — with **one human doing the final check before the client sees anything**. v4 proved the spine on two streams (BIP + landing) with a deterministic anti-slop gate. v5 extends it to all five streams, adds an image-generation lane, adds a back-of-house design-director/QA role, gives every agent a shared machine-readable design constitution, and loads each soul with researched, world-class design craft.

## 0.1 The problem we are solving

A human design team had six months and could not ship one good website. The failure modes that an AI factory removes:
- **No repeatable process** → we have a stage-gated pipeline (`00-input → 06-deliverables`).
- **Taste is inconsistent and unaccountable** → we have a deterministic anti-slop gate (gate of record) plus an advisory critic plus a human gate.
- **Throughput is one-person-deep** → profiles run in parallel; the Kanban board routes work.
- **"AI made a page" ≠ "client-ready"** → the 80/20 rule: AI delivers the 80% draft, a human enforces the final 20% (taste, originality, accessibility) before delivery.

## 0.2 Design principles (non-negotiable, inherited by every profile)

1. **Facts before layout.** Extract a source-truth fact bank first; never jump to design.
2. **Never invent proof.** No invented metrics, logos, testimonials, certifications, results. Missing proof stays in `unknowns`/`assumptions.md`.
3. **Real text stays real.** Important text is HTML/SVG, never baked into a generated image.
4. **Deterministic gate is the source of record.** The LLM critic is advisory only and must cite exact file evidence (it has hallucinated metrics before).
5. **Reference, never copy.** Competitor/reference sites are for Deconstruct → Rebrand/Re-compose, never Capture → Ship.
6. **Prototype on free, deliver on licensed.** Free models/assets for drafts; licensed models/assets for client delivery, tracked in `asset-manifest.json`.
7. **Australian English**, no contractions, no dash punctuation in final body copy.
8. **Accessibility is not optional.** Respect `prefers-reduced-motion`; meet WCAG contrast; semantic structure.
9. **The 7 anti-slop sins are banned** (indigo/purple defaults; two-stop purple/blue/cyan hero gradients; emoji feature icons; wrong display font; rounded cards with coloured left-border accents; invented metrics; filler copy). v5 expands this list from research (§6).

---

## 1. Streams → profiles map

The five streams from `Design Team Streams.pdf`, each mapped to an owning specialist Hermes profile, plus the cross-cutting roles that serve all of them.

| # | Stream (from streams doc) | Deliverables | Owning profile | Status | Production model |
|---|---|---|---|---|---|
| 1 | **Websites** | landing pages, interactive, animated, static | `landing-page-studio` | ✅ exists | MiniMax M3 (free) → Sonnet 4.6 (deliver) |
| 2 | **BIP** | Business Information Pack PDF | `business-pack-studio` | ✅ exists | MiniMax M3 (free) → Sonnet 4.6 (deliver) |
| 3 | **LinkedIn** | featured/newsletter/personal/business banners, text posts, carousel PDFs, single infographics | `linkedin-studio` | 🆕 new | MiniMax M3 / Sonnet 4.6 + image lane |
| 4 | **Email Newsletter** | HTML-into-CRM + PDF | `email-newsletter-studio` | 🆕 new | MiniMax M3 / Sonnet 4.6 |
| 5 | **Print / Editorial** | catalogue, magazine, article, blog (PDF/Word + elements) | `print-editorial-studio` | 🆕 new | MiniMax M3 / Sonnet 4.6 |

**Cross-cutting roles** (serve every stream — not tied to one):

| Role | Purpose | Profile | Status | Model |
|---|---|---|---|---|
| **Intake & strategy** | Fathom/assets/URL → source-truth + `DESIGN.md` + per-stream strategy + reference pass | `intake-strategist` | 🆕 new (scripts exist) | Qwen 3.5 (vision/reference), MiniMax M3 (strategy) |
| **Image prompting** | DESIGN.md + slot brief → model-specific image prompts | `image-prompter` | 🆕 new | MiniMax M3 / Qwen |
| **Image/asset generation** | runs image models, returns assets + provenance | `image-asset-lab` | 🆕 new | Nano Banana Pro / FLUX 2 / Cloudflare free |
| **Orchestration** | owns job context; decomposes, routes tickets → profiles via Kanban, synthesises; **never builds** | `design-director` | 🆕 new | MiniMax M3 (routing) |
| **Design QA / critique** | the layered audit loop + deterministic gate of record; a **separate, clean-context** critic; creates the human-review card | `design-qa` | ◑ partial (router/prompts/scanner exist) | different family from maker + deterministic scripts |

> **Decision — profile count:** 5 stream profiles + 5 cross-cutting roles (intake-strategist, image-prompter, image-asset-lab, design-director [orchestrator], design-qa [critic]). This honours the founder-guide directive to add *bounded asset-worker lanes* rather than "one giant all-in-one designer," **and** the research rule that the critic must be a separate, clean-context profile from the maker (LLMs favour their own output). We do **not** build all at once — see the rollout in §11.

---

## 2. The pipeline (the spine)

Keep the proven numbered folder pipeline; extend it per the founder-guide. **One physical folder per client; every artifact has an owner and a stage.**

```text
clients/<client-slug>/
  00-input/                      # raw: assets/, transcripts/, docs/, urls.md           [human/client]
  01-extracted/                  # website.md, transcript.md, docx.md, asset-inventory.md,
                                 #   screenshots/, reference-captures/                    [intake-strategist]
  02-source-truth/               # client-facts.json (schema), client-facts.md,
                                 #   assumptions.md, brand-kit.md,
                                 #   DESIGN.md (control file), system-spec.md (clone jobs) [intake-strategist]
  03-strategy/                   # per-stream strategy: landing-strategy.md, bip-strategy.md,
                                 #   linkedin-strategy.md, newsletter-strategy.md, print-strategy.md [stream profile]
  04-production/                 # bip/, landing-page/, linkedin/, newsletter/, print/,
                                 #   assets/{icons,images,motion}/                        [stream profile + image lane]
  05-qa/                         # qa-report.md, anti-slop-report.md (deterministic = gate of record),
                                 #   vision-critique.md (advisory), asset-manifest.json    [design-director]
  06-deliverables/               # final-pdf/, final-web/, screenshots/, handoff.md        [released only after HUMAN GATE]
```

**The single human gate sits between `05-qa` and `06-deliverables`.** Nothing reaches `06-deliverables` (the client) until a human signs off the `qa-report.md` human-sign-off field. This is the "human does the final check before sending to the client" requirement, made physical.

---

## 3. End-to-end workflow (the dynamic flow)

```text
                         ┌─────────────────────────────────────────────────────────┐
 CLIENT INTAKE           │ Fathom transcript · assets folder · discovery doc · URL  │
 (00-input)              └───────────────────────────┬─────────────────────────────┘
                                                      ▼
 EXTRACT + RESEARCH      intake-strategist:  extract facts → client-facts.json
 (01→02)                                     + brand-kit → DESIGN.md (control file)
                                             + DYNAMIC REFERENCE PASS (fan-out, §3.1)
                                                      ▼
 STRATEGY (03)           stream profile:     conversion/IA strategy per requested deliverable
                                                      ▼
 PRODUCTION (04)         stream profile:      build deliverable (HTML/CSS → web or → PDF)
                              │  needs imagery? ──▶ image-prompter → image-asset-lab → assets/ (embedded, real text stays HTML)
                                                      ▼
 QA (05)                 design-director:      (1) deterministic gate  → anti-slop-report.md  [GATE OF RECORD]
                                              (2) vision critique loop → vision-critique.md  [ADVISORY]
                                              (3) rubric score (≥21/24 client-ready)
                                                      ▼
 ╔═══════════════════════════ HUMAN GATE (the one human check) ═══════════════════════════╗
 ║ Reviewer reads qa-report + screenshots/PDF. Approve → release. Reject → back to 03/04.  ║
 ╚════════════════════════════════════════════════════════════════════════════════════════╝
                                                      ▼
 DELIVER (06)            final-web / final-pdf + screenshots + handoff.md → client
```

### 3.1 The dynamic research/reference pass (per client, per job)

This is the repeatable, per-client version of the factory-build research workflow. When a job enters, `intake-strategist` spins out a **bounded reference fan-out**:

- one agent per reference category relevant to the deliverable (e.g. for a SaaS landing page: *direct competitors*, *same-category Dribbble/Mobbin shots*, *component-library hero patterns (21st.dev/shadcn)*, *industry market language*);
- each returns a structured `reference-analysis` (borrow-list + **avoid-list** + one recomposition opportunity);
- `design-director` deconstructs references into `system-spec.md` (clone-mode jobs only);
- output feeds `DESIGN.md` and the per-stream strategy.

**Boundaries (founder-guide):** parallelise only independent work (reference categories, and later independent assets — icons/images/motion). Keep dependency-heavy work sequential (deconstruction → DESIGN.md → build → QA).

---

## 4. The image-generation sub-system

Your explicit requirement — *one model generates images, another model creates the deliverable and embeds them, and an AI handles the image prompting* — is a clean three-role separation:

```text
 stream profile (BIP/landing/linkedin)            image-prompter                    image-asset-lab
   needs "hero illustration for slot X"   ──▶   reads DESIGN.md + slot brief  ──▶  picks model, runs it,
   (knows the design context + slot)            writes MODEL-SPECIFIC prompt       returns asset + provenance
                                                (Nano Banana Pro / FLUX 2 / …)     to 04-production/assets/
            ▲                                                                              │
            └──────────────── embeds asset, keeps all real text in HTML/SVG ◀──────────────┘
                                              + logs to 05-qa/asset-manifest.json
```

- **`image-prompter` (the brain):** understands both the design intent *and* the target model's prompt grammar. Given `DESIGN.md` (brand tokens, mood, style) and a slot brief, it writes the optimal prompt + negative prompt + aspect ratio + reference-image plan. Per-model cheat sheets from research R4.
- **`image-asset-lab` (the hands):** executes against the chosen model. **Free for prototype** (Cloudflare FLUX-1-schnell / SDXL), **licensed for delivery** (Nano Banana Pro / FLUX 2 Pro / Ideogram / Recraft). Returns asset + writes provenance.
- **The stream profile (the assembler):** embeds the returned asset into the HTML/CSS deliverable. **Important text never goes into the image** — only short decorative labels at most; headlines/CTAs/data are real HTML/SVG.
- **`asset-manifest.json`** records: asset path · purpose · model/tool · prompt/source · licence class · approved-for-client (bool) · est. cost. The human gate checks every delivered asset is `approved-for-client: true`.

> Model menu + commercial-licence status: filled from research R11/V3 (§7, §8).

---

## 5. The souls (system architecture)

Three tiers, so knowledge lives in exactly one place:

```text
  DESIGN-OS.md  (the constitution — global, every profile inherits)   ← shared design MD
        │
        ├── per-profile SOUL.md  (who this profile is + its craft rules)
        │       └── SOP SKILL.md (the step-by-step workflow)
        │       └── references/  (rubric, reference library, cheat sheets)
        │
        └── per-client DESIGN.md (brand control file, generated per job)  ← overrides defaults
```

- **`DESIGN-OS.md` (NEW — the shared design constitution / "design MD"):** the machine-readable design principles every soul inherits — the expanded anti-slop checklist, the token philosophy, typography/colour/spacing/iconography defaults, motion rules, the distinctiveness doctrine, and the QA contract. This is the single source of truth that today is duplicated across `soft-visual-design`, `taste-frontend`, `redesign`, etc. *Written: `souls/DESIGN-OS.md`.*
- **Per-profile `SOUL.md`:** identity + the domain-specific craft, loaded with researched rules. One per profile in §1.
- **SOP `SKILL.md`:** the workflow (we already have strong ones for BIP + landing; extend + add for new profiles).
- **Per-client `DESIGN.md`:** the v4 control file (upgraded structure from research R13).

> The actual soul content (rules per profile) is written into `souls/` after the dossier lands.

---

## 6. The design audit / "design MD" system

**Layered, and the deterministic layers are the gate of record** — forced by evidence: a vision LLM caught only **24%** of real usability issues and **72%** of its fix suggestions were wasted (9% harmful). The LLM is advisory only and may never assert a fact. Owned by `design-qa` (a separate, clean-context profile).

**The machine-readable "design MD":** adopt **Google Labs' `design.md` spec** (Apache-2.0) as the per-client constitution format — YAML token front-matter + Markdown rationale — and run its CLI linter (`npx @google/design.md lint`, which checks broken refs + WCAG contrast) as the L0 gate. Our `DESIGN-OS.md` + per-client `DESIGN.md` are this layer.

**The loop (per HTML deliverable):**
- **L0 — Constitution lint:** `@google/design.md lint` + token-lint (`@lapidist/design-lint` / stylelint token plugin) → fail on broken refs / off-token values.
- **L1 — Deterministic browser gates** at 1440/768/375: **axe-core** (`@axe-core/playwright`, `wcag2a`→`wcag22aa`), **Lighthouse CI** (a11y minScore 1; perf ≥0.9), HTML validity (html-validate → W3C Nu), WCAG 2.2 AA contrast (hard) + APCA advisory, the existing **anti-slop scanner** (all `[D]` rules in DESIGN-OS §3), DOM probes (real-text-not-image; `prefers-reduced-motion` present; no overflow/overlap).
- **L2 — Visual regression:** Playwright `toHaveScreenshot()` vs baseline (threshold 0.2, maxDiffPixelRatio 0.02, animations disabled, mask dynamic) — baselines generated in the CI container (macOS baselines diff against Linux).
- **L3 — Vision critique (advisory):** temp 0, structured output, "raise candidates only, never assert a number/pass-fail", optional cross-family ensemble + majority vote, calibrated against 30–50 expert examples. Opens tickets, never closes the gate.
- **L4 — Human 20%:** `design-qa` creates a `#human-review` card and blocks it; the human enforces taste/originality and gives final approval.
- **Loop behaviour:** L0–L2 failures auto-bounce the card to the maker with structured findings; cap the revise loop at 2–3 cycles then escalate; retries read prior `task_runs` failure summaries.

**Implementation step:** generalise the existing `export_inspra_ai_pilot.py` (already does Playwright screenshots + the deterministic anti-slop scan) into reusable `qa_landing_export.py` / `qa_bip_export.py`, then add the axe-core + Lighthouse + design.md-lint + `toHaveScreenshot` stages. *(Exact tool packages/versions confirmed in the verify pass; see resource library §8.)*

## 7. Model routing

**"Prototype on free, deliver on licensed."** Each role gets a FREE primary (NVIDIA NIM / Cloudflare Workers AI) and a PAID escalation. Re-verify pricing before any swap — this field moves monthly.

> **Production-model update (2026-06-15):** Kimi K2.6 underdelivered in real use, so it is **demoted from the production default.** Two findings drive the change: (1) **most generic output is a *prompting* problem, not the model** — every model collapses to slop ("Inter + purple + 3 cards") when the brief is silent, so the new dense souls + `DESIGN-OS.md` + per-client `DESIGN.md` lift *any* model; deploy that first and re-test. (2) On *design taste* (not raw code) the order is **Claude Sonnet 4.6 > Qwen 3.7 Max ≈ MiniMax M3 > Kimi K2.6 > GLM-5.1 / DeepSeek V4 / Qwen3-Coder** (the last three are strong coders but default to templated UI — they will *not* fix "generic"). **New default: draft/build on free MiniMax M3 (NIM, multimodal), deliver client-grade work on Claude Sonnet 4.6 (paid).**

| Role | FREE primary | PAID escalation | Why |
|---|---|---|---|
| Reference / vision (read screenshots/PDFs) | Gemini 3 Flash (if free key) · MiniMax M3 (NIM) · Kimi K2.6 (CF, vision) | Gemini 3 Flash $0.50/$3 · Sonnet 4.6 | must be multimodal |
| DESIGN.md drafting (brief→spec) | MiniMax M3 (NIM) | DeepSeek V4 Pro $0.44/$0.87 · Qwen 3.7 Max | cheap long-context reasoning |
| Greenfield 80% draft | **MiniMax M3 + GLM-5.1 (NIM)** — run two, fight convergence | Claude Sonnet 4.6 $3/$15 | top free WebDev; two families = no two designs alike |
| **Production build (final HTML)** | **MiniMax M3 (NIM, free, multimodal)** — new draft/build default | **Claude Sonnet 4.6 ($3/$15)** for client delivery; **Qwen 3.7 Max** (~$1.25/$3.75) for max distinctiveness; Kimi K2.6 / K2.7-Code (Cloudflare) as A/B | Sonnet = consensus best design taste, no one-shot regression; M3 is the best free model that can also read reference screenshots |
| Design critique | MiniMax M3 (NIM) = current critic | Claude Sonnet 4.6 | multimodal; cheap per draft |
| Anti-slop review | GLM-5.1 / Qwen3 Coder (NIM) — **different family than builder** | Claude Sonnet 4.6 (final gate) | avoid rubber-stamping own clichés |
| Last-mile polish | — | Claude Opus 4.8 $5/$25 · Fable 5 (flagship one-shot only) | precise pair-programmer |
| Image gen | Cloudflare FLUX-1-schnell / SDXL (prototype) | Nano Banana Pro ~$0.13/2K · FLUX.2 pro $0.03 · Recraft (vector) · Ideogram (text) · Firefly (indemnified) | §8 |
| Video / motion | — | Kling 3.0 ~$0.10/s · Veo 3.1 Fast ~$0.15/s (audio) | short loops only |

**Notes:** the critic must always be a different family than the builder (self-bias rule, §6) — so build on MiniMax M3, critique on GLM-5.1/Qwen (or vice-versa). **DeepSeek V4 is OFF free-tier builds** — its free NIM endpoint is ~131k context / 8k output (the earlier "64k cap" was a myth, but it still stalls on full builds and defaults to dated layouts); use V4 Flash via OpenRouter for bounded sub-tasks only. **Kimi K2.7 Code** (Cloudflare, 2026-06-12) is a one-ID drop-in (`@cf/moonshotai/kimi-k2.7-code`) but a *coding-efficiency* fork with no evidence of better design — A/B it for cost/reliability, not aesthetics. **Fable 5** ($10/$50, slow) is reserved for one-shot full-app / screenshot→code (reference-clone) jobs, human-gated. Re-verify availability/pricing before any swap.

## 8. Resource library

Verified June 2026 (URLs fetched during research; the V1–V4 verification reports in `research/raw/` cross-check libraries/models/pricing/audit-tools; full detail in `research/dossier/`).

**Inspiration / reference** (ingestion ladder: official MCP > public RSS > authenticated browser-capture; *never scrape a paywall, never ship a capture*. The "design API era is over" — Behance API dead, Dribbble v2 = own shots only, most galleries 403 naive fetch → use claude-in-chrome/Playwright).
- *Programmatic:* **Mobbin MCP** (621k+ app screens; ~$19/mo), **shadcn MCP** (97 blocks; free MIT; wired), **21st Magic MCP** (5 free then ~$20/mo).
- *Web/landing:* Awwwards (animation bar), Godly, Land-book (200k+ sections), **Lapa Ninja** (RSS `/index.xml` ✓), Siteinspire/Httpster (typographic), One Page Love.
- *SaaS:* SaaS Landing Page, SaaSframe (+email), Saaspo, Nicelydone, Refero.
- *Email:* **Really Good Emails** (study real table/inline-CSS builds), Email Love.

**Component libraries** (license for client work).
- *Free/MIT, drop straight into single-file HTML (best for our single-file HTML + PDF output):* **DaisyUI**, **Flowbite**, **Preline**, Tailwind raw HTML — all vanilla/Tailwind, no React.
- *Free/MIT React (use as patterns via shadcn MCP):* shadcn/ui, Origin UI (400+), Magic UI, Aceternity (⚠ default = banned purple gradients — keep mechanic, rebrand), Cult UI, Tremor (charts), Motion Primitives, Kokonut, Skiper, Tailark, React Bits (MIT+Commons Clause — use in builds, don't resell).
- *Paid, delivery-clean (recommended buys):* **Tailwind Plus** ($299, raw HTML — top priority), shadcnblocks ($79), Aceternity/Magic UI Pro (~$199 ea).
- *Bridge rule:* for React/Motion libs, read source via shadcn MCP, extract structure+timing, re-implement in plain HTML with GSAP/Motion-One. Deconstruct→Rebrand, never Capture→Ship.

**Fonts** (prototype any; deliver on a provable licence; self-host for PDF): **Fontshare** [FFL, free commercial] — Satoshi, General Sans, Switzer, Clash Display (premium, less overused); **Google Fonts** [OFL/Apache] (avoid Inter/Geist/Space Grotesk as the signature face). Record font+licence+URL in `DESIGN.md`.

**Icons** [MIT/ISC]: Lucide (baseline), Phosphor (weights/personality), Heroicons (Tailwind), Tabler (coverage), Radix (tight UI). One family per artifact; never emoji.

**Colour / tokens:** DTCG 2025.10 + **Style Dictionary** (build) [Apache]; **Radix Colors** 12-step semantic map; **OKLCH** authoring; **Leonardo** (contrast-targeted palettes); tints.dev / Realtime Colors / Huemint. Extractors (seed only, human re-maps): arvindrk/extract-design-system, Peel, FontOfWeb (DTCG export).

**Image / video models** (deliver on licensed): **Nano Banana Pro** (`gemini-3-pro-image-preview`, ~$0.13/2K, 14 refs, 94% text accuracy, SynthID) = default hero/brand; FLUX.2 [pro] ($0.03; [dev]=non-commercial); Seedream 4.5 (text-heavy); Ideogram 3 ($0.03–0.09, readable text); **Recraft V3** ($0.04/$0.08, only true SVG/vector); Adobe Firefly (IP-indemnified, ~$1k/mo API min); Qwen-Image [Apache, self-host]. Midjourney excluded (no API). *Free prototype:* Cloudflare FLUX-1-schnell / SDXL / Leonardo Lucid Origin (10k neurons/day). *Video (short loops):* Veo 3.1 Fast (~$0.15/s, audio), Kling 3.0 (~$0.10/s).

**Design-audit tooling** (the gate): axe-core (`@axe-core/playwright`), Lighthouse CI, W3C Nu validator/html-validate, Playwright `toHaveScreenshot()`, **`@google/design.md` lint** (contrast+token), `@lapidist/design-lint`; WCAG 2.2 (gate) + APCA/Bridge-PCA (advisory).

**Portable design skills** (port into souls): **Anthropic frontend-design** [MIT], **Vercel Web Interface Guidelines** [MIT, machine-checkable], Refactoring UI skill, **Black Forest Labs image skills** [MIT], OneRedOak design-review agent, bergside/awesome-design-skills (67 aesthetic packs), VoltAgent/awesome-design-md (~60 brand DESIGN.md files), GSAP/Framer scroll skills.

---

## 9. Skills consolidation (the existing ~45 Content-Os skills)

The Content-Os `Skills/` library already covers most domains but with heavy duplication and no shared token layer. v5 maps them onto the new profile structure:

| New profile | Absorbs / supersedes (Content-Os skills) | Action |
|---|---|---|
| `landing-page-studio` | `landing-page`, `landing-page-architect`, `website-copy`, `scroll-stop-builder`, `redesign` | merge into SOP + references |
| `business-pack-studio` | `bip`, `bip-architect` | merge (visual PDF + strategy/DOCX paths) |
| `linkedin-studio` | `linkedin-business-posts`, `linkedin-personal-posts`, `linkedin-content-calendar`, `linkedin-newsletter-architect` | merge near-duplicates behind a voice flag |
| `email-newsletter-studio` | `newsletter-designer` | adopt + extend with HTML-email research |
| `print-editorial-studio` | `diagram`, `diagram-excalidraw`, `brand-doc` | adopt for editorial + data-viz |
| `image-prompter` / `image-asset-lab` | `nanobanana`, `logo-creator` | adopt as the image lane |
| `design-director` | `qa-review`, `client-voice`, `soft-visual-design`, `taste-frontend`, `ux-motion` | distil into `DESIGN-OS.md` + critic prompts |
| `intake-strategist` | `client-onboard`, `brand-guide-extractor`, `autoresearch`, `lead-researcher`, `research-document-generator` | adopt for intake |
| shared | `shared/` (forbidden words, AU English, PTMRO, quality standards) | promote into `DESIGN-OS.md` |

**The biggest consolidation wins** (from the catalog): one shared design-token/brand layer; one image-model wrapper; merge the near-duplicate visual-taste skills and the near-duplicate LinkedIn-post skills; one canonical forbidden-words list (currently restated in ~6 files).

---

## 10. The Kanban board (orchestration)

Follows the converged 2025-26 multi-agent pattern: a single orchestrator (`design-director`) owns context and spawns specialists that return a **compressed summary + file references**; **writes stay single-threaded**; the numbered job folder + the constitution are the shared "blackboard" everyone reads. (Blueprint: the published "Hermes Kanban" guide, R12.)

**Seven-state machine:** `triage → todo → ready → running → blocked | done → archived`. Auto-promotion: a card stays in `todo` until every parent is `done`, then promotes to `ready`.

**Ticket schema:** `{ title, client, deliverable_type (#web/#bip/#print/#linkedin/#email/#copy/#image/#qa/#human-review), mode (greenfield|reference), assignee (profile), parents:[…], source_truth_path, status, claim_lock, summary, metadata }`. Blank assignee auto-routes to a default.

**Handoff contract (on `kanban_complete`):** `summary` = 1–3 plain-English sentences; `metadata = { produced_files:[next-folder paths], decisions, assumptions, open_questions, checks_passed }`. Heavy assets live in the folder, never the message.

**Routing rules (design-director):** decompose first → create cards → assign every card → order via `parents=[…]`; scale agents to job size (1 maker for a post; the full set with parallel makers for a website); every deliverable card gets a `#qa` child → `design-qa`; every passed `#qa` gets a `#human-review` child (the gate).

**Safety:** atomic claim (`status='running' WHERE status='ready'`); circuit breaker auto-blocks after **2 consecutive failures**; stale-claim reclaim (TTL ~15 min); every run logged to `task_runs` (the episodic memory retries read). Any invent-a-metric/logo/testimonial attempt hard-blocks immediately.

**Human gate:** exactly one — after `#qa` passes, before `#delivered`.

---

## 11. Pilot & rollout (do not build everything at once)

Honour the v4 discipline — prove repeatability before expanding.

1. **Now:** finish v5 foundations — `DESIGN-OS.md`, upgraded `DESIGN.md` schema, generalised QA/export scripts, upgraded souls for the two existing profiles.
2. **Pilot A — 2nd full client** through BIP + landing using the upgraded souls + audit loop (validates the soul upgrade end-to-end).
3. **Expansion 1:** stand up `image-prompter` + `image-asset-lab` (unblocks LinkedIn + richer BIP/landing imagery).
4. **Expansion 2:** `linkedin-studio` (highest volume, fastest ROI once image lane exists).
5. **Expansion 3:** `email-newsletter-studio`, then `print-editorial-studio`.
6. **Always-on:** `design-director` audit loop + `intake-strategist` run from Pilot A onward.
7. **Team rollout:** 4-week founder-guide program (slop detection → reference workflow → greenfield → assets/licence).

## 12. Risks & open decisions

- **MiniMax M3 role** — advisory critic vs production model (decide after Pilot A; it hallucinates proof, so keep source-truth-constrained).
- **Image quality ceiling** — confirm whether licensed image models are needed for brand-critical visuals vs free Cloudflare (research R11/V3).
- **Credential plumbing** — profiles read their own `.env`; keep the sync approach consistent.
- **DeepSeek V4** — currently failing/timeouts; do not route to it until retested.
- **Commercial licence tracking** — `asset-manifest.json` must be enforced at the human gate.

---

*Sections 6, 7, 8 and the per-profile soul content complete when research workflow `wndkltbgf` returns. Architecture (1–5, 9–12) is stable and derived from the locked v4 pilot + founder-guide + streams doc.*
