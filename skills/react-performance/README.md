# React Performance Patterns

Performance optimization guide for React and Next.js applications. Patterns across 7 categories, prioritized by impact.

## What's Inside

- Async / Waterfalls (CRITICAL) — parallel fetching, deferred await, Suspense boundaries
- Bundle Size (CRITICAL) — barrel imports, dynamic imports, deferred third-party libs, preloading
- Server Components (HIGH) — RSC serialization, parallel data fetching, React.cache(), after()
- Re-renders (MEDIUM) — derived state, functional setState, lazy init, transitions, memoization
- Rendering (MEDIUM) — content-visibility, static JSX hoisting
- Client-Side Data (MEDIUM) — SWR for deduplication and caching
- JS Performance (LOW-MEDIUM) — Set/Map lookups, combined iterations, early returns
- Quick decision guide for diagnosing performance issues

## When to Use

- Writing new React components or Next.js pages
- Implementing data fetching (client or server-side)
- Reviewing or refactoring for performance
- Optimizing bundle size or load times

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/frontend/react-performance
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install react-performance
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/frontend/react-performance .cursor/skills/react-performance
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/frontend/react-performance ~/.cursor/skills/react-performance
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/frontend/react-performance .claude/skills/react-performance
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/frontend/react-performance ~/.claude/skills/react-performance
```

## Related Skills

- `react-best-practices` — Full 57-rule guide with detailed code examples

---

Part of the [Frontend](..) skill category.
