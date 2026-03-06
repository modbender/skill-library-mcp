# E-commerce Product Photography

## Resolution & Dimensions

- **Minimum:** 1000 × 1000 px (enables Amazon zoom)
- **Recommended:** 2000 × 2000 px
- **Aspect ratio:** 1:1 for main images
- **Zoom requirement:** 3x without pixelation (needs 2000px+ source)
- **For jewelry/small items:** Minimum 1500px on longest edge

---

## Background Requirements

- **Main product image:** Pure white RGB(255, 255, 255)
- **Tolerance:** No more than 5 RGB variance (250-255 OK)
- **Product fill:** 85-95% of frame (Amazon requires 85% minimum)
- **No watermarks, logos, or text** on main image
- **Edge quality:** Clean, anti-aliased, 1-2px feathering

---

## Shadow & Reflection

- **Drop shadow:** 15-25% opacity, 5-10px offset, 20-30px blur
- **Reflection (if used):** Maximum 30% opacity, fade within 20% of height
- **Shadow angle:** Same across entire catalog (typically 135°)
- **Contact shadow:** 3-5px soft edge at product base

---

## Color Accuracy

- **Color variance:** Maximum ΔE of 2.0 from actual product
- **White balance:** 5500-6500K (daylight neutral)
- **Color profile:** sRGB embedded
- **Never auto-enhance colors** without validation
- **Document hex codes** for brand colors

---

## Marketplace Requirements

| Platform | Min Pixels | Background | Max Size | Format |
|----------|-----------|------------|----------|--------|
| Amazon | 1000×1000 | Pure white | 10 MB | JPEG/PNG |
| eBay | 500×500 | White preferred | 12 MB | JPEG/PNG |
| Shopify | 2048×2048 | Any | 20 MB | JPEG/PNG/WebP |
| Etsy | 2000×2000 | Any | 10 MB | JPEG/PNG |
| Walmart | 1000×1000 | Pure white | 5 MB | JPEG |

---

## File Naming Convention

```
{SKU}_{ViewType}_{Sequence}.{ext}
```

**Examples:**
- `ABC123_MAIN_01.jpg`
- `ABC123_BACK_02.jpg`
- `ABC123_DETAIL_03.jpg`

**View types:** MAIN, FRONT, BACK, SIDE, DETAIL, LIFESTYLE, SIZE

**Rules:**
- No spaces — use underscores
- Lowercase extensions (`.jpg` not `.JPG`)
- Maximum 80 characters total

---

## File Format & Compression

- **Primary:** JPEG for product photos
- **Quality:** 80-92% compression
- **PNG:** Only when transparency required
- **WebP:** Secondary format when supported
- **Target size:** 100-500 KB

---

## Catalog Consistency

- Same lighting setup across all products in category
- Consistent crop margins: 5-10% padding all sides
- Uniform shadow direction
- Color temperature: ±200K variance maximum
- Product centering: within 2% of frame center

---

## Alt Text for SEO

**Structure:** `[Brand] [Product Name] [Key Feature] [Color/Size]`

**Example:**
```
"Nike Air Max 90 Running Shoes in White/Black, Men's Size 10, Mesh Upper"
```

**Rules:**
- 80-125 characters optimal
- Include: material, use case, features
- Avoid: "Image of", "Photo of", keyword stuffing
- Unique per image variant

---

## Multi-Image Set (Amazon)

| Position | Content |
|----------|---------|
| Main | Product on white, front view |
| 2 | Back/alternate angle |
| 3 | Side view |
| 4 | Detail/feature close-up |
| 5 | Scale/size reference |
| 6 | Lifestyle/in-use |
| 7+ | Additional angles, packaging |

---

## Quality Control Checklist

```
□ No highlight/shadow clipping
□ Clean edges (no halos or fringing)
□ Dust spots removed
□ Consistent exposure (±0.3 EV)
□ No chromatic aberration
□ Metadata stripped (EXIF)
□ Background pure white verified
□ Color accuracy checked
```
