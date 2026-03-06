# Monorepo Management

Build and manage monorepos with Turborepo, Nx, and pnpm workspaces — covering workspace structure, dependency management, task orchestration, caching, CI/CD, and publishing. Use when setting up monorepos, optimizing builds, or managing shared packages.

## What's Inside

- Tool Selection — package managers (pnpm, npm, Yarn) and build systems (Turborepo, Nx, Lerna)
- Workspace Structure — apps/ vs packages/ convention
- Turborepo Setup — root configuration, pipeline config, package configuration
- Nx Setup — workspace generation, project generation, affected commands
- Dependency Management (pnpm) — workspace dependencies, filter patterns, .npmrc config
- Shared Configurations — TypeScript, ESLint, Prettier
- Build Optimization — remote caching, cache configuration, precise inputs
- CI/CD — GitHub Actions setup, deploy affected only
- Publishing Packages with Changesets
- Best Practices and Common Pitfalls

## When to Use

- Setting up a new monorepo or migrating from multi-repo
- Optimizing build and test performance
- Managing shared dependencies across packages
- Configuring CI/CD for monorepos
- Versioning and publishing packages

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/backend/monorepo
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/backend/monorepo .cursor/skills/monorepo
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/backend/monorepo ~/.cursor/skills/monorepo
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/backend/monorepo .claude/skills/monorepo
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/backend/monorepo ~/.claude/skills/monorepo
```

## Related Skills

- `service-layer-architecture` — API patterns within monorepo apps
- `postgres-job-queue` — Background jobs for monorepo services

---

Part of the [Backend](..) skill category.
