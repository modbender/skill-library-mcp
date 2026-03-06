# Design System Template

Use this template when extracting design system documentation from a project.

---

## Template

```markdown
# [Project Name] - Design System

The visual language and token system for this project.

---

## Aesthetic Foundation

### The Vibe
[Describe the overall aesthetic in 2-3 sentences. What does it look like? What does it feel like?]

### Inspirations
- [Reference 1 - what was taken from it]
- [Reference 2 - what was taken from it]
- [Mood board link if exists]

### Emotions to Evoke
| Emotion | How It's Achieved |
|---------|-------------------|
| [e.g., Satisfaction] | [e.g., Micro-interactions on completion] |
| [e.g., Nostalgia] | [e.g., CRT scan lines, pixel fonts] |
| [e.g., Power] | [e.g., Dark mode, sharp angles] |

---

## Color Tokens

### Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | [hex/hsl] | [Primary actions, key elements] |
| `--color-secondary` | [hex/hsl] | [Secondary elements] |
| `--color-accent` | [hex/hsl] | [Highlights, emphasis] |
| `--color-background` | [hex/hsl] | [Base background] |
| `--color-surface` | [hex/hsl] | [Cards, elevated surfaces] |
| `--color-text` | [hex/hsl] | [Primary text] |
| `--color-text-muted` | [hex/hsl] | [Secondary text] |

### Semantic Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--color-success` | [hex/hsl] | [Success states] |
| `--color-warning` | [hex/hsl] | [Warning states] |
| `--color-error` | [hex/hsl] | [Error states] |
| `--color-info` | [hex/hsl] | [Info states] |

### Dark Mode
[How dark mode is implemented, token overrides]

---

## Typography

### Font Families

| Token | Value | Usage |
|-------|-------|-------|
| `--font-primary` | [font stack] | [Body text] |
| `--font-heading` | [font stack] | [Headings] |
| `--font-mono` | [font stack] | [Code, technical] |

### Type Scale

| Token | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `--text-xs` | [rem] | [value] | [Captions, labels] |
| `--text-sm` | [rem] | [value] | [Secondary text] |
| `--text-base` | [rem] | [value] | [Body text] |
| `--text-lg` | [rem] | [value] | [Lead paragraphs] |
| `--text-xl` | [rem] | [value] | [H4, subheadings] |
| `--text-2xl` | [rem] | [value] | [H3] |
| `--text-3xl` | [rem] | [value] | [H2] |
| `--text-4xl` | [rem] | [value] | [H1] |

### Font Weights
| Token | Value | Usage |
|-------|-------|-------|
| `--font-normal` | 400 | [Body] |
| `--font-medium` | 500 | [Emphasis] |
| `--font-semibold` | 600 | [Subheadings] |
| `--font-bold` | 700 | [Headings] |

---

## Spacing

### Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | [rem] | [Tight gaps] |
| `--space-2` | [rem] | [Small gaps] |
| `--space-3` | [rem] | [Medium gaps] |
| `--space-4` | [rem] | [Default gaps] |
| `--space-6` | [rem] | [Section gaps] |
| `--space-8` | [rem] | [Large gaps] |
| `--space-12` | [rem] | [Page sections] |

### Layout Rhythm
[How spacing is applied consistently across the UI]

---

## Motion

### Timing

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | [ms] | [Micro-interactions] |
| `--duration-normal` | [ms] | [Standard transitions] |
| `--duration-slow` | [ms] | [Page transitions] |

### Easing

| Token | Value | Usage |
|-------|-------|-------|
| `--ease-default` | [cubic-bezier] | [Most animations] |
| `--ease-in` | [cubic-bezier] | [Enter animations] |
| `--ease-out` | [cubic-bezier] | [Exit animations] |
| `--ease-bounce` | [cubic-bezier] | [Playful interactions] |

### Animation Patterns
- **Hover states**: [How hovers work]
- **Loading**: [Skeleton, spinner patterns]
- **Transitions**: [Page/component transitions]

---

## Borders & Shadows

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | [rem] | [Buttons, inputs] |
| `--radius-md` | [rem] | [Cards] |
| `--radius-lg` | [rem] | [Modals, large cards] |
| `--radius-full` | 9999px | [Circles, pills] |

### Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | [value] | [Subtle elevation] |
| `--shadow-md` | [value] | [Cards, dropdowns] |
| `--shadow-lg` | [value] | [Modals, popovers] |

---

## Components

### Key Component Patterns
[Document the most important reusable components and their variants]

### Component Tokens
[Any component-specific tokens like button colors, card padding, etc.]

---

## Implementation

### Tailwind Config
```javascript
// Relevant tailwind.config.js excerpt
```

### CSS Variables
```css
/* Root variable definitions */
```

---

## Anti-Patterns

Things to NEVER do in this design system:

- [Specific thing to avoid + why]
- [Specific thing to avoid + why]
```

---

## Usage Notes

When filling this template:

1. **Extract actual values** — Don't guess, pull from Tailwind config, CSS files
2. **Document the "why"** — Why these colors? Why this font? What feeling?
3. **Include code** — Actual Tailwind config, CSS variable definitions
4. **Note anti-patterns** — What should never be done in this system
5. **Capture the vibe** — The aesthetic direction is as important as the tokens
