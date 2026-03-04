---
name: minimalist-ui
description: Design system and implementation playbook for minimalist Notion x OpenAI style UI/UX. Use when designing dashboards, chat interfaces, agent control panels, docs UIs, or product surfaces that need clean typography, high information density, subtle hierarchy, low-noise visuals, and execution-ready frontend specs.
---

# Minimalist Notion × OpenAI UI

Build crisp, low-noise product UI with strong hierarchy and operator-grade usability.

## Core Principles

1. Prioritize clarity over decoration.
2. Keep layout breathable but dense enough for serious work.
3. Use typography, spacing, and contrast as the primary hierarchy tools.
4. Avoid visual noise (heavy shadows, flashy gradients, random color accents).
5. Every element must justify its presence.

## Workflow

1. Define screen intent in one sentence.
2. Choose one primary user action.
3. Build skeleton with spacing + typography first (no color dependency).
4. Add semantic color only for state/meaning.
5. Run the checklist in `references/qa-checklist.md`.

## Mandatory Style Constraints

- Max 1 accent color per screen.
- Border radius: 8–12px (consistent scale).
- Shadows: subtle only; no layered “dribbble” effects.
- Animation: 120–180ms, ease-out, functional only.
- Empty states must suggest a next action.
- Error states must include fix guidance.

## Use These References

- Token system: `references/design-tokens.md`
- Layout and spacing logic: `references/layout-patterns.md`
- Components and behavior: `references/component-specs.md`
- Acceptance gate: `references/qa-checklist.md`

## Output Contract (when generating UI specs/code)

Always produce:

- **Intent**: what this screen optimizes for
- **Structure**: zones/regions and hierarchy
- **Tokens used**: type scale, spacing, colors
- **Interaction states**: hover/focus/disabled/loading/error
- **Accessibility**: keyboard + contrast notes
- **Implementation notes**: concrete Tailwind/CSS/React guidance

Keep output implementation-ready and concise.
