# Logo Lockup Construction

Standards for icon container and lockup variants.

---

## Icon Container (Critical)

The `icon.svg` file is ALWAYS a square container (1:1 aspect ratio).

**Rule: Never stretch, always pad.**

```
WRONG (stretched):          RIGHT (padded):
┌─────────────────┐         ┌─────────────────┐
│█████████████████│         │                 │
│█████████████████│         │   ██████████    │
│█████████████████│         │   ██████████    │
│█████████████████│         │                 │
└─────────────────┘         └─────────────────┘
  (distorted icon)            (icon with space)
```

**Specifications:**
- Container: Always 1:1 square
- Icon: Centered, never distorted
- Padding: Add negative space if icon shape is not square
- Minimum size: 16×16px
- Use cases: Favicons, app icons, profile pictures, watermarks

---

## The Two Lockups

### 1. Stacked (Vertical)
**Aspect Ratio:** 1:1 (square to portrait)
**Use Cases:** Social media, business cards, centered layouts, print collateral

```
┌─────────────────┐
│                 │
│      ████       │
│     ██████      │
│      ████       │
│                 │
│    BRANDNAME    │
│                 │
└─────────────────┘
```

**Specifications:**
- Icon above, wordmark below
- Both centered horizontally
- Spacing between icon and wordmark: 0.5× to 1× icon height
- Safe area: 10% padding on all sides
- Wordmark width ≤ 1.5× icon width (prevents imbalance)

### 3. Horizontal (Landscape)
**Aspect Ratio:** 3:1 to 5:1
**Use Cases:** Headers, navigation, letterhead, wide formats

```
┌─────────────────────────────────┐
│                                 │
│    ████                         │
│   ██████    BRANDNAME           │
│    ████                         │
│                                 │
└─────────────────────────────────┘
```

**Specifications:**
- Icon left, wordmark right
- Vertically centered alignment
- Spacing between icon and wordmark: 0.5× to 1× icon width
- Safe area: 10% padding on all sides
- Icon and wordmark optically balanced (not mathematically)

---

## Spacing System

Use a consistent spacing unit derived from the icon dimensions.

### Unit Definition
```
1 unit (U) = icon width / 8
```

### Minimum Clear Space
```
┌───────────────────────────────┐
│                               │
│   ┌───────────────────────┐   │
│   │                       │   │  ← 2U minimum
│   │        LOGO           │   │
│   │                       │   │
│   └───────────────────────┘   │
│                               │  ← 2U minimum
└───────────────────────────────┘
     ↑                     ↑
    2U                    2U
```

### Internal Spacing (Stacked)
```
        ████
       ██████
        ████
          ↕ 4U
      BRANDNAME
```

### Internal Spacing (Horizontal)
```
    ████ ←2U→ BRANDNAME
   ██████
    ████
```

---

## Optical Alignment

Mathematical centering ≠ visual centering.

### Pointed Icons
Triangular or pointed icons need to be shifted slightly to appear centered.

```
Mathematical center:     Optical center:
       △                       △
       │                       │
   ────┼────               ────┼────
       │                     ↑ shifted up slightly
```

### Dense vs. Open Icons
Dense icons appear heavier. Balance by:
- Reducing size slightly
- Increasing space around them

### Descenders in Wordmarks
If wordmark has descenders (g, y, p, q), shift up slightly for optical balance.

---

## Size Specifications

### Minimum Sizes
| Lockup | Print (mm) | Digital (px) |
|--------|-----------|--------------|
| Icon Only | 10mm | 16px |
| Stacked | 20mm wide | 48px wide |
| Horizontal | 40mm wide | 80px wide |

### Recommended Sizes for Export
```
icon-only.svg    → viewBox: 0 0 512 512
stacked.svg      → viewBox: 0 0 512 640 (or 512 512)
horizontal.svg   → viewBox: 0 0 1024 256
```

---

## Color Variants

Each lockup should work in these color modes:

1. **Full Color** — Primary brand colors
2. **Single Color (Black)** — #000000
3. **Single Color (White)** — #FFFFFF (for dark backgrounds)
4. **Single Color (Brand)** — Primary brand color only

---

## File Naming Convention

```
output/
├── {brand}-icon.svg                # Icon in square container (1:1)
├── {brand}-wordmark.svg            # Isolated wordmark
├── {brand}-stacked.svg             # Vertical lockup
├── {brand}-horizontal.svg          # Horizontal lockup
└── {brand}-logo-system.json        # Metadata
```

---

## SVG Optimization

Before delivery, all SVGs should be:

1. **Single layer** — No unnecessary groups
2. **Cleaned paths** — Remove redundant points
3. **No transforms** — Bake all transforms into paths
4. **No live text** — All text outlined to paths
5. **Proper viewBox** — Matches content bounds
6. **No embedded styles** — Inline fills only

---

## Anti-Patterns

- Different spacing ratios across lockups
- Icon too small relative to wordmark
- Wordmark too long (breaks at small sizes)
- Inconsistent safe areas
- Centered text with left-aligned icon
- Complex backgrounds in logo area
