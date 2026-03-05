---
name: Fonts
description: Choose and implement web typography avoiding common rendering, pairing, and hierarchy mistakes.
metadata: {"clawdbot":{"emoji":"🅰️","requires":{},"os":["linux","darwin","win32"]}}
---

## Display vs Text Fonts

- Display fonts (Abril Fatface, Bebas Neue, Lobster) are for headings 24px+ only—using them for body text destroys readability
- If a font looks decorative or has extreme thick/thin contrast, it's display—not for paragraphs
- Text fonts (Inter, Roboto, Georgia) are designed for 12-18px—use these for body copy

## Pairing Traps

- Two fonts too similar look like a mistake—if you can't tell them apart instantly, use one font
- Contrast in category works: serif heading + sans-serif body, or different weights of same family
- Two decorative fonts clash—never pair Lobster with Pacifico
- Safe pairs: same superfamily (Roboto + Roboto Slab) or proven combos (Playfair Display + Source Sans Pro)

## Weight and Rendering

- Thin weights (100-300) render poorly on Windows—avoid for body text, use 400+ for cross-platform
- Light fonts on dark backgrounds look thinner—bump weight up one level for dark mode
- Faux bold (browser-generated) looks wrong—only use weights the font actually includes
- Check font has italic—faux italic (slanted roman) is noticeably worse than true italic

## Line Height and Length

- Body text needs 1.4-1.6 line-height—1.0 or 1.2 makes paragraphs unreadable walls
- Headings need tighter line-height (1.1-1.3)—large text with 1.5 line-height has awkward gaps
- Line length 45-75 characters max—wider than 75 chars causes readers to lose their place
- Set `max-width` on text containers in ch units: `max-width: 65ch`

## All Caps

- ALL CAPS needs increased letter-spacing—without it, letters collide and look cramped
- `text-transform: uppercase` + `letter-spacing: 0.05em` minimum
- Never use all caps for more than a few words—extended caps text is significantly harder to read
- Small caps (`font-variant: small-caps`) only if font supports it—faux small caps look amateurish

## Widows and Orphans

- Single word alone on last line of paragraph looks broken—adjust text or container width
- `text-wrap: balance` (CSS) distributes lines more evenly in headings
- `text-wrap: pretty` for body text—prevents orphans in browsers that support it
- Manual fix: non-breaking space (`&nbsp;`) between last two words

## Loading and Performance

- `font-display: swap` prevents invisible text—without it, text is blank until font loads
- Subset fonts to characters you need—Latin-only saves 60%+ over full Unicode
- WOFF2 is the only format you need—universal support, best compression
- Preload critical fonts: `<link rel="preload" href="font.woff2" as="font" crossorigin>`

## System Font Stack

```css
font-family: system-ui, -apple-system, BlinkMacSystemFont, 
  'Segoe UI', Roboto, sans-serif;
```
- Zero load time, native look per platform—use for UI-heavy apps
- `system-ui` is now widely supported—simpler than listing all fallbacks
- Always end with generic fallback (`sans-serif`, `serif`, `monospace`)

## Hierarchy Mistakes

- Using too many font sizes—stick to a type scale (1.25 or 1.333 ratio), not random sizes
- Headings not distinct enough from body—skip at least one scale step between h1 and body
- Overusing bold—if everything is emphasized, nothing is emphasized
- Color as only differentiator—size and weight should establish hierarchy before color
