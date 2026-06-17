# Reference site + brand asset deconstruction

Use this when a client gives you a reference URL and says "build my site with the same design/style".

## Goal
Capture the reference as a *system*, not a screenshot. Extract enough structural and visual information to rebuild the same pattern in the client's brand.

## Reference site deconstruction checklist

Open the reference in the browser and capture a full-page screenshot. For each item, note the value in CSS-friendly terms (hex/HSL, px/rem, font family, font weight, spacing tokens).

### 1. Global system
- [ ] Background colors (page, alternate sections, footer, hero)
- [ ] Text colors (primary, muted, light, links, on-dark)
- [ ] Accent color usage (how many places per screen?)
- [ ] Max container width and page padding
- [ ] Grid feel (single column, 2-col, 3-col, 4-col, asymmetric split)
- [ ] Border style (color, radius, 1px solid vs shadow cards)
- [ ] Shadow system (levels, blur, opacity)

### 2. Typography
- [ ] Display / heading font vs body font
- [ ] Heading scale (H1, H2, H3, eyebrow)
- [ ] Italic / serif accent treatment inside headlines
- [ ] Line heights and letter spacing
- [ ] Body measure (max-width)

### 3. Hero composition
- [ ] Layout pattern: centered, split copy/media, full-bg, dashboard mockup
- [ ] Eyebrow → H1 → lede → CTA → proof cue → visual relationship
- [ ] CTA style (filled, outline, pill, rounded)
- [ ] Number of H1 lines on desktop

### 4. Components
- [ ] Card style (radius, border, shadow, hover)
- [ ] Icon treatment (circle bg, size, stroke, color)
- [ ] Buttons (primary, secondary, ghost)
- [ ] Tables / comparison blocks
- [ ] Stats / metric blocks
- [ ] CTA bands

### 5. Footer
- [ ] Background color
- [ ] Layout columns
- [ ] Link style and social icon treatment

## Brand asset extraction from PDF

When the client provides a branding guide as PDF:

1. **Render pages to PNG** for visual inspection:
   ```bash
   python3 - <<'PY'
   import fitz
   pdf = fitz.open('branding-guide.pdf')
   for i, page in enumerate(pdf):
       page.get_pixmap(dpi=300).save(f'page_{i+1}.png')
   PY
   ```

2. **Extract embedded images/logos**:
   ```bash
   python3 - <<'PY'
   import fitz, io
   from PIL import Image
   pdf = fitz.open('branding-guide.pdf')
   for i, page in enumerate(pdf):
       for j, img in enumerate(page.get_images(full=True)):
           xref = img[0]
           base = pdf.extract_image(xref)
           if base['ext'] == 'svg':
               open(f'logo_{i}_{j}.svg','wb').write(base['image'])
           else:
               try:
                   im = Image.open(io.BytesIO(base['image']))
                   if min(im.size) >= 80:
                       im.save(f'logo_{i}_{j}.png')
               except Exception:
                   pass
   PY
   ```

3. **Inspect rendered pages with vision** to confirm colors, logo shape, and typography notes when the extracted images are too low-resolution or missing.

## Pitfalls
- Do not skip deconstruction and jump straight to code. Capture → Ship yields a generic copy.
- A reference's *proprietary* visuals (custom illustrations, branded photography, exact layout) must be transformed; copy only the structural system.
- If the client has brand colors that clash with the reference palette, rebuild the reference's value/weight system in the brand palette, not pixel-by-pixel colors.
