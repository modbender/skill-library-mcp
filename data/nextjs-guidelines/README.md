# Next.js App Router

Next.js App Router best practices — Server Components, data fetching, caching, routing, middleware, metadata, error handling, streaming, Server Actions, and performance optimization for Next.js 14-16+.

## What's Inside

- Rendering modes: Server Components, Client Components, Static, Dynamic, Streaming
- File conventions and route organization
- Data fetching patterns and waterfall avoidance
- Server Actions for mutations
- Caching strategy (no-cache, static, ISR, tag-based)
- RSC boundary rules and serialization
- Async APIs (Next.js 15+)
- Parallel routes, intercepting routes, and modal patterns
- Metadata and SEO optimization
- Error handling and redirect gotchas
- Streaming with Suspense
- Performance: next/image, next/link, next/font, next/script
- Hydration error causes and fixes
- Self-hosting with Docker and PM2

## When to Use

- Building Next.js applications with App Router
- Migrating from Pages Router to App Router
- Implementing Server Components and streaming
- Setting up parallel and intercepting routes
- Optimizing data fetching and caching
- Building full-stack features with Server Actions
- Debugging hydration errors or RSC boundary issues

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/frontend/nextjs
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install nextjs
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/frontend/nextjs .cursor/skills/nextjs
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/frontend/nextjs ~/.cursor/skills/nextjs
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/frontend/nextjs .claude/skills/nextjs
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/frontend/nextjs ~/.claude/skills/nextjs
```

## Related Skills

- `react-best-practices` — React/Next.js performance optimization rules
- `react-performance` — Performance patterns prioritized by impact

---

Part of the [Frontend](..) skill category.
