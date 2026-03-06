# Prompting for Visual Design

## The Prompt Stack

Structure prompts in layers:

```
[Subject/Type] — What you're designing
[Style] — Visual treatment
[Details] — Specific elements
[Technical] — Aspect ratio, version, quality
```

## Effective Patterns

### UI Design Prompt Template
```
[project type] UI design for [product or audience],
[style keywords],
[layout type],
[color palette],
[design system],
--ar [ratio] --style raw --v 7
```

Example:
```
Mobile app UI for fitness tracking, dark mode,
Material Design 3, vibrant accent colors,
modern data visualization, rounded cards,
motivational look --ar 4:5 --style raw
```

### Marketing/Graphic Prompt Template
```
[Format] for [brand/purpose],
[style keywords],
[color scheme],
[mood/feeling],
[composition notes]
```

### Icon/Component Prompt Template
```
[Component type] set, [style] styles,
[design system] tokens,
[organization method],
consistent [grid] grid --ar 1:1 --style raw
```

## Vocabulary Guide

### Words That Work for UI
- Interface, layout, component, module
- Hierarchy, spacing, grid, alignment
- Card, panel, dashboard, navigation
- Clean, minimal, functional, structured
- Design system, HIG, Material Design

### Words to Avoid for UI
- Beautiful, stunning, gorgeous (vague)
- Fantasy, magical, dreamy (wrong domain)
- Render, painting, illustration (art terms)
- Perfect, amazing, best (meaningless)

### Style Modifiers
- **Clean**: Minimal decoration, clear hierarchy
- **Glassmorphism**: Frosted glass, transparency, blur
- **Neumorphism**: Soft shadows, extruded feel
- **Brutalist**: Raw, bold, unconventional
- **Corporate**: Professional, trustworthy, structured

## Iteration Prompts

After first generation:
- "Like [image number] but with [specific change]"
- "Same layout, different color palette: [colors]"
- "More [adjective], less [adjective]"
- "Combine [element from A] with [element from B]"

## Common Mistakes

### Too Vague
❌ "A nice website design"
✅ "SaaS landing page for productivity app, hero section with product screenshot, feature grid, dark mode, purple accent, Inter typography"

### Too Many Styles
❌ "Minimalist but also maximalist with lots of colors but clean"
✅ Pick ONE direction. Explore variations within it.

### No Technical Specs
❌ Missing aspect ratio, version, style flags
✅ Always include --ar, --v, --style raw for UI work
