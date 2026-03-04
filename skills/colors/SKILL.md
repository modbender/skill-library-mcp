---
name: Colors
description: Build accessible color palettes with proper contrast ratios and semantic tokens.
metadata: {"clawdbot":{"emoji":"🎨","requires":{},"os":["linux","darwin","win32"]}}
---

## Contrast Ratios (WCAG)

| Level | Normal Text | Large Text (≥18pt or ≥14pt bold) | UI Components |
|-------|-------------|----------------------------------|---------------|
| AA (minimum) | ≥ 4.5:1 | ≥ 3:1 | ≥ 3:1 |
| AAA (enhanced) | ≥ 7:1 | ≥ 4.5:1 | — |

Critical thresholds on white background:
- `#767676` → 4.54:1 ✅ barely passes
- `#777777` → 4.47:1 ❌ fails (cannot round up)
- `#757575` → 4.6:1 ✅ safe minimum gray

Pure colors on white:
- Red `#FF0000` → 4:1 ❌ fails for normal text
- Green `#00FF00` → 1.4:1 ❌ always fails (never use for text)
- Blue `#0000FF` → 8.6:1 ✅ passes AAA

## Color-Only Information

Never rely on color alone to convey meaning. 8% of men have color vision deficiency.

```html
<!-- ❌ Bad: only color differentiates states -->
<span class="text-green-500">Active</span>
<span class="text-red-500">Inactive</span>

<!-- ✅ Good: icon + text + color -->
<span class="text-green-500">✓ Active</span>
<span class="text-red-500">✗ Inactive</span>
```

Test designs in grayscale to verify information is still distinguishable.

## Semantic Color Tokens

Three-layer architecture for maintainable palettes:

```css
/* Layer 1: Primitives (raw values) */
--blue-500: #3B82F6;
--gray-900: #111827;

/* Layer 2: Semantic (roles) */
--color-primary: var(--blue-500);
--color-text: var(--gray-900);
--color-error: var(--red-500);

/* Layer 3: Component (specific use) */
--btn-primary-bg: var(--color-primary);
--input-border-error: var(--color-error);
```

Name tokens by function, not appearance: `text-primary` not `text-blue`.

## Dark Mode

Create depth with luminosity, not shadows:

```css
/* Light mode uses shadows for depth */
/* Dark mode uses surface brightness */
--surface-0: hsl(220 15% 8%);   /* page background */
--surface-1: hsl(220 15% 12%);  /* card */
--surface-2: hsl(220 15% 16%);  /* elevated element */
--surface-3: hsl(220 15% 20%);  /* modal */
```

Avoid pure black `#000` and pure white `#FFF` as backgrounds. Use `#0a0a0a` and `#fafafa` to reduce eye strain.

## Neutral Grays

Add a subtle tint of your primary color to grays for cohesion:

```css
/* Instead of pure gray */
--gray-100: hsl(220 10% 96%);  /* slight blue tint */
--gray-500: hsl(220 10% 46%);
--gray-900: hsl(220 10% 10%);
```

This creates a more polished, intentional palette.

## HSL for Variations

HSL makes generating consistent color scales trivial:

```css
--primary-100: hsl(220 90% 95%);
--primary-300: hsl(220 90% 75%);
--primary-500: hsl(220 90% 55%);
--primary-700: hsl(220 90% 35%);
--primary-900: hsl(220 90% 15%);
```

Same hue and saturation, only lightness changes.

## Balance Rule

60-30-10 distribution:
- 60% dominant (backgrounds, containers)
- 30% secondary (cards, sections)
- 10% accent (CTAs, highlights)

Limit palette to 3-5 colors plus neutrals. More creates visual noise.

## Common Mistakes

- `text-gray-400` or lighter on white background typically fails contrast
- Primary/accent colors for body text cause eye fatigue—use for headings and CTAs only
- Hover states that only change opacity may fail contrast—change hue or lightness
- Purple-to-blue gradients are an AI cliché—choose intentional combinations
- Testing only light mode—dark mode often reveals contrast issues
- Red/green as only differentiator—use icons or text labels alongside

## Safe Combinations

| Sector | Primary | Secondary | Why |
|--------|---------|-----------|-----|
| Fintech | Navy #00246B | Light Blue #CADCFC | Trust + clarity |
| Healthcare | Light Blue #89ABE3 | White | Calm + clean |
| E-commerce | Red #F96167 | Yellow #F9E795 | Urgency + optimism |

Avoid: red + green (colorblindness), adjacent hues (blue + purple), yellow + white (no contrast).
