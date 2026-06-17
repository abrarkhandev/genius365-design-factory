---
name: business-information-pack-production
description: Use when creating or improving a Business Information Pack PDF from assets, transcripts, DOCX/PDF briefs, or a website URL.
version: 1.0.0
created_by: agent
---

# Business Information Pack Production SOP

## Trigger
Use this skill whenever the task is to create, improve, critique, or plan a BIP / Business Information Pack.

## Definition
A BIP is a client-ready PDF that explains:
- what the business/product does
- who it serves
- problems it solves
- services/products/offerings
- process / how it works
- differentiators
- proof and credibility
- next step / contact

## Required workflow

### 0. Model routing and design-control files
Before building the BIP, ensure these source-truth files exist:

```text
clients/<client>/02-source-truth/client-facts.json
clients/<client>/02-source-truth/DESIGN.md
clients/<client>/02-source-truth/system-spec.md   # required for reference/clone-inspired work
```

Use the Design Hermes NIM router before final production where useful:

```bash
# MiniMax M3: editorial/design critique, distinctive move, anti-slop review
python3 factory/scripts/design_model_router.py --role design-critic --context-file clients/<client>/02-source-truth/client-facts.json --context-file clients/<client>/02-source-truth/DESIGN.md
python3 factory/scripts/design_model_router.py --role distinctive-move --context-file clients/<client>/02-source-truth/DESIGN.md
python3 factory/scripts/design_model_router.py --role anti-slop-review --context-file clients/<client>/04-production/bip/bip.html
```

Model roles:
- `minimaxai/minimax-m3` = free NIM design director / craft critic for BIP information architecture, visual hierarchy, and anti-slop checks. Keep it source-truth constrained because it may otherwise suggest invented proof.
- `qwen/qwen3.5-122b-a10b` = free NIM reference/system-spec reader.
- Cloudflare Kimi K2.6 remains the stable production model until NIM production quality is proven on multiple pilots.

### 1. Intake mode detection
Classify the input:
- **Mode A:** assets folder + Fathom transcript/DOCX/PDF/brief.
- **Mode B:** existing website URL.
- **Mode C:** existing BIP to improve.
- **Mode D:** mixed materials.

### 2. Extract source-truth
Create or update:
- `client-facts.json`
- `client-facts.md`
- `assumptions.md`
- `brand-kit.md`

Extract:
- one-line positioning
- business summary
- audience segments
- problems solved
- services/offers/products
- inclusions and outcomes
- process/how it works
- proof/testimonials/case studies
- differentiators
- founder/team credibility
- CTA/contact
- unknowns/missing proof

Never invent proof.

### 3. BIP information architecture
Before design, produce a page plan:
1. Cover / promise
2. Business overview
3. Audience / problem
4. Solution / value proposition
5. Services / offerings
6. How it works / process
7. Use cases / industries
8. Differentiators
9. Proof / results / testimonials
10. Team/founder credibility if relevant
11. CTA / contact

Adjust page count to fit the client. Do not force all sections if not useful.

### 4. Reference pass
Gather 5–10 relevant references:
- company profile PDFs
- capability statements
- service brochures
- pitch decks
- competitor pages
- strong editorial layouts

Record what works and what to avoid.

### 5. Copywriting pass
Rewrite into clear sales language:
- concise, outcome-led headings
- scannable blocks
- service cards with inclusions/outcomes
- proof linked to buyer objections
- no vague filler

### 6. Visual/page system
Define:
- page grid
- typography scale
- colour system
- section/card patterns
- diagrams/process visuals
- image usage
- icon style
- CTA treatment

Prefer HTML/CSS source for repeatable PDF export where possible.

### 7. QA rubric
Score each 0–2:
1. Business clarity
2. Audience/use-case clarity
3. Service/offering structure
4. Value proposition
5. Proof/credibility
6. Differentiation
7. Offer depth
8. Visual hierarchy
9. Brand consistency
10. Sales usefulness
11. Contact/next step
12. Export quality

Pass:
- 18/24 acceptable
- 21/24 client-ready
- Any 0 in business clarity, service/offering structure, proof, or export quality requires revision.

### 8. Handoff
Deliver:
- final PDF
- editable source
- copy/source-truth files
- asset folder
- QA score
- assumptions/missing proof notes
