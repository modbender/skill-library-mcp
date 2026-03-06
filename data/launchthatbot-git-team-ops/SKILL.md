---
name: launchthatbot-git-team-ops
version: 0.1.3
description: Role-based GitOps skill for OpenClaw agents with junior and senior operating modes.
author: LaunchThatBot
homepage: https://launchthatbot.com
requires:
  mcp: launchthatbot
metadata:
  {
    "openclaw":
      { "emoji": "🛠️", "requires": { "bins": [], "env": [], "config": [] } },
  }
---

# Skill: launchthatbot/git-team-ops

You are operating the `launchthatbot/git-team-ops` skill.

## What this skill does

This skill configures an OpenClaw agent to work in a multi-agent Git workflow with strict role behavior.

Supported roles:

- `junior`: code + PR only.
- `senior`: review, merge, release, and repo workflow management.

## First question to ask user

Ask exactly:

1. `What type of agent am I? (junior/senior)`
2. `Which GitHub repository should I operate on?`
3. `How should I authenticate? (managed-app/byo-app/pat)`

If any answer is missing, stop and request it.

## Role policies

### junior policy

- Allowed:
  - Create branch from latest `main`.
  - Commit scoped changes.
  - Push branch.
  - Open PR with test notes.
- Not allowed:
  - Merge PRs.
  - Force push protected branches.
  - Modify `.github/workflows` unless explicitly approved by senior user.

### senior policy

- Allowed:
  - Review and merge junior PRs.
  - Enforce branch protection checks.
  - Add/update workflow files from this package templates.
  - Trigger release/deploy workflows.
- Required:
  - Keep PRs small and scoped.
  - Require CI pass before merge.
  - Reject direct commits to `main` except controlled automation commits.

## Authentication modes

### managed-app mode

Default path for this skill. No LaunchThatBot login is required.

Use platform endpoints and short-lived onboarding token:

- `POST /github/install/start`
- `GET /github/install/status`
- `POST /github/agent/onboard`

Never persist onboarding token longer than one session.
Treat all onboarding tokens as sensitive and short-lived.

Rate limits:

- Anonymous: max 3 active bot leases per source IP.
- Authenticated LaunchThatBot users: higher per-IP cap.

### byo-app mode

User must provide:

- GitHub App ID
- Installation ID
- App private key (PEM)

Use only installation access tokens for repo operations.
Never request long-lived user PAT if installation token flow is available.

### pat mode

Allowed as fallback only when app setup is unavailable.
Recommend migration to app mode.

## Senior onboarding flow

1. Validate access to target repository.
2. Create branch `chore/gitops-bootstrap`.
3. Copy templates from this package into repo:
   - `templates/github/workflows/junior-pr-validate.yml` -> `.github/workflows/junior-pr-validate.yml`
   - `templates/github/workflows/senior-release-control.yml` -> `.github/workflows/senior-release-control.yml`
   - `templates/github/CODEOWNERS.md` -> `.github/CODEOWNERS`
4. Commit and open PR.
5. Ask user to merge after review.
6. Verify workflows are active on default branch.

## Junior onboarding flow

1. Confirm repository access.
2. Create branch `test/junior-onboarding-<agent-name>`.
3. Add lightweight verification commit (for example, docs note under `.agent-work/`).
4. Open PR to prove branch/PR permissions are working.
5. Wait for senior review.

## Operational guardrails

- Always fetch latest `main` before branch creation.
- One task branch per logical change.
- Keep commit messages descriptive and scoped.
- Do not auto-delete branches until PR is merged and user approves cleanup.
- Never bypass branch protections.

## Security

- Use least-privilege permissions.
- Prefer short-lived installation tokens over PATs.
- Do not print secrets in logs.
- Do not write secrets into repository files.
- Respect source-IP limits in managed mode.

## Output style

When reporting actions:

- State the role mode (`junior` or `senior`).
- State repository and branch used.
- State exactly which files/workflows were changed.
- State next required human approval step.
