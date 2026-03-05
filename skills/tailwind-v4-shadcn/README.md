# Tailwind v4 + shadcn/ui Stack

Production-tested setup for Tailwind v4 with shadcn/ui. Prevents 8 documented errors through a mandatory four-step architecture.

## What's Inside

- Mandatory four-step theming architecture
- CSS variable-based color system with HSL
- Automatic dark mode switching
- Error prevention for 8 common mistakes (with solutions)
- Quick start setup for Vite projects
- `@theme inline` mapping and `@layer base` patterns
- OKLCH color space and container queries (v4 built-in)
- Migration guide from Tailwind v3 to v4
- Production-ready templates (CSS, ThemeProvider, Vite config, utils)

## When to Use

- Starting a new React/Vite project with Tailwind v4
- Migrating from Tailwind v3 to v4
- Setting up shadcn/ui with Tailwind v4
- Debugging: colors not working, dark mode broken, build failures
- Fixing `@theme inline`, `@apply`, or `@layer base` issues

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/frontend/tailwind-v4-shadcn
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install tailwind-v4-shadcn
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/frontend/tailwind-v4-shadcn .cursor/skills/tailwind-v4-shadcn
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/frontend/tailwind-v4-shadcn ~/.cursor/skills/tailwind-v4-shadcn
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/frontend/tailwind-v4-shadcn .claude/skills/tailwind-v4-shadcn
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/frontend/tailwind-v4-shadcn ~/.claude/skills/tailwind-v4-shadcn
```

## Related Skills

- `tailwind-design-system` — Design system patterns with CVA and Tailwind
- `shadcn-ui` — shadcn/ui component patterns and usage

---

Part of the [Frontend](..) skill category.
