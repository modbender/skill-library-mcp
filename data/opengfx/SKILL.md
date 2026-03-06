---
name: opengfx-logo
description: Generate complete logo systems with icon + wordmark + lockups. Creates production-ready SVG vector logos from natural language prompts. Use when a user requests a logo, brand mark, icon design, or visual identity foundation.
version: 1.3.0
note: This is the INTERNAL implementation skill for OpenGFX. For the external SERVICE documentation (ACP/x402 API), see clawhub.com/skills/opengfx.
---

# OpenGFX Logo System

Generate production-ready logo systems from natural language input.

## What This Skill Produces

Every logo system includes:

1. **Icon** — Single-color vector path in square container (1:1)
2. **Wordmark** — Typography-based name, single-color vector
3. **Stacked Lockup** — Icon above wordmark, centered
4. **Horizontal Lockup** — Icon left, wordmark right
5. **Logo System JSON** — Machine-readable metadata

All outputs are SVG vectors optimized for scalability (16px → billboard).

### Icon Container Rule (Critical)
The icon SVG is ALWAYS a square container (1:1 aspect ratio).
- If the icon shape is not square, add **negative space** to make the container square
- **NEVER stretch or distort** the icon to fill a square
- The icon floats within the square with appropriate padding

---

## Generation Pipeline

### Step 1: Parse User Input

Extract from prompt:
- **Brand Name** (required)
- **Icon Direction** (emoji, concept, or abstract reference)
- **Style Direction** (minimal, playful, corporate, tech, etc.)
- **Typeface Direction** (sans-serif, serif, geometric, humanist, etc.)

If missing, ask clarifying questions before proceeding.

### Step 2: Conceptualize Icon

Apply geometric construction principles:

1. **Select Base Shape** — Circle, triangle, square, or compound
2. **Apply Concept** — Map user's icon direction to geometric form
3. **Simplify** — Reduce to single vector path that works at 16px
4. **Test in Black** — No color until form is solid

Reference: [GEOMETRY.md](references/GEOMETRY.md) for shape meanings and construction.

### Step 3: Select Typeface

Match typeface to brand personality:

| Style | Typeface Families |
|-------|-------------------|
| Tech/Modern | Inter, SF Pro, Söhne, Geist, Manrope |
| Minimal/Apple | SF Pro Display, Helvetica Neue, Avenir |
| Geometric | Futura, Century Gothic, Proxima Nova |
| Humanist | Gill Sans, Frutiger, Myriad Pro |
| Elegant | Didot, Bodoni, Playfair Display |
| Playful | Quicksand, Poppins, Nunito |
| Corporate | IBM Plex Sans, Roboto, Open Sans |

Convert wordmark to single-path SVG (outlined, not live text).

Reference: [TYPOGRAPHY.md](references/TYPOGRAPHY.md) for type selection.

### Step 4: Construct Lockups

Generate two SVG lockups with consistent proportions:

**Stacked (1:1)**
```
┌─────────────────┐
│      ICON       │
│                 │
│    WORDMARK     │
└─────────────────┘
```

**Horizontal (3:1 to 4:1)**
```
┌─────────────────────────────┐
│  ICON  │     WORDMARK       │
└─────────────────────────────┘
```

Reference: [LOCKUPS.md](references/LOCKUPS.md) for spacing ratios.

### Step 5: Output Package

Generate output files:
```
output/
├── icon.svg           # Icon in square container (1:1)
├── wordmark.svg       # Isolated wordmark
├── stacked.svg        # Icon + wordmark vertical
├── horizontal.svg     # Icon + wordmark horizontal
└── logo-system.json   # Metadata + tokens
```

---

## Design Principles (Enforce Always)

### The One Thing Rule
Every logo must have exactly ONE memorable feature. Not two, not three. One.

### Black First
Design in solid black (#000000). Color comes last. If the logo doesn't work in black, it doesn't work.

### Geometric Foundation
All icons derive from the five universal shapes. Even organic forms should be constructed on a geometric grid.

### Scalability Test
Every logo must pass:
- 16px (favicon)
- 32px (app icon)
- 64px (small UI)
- 256px+ (print/display)

### Single Path Principle
Icon should be reducible to a single compound path. Wordmark should be outlined (no live text).

---

## Quality Checklist

Before delivering any logo:

- [ ] Icon works in solid black
- [ ] Icon works at 16px without detail loss
- [ ] Wordmark is outlined (paths, not text)
- [ ] All three lockups have consistent spacing
- [ ] One memorable feature, not multiple
- [ ] Appropriate to industry/context
- [ ] SVG is optimized (no unnecessary groups, transforms)

---

## Example Prompt → Output

**Input:**
> "I need a logo for my new company called OpenGFX, it should be a paint palette like this emoji 🎨 paired with a clean sans serif font, think Apple / Steve Jobs design style"

**Parsed:**
- Brand Name: OpenGFX
- Icon Direction: Paint palette (🎨)
- Style: Apple-minimal, Steve Jobs aesthetic
- Typeface: Clean sans-serif (SF Pro Display, Helvetica Neue)

**Generated:**
- Icon: Simplified paint palette derived from circle + 3 dots
- Wordmark: "OpenGFX" in SF Pro Display (or Helvetica Neue), tracked -10
- Lockups: All three variants with Apple-style generous whitespace

---

## References

- [GEOMETRY.md](references/GEOMETRY.md) — Shape meanings, construction grids
- [TYPOGRAPHY.md](references/TYPOGRAPHY.md) — Type selection, pairing, tracking
- [LOCKUPS.md](references/LOCKUPS.md) — Spacing ratios, safe areas
- [MODERNISM.md](references/MODERNISM.md) — Logo Modernism principles

---

## Anti-Patterns (Never Do)

- ❌ Multiple competing visual ideas in one icon
- ❌ Gradients or effects in primary logo
- ❌ Live text in SVG (always outline)
- ❌ Icons that lose detail at small sizes
- ❌ Trendy effects (drop shadows, 3D, bevels)
- ❌ Literal representations (restaurant logo = fork, dental = tooth)
- ❌ Generic shapes without conceptual connection
