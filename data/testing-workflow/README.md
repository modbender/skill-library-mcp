# Testing Workflow

Meta-skill that orchestrates comprehensive testing across a project by coordinating testing-patterns, e2e-testing, and testing agents. Routes to the right skill at each stage and ensures nothing is missed.

## What's Inside

- Five-phase orchestration flow:
  1. Discovery and baseline (scan infrastructure, measure coverage, map gaps)
  2. Strategy selection (project type, test patterns, critical journeys)
  3. Implementation (unit → integration → E2E → edge cases)
  4. Validation (run suite, measure coverage, check quality, verify CI)
  5. Maintenance (coverage ratcheting, flaky test policy, test review standards, health audits)
- Skill routing table (which skill to use for which need)
- Coverage targets by project type (startup MVP through critical infrastructure)
- Testing strategy template for documentation
- Quality gates for testing completion

## When to Use

- Setting up testing for a new project from scratch
- Improving coverage for an existing project with gaps
- Establishing or revising a testing strategy
- Before a major release to verify quality gates are met
- After a large refactor to confirm nothing broke
- During code review when test adequacy is in question
- Onboarding a team to a testing workflow

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/testing/testing-workflow
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/testing/testing-workflow .cursor/skills/testing-workflow
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/testing/testing-workflow ~/.cursor/skills/testing-workflow
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/testing/testing-workflow .claude/skills/testing-workflow
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/testing/testing-workflow ~/.claude/skills/testing-workflow
```

## Related Skills

- [testing-patterns](../testing-patterns/) — Unit and integration test patterns (routed to in Phase 3)
- [e2e-testing-patterns](../e2e-testing-patterns/) — E2E test patterns (routed to in Phase 3)
- [clean-code](../clean-code/) — Code quality standards
- [code-review](../code-review/) — Review checklist
- [quality-gates](../quality-gates/) — CI/CD quality checkpoints
- [debugging](../debugging/) — Debugging test failures

---

Part of the [Testing](..) skill category.
