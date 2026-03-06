# @launchthatbot/git-team-ops

## What is LaunchThatBot

LaunchThatBot is a platform for operating OpenClaw agents with a managed control plane, security defaults, and real-time visibility while still keeping your agents on your infrastructure.

## What this skill is for

`@launchthatbot/git-team-ops` is a role-based GitOps skill for teams running multiple coding agents in one repository.

It supports:

- `junior` agents (main coders)
- `senior` agents (main branch + release controllers)

This skill can work with:

- LaunchThatBot managed GitHub App mode (default, no login required)
- Bring-your-own GitHub App mode (advanced)

## Role model

### Junior

- Can create branch, commit, push, and open PRs.
- Cannot merge to main.
- Cannot publish releases.
- Cannot modify repository workflow automation.

### Senior

- Can review/merge PRs.
- Can install/update repository workflow templates.
- Can trigger release and deployment workflows.
- Can orchestrate junior agent workstreams.

## Install

```bash
npx clawhub@latest install launchthatbot-git-team-ops
```

## Skill templates

This package ships templates under `templates/` for:

- `.github/workflows` examples
- `CODEOWNERS` baseline

Senior agents can copy these templates into the target repository and open a bootstrap PR.

Source paths in this package:

- `templates/github/workflows/junior-pr-validate.yml`
- `templates/github/workflows/senior-release-control.yml`
- `templates/github/CODEOWNERS.md`

Target paths in the destination repository:

- `.github/workflows/junior-pr-validate.yml`
- `.github/workflows/senior-release-control.yml`
- `.github/CODEOWNERS`

## GitHub App setup model

Use one of:

- Managed App (default): platform handles installation + token minting without requiring a LaunchThatBot login for baseline usage.
- BYO App: user provides App ID, Installation ID, and private key.

Managed App limits:

- Anonymous usage is limited to 3 active bots per source IP.
- Signed-in LaunchThatBot users get a higher per-IP cap.

For either mode, keep permissions least-privilege and enforce branch protections on `main`.

## Support

- Website: https://launchthatbot.com
- Discord: https://discord.gg/launchthatbot
