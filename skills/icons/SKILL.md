---
name: Icons
description: Implement accessible icons with proper sizing, color inheritance, and performance.
metadata: {"clawdbot":{"emoji":"🔣","requires":{},"os":["linux","darwin","win32"]}}
---

## SVG vs Icon Fonts

SVG is the modern standard:
- Better accessibility (native ARIA support)
- No flash of invisible/wrong icon (FOIT)
- Multicolor support
- Smaller bundles with tree-shaking

Only consider icon fonts for legacy IE11 support.

## Accessibility Patterns

**Decorative icons (next to visible text):**
```html
<button>
  <svg aria-hidden="true" focusable="false">...</svg>
  Save
</button>
```

**Informative icons (standalone, no label):**
```html
<button aria-label="Save document">
  <svg aria-hidden="true" focusable="false">...</svg>
</button>

<!-- Or with visually hidden text -->
<button>
  <svg aria-hidden="true">...</svg>
  <span class="sr-only">Save document</span>
</button>
```

**SVG with accessible name:**
```html
<svg role="img" aria-labelledby="icon-title">
  <title id="icon-title">Warning: system error</title>
  <!-- paths -->
</svg>
```

Key rules:
- `aria-hidden="true"` on SVGs that duplicate visible text
- `focusable="false"` prevents unwanted tab stops in IE/Edge
- `<title>` must be first child inside `<svg>` for screen reader support
- IDs must be unique if multiple SVGs are inline

## Color Inheritance

```svg
<svg fill="currentColor">
  <path d="..."/>
</svg>
```

`currentColor` inherits from CSS `color` property. The icon changes color with hover states automatically:

```css
.button { color: blue; }
.button:hover { color: red; } /* icon turns red too */
```

Remove hardcoded `fill="#000"` from SVGs before using currentColor.

For stroke-based icons, use `stroke="currentColor"` instead.

## Sizing

Standard grid sizes: 16, 20, 24, 32px

Match stroke weight to size:
| Size | Stroke | Use case |
|------|--------|----------|
| 16px | 1px | Dense layouts, small text |
| 20px | 1.25px | Default UI |
| 24px | 1.5px | Buttons, primary actions |
| 32px | 2px | Headers, navigation |

Touch targets need 44x44px minimum—icon can be smaller if tappable area is larger via padding.

```css
.icon-button {
  width: 24px;
  height: 24px;
  padding: 10px; /* Creates 44x44 touch target */
}
```

## Scaling with Text

```css
.icon {
  width: 1em;
  height: 1em;
}
```

Icon scales with surrounding text size automatically.

## Symbol Sprites

For many repeated icons, reduce DOM nodes with sprites:

```html
<!-- Define once, hidden -->
<svg style="display:none">
  <symbol id="icon-search" viewBox="0 0 24 24">
    <path d="..."/>
  </symbol>
  <symbol id="icon-menu" viewBox="0 0 24 24">
    <path d="..."/>
  </symbol>
</svg>

<!-- Use anywhere -->
<svg aria-hidden="true"><use href="#icon-search"/></svg>
```

External sprites (`<use href="/icons.svg#search"/>`) don't work in older Safari without polyfill.

## Performance

Benchmark (1000 icons):
- `<img>` with data URI: 67ms (fastest)
- Inline SVG optimized: 75ms
- Symbol sprite: 99ms
- `<img>` external: 76ms

Recommendations:
- Tree-shake icon libraries (Lucide, Heroicons support this)
- Don't import entire Font Awesome (1MB+)—use subset or switch to SVG
- Inline critical icons, lazy-load sprite for non-critical

## Consistency

- Stick to one icon set—mixing styles looks unprofessional
- Match icon stroke weight to your font weight (regular text = 1.5px stroke)
- Pick one style per context: outlined for inactive, filled for active
- Optical alignment differs from mathematical—circles reach edges, squares don't
- Name icons by appearance, not meaning: `stopwatch` not `speed`

## Common Mistakes

- Missing `aria-hidden` on decorative icons—screen readers announce gibberish
- Mixing rounded and sharp icon styles in same interface
- Giant icon libraries for 10 icons—massive bundle bloat
- Icon-only buttons without accessible name—impossible to use with screen readers
- Hardcoded colors preventing theme switching
- Stroke width not scaling with icon size—16px icon with 2px stroke looks heavy
