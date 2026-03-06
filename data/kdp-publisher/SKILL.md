---
name: kdp-publisher
description: Helps agents create, format, and publish children's books and activity books to Amazon KDP. Covers the full pipeline from story prompt through PDF assembly, cover creation, and upload guidance. Triggers on KDP publishing, children's book creation, activity book generation, book formatting, Amazon self-publishing, and book cover design.
---

# kdp-publisher

Helps agents create, format, and publish children's books and activity books to Amazon Kindle Direct Publishing (KDP). Covers the full pipeline from story generation through KDP upload.

## Triggers

Load this skill when the user mentions:
- KDP, Kindle Direct Publishing, Amazon self-publishing
- Children's book creation, picture book, storybook
- Activity book, coloring book, workbook, puzzle book
- Book formatting, PDF for print, cover design, book cover wrap
- KDP upload, manuscript upload, interior PDF

---

## Supported Book Types

| Type | Trim Size | Interior | Notes |
|------|-----------|----------|-------|
| Children's picture book | 8.5×8.5" | Full color | Illustration + text spreads |
| Activity book | 8.5×11" | Color or B&W | I Spy, dot-to-dot, etc. |
| Coloring book | 8.5×11" | B&W | Thick clean lines, no shading |
| Math workbook | 8.5×11" | B&W | Practice problems + answer key |
| Puzzle book | 8.5×11" | B&W | Word search, sudoku, crossword |

---

## Core Workflow

```
prompt → story generation → illustration → interior PDF → cover PDF → metadata → KDP upload
```

### Step 1 — Generate story and plan

Use `scripts/generate-book.py` for picture books. For workbooks/puzzles, use a puzzle generator tool (BookBolt, custom scripts).

```bash
python3 scripts/generate-book.py "a curious octopus who learns to share" \
  --type picture-book \
  --age-group 3-5 \
  --style watercolor \
  --output-dir output/
```

**Story requirements:**
- Title ≤ 60 characters
- 12 spreads → 24 story pages → ~28 pages total (title + dedication + The End + author bio)
- Ages 3-5: 10-20 words per spread, simple/repetitive sentences
- Ages 5-8: 20-40 words per spread, clear story arc
- Always include moral/lesson, dedication, back-cover description, 7 keywords

### Step 2 — Generate illustrations

**Critical image rules:**
- ALWAYS add "no text, no words, no letters, no writing" to every image prompt
- Define character reference (colors, features, accessories) before generating spread #1
- Reference first image style in all subsequent prompts: "match the watercolor style of page 1"
- Use 1:1 aspect ratio for 8.5×8.5 picture books; use 3:4 for 8.5×11 activity books
- Minimum 300 DPI for print — Imagen 1024px = ~3.4" at 300 DPI, which is fine for a scaled-up 8.5×8.5 page
- Inspect every image for AI text artifacts before embedding in PDF

### Step 3 — Assemble interior PDF

See `references/kdp-specs.md` for exact dimensions.

**8.5×8.5 No Bleed (picture books):**
- Page size: 612×612 pt
- Content area: 576×576 pt (0.25" margins on all sides)
- Images MUST fit within the content area — do not let image touch trim edge on a no-bleed file
- Layout: odd pages = illustration, even pages = text (or full-spread alternate)

**Text rules:**
- Embed fonts (ReportLab: register TTFont before use)
- Font size ≥ 14pt for ages 3-5; use centered text, generous leading
- No text inside AI images — overlay programmatically after generation

### Step 4 — Create cover

Use `scripts/create-cover.py` for the full wrap PDF (front + spine + back + bleed):

```bash
python3 scripts/create-cover.py \
  --title "The Curious Octopus" \
  --author "Your Name" \
  --pages 28 \
  --paper white \
  --front-image output/curious-octopus/images/cover.png \
  --back-text "Follow Otto the octopus as he discovers the joy of sharing..." \
  --output output/curious-octopus/cover.pdf
```

**Spine width formulas (KDP standard):**
- White paper B&W: pages × 0.002252 inches
- Cream paper B&W: pages × 0.0025 inches
- White paper color: pages × 0.002347 inches

**Cover dimensions (8.5×8.5, white color, 28 pages):**
- Spine width: 28 × 0.002347 = 0.0657"
- Total cover width: 8.5 + 0.0657 + 8.5 + 0.25" bleed = 17.316"
- Total cover height: 8.5 + 0.25" bleed = 8.75"

**Cover design rules:**
- Put title + author text as a PDF overlay — never bake text into the AI cover image
- Leave bottom-right 2"×1.5" of back cover clear for ISBN barcode
- Spine text is optional for books < 100 pages (too narrow to read)
- KDP will overlay its own barcode on the back cover — leave space

### Step 5 — Write metadata

**Description rules:**
- Write from the finished story, NOT from the prompt or outline
- Use character names exactly as they appear in the final text
- 2-3 sentences: hook + plot + moral/appeal
- Include age range in description text ("Perfect for ages 3-6")
- Do not keyword-stuff; Amazon indexes naturally

**KDP metadata fields:**
- Title + subtitle (subtitle is optional but good for search)
- Author: pen name
- 7 backend keywords (use all 7 slots; 50 chars each; use phrases not single words)
- 2 categories (research BSR before choosing)
- Language, publication date
- AI-generated content disclosure: required if text or images are AI-generated

### Step 6 — Validate before upload

```bash
python3 scripts/validate-book.py \
  --interior output/curious-octopus/interior.pdf \
  --cover output/curious-octopus/cover.pdf \
  --metadata output/curious-octopus/metadata.json
```

Checks: page count, trim dimensions, image resolution, no-text-in-images, description/story consistency.

### Step 7 — Upload to KDP

**Browser automation rules (critical):**
- Do NOT use Playwright `type` on KDP form fields — focus shifts and input breaks
- Use JavaScript `evaluate` with element IDs:
  ```js
  document.getElementById('data-print-book-title').value = 'The Curious Octopus';
  document.getElementById('data-print-book-title').dispatchEvent(new Event('input', {bubbles:true}));
  ```
- File uploads require CDP `DOM.setFileInputFiles` + change event (Playwright upload action doesn't work):
  ```js
  // After DOM.setFileInputFiles:
  document.querySelector('input[type=file]').dispatchEvent(new Event('change', {bubbles:true}));
  ```
- Wait for `#data-print-book-interior-processing-status` to show COMPLETED before proceeding
- Reload KDP page before each upload session — stale form state causes silent failures

**Category selection:**
- Use the cascade-select dropdowns in the category modal
- After selecting all levels, JS-click the placement checkbox (don't Playwright-click)

---

## Activity Books & Workbooks

For non-narrative books, skip the story generation step. Instead:

1. Plan content structure (sections, problem counts, difficulty levels)
2. Generate content programmatically or with a puzzle generator
3. Layout with ReportLab or a worksheet template
4. Apply the same cover + metadata workflow

**Math workbook rules:**
- Do NOT add answer lines below equations — kids write directly below the problem line
- Use ≥ 14pt font for problem numbers; ≥ 20pt for the math itself
- Include answer key as last section
- 8.5×11", 1" margins, B&W interior

**Coloring book rules:**
- Image prompts: "simple black and white coloring page, thick lines, no shading, age-appropriate"
- Do not use grayscale images — must be pure black line art on white background
- Leave blank back sides of pages to prevent marker bleed-through

---

## Pricing Quick Reference

| Book Type | Paperback Price | Expected Royalty/Sale |
|-----------|----------------|-----------------------|
| Kids picture book | $12.99 | ~$5.00 |
| Activity book (color) | $8.99-$10.99 | ~$3.10-$4.50 |
| Math/puzzle workbook | $9.99-$12.99 | ~$4.30-$6.00 |
| Coloring book | $7.99-$9.99 | ~$3.30-$4.50 |

Use 70% royalty tier: price must be $2.99-$9.99 for ebooks. Paperbacks always use 60% tier.

---

## Amazon Ads Quick-Start

See `references/ads-quickstart.md` for full setup. Summary:
- Start with Automatic Targeting, $5/day
- After 2 weeks, harvest converting search terms → Manual Exact Match campaign
- Target ACoS: 30-45%
- Kill keywords: 8+ clicks, 0 sales → reduce bid to $0.02
- Scale: increase bids 20% on keywords with ACoS < 20%

---

## Key Lessons

These were learned through production and would not be obvious from KDP documentation:

1. **KDP form automation**: Use JS evaluate + element IDs. Never use browser `type` action — fields shift focus mid-input.

2. **File upload via CDP**: Standard Playwright upload fails on KDP. Use `DOM.setFileInputFiles` + dispatch change event. See TOOLS.md for full script path.

3. **Spine width formula**: White paper B&W = `pages × 0.002252`. White paper color = `pages × 0.002347`. This is what KDP Cover Calculator gives you.

4. **8.5×8.5 No Bleed margin**: Images must fit within 576×576 pt content area on a 612×612 pt page. Images touching the trim edge will fail KDP preflight.

5. **No text in AI illustrations**: Every image prompt must include "no text, no words, no letters". Text baked into AI images is often garbled. Always overlay text programmatically.

6. **Descriptions from finished content**: Never write the description from the original prompt. Write it after the story is final — use actual character names and plot.

7. **KDP categories**: Select via cascade dropdowns in the modal, then JS-click the placement checkbox. Don't rely on Playwright click for the final checkbox.

8. **Math workbooks**: No answer lines below equations. Kids write below the problem line.

9. **Stale form state**: Reload the KDP page before each upload session. Uploading a second file to a page already mid-process fails silently.

10. **AI disclosure**: Amazon requires disclosure if text OR images are AI-generated. Select Yes during upload. Non-disclosure can result in account action.

---

## References

- `references/kdp-specs.md` — Trim sizes, margins, bleed, spine width tables, file requirements
- `references/qa-checklist.md` — Pre-upload quality checklist
- `references/niche-guide.md` — Profitable niches with pricing and competition data
- `references/ads-quickstart.md` — Amazon Ads campaign setup and optimization

## Scripts

- `scripts/generate-book.py` — Full book generation pipeline (story + illustrations + interior PDF)
- `scripts/create-cover.py` — Standalone cover wrap PDF generator
- `scripts/validate-book.py` — Pre-upload validator

## Dependencies

```bash
pip install reportlab Pillow google-genai PyPDF2
# Optional for validation:
pip install pytesseract  # OCR-based text-in-image detection
```

API key: Set `GOOGLE_AI_API_KEY` env var, or pass `--api-key`, or create `~/.clawdbot/credentials/google_ai.json` with `{"api_key": "..."}`.
