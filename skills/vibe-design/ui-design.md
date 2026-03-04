# UI/UX Design with AI

## The Vibe UI Workflow

1. **Explore** — Generate concepts with AI (Midjourney, Figma AI)
2. **Select** — Identify what works across variants
3. **Reference** — Import as reference, not final asset
4. **Rebuild** — Recreate in your design system
5. **Iterate** — Use AI for variations, human for polish

## Prompting for UI Screens

### Landing Pages
```
Modern SaaS landing page UI for [product type],
clean layout, hero section with [key element],
[color palette], [style blend],
minimal typography --ar 16:9 --style raw --v 7
```

### Dashboards
```
Web dashboard UI for [domain] system,
clean data visualization, [color scheme],
modular card layout, [design system] influence,
professional tone --ar 16:9 --style raw
```

### Mobile Apps
```
Mobile app UI for [purpose], [mode],
[design system], [accent colors],
modern [specific elements], rounded cards,
[mood/feeling] --ar 4:5 --style raw
```

## Design System Anchors

Reference these for consistent structure:

| System | Effect |
|--------|--------|
| Material Design 3 | Cards, elevation, spacing rhythm |
| Apple HIG | Soft corners, system fonts, native feel |
| IBM Carbon | Enterprise, data-dense, crisp |
| Atlassian | Collaborative tools, blue palette |
| Tailwind UI | Utility-first, clean components |

## Component Generation

### Buttons
```
UI design system buttons set, 
primary/secondary/ghost styles,
Material 3 tokens, Figma component sheet,
consistent 8px grid --ar 1:1 --style raw
```

### Forms
```
Form component library, 
input fields, dropdowns, checkboxes,
[design system] styling, 
states: default, hover, focus, error,
light mode --ar 16:9 --style raw
```

### Cards
```
Card component variations for [purpose],
[content type] layouts,
[visual style], consistent padding,
[design system] shadows --ar 1:1 --style raw
```

## Version Differences (Midjourney)

- **v7**: Tends toward 3D, depth, gradients
- **v6**: Flatter, more traditional UI look

Test both for UI work. v6 often better for production-style mockups.

## From AI to Production

### What to Extract
- Color palettes and relationships
- Layout structure and proportions
- Component ideas and arrangements
- Mood and visual direction

### What to Rebuild
- Exact spacing (use your grid)
- Typography (use your type scale)
- Interactive states
- Responsive behavior
- Real content

### Anti-Pattern
❌ Trying to use AI output directly in production
✅ Using AI output as detailed reference for manual rebuild
