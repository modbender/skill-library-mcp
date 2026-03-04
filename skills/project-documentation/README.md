# Project Documentation

Complete workflow for project documentation including ADRs, PRDs, personas, and docs organization. Ensures consistent documentation across projects with a docs-first philosophy.

## What's Inside

- Docs-first philosophy (define before building)
- Directory structure for documentation
- Critical separation: current state vs future planning
- Documentation type templates (ADRs, PRDs, personas, runbooks)
- Roadmap format
- Quality gates for shipping docs
- Anti-patterns
- New project checklist

## When to Use

- Starting a new project and need docs structure
- Improving documentation on an existing project
- Setting up ADRs, PRDs, or persona docs
- Want consistent documentation across projects

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/meta/project-documentation
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install project-documentation
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/meta/project-documentation .cursor/skills/project-documentation
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/meta/project-documentation ~/.cursor/skills/project-documentation
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/meta/project-documentation .claude/skills/project-documentation
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/meta/project-documentation ~/.claude/skills/project-documentation
```

## Related Skills

- `/bootstrap-docs` command — Bootstrap documentation for a project
- `/new-feature` command — Feature development workflow
- `development` agent — Docs-first feature development

---

Part of the [Meta](..) skill category.
