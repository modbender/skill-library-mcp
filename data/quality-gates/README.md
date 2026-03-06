# Quality Gates

Enforce quality checkpoints at every stage of the development lifecycle — pre-commit through post-deploy — with configuration examples, threshold tables, bypass protocols, and CI/CD integration.

## What's Inside

- Gate overview (pre-commit, pre-push, pre-merge, pre-deploy staging/production, post-deploy)
- Pre-commit setup (Husky + lint-staged for Node.js, pre-commit framework for Python, secrets scanning)
- CI/CD gate configuration with GitHub Actions
- Coverage gates with threshold enforcement (Jest/Vitest config)
- Security gates (dependency scanning, secret detection tools)
- Performance gates (bundle size budgets, Lighthouse CI thresholds, API response time limits)
- Review gates (required approvals, CODEOWNERS configuration)
- Gate bypass protocol with required documentation

## When to Use

- Setting up quality automation for a new or existing project
- Configuring CI pipelines with automated checks
- Establishing coverage thresholds and enforcement
- Defining deployment requirements and approval workflows
- Before committing, merging, deploying, or during code review

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/testing/quality-gates
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/testing/quality-gates .cursor/skills/quality-gates
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/testing/quality-gates ~/.cursor/skills/quality-gates
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/testing/quality-gates .claude/skills/quality-gates
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/testing/quality-gates ~/.claude/skills/quality-gates
```

## Related Skills

- [testing-patterns](../testing-patterns/) — Test patterns that gates enforce
- [e2e-testing-patterns](../e2e-testing-patterns/) — E2E tests for critical journey gates
- [code-review](../code-review/) — Review standards for the review gate
- [testing-workflow](../testing-workflow/) — Orchestrates quality gates within the testing strategy

---

Part of the [Testing](..) skill category.
