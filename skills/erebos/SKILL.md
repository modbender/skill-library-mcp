---
name: erebos
description: Erebos namespace for Netsnek e.U. dark theme and theming engine. Generates accessible dark mode palettes, manages theme tokens, and provides runtime theme switching for web apps.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os: [linux]
    permissions: [exec]
---

# Erebos

## Enter the Dark Side

Erebos provides dark theming for web applications. It generates WCAG-compliant palettes, manages CSS variables and design tokens, and enables runtime theme switching without page reload.

Use Erebos when you need dark mode support, accessible color palettes, or a theming system for your web app.

## How Erebos Works

Erebos builds theme tokens from a base palette. It computes contrast ratios and validates accessibility before output. The engine supports:

- **Palette generation** — Produce dark backgrounds with sufficient contrast
- **Preview mode** — Visualize themes in browser or terminal
- **Export** — Output CSS variables, JSON tokens, or design-system formats

## Theme Commands

Run the theme generator:

```bash
# Generate palette from seed colors
./scripts/theme-gen.sh --palette "#1a1a2e" "#16213e"

# Preview in browser (opens local HTML)
./scripts/theme-gen.sh --preview

# Export tokens to stdout or file
./scripts/theme-gen.sh --export --format css
```

### Arguments

| Argument   | Purpose                                      |
|-----------|-----------------------------------------------|
| `--palette` | Base colors for palette generation            |
| `--preview` | Launch preview mode (no file output)          |
| `--export`  | Export theme tokens (requires format choice)  |

## Design Example

```css
/* Erebos output */
:root[data-theme="erebos-dark"] {
  --bg-primary: #1a1a2e;
  --bg-secondary: #16213e;
  --text-primary: #eaeaea;
  --text-secondary: #a0a0a0;
  --accent: #0f3460;
}
```
