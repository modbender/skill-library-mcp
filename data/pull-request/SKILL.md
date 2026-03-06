---
name: Pull Request
slug: pull-request
version: 1.0.1
description: Create high-quality pull requests with pre-submission validation, maintainer-friendly formatting, and automated quality checks.
---

## When to Use

Before creating or suggesting a pull request to ANY repository. Acts as a quality filter to prevent wasting maintainer time and embarrassing the contributor.

## Quick Reference

| Domain | File |
|--------|------|
| Pre-submission checklist | `checklist.md` |
| Red flags to avoid | `red-flags.md` |
| Repository context gathering | `repo-context.md` |
| PR description templates | `templates.md` |

## Critical Rules

- **Read CONTRIBUTING.md first** — Adapt to project's workflow, not a fixed pattern
- **Issue policy depends on scope** — Small fixes may PR directly; features need discussion first
- **Disclose AI involvement** — Mark AI-assisted PRs in title/description
- **Run checks if possible** — If you can't run tests, say so explicitly
- **Match existing style** — Check for `.editorconfig`, `prettier`, `eslint` configs
- **Small and focused** — One logical change per PR
- **No secrets ever** — Use `<PLACEHOLDER>` syntax

## Issue Policy (Contextual)

**NOT all projects require issues first.** Check CONTRIBUTING.md, then:

| Change Type | Default Action |
|-------------|----------------|
| Typo, small bug fix | PR directly (unless CONTRIBUTING.md says otherwise) |
| New feature | Open Discussion/Issue first, wait for approval |
| Architecture change | RFC or Discussion required |
| When in doubt | Ask in issue before coding |

## AI-Assisted PRs

If this PR was created with AI assistance:

1. **Mark it** — Add `[AI-assisted]` to PR title or note in description
2. **Testing level** — State: `untested` / `lightly tested` / `fully tested`
3. **Include context** — Prompts or session logs if available and helpful
4. **Confirm understanding** — "I have reviewed this code and understand what it does"
5. **Human accountable** — Link to the human directing the contribution

## Rate Limiting (Avoid Spam)

- MAX 1 open PR per repo at a time
- Wait 24h between PRs to same repo
- If 2 PRs rejected consecutively → STOP and escalate to human
- Check repo's PR velocity first (don't flood low-activity projects)

## Abandonment Prevention

- MUST respond to review feedback within 48h
- If unable to address feedback, close with: "I cannot continue; @human please take over or close"
- Never leave PRs to rot

## Scope Boundaries — STOP and Discuss First If:

- Change touches >5 files OR >200 lines
- Change modifies public API
- Change involves security, auth, or crypto
- Change is in governance, licensing, or CoC
- Maintainer requested discussion in issue
- You're unsure if this aligns with project philosophy

## Human Escalation Required

Escalate to human when:
- Reviewer asks clarifying questions about design intent
- CI fails in non-obvious way
- Any pushback beyond "fix this typo"
- Reviewer seems confused or frustrated
- You can't run the test suite locally
