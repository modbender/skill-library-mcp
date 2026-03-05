# Visual Design Rules for Slides

## Hierarchy Fundamentals

### Size Scale
| Element | Minimum Size | Recommended |
|---------|--------------|-------------|
| Title | 36pt | 44pt |
| H1 | 28pt | 36pt |
| H2 | 24pt | 28pt |
| Body | 20pt | 24pt |
| Caption | 16pt | 18pt |

**Rule:** Each level 1.2-1.5x larger than the one below.

### Weight Hierarchy
1. **Bold** — Titles, key terms, emphasis
2. **Medium** — Subtitles, labels
3. **Regular** — Body text
4. **Light** — Captions, secondary info

Never use more than 3 weights in one deck.

## Color System

### Palette Limits
- **Maximum 4 colors** plus neutrals
- Primary: Brand/main color
- Secondary: Complement or accent
- Accent: Call-to-action, highlights
- Neutral: Grays for text, backgrounds

### Contrast Requirements
| Use Case | Minimum Contrast |
|----------|------------------|
| Body text on background | 4.5:1 |
| Large text (24pt+) | 3:1 |
| Decorative elements | No minimum |

**Test:** If squinting makes text hard to read → increase contrast.

### Color Usage
```
Background: Neutral (white, light gray, dark)
Text: High contrast to background
Accent: Sparingly (1-2 elements per slide)
Charts: Distinct colors, not random
```

## Typography

### Font Pairing
- **Maximum 2 font families**
- Safe combinations:
  - Sans-serif headings + Serif body
  - One geometric + one humanist
  - Same family, different weights

### System Fonts (Safe)
| Platform | Sans | Serif | Mono |
|----------|------|-------|------|
| Cross-platform | Arial, Helvetica | Georgia, Times | Courier |
| Modern | Inter, Roboto | Merriweather | JetBrains Mono |
| macOS | SF Pro | New York | SF Mono |
| Windows | Segoe UI | Cambria | Cascadia |

### Text Alignment
- **Left-align** body text (never justify)
- **Center** titles only if short
- **Right-align** rarely, only for specific layouts

## Layout & Composition

### Content Density
- **6x6 Rule:** Max 6 bullets, 6 words each
- **One idea per slide**
- If content doesn't fit → split slides

### Margins & Spacing
- **Consistent margins** all around (typically 0.5-1 inch)
- **8px grid** or similar for spacing
- **Breathing room** between elements

### Alignment
- Everything aligns to invisible grid
- Left edges of text blocks match
- Images align with text or to each other

### Balance
| Layout | Use |
|--------|-----|
| Centered | Titles, quotes, emphasis |
| Left-heavy | Text-focused slides |
| Split (50/50) | Comparisons |
| Rule of thirds | Image placement |

## Images & Graphics

### Image Quality
- **Minimum resolution:** 150 DPI for print, 72 DPI for screen
- **Never stretch** — maintain aspect ratio
- **Consistent treatment:** Same border radius, shadows, or none

### Icon Consistency
- One icon set per deck (don't mix styles)
- Same size for similar-purpose icons
- Match icon weight to text weight

### Chart Design
| Element | Rule |
|---------|------|
| Grid lines | Remove or minimize |
| Legends | Near data, not in corner |
| Colors | Match brand palette |
| Labels | On data points when possible |
| 3D effects | Never |

### Background Images
- Use overlays for text legibility
- Position subject to not conflict with text
- Lower opacity (40-60%) for subtle backgrounds

## Animations & Transitions

### Transitions Between Slides
- **One transition type** for entire deck
- Recommended: Fade, Slide (horizontal)
- Avoid: Spin, Zoom, Flip (distracting)

### Build Animations (Within Slide)
- Use to reveal information progressively
- Same timing for all similar elements
- **Easing:** ease-out for entrance, ease-in for exit

### When to Animate
| ✅ Do | ❌ Don't |
|-------|---------|
| Reveal quiz answers | Animate every bullet |
| Build complex diagrams | Spin logos |
| Highlight sequence | Use different effects per slide |
| Draw attention once | Repeat same animation |

## Anti-Patterns to Avoid

### Visual Chaos
- ❌ Multiple fonts fighting for attention
- ❌ Rainbow colors with no system
- ❌ Inconsistent spacing/margins
- ❌ Clipart from different eras

### Text Problems
- ❌ Walls of text (paragraphs on slides)
- ❌ Full sentences as bullets
- ❌ ALL CAPS for body text
- ❌ Tiny text "I'll just talk through this"

### Image Problems
- ❌ Stretched/distorted images
- ❌ Low-res images on large slides
- ❌ Watermarked stock photos
- ❌ Decorative images with no purpose

### Chart Problems
- ❌ 3D pie charts
- ❌ Excessive grid lines
- ❌ Legends far from data
- ❌ Too many data series (max 5-6)

## Validation Checklist

Before delivering any deck:
- [ ] Text readable at 50% zoom?
- [ ] Consistent margins all slides?
- [ ] Color palette matches brand?
- [ ] No orphan words in titles?
- [ ] Images high quality, aligned?
- [ ] Animations serve a purpose?
- [ ] Exported correctly (fonts embedded)?
