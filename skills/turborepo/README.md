# Turborepo

Build system for JavaScript/TypeScript monorepos. Caches task outputs and runs tasks in parallel based on dependency graph. Comprehensive configuration, caching, CI/CD, and anti-pattern prevention.

## What's Inside

- Package tasks vs root tasks (critical distinction)
- Quick decision trees (configure tasks, fix cache, run changed packages, filter, env vars, CI setup, watch mode, package structure, boundaries)
- Critical anti-patterns (root tasks, `turbo` shorthand, `&&` chaining, `prebuild` scripts, overly broad globalDependencies, missing outputs, root `.env`)
- Common task configurations (standard build pipeline, dev with `turbo watch`, transit nodes for parallel tasks)
- Environment variable management (strict mode, `.env` files, framework inference)
- Comprehensive reference index (configuration, caching, environment, filtering, CI/CD, CLI, best practices, watch mode, boundaries)

## When to Use

- Configuring turbo.json task pipelines
- Creating packages and sharing code between apps
- Setting up monorepo structure (apps/, packages/)
- Running `--affected` builds in CI
- Debugging cache misses
- Managing environment variables across packages

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/devops/turborepo
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install turborepo
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/devops/turborepo .cursor/skills/turborepo
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/devops/turborepo ~/.cursor/skills/turborepo
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/devops/turborepo .claude/skills/turborepo
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/devops/turborepo ~/.claude/skills/turborepo
```

---

Part of the [DevOps](..) skill category.
