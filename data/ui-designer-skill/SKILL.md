---
name: ui-designer
description: Design beautiful interfaces using Material You, Minimalism, Glassmorphism, Neo-Brutalism, Claymorphism, and Swiss Design. Expert in Tailwind CSS, color harmonics, component theming, and accessibility (WCAG).
---

# UI Designer Skill

Expert design guidance for creating aesthetically pleasing, user-centric interfaces. This skill focuses on the visual and structural design intent before and during implementation.

## Core Capabilities

### 1. Color Palette Generation
Generate cohesive and harmonic color palettes tailored to the project's vibe.
- Deliverables: HEX codes, Tailwind config extensions, and CSS variables.
- Palettes: Default to high-end pastels, dark luxury, or tonal Material You sets.

### 2. Component Theming
Establish robust theme systems (Light/Dark) through consistent design tokens.
- Define --bg, --text, --accent, and --border variables.
- Ensure unified states (hover, focus, active) across all UI elements.

### 3. Accessibility Audits
Evaluate and refine interfaces for maximum inclusivity and compliance.
- Focus: WCAG AA/AAA contrast ratios, semantic HTML, and intuitive navigation.
- Guidance: ARIA attributes, focus ring management, and screen-reader friendliness.

## Core Design Languages

### 1. Material You (M3)
- **Key traits:** Large rounded corners, tonal color palettes, expressive typography.
- **Reference:** [material-you.md](references/material-you.md)

### 2. Minimalism
- **Key traits:** Generous padding, typography-driven hierarchy, neutral palettes.
- **Reference:** [minimalism.md](references/minimalism.md)

### 3. Glassmorphism
- **Key traits:** Backdrop blur, thin borders, vibrant background gradients.
- **Reference:** [glassmorphism.md](references/glassmorphism.md)

### 4. Neo-Brutalism
- **Key traits:** Thick black borders, hard shadows, vibrant clashing colors, bold typography.
- **Reference:** [neo-brutalism.md](references/neo-brutalism.md)

### 5. Claymorphism
- **Key traits:** Soft 3D shapes, double inner shadows, large border radius, playful pastels.
- **Reference:** [claymorphism.md](references/claymorphism.md)

### 6. M3 Pastel Glass (Hybrid)
- **Key traits:** Pastel Blue/Deep Blue, 28px corners, morphing hover effects.
- **Reference:** [m3-pastel-glass.md](references/m3-pastel-glass.md)

### 7. Neo-M3 Hybrid (Wired/Verge Style)
- **Key traits:** Wired/Verge inspired high-contrast, 3px solid black borders, hard shadows (6px+), 24px rounded corners, tonal pastel accents.
- **Reference:** [neo-m3-hybrid.md](references/neo-m3-hybrid.md)

### 8. Swiss Design (International Typographic Style)
- **Key traits:** Strict 12-column grid, massive sans-serif typography, zero border-radius, no shadows, restrained 1–2 color accent palette, asymmetric layouts, whitespace as structure.
- **Reference:** [swiss-design.md](references/swiss-design.md)

## Automation: Cursor Integration

This skill can automatically update your project's `.cursorrules` to keep the AI aligned with your design goals.

### `apply_ui_rules.py`
Run this script to append design rules to your current directory's .cursorrules.

```bash
python3 $WORKSPACE/skills/ui-designer-skill/scripts/apply_ui_rules.py --style [material|minimal|glass|neo-brutalism|claymorphism|m3-pastel|neo-m3|swiss] --palette [pastel|dark|vibrant]
```

## Workflows

### 1. Design Conception
When starting a new feature, ask for:
- Primary design language? (Material You, Minimalism, Glassmorphism, Neo-Brutalism, Claymorphism, M3 Pastel Glass, Neo-M3 Hybrid, Swiss Design)
- Color vibe? (Pastel, Dark, High-Contrast)

### 2. Component Architecture
Plan the HTML/React structure with Tailwind classes. Focus on Grid/Flex layouts and responsiveness.

## Best Practices
- **Consistency:** Stick to one design language per project.
- **Accessibility:** Ensure enough contrast for text.
- **Azzar's Rule:** "Just enough engineering to get it done well." (Wong edan mah ajaib).
