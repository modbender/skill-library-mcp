# React Composition Patterns

Build flexible, maintainable React components using compound components, context providers, and explicit variants. Avoid boolean prop proliferation.

## What's Inside

- Core principle: avoiding boolean prop proliferation
- Compound components with shared context
- Generic context interface (state/actions/meta)
- Explicit variant components over boolean props
- Lifted state in provider components
- Children composition over render props
- Decoupling state from UI

## When to Use

- Refactoring components with many boolean props
- Building reusable component libraries
- Designing flexible component APIs
- Creating compound components (Card, Dialog, Form, etc.)
- Components need shared state across sibling elements

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/frontend/composition-patterns
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install composition-patterns
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/frontend/composition-patterns .cursor/skills/composition-patterns
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/frontend/composition-patterns ~/.cursor/skills/composition-patterns
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/frontend/composition-patterns .claude/skills/composition-patterns
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/frontend/composition-patterns ~/.claude/skills/composition-patterns
```

## Related Skills

- `react-composition` — Overlapping patterns with a condensed decision guide
- `react-best-practices` — Performance optimization rules for React

---

Part of the [Frontend](..) skill category.
