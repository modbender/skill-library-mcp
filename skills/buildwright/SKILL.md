---
name: buildwright
description: Autonomous development workflow — research codebase, generate spec, get one human approval, then implement with TDD, security scan, and code review without interruption. Use when building features, fixing bugs, or shipping code with consistent quality gates.
license: MIT
compatibility: Requires git and gh (GitHub CLI) with push/PR credentials. Security scans use semgrep, gitleaks, trufflehog if installed (optional). Works with Claude Code, OpenCode, and OpenClaw.
metadata:
  homepage: https://github.com/raunakkathuria/buildwright
  version: "1.0.2"
  author: raunakkathuria
  openclaw:
    requires:
      bins:
        - git
        - gh
      env:
        - BUILDWRIGHT_AUTO_APPROVE
    primaryEnv: BUILDWRIGHT_AUTO_APPROVE
---

# Buildwright

Spec-driven autonomous development. Humans approve intent; agents handle everything else.

## What this skill does

When activated, Buildwright directs the agent to:

1. Read your codebase and steering documents
2. Write a one-page spec (`docs/specs/[feature]/spec.md`)
3. Stop for human approval — unless `BUILDWRIGHT_AUTO_APPROVE=true`
4. Implement the feature with TDD
5. Run quality gates: typecheck, lint, test, build
6. Run optional security scans (if semgrep / gitleaks / trufflehog are installed)
7. Run a Staff Engineer prompt-based code review
8. Commit, push, and open a PR via `gh`

## Requirements

| Requirement | Purpose | Required |
|-------------|---------|----------|
| `git` | Commits and pushes | Yes |
| `gh` (GitHub CLI) | Opens PRs | Yes |
| Git credentials (SSH key or token) | Push access to repo | Yes |
| `semgrep` | SAST security scan | Optional |
| `gitleaks` / `trufflehog` | Secrets detection | Optional |

## Agent Personas (prompt-based, no binaries)

**Staff Engineer** and **Security Engineer** are prompt-engineering personas — instructions loaded from `.claude/agents/` files. They are not external tools or binaries. The agent adopts these personas to review specs and code using defined criteria and confidence thresholds.

## Autonomous Mode

`BUILDWRIGHT_AUTO_APPROVE` controls whether the agent waits for human approval at the spec stage.

| Value | Behavior |
|-------|---------|
| Not set | **Interactive** — stops and waits for "approved" before building |
| `false` | Interactive — same as default |
| `true` | **Autonomous** — commits spec to git (audit trail) and proceeds without waiting |

**Recommendation for first use:** Leave `BUILDWRIGHT_AUTO_APPROVE` unset until you have reviewed a few specs and are comfortable with the workflow.

## Commands

### /bw-new-feature \<description\>

Full pipeline for new features. Auto-detects greenfield vs existing projects.

```
/bw-new-feature "Add OAuth2 login"
```

Flow: Research → Spec → Staff Engineer validates → Human approves → TDD build → Verify → Security scan → Code review → PR

**Artifacts produced:**
- `docs/specs/[feature]/research.md` — what the agent found in your codebase
- `docs/specs/[feature]/spec.md` — implementation plan with approaches considered

---

### /bw-quick \<task\>

Fast path for bug fixes and small tasks (<2 hrs). No spec, no approval step.

```
/bw-quick "Fix the login timeout bug"
```

---

### /bw-ship \[message\]

Quality pipeline for existing work: verify → security → review → PR.

```
/bw-ship "feat(auth): add OAuth2 support"
```

---

### /bw-verify

Quick checks only: typecheck → lint → test → build.

---

### /bw-help

Show all available commands.

---

## Failure Behavior

If any gate fails after retries, the agent commits completed work, pushes, and opens a PR with a structured failure report. It does not leave orphaned branches or silent failures.

## Retry Policy

| Gate | Retries | Rationale |
|------|---------|-----------|
| Verify (typecheck, lint, test, build) | 2x | Fixable by the agent |
| Security scan | None | Requires human judgment |
| Code review | None | Architectural decisions need humans |

## More Information

Full documentation, source code, and setup instructions: https://github.com/raunakkathuria/buildwright
