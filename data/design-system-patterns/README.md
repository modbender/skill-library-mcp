# Design System Patterns

Foundational design system architecture — token hierarchies, theming infrastructure, token pipelines, and governance. The structural backbone for scalable, multi-brand design systems.

## What's Inside

- Three-layer token hierarchy (primitive → semantic → component)
- Theme switching with React (light/dark/system, localStorage, FOUC prevention)
- Multi-brand theming for white-label products
- Style Dictionary pipeline (CSS, iOS Swift, Android XML)
- Accessibility tokens (reduced motion, high contrast, forced colors)
- Token naming conventions and governance process
- Common pitfalls and best practices

## When to Use

- Defining token architecture (primitive → semantic → component layers)
- Implementing light/dark/system theme switching with React
- Setting up Style Dictionary or Figma-to-code token pipelines
- Building multi-brand theming systems
- Establishing token naming conventions and governance
- Preventing flash of unstyled content (FOUC) in SSR

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/design-systems/design-system-patterns
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/design-systems/design-system-patterns .cursor/skills/design-system-patterns
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/design-systems/design-system-patterns ~/.cursor/skills/design-system-patterns
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/design-systems/design-system-patterns .claude/skills/design-system-patterns
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/design-systems/design-system-patterns ~/.claude/skills/design-system-patterns
```

## Related Skills

- [design-system-components](../design-system-components/) — CVA variant patterns and Surface primitives
- [distinctive-design-systems](../distinctive-design-systems/) — Aesthetic documentation and visual identity
- [theme-factory](../theme-factory/) — Pre-built theme palettes for artifacts

---

Part of the [Design Systems](..) skill category.
