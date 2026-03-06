# KDP Quality Assurance Checklist

Run this checklist before uploading any book to KDP. The goal: no AI gibberish, no mismatched content, no silent preflight failures.

---

## Before Generation

### Story / Content Planning
- [ ] Prompt is specific enough to produce consistent characters and setting
- [ ] Age group and tone defined (ages 3-5 = ultra simple; ages 5-8 = slightly more complex)
- [ ] Character reference written down: name, appearance, colors, defining features
- [ ] Book type confirmed: picture book / activity book / coloring book / workbook
- [ ] Page count target set (24-32 for picture books; 50-80 for activity; 80-150 for workbooks)

### Image Prompts
- [ ] Every image prompt includes: `no text, no words, no letters, no writing`
- [ ] Style established on first image; subsequent prompts reference it explicitly
- [ ] Character description is consistent in all illustration prompts

---

## After Story Generation (Before Images)

- [ ] Read entire story aloud (or TTS) — catch awkward phrasing
- [ ] Spell check all text
- [ ] Character names are consistent throughout (no draft leftovers like "Character_Name")
- [ ] Word count per page is appropriate for age group
- [ ] Moral/lesson is clear and age-appropriate
- [ ] Dedication text finalized
- [ ] Back-cover description written from the **finished story** (not the original prompt)

---

## After Image Generation

### Each Image — Visual Inspection Required
- [ ] No AI text artifacts (gibberish, misspelled words, stray letters)
- [ ] No watermarks or logos
- [ ] Character looks consistent across all pages (same colors, features, proportions)
- [ ] Scene matches the story text on that spread
- [ ] Image is not blurry or corrupted
- [ ] Image is clean — no unexpected objects, disturbing content, inappropriate themes

### Run Automated Check (Optional)
```bash
python3 validate-book.py --images output/my-book/images/ --check-text-in-images
```

---

## Interior PDF Checks

- [ ] Open PDF in a viewer (Preview, Adobe Reader) at 100% zoom
- [ ] Check first page (title page): title, subtitle, author name all correct
- [ ] Check dedication page
- [ ] Every spread has its illustration
- [ ] Every spread has its story text — no spreads missing
- [ ] Text is readable — no encoding issues with special characters
- [ ] No blank pages where there shouldn't be
- [ ] "The End" page present
- [ ] About the Author page (optional but professional)
- [ ] Page count is even and within range (24-32 for picture books)
- [ ] All images are sharp, no compression artifacts

```bash
# Validate automatically:
python3 validate-book.py --interior output/my-book/interior.pdf --book-type picture-book
```

---

## Cover Checks

- [ ] Open cover PDF at 100% zoom
- [ ] Title is correct and readable
- [ ] Author name is correct
- [ ] Cover image has no AI text artifacts
- [ ] Spine (if visible): text is correct and readable
- [ ] Back cover description matches the actual story
- [ ] Bottom-right of back cover: ISBN area is clear (2"×1.5" white space)
- [ ] Bleed extends 0.125" beyond trim on all edges
- [ ] All important content is 0.125" inside trim lines

```bash
# Validate dimensions:
python3 validate-book.py --cover output/my-book/cover.pdf --pages 28 --trim 8.5x8.5
```

---

## Metadata Checks

- [ ] Title exactly matches cover
- [ ] Subtitle (if any) correct
- [ ] Author name matches pen name
- [ ] Description: 150-400 characters, written from final story, no spoilers
- [ ] 7 keywords filled — all relevant, 50 chars max each, use phrases not single words
- [ ] 2 categories chosen (research BSR rankings first)
- [ ] Age range accurate
- [ ] AI disclosure marked: Yes (if text or images are AI-generated)
- [ ] Language: English (or correct language)

---

## KDP Upload Checks

- [ ] Reload the KDP page before starting upload (avoid stale form state)
- [ ] Interior uploaded successfully → status shows "COMPLETED"
- [ ] Cover uploaded successfully → no error messages
- [ ] KDP Previewer: check first page, a middle spread, last page
- [ ] KDP Previewer: 3D view looks correct (title on cover, spine readable)
- [ ] Pricing set for all target marketplaces (US, UK, CA, AU minimum)
- [ ] AI content disclosure completed

---

## Book-Specific Notes

### Picture Books (8.5×8.5)
- Images must fit within 576×576 pt content area on 612×612 pt page (no-bleed)
- If images are bleeding, use Ghostscript to add margins: `gs -sDEVICE=pdfwrite -o fixed.pdf -c "<<BeginPage>> 0.94 0.94 scale 18 18 translate <<EndPage>>" -f interior.pdf`

### Math Workbooks
- **Never add a separate answer line below equations** — kids write directly below the math line
- Include section headings, clear problem numbering, and answer key at back
- Check that all problems have correct difficulty for target grade

### Coloring Books
- Confirm images are pure black line art on white — not grayscale
- If any gray tones appear, regenerate or convert: `convert page.png -threshold 50% bw_page.png`
- Leave back sides of pages blank (prevent marker bleed-through)

### Activity Books
- Test each puzzle/activity yourself: can a child actually complete it?
- Ensure answer key matches every puzzle
- Check that difficulty progression makes sense (easy → harder)

---

## Final Sign-Off

- [ ] Book title confirms correct  
- [ ] All pages verified (spread count, page count, no blanks)
- [ ] All images inspected for AI artifacts
- [ ] Description verified against final story
- [ ] Metadata complete and accurate
- [ ] AI disclosure done
- [ ] Cover dimensions validated
- [ ] KDP Previewer reviewed

**→ Ready to publish.**

---

*Encode this process into scripts wherever possible. Human review is still required for image inspection and description verification.*
