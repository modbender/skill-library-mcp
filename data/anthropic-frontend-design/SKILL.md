---
name: anthropic-frontend-design
description: Create distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Combines the design intelligence of UI/UX Pro Max with Anthropic's anti-slop philosophy. Use for building UI components, pages, applications, or interfaces with exceptional attention to detail and bold creative choices.
---

# Anthropic Frontend Design

This skill guides the creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. It integrates structured design intelligence (accessibility, UX rules, stack guidelines) with a bold, intentional aesthetic philosophy.

## Core Philosophy: Anti-AI Slop

Claude (and all AI agents) are capable of extraordinary creative work, yet often default to safe, generic patterns. This skill MANDATES breaking those patterns.

- **AVOID**: Inter, Roboto, Arial, system fonts, purple-on-white gradients, cookie-cutter SaaS layouts, emojis as icons.
- **MANDATE**: Unique typography, context-specific color schemes, intentional motion, unexpected spatial composition, and production-grade functional code.

---

## Design Thinking Process

Before coding, understand the context and commit to a BOLD aesthetic direction:

1. **Purpose**: What problem does this solve? Who is it for?
2. **Tone**: Pick an extreme direction—brutally minimal, maximalist chaos, retro-futuristic, organic, luxury, playful, editorial, etc.
3. **Intelligence (Reference)**: Use the internal design tool to gather data (see below).
4. **Differentiation**: What makes this UNFORGETTABLE?

---

## Design Intelligence Tool

Use the internal search tool to gather palettes, font pairings, and UX guidelines. **CRITICAL: You MUST filter the results through the Anti-AI Slop lens.** If the tool suggests "Inter" or "Roboto", you are REQUIRED to ignore it and pick a distinctive alternative.

```bash
# Generate a complete design system
python scripts/search.py "<product_type> <industry> <keywords>" --design-system

# Search specific domains (style, typography, color, ux, chart, landing)
python scripts/search.py "<keyword>" --domain <domain>

# Get stack-specific guidelines (html-tailwind, react, nextjs, shadcn, etc.)
python scripts/search.py "<keyword>" --stack <stack_name>
```

---

## Implementation Standards

### 1. Professional UI Rules

| Rule | Do | Don't |
|------|----|----- |
| **Icons** | Use SVG (Heroicons, Lucide, Simple Icons) | Use emojis like 🎨 🚀 ⚙️ as UI icons |
| **Typography** | Beautiful, unique Google/Custom fonts | Inter, Roboto, Arial, System fonts |
| **Hover** | Stable transitions (color/opacity/shadow) | Scale transforms that shift layout |
| **Cursor** | Add `cursor-pointer` to all interactive items | Leave default cursor on buttons/cards |
| **Contrast** | Minimum 4.5:1 for accessibility | Low-contrast "vibes" that are unreadable |

### 2. Motion & Animation
- Prioritize CSS-only solutions where possible.
- Focus on high-impact moments (staggered reveals on page load).
- Use duration 150-300ms for micro-interactions.

### 3. Spatial Composition
- Use asymmetry, overlap, or diagonal flow to break standard grids.
- Balance generous negative space OR intentional density.

---

## Pre-Delivery Checklist

Before delivering code, verify every item:

### Visual Quality
- [ ] No emojis used as icons (SVG only).
- [ ] Typography is characterful and NOT "AI standard".
- [ ] Color scheme is unique to the context (no generic gradients).
- [ ] Hover states provide clear, stable visual feedback.

### UX & Accessibility
- [ ] All interactive elements have `cursor-pointer`.
- [ ] Form inputs have labels; images have alt text.
- [ ] Text contrast meets 4.5:1 minimum (test Light/Dark modes).
- [ ] Responsive at all breakpoints (375px, 768px, 1024px, 1440px).
- [ ] No horizontal scroll on mobile.

---

## Aesthetic Directions (Reference)

- **Brutally Minimal**: Monochrome, extreme white space, sparse typography.
- **Maximalist Chaos**: Overlapping elements, dense information, pattern mixing.
- **Retro-Futuristic**: Chrome effects, neon accents, 80s-inspired.
- **Luxury/Refined**: Gold/Dark accents, serif fonts, generous spacing.
- **Playful/Toy-like**: Rounded corners, bright pastels, bouncy animations.
- **Editorial/Magazine**: Grid-based, bold headlines, clean hierarchy.
- **Brutalist/Raw**: Monospace fonts, harsh contrasts, industrial.
- **Art Deco**: Sharp angles, metallic accents, ornate borders.

*Commit to ONE direction and execute it fully—no half measures.*
