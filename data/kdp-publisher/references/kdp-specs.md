# KDP Publishing Specifications

Reference for all KDP file requirements, dimensions, and constraints.

---

## Trim Sizes

### Children's & Activity Books
| Size | Use Case | Bleed Option |
|------|----------|--------------|
| 8.5" × 8.5" | Children's picture books (square) | No Bleed or Bleed |
| 8.5" × 11" | Activity books, workbooks, coloring books | No Bleed or Bleed |
| 6" × 9" | Chapter books, journals | No Bleed or Bleed |
| 5.5" × 8.5" | Small workbooks, pocket guides | No Bleed or Bleed |
| 7" × 10" | Larger workbooks | No Bleed or Bleed |

**Most popular for each type:**
- Picture books: 8.5×8.5 (full color, square)
- Workbooks/activity books: 8.5×11 (standard page)
- Journals: 6×9

---

## Margins

### No Bleed (recommended for picture books)
| Dimension | Minimum |
|-----------|---------|
| Outside margin (top, bottom, outside edge) | 0.25" |
| Inside/gutter margin (binding edge) | 0.375" for 24-150 pages |
| Inside/gutter margin | 0.5" for 151-300 pages |
| Inside/gutter margin | 0.625" for 301+ pages |

**For 8.5×8.5 No Bleed:**
- Page size in PDF: 612 × 612 pt (8.5" × 8.5" exactly)
- Safe content area: 576 × 576 pt (images and text must stay within this)
- Images touching the trim edge = **preflight failure**

### With Bleed
| Dimension | Value |
|-----------|-------|
| Bleed | 0.125" on all sides |
| Outside margin (within bleed) | 0.25" from trim edge |
| Gutter margin (within bleed) | 0.375"+ from trim edge |

**For 8.5×8.5 With Bleed:**
- PDF page size: 8.75" × 8.75" (8.5 + 0.125 each side)
- In points: 630 × 630 pt

---

## Spine Width Formulas

KDP calculates spine based on page count and paper type:

| Paper Type | Formula | Example (28 pages) |
|------------|---------|-------------------|
| White, B&W interior | pages × 0.002252" | 28 × 0.002252 = 0.063" |
| Cream, B&W interior | pages × 0.002500" | 28 × 0.002500 = 0.070" |
| White, Color interior | pages × 0.002347" | 28 × 0.002347 = 0.066" |

**Minimum spine for text: 0.25"**  
(Text on spine is only legible above ~100 pages on most trim sizes)

Use the [KDP Cover Calculator](https://kdp.amazon.com/en_US/cover-calculator) to confirm exact dimensions before creating your cover file.

---

## Cover File Specifications

### Full Wrap Cover Dimensions
```
Total Width  = Back Cover Width + Spine Width + Front Cover Width + 2 × Bleed
Total Height = Trim Height + 2 × Bleed
```

**Example: 8.5×8.5, 28 pages, white color paper:**
```
Spine        = 28 × 0.002347 = 0.0657"
Total Width  = 8.5 + 0.0657 + 8.5 + 0.25  = 17.316"
Total Height = 8.5 + 0.25                  = 8.75"
```

### Cover File Requirements
- Format: PDF (preferred) or JPG/TIFF
- Color mode: RGB (not CMYK — KDP converts to CMYK internally)
- Resolution: 300 DPI minimum at final print size
- Bleed: 0.125" on all edges
- Safety margin: Keep all important content 0.125" inside trim lines
- ISBN barcode area: Leave 2" × 1.5" clear on bottom-right of back cover
- KDP overlays its own barcode — do not add a final barcode yourself

---

## Interior File Specifications

### PDF Requirements
- Format: PDF (PDF/X-1a for best results, standard PDF accepted)
- No crop marks or printer marks
- Page size must match trim size exactly (no-bleed files) or trim+bleed (bleed files)
- All fonts embedded
- Color mode: RGB for color interiors; grayscale or B&W for B&W interiors
- Resolution: 300 DPI minimum for images at final print size

### Image Resolution Guide
| Image Size in Book | Min Pixel Width |
|--------------------|----------------|
| Full page 8.5×8.5 at 300 DPI | 2550 × 2550 px |
| Full page 8.5×11 at 300 DPI | 2550 × 3300 px |
| Half page at 300 DPI | 1275+ px wide |
| Imagen default output (1024px) | ~3.4" at 300 DPI; scales acceptably to 8" |

> **Note:** Imagen 1024×1024 output is technically 128 DPI when scaled to fill an 8" page, but KDP preflight usually accepts it. For best results, upscale images to 2550px before embedding (use Pillow `resize` with `LANCZOS`).

### Page Count Rules
- **Minimum:** 24 pages (color); 48 pages (B&W)
- **Maximum:** 828 pages
- KDP prefers even page counts
- Children's picture books: typically 24-32 pages
- Activity/workbooks: 40-200 pages

---

## Interior Types & Pricing Impact

| Interior Type | Paper Color | Printing Cost (approx.) |
|--------------|-------------|------------------------|
| Black & White | White | Lower (~$0.015/page) |
| Black & White | Cream | Similar to B&W white |
| Standard Color | White | Higher (~$0.035/page) |
| Premium Color | White | Highest (~$0.065/page) |

**Printing cost example:**
- 28-page color interior, 8.5×8.5: ~28 × $0.035 = ~$0.98 base + fixed cost
- Actual KDP printing cost for 28-page color 8.5×8.5: approximately $3.00-$4.50

---

## Ebook Specifications (EPUB/Mobi)

Not typically used for children's picture books or activity books (print-only).

- Format: EPUB 3 (preferred), MOBI, or DOCX
- Images: RGB, 72-96 DPI acceptable for ebook
- Cover image: Min 1600 px wide, max 10,000 px; JPG or PNG
- For illustrated books: Use fixed-layout EPUB to preserve image positioning

---

## Royalty Calculation

### Paperback (all prices)
```
Royalty = 0.60 × (List Price - Printing Cost - Amazon Fee)
Amazon Fee = 0.15 × List Price  (included in 60% calc)
Net Royalty ≈ 0.60 × List Price - Printing Cost
```

### Ebook — 70% Royalty (requires $2.99-$9.99 price)
```
Royalty = (List Price × 0.70) - Delivery Fee
Delivery Fee ≈ $0.06/MB average
```

### Ebook — 35% Royalty (any price)
```
Royalty = List Price × 0.35
```

**Optimal pricing for picture books:**
- Paperback: $12.99-$14.99
- Ebook: $3.99-$4.99 (if offered)

---

## File Upload Process

1. Log into KDP → Create New Title → Paperback
2. Enter metadata (Title, Author, Description, Keywords, Categories)
3. **Upload interior:** Upload interior PDF → wait for "COMPLETED" status
4. **Upload cover:** Upload cover PDF (full wrap) or use Cover Creator
5. Preview with KDP Previewer (3D + interior viewer)
6. Set pricing for each marketplace
7. Disclose AI-generated content (text and/or images)
8. Submit for review (typical: 12-72 hours)

---

## ISBN

| Option | Cost | Notes |
|--------|------|-------|
| KDP Free ISBN | Free | KDP is publisher of record |
| Own ISBN | $125 (single) / $295 (10-pack) | You are publisher of record |

For starting out, KDP free ISBN is recommended. Purchase your own when expanding to other retailers (Ingram Spark, Barnes & Noble, etc.).

---

## AI Content Disclosure (Required)

Amazon KDP requires disclosure of AI-generated content since 2023:

- **Disclose:** AI-generated text (even if heavily edited), AI-generated images
- **No disclosure needed:** AI grammar/spelling assistance, AI outlining/brainstorming, AI proofreading
- **Location:** During book creation/editing in KDP dashboard, under "Content" section
- **Field:** "Does this book contain AI-generated content?" → Yes, and specify (text/images)

Non-compliance risks: title removal or account suspension.

---

## Quick Reference Card

```
8.5×8.5 picture book, no bleed, 28 pages, white color:
  Interior PDF : 612 × 612 pt (8.5" × 8.5"), content within 576×576 pt
  Cover PDF    : 17.316" × 8.75" (spine = 0.0657")
  Min pages    : 24
  DPI          : 300 min

8.5×11 workbook, no bleed, 100 pages, white B&W:
  Interior PDF : 612 × 792 pt (8.5" × 11"), 0.5"+ margins
  Cover PDF    : 17.225" × 11.25" (spine = 0.2252")
  Min pages    : 48
```
