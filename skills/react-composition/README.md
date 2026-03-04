# React Composition Patterns

Composition patterns for building flexible, maintainable React components. Avoid boolean prop proliferation by using compound components, lifting state, and composing internals.

## What's Inside

- Avoid boolean prop proliferation (CRITICAL)
- Compound components with shared context (HIGH)
- Generic context interface / dependency injection (HIGH)
- State lifting into providers (HIGH)
- Explicit variant components (MEDIUM)
- Children over render props (MEDIUM)
- Decision guide for choosing the right pattern

## When to Use

- Refactoring components with many boolean props
- Building reusable component libraries
- Designing flexible component APIs
- Working with compound components or context providers

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/frontend/react-composition
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install react-composition
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/frontend/react-composition .cursor/skills/react-composition
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/frontend/react-composition ~/.cursor/skills/react-composition
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/frontend/react-composition .claude/skills/react-composition
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/frontend/react-composition ~/.claude/skills/react-composition
```

## Related Skills

- `composition-patterns` — Extended examples with detailed code patterns

---

Part of the [Frontend](..) skill category.
