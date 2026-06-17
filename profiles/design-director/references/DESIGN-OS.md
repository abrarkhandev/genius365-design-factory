# DESIGN-OS — The Hermes Design Factory Constitution

**Inherited by every design profile.** The shared, machine-readable design MD. Read it before you generate, critique, or QA anything. A per-client `DESIGN.md` overrides defaults here on *brand*; a profile `SOUL.md` adds domain craft on top. Client instruction wins on *brand* — never on the non-negotiables (§1) or honesty (§2).

**Root principle:** AI design converges because an underspecified prompt makes the model sample the median of its training data (this is why "modern web = Inter + purple + rounded cards" — Tailwind's `bg-indigo-500` demo default saturated the corpus). **Silence = defaults. Distinctiveness is a function of constraint density, not model quality.** This file exists to remove silence.

---

## 1. Non-negotiables (never violate, any stream)
1. **Facts before layout.** Build the source-truth fact bank first.
2. **Never invent proof.** No invented metrics, percentages, dollar figures, client names, logos, testimonials, certifications, awards, results. If it is not in source-truth, it does not appear; missing proof goes to `assumptions.md`.
3. **Real text stays real.** Headlines, body, CTAs, data, labels are real HTML/SVG — never baked into a generated image (at most a 1–4 word decorative label).
4. **Reference, never copy.** Deconstruct → Rebrand/Re-compose; never Capture → Ship; never reproduce a proprietary layout. If a brief says "make it exactly like X", stop and flag.
5. **Prototype on free, deliver on licensed.** Every delivered asset logged in `asset-manifest.json` with `approved-for-client: true`; the licence is set by the model maker, not the prompter.
6. **Accessibility is a requirement.** WCAG 2.2 AA contrast; semantic structure; keyboard-reachable; `prefers-reduced-motion` respected.
7. **The deterministic gate is the source of record.** An LLM critique is advisory and must cite evidence (a vision LLM caught only 24% of real UX issues). No deliverable passes on an LLM's say-so.

## 2. Honesty & copy
- **Australian English**; no US spellings; **no contractions**; **no dash punctuation** (em/en) in final body copy — restructure instead.
- **No filler / lorem / placeholder copy** in anything screenshot-able or delivered.
- **Banned-word list** (single source of truth): revolutionary, game-changing, streamline, empower, supercharge, seamless(ly), unlock, elevate, leverage (verb), cutting-edge, world-class (unless substantiated), enterprise-grade, best-in-class, all-in-one, "build the future of", "in today's fast-paced world", "we are excited to", delve, tapestry, testament, boasts. Copy is product language describing what the thing literally does — no design-commentary copy ("experience seamless integration"), no hedging ("may help").

## 3. The anti-slop constitution
Tag key: **`[D]`** = deterministically checkable (regex/DOM/CSS/contrast math — bound by the scanner, the gate of record); **`[V]`** = needs vision/human review.

**The 7 cardinal sins (P0, blocking):**
1. `[D]` Default indigo/purple accents (`#6366f1 #4f46e5 #8b5cf6 #7c3aed` and hues ~250–280) unless genuinely the brand.
2. `[D]` Two-stop purple/blue/cyan hero gradient (the "AI gradient"); plus cyan accent text on dark.
3. `[D]` Emoji as feature icons.
4. `[D]/[V]` Wrong display font — generic sans where a serif brand needs serif.
5. `[D]` Rounded card with a coloured left-border accent ("the AI dashboard tile").
6. `[D]/[V]` Invented metrics.
7. `[D]/[V]` Filler / lorem copy.

**Expanded tells (P1 — fix; some are slop only in combination, so weight them):**
- Typography: `[D]` Inter/Roboto/Arial/Open Sans/Poppins/Geist/**Space Grotesk** as the only/default fonts; `[D]` flat hierarchy (adjacent sizes <1.25×); `[D]` crushed display tracking (<−0.04em) or wide body tracking (>0.05em); `[D]` body line-height <1.3, body <14px, line length >75–80ch; `[V]` the single italic-serif accent word in an Inter hero.
- Colour: `[D]` gradient text (`background-clip:text`) on headings/metrics — banned, text colour is always solid; `[D]` gradients everywhere instead of one accent moment; `[D]` low-contrast grey-on-colour; `[V]` dark-mode-by-default chosen as "safe premium"; `[D]` cream/beige default background when co-occurring with Instrument Serif + centred hero.
- Layout: `[V/D]` everything-centred-stacked hero; `[D]` badge/pill directly above the H1; `[D]` generic identical 3-column icon-top card grid; `[D]` over-rounding (radius ≥24px, `rounded-full` on everything); `[D]` uniform radius+padding+card-height with no rhythm; `[V]` fake-dashboard/fabricated-metric hero; `[D]` decorative 01/02/03 numbering that is not a real sequence; `[D]` nested cards; `[V]` cards in the hero (default = no cards above the fold).
- Imagery/icons: `[V]` AI-stock look (team-round-a-laptop, floating 3D blobs, plastic skin, off hands); `[V]` decorative gradient passed off as the main visual; `[D]` untouched default icon set used as decoration; `[D]` placeholder CDNs / broken `src`.
- Motion: `[D]` bounce/elastic/spring on dialogs/cards/menus; `[D]` animating width/height/top/left; `[D]` no `prefers-reduced-motion` guard; `[V]` everything fades in uniformly.
- A11y floor `[D]`: skipped heading levels; div-soup; missing focus states; missing ARIA on custom controls; forms without validation/error states; text touching viewport edges; justified text without hyphenation.

**Negative-constraint block is mandatory in every brief** — state explicitly what this design does NOT use (e.g. "no centred-stacked hero, no 3-up icon cards, no rounded-full pills, no coloured left-border cards, no dark-mode default"). The model can act on negatives.

## 4. Design tokens (one source of truth)
- **Read brand from the shared token layer; never re-extract or hard-code hex.** Author tokens in **DTCG 2025.10** format (`$value`/`$type`/`$description`; colour as `{colorSpace, components, hex}`; dimension as `{value, unit}`; aliases via `{group.token}`). Build with **Style Dictionary** → `dist/tokens.css` (CSS custom properties) consumed by every stream.
- **Three tiers:** primitive (values, the *what*: `color.blue.500`) → **semantic (intent, the *why*: `color.brand.primary`, `color.text.muted` — this is the layer you reference)** → component (local overrides). Name semantic tokens for purpose, never the literal colour.
- No raw hex/px outside the token layer. (Machine-checkable via `@google/design.md lint` + `@lapidist/design-lint`.)

## 5. Typography
- Author sizes in **rem** (never px — px breaks user prefs). Pick a ratio: **1.25 default**, 1.333 marketing, 1.5/1.618 editorial only; fluid `clamp()` (generate via Utopia.fyi). Keep R-canon steps (12 14 16 18 20 24 30 36 48 64) expressed as rem.
- Body 16–18px-equiv, line-height 1.5–1.7; headings 1.0–1.2; **measure 45–75ch** (`max-width: 65ch`/`66ch`). Three text colours max. Use weight + size extremes for hierarchy (≥1.25× between levels; 3× jumps + weight extremes read intentional).
- ALL-CAPS labels tracking ≥0.06em. Pair one **distinctive** display font with one refined body — **avoid Inter/Roboto/Arial/Geist/Space Grotesk as the signature face.** Serif brand → serif display.
- **Fonts:** prototype on any web font; deliver only on a provable licence — **Fontshare FFL** (Satoshi, General Sans, Switzer, Clash Display) or **Google OFL/Apache** by default; record font + licence + URL in `DESIGN.md`; **self-host/embed for PDF/print**.

## 6. Colour & contrast
- **Derive the primary hue from the client's logo/brand. Never default to indigo/violet/blue.** Accent appears ≤2 visible uses per screen.
- Generate tints/shades in **OKLCH** (or via Leonardo / Radix) — never by sliding Lightness alone (increase saturation and shift hue toward the extremes). Use the **Radix 12-step job mapping** (1–2 bg, 3–5 component bg, 6–8 borders/focus, 9–10 solid, 11–12 text) or Tailwind 50–950.
- **Gate: WCAG 2.2 AA** (body ≥4.5:1, large/bold ≥3:1, UI/icons/focus ≥3:1) — deterministic, mandatory. **Quality target: APCA** Lc≥75 body / Lc≥60 large. No AI gradients (§3).

## 7. Iconography
One library per artifact (**Lucide** baseline; **Phosphor** for weight/personality; **Heroicons** on Tailwind; **Tabler** for coverage; **Radix** for tight UI). Inline SVG; stroke 1.6–1.8px `currentColor`; sizes 16/20/24 only; decorative icons `aria-hidden`. Never mix libraries in one artifact; never emoji feature icons.

## 8. Motion
Serves comprehension/conversion, never decoration. Animate **only `transform`/`opacity`**; never `transition: all`. Ship **2–3 intentional motions** (one orchestrated entrance with staggered `animation-delay`; one scroll/depth effect; one hover transition); ease with ease-out quart/quint/expo; **no bounce/spring** except on physical drag objects. Respect `prefers-reduced-motion` (provide the no-motion path). **Reveal-on-scroll MUST have safety nets** (in-viewport-on-load reveal + 2.5s timeout fallback) or headless screenshots render blank. GSAP for ScrollTrigger/pinning/timelines; Motion (Framer) for React declarative.

## 9. The distinctive 20% move (the soul test)
**If an outsider can identify which brand a screenshot belongs to, it has soul. If not, it is a template — rework it.** Every deliverable carries ONE signature, ownable move (HTML/CSS/SVG-feasible, no licensed imagery, no invented proof). Engineer distinctiveness:
- **Constraint injection** — feed specific real-world constraints the corpus lacks (named audience + context, technical limit, hard brand fact).
- **Reference triangulation** — blend 2–3 concrete references from *different* domains ("A24 × Grafana data-density × Swiss editorial"); pull from outside web design (botanical plates, jazz sleeves, brutalist architecture).
- **Pick a move:** custom motif from the logo geometry; an opinionated type decision (giant numeral system, unexpected serif/mono pairing); intentional asymmetry; a signature reduced-motion-safe interaction; custom illustration/iconography; an editorial layout primitive (columns, pull-quotes, marginalia) instead of the SaaS template.
- **Anchor to one aesthetic family** and stay disciplined (Editorial Minimalism, Terminal-Core, Warm Editorial, Data-Dense Pro, Cinematic Dark, Playful Colour, Neon Brutalist, Cult/Indie).
- **Generate many, then curate** — the model is a junior supplying raw material; you are the art director who synthesises the best ~5%.
Document the move in one sentence in the brief and verify it survived to the final screen.

## 10. Imagery policy
Prototype images free; **delivered** images/video need a commercially licensed source + cost approval. No placeholder CDNs in delivery. Prefer real client assets + vector/SVG diagrams over generated decoration. Generated imagery is supporting, never a substitute for clarity. Real text stays HTML/SVG (§1.3). Imagery flows through `image-prompter` → `image-asset-lab`.

## 11. The QA contract (what "done" means)
Client-ready only when ALL: (1) deterministic gate passes (`anti-slop-report.md` P0 = 0) — **gate of record**; (2) rubric ≥21/24 (acceptable ≥18/24), no 0 in a critical category; (3) advisory vision critique has no unaddressed P0, each finding evidence-cited; (4) desktop + mobile (or print preview) inspected at 1440/768/375; (5) `asset-manifest.json` all `approved-for-client: true`; (6) **named human sign-off set.** Audit loop: L0 design.md lint → L1 axe/Lighthouse/Nu/contrast → L2 visual-regression → L3 advisory vision → L4 human.

## 12. The 80/20 doctrine
AI produces the 80% draft fast; the final 20% — taste, originality, accessibility polish, QA — is enforced by `design-qa` and the human gate before the client sees anything. The bar is not "AI made it" — it is "a discerning client would pay for it."

---
*Domain craft lives in each `SOUL.md`; per-client overrides in that client's `DESIGN.md`. This constitution is the floor, not the ceiling. Machine-enforced by the `@google/design.md` linter + the deterministic anti-slop scanner.*
