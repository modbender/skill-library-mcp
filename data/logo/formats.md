# Logo Formats and Files

## Required Formats

| Format | Purpose | When to Use |
|--------|---------|-------------|
| **SVG** | Vector, web, scalable | Website, app, any digital that scales |
| **PNG** | Raster with transparency | Social media, documents, slides |
| **PDF** | Vector, print-ready | Print vendors, professional documents |
| **EPS/AI** | Editable vector source | Designers, print shops, merchandise |
| **ICO/Favicon** | Browser tab icons | Website only |

---

## Size Requirements

**Digital standard sizes:**

| Use Case | Size | Format |
|----------|------|--------|
| Favicon | 16x16, 32x32 | ICO, PNG |
| Apple Touch Icon | 180x180 | PNG |
| Android/PWA | 192x192, 512x512 | PNG |
| Social avatar | 400x400 | PNG |
| Open Graph | 1200x630 | PNG |
| Email signature | 200-300px wide | PNG |

**Print considerations:**
- Minimum: 1 inch at 300 DPI = 300px
- Business card: 1.5-2 inches wide typically
- Letterhead: 2-3 inches wide typically
- Large format: Vector (SVG/PDF/EPS) required

---

## Color Versions

**Minimum set:**

| Version | Use Case |
|---------|----------|
| Full color | Primary use, color backgrounds okay |
| Black (single color) | Documents, fax, stamps |
| White/reversed | Dark backgrounds, overlays |
| Grayscale | Black and white printing |

**Optional but useful:**
- Monochrome variations for each brand color
- Simplified version for small sizes
- Animated version for video/web

---

## Lockup Variations

**Standard lockups to prepare:**

```
1. Primary lockup (full logo as designed)
2. Horizontal (icon left, text right)
3. Stacked (icon top, text bottom)
4. Icon only (for tight spaces)
5. Text only (when context provides icon)
```

**For each lockup, provide:**
- Full color + transparent background
- Full color + white background
- White version + transparent
- Black version + transparent

---

## File Naming Convention

```
companyname-logo-[lockup]-[color]-[size].[format]

Examples:
acme-logo-primary-color.svg
acme-logo-horizontal-white.png
acme-logo-icon-black.png
acme-logo-stacked-color-400x400.png
acme-favicon-32x32.png
```

---

## Clear Space Rules

**Define minimum clear space around logo:**
- Usually measured as fraction of logo (e.g., "height of the 'A'")
- Apply consistently across all uses
- Document in brand guidelines

**Example specification:**
```
Minimum clear space = 50% of logo height on all sides
At minimum size, clear space may reduce to 25%
```

---

## Minimum Size Specifications

**Define the smallest usable size:**

| Lockup | Minimum Width | Use Case |
|--------|---------------|----------|
| Primary | 100px digital, 1 inch print | Most uses |
| Horizontal | 120px digital | Headers, signatures |
| Icon only | 16px digital, 0.25 inch print | Favicons, small badges |

**Below minimum:**
- Switch to simplified version
- Or use icon-only

---

## File Organization

**Recommended folder structure:**

```
/logo
  /svg
    primary-color.svg
    primary-white.svg
    primary-black.svg
    horizontal-color.svg
    ...
  /png
    /primary
      color-1000.png
      color-500.png
      white-1000.png
      ...
    /icon
      color-512.png
      color-192.png
      ...
  /favicon
    favicon.ico
    apple-touch-icon.png
    ...
  /print
    logo-cmyk.pdf
    logo-cmyk.eps
  /source
    logo-editable.ai
    logo-editable.fig
  brand-guidelines.pdf
```

---

## Quality Checklist

Before final delivery:
- [ ] SVG renders correctly in browsers
- [ ] PNGs have proper transparency (no white halos)
- [ ] Colors match across formats
- [ ] All lockups at all sizes provided
- [ ] Naming convention consistent
- [ ] Source files included for future edits
