---
name: whoop-cli
description: Companion skill for @andreasnlarsen/whoop-cli: agent-friendly WHOOP access via stable CLI JSON (day briefs, health flags, trends, exports) without raw API plumbing.
metadata:
  openclaw:
    requires:
      bins:
        - whoop
      env:
        - WHOOP_CLIENT_ID
        - WHOOP_CLIENT_SECRET
        - WHOOP_REDIRECT_URI
    primaryEnv: WHOOP_CLIENT_SECRET
    homepage: https://github.com/andreasnlarsen/whoop-cli
    install:
      - kind: node
        package: "@andreasnlarsen/whoop-cli@0.3.1"
        bins:
          - whoop
        label: Install whoop-cli from npm
---

# whoop-cli

Use the installed `whoop` command.

## Security + credential handling (required)

- Never ask users to paste client secrets/tokens into chat.
- For first-time auth, the user should run login **locally on their own shell**.
- Prefer read-only operational commands in agent flows (`summary`, `day-brief`, `health`, `trend`, `sync pull`).
- Do not run `whoop auth login` unless the user explicitly asks for login help.
- Tokens are stored locally at `~/.whoop-cli/profiles/<profile>.json` by the CLI.

## Install / bootstrap

If `whoop` is missing:

```bash
npm install -g @andreasnlarsen/whoop-cli@0.3.1
```

Optional OpenClaw skill install from package bundle:

```bash
whoop openclaw install-skill --force
```

## Core checks

1. `whoop auth status --json`
2. If unauthenticated, ask the user to run local login:
   - `whoop auth login --client-id ... --client-secret ... --redirect-uri ...`
3. Validate:
   - `whoop day-brief --json --pretty`

## Useful commands

- Daily:
  - `whoop summary --json --pretty`
  - `whoop day-brief --json --pretty`
  - `whoop strain-plan --json --pretty`
  - `whoop health flags --days 7 --json --pretty`
- Activity analysis:
  - `whoop activity list --days 30 --json --pretty`
  - `whoop activity trend --days 30 --json --pretty`
  - `whoop activity types --days 30 --json --pretty`
  - training-only: `whoop activity trend --days 30 --labeled-only --json --pretty`

### Activity interpretation guardrail (important)

- WHOOP generic `activity` rows (often `sport_id=-1`) are auto-detected and may be unlabeled movement (housework/incidental activity), not intentional training.
- Do not treat generic `activity` as confirmed training volume by default.
- For coaching/training recommendations, default to `--labeled-only` and report both total vs filtered counts.

### Agent filtering pattern (jq-friendly)

- Canonical source: `whoop activity list --json`
- Prefer built-in filters first (`--labeled-only`, `--generic-only`, `--sport-id`, `--sport-name`).
- If custom slicing is needed and `jq` is available, filter shell-side from raw JSON (example):

```bash
whoop activity list --days 30 --json | jq '.data.records | map(select(.sport_id != -1))'
```

- Export:
  - `whoop sync pull --start YYYY-MM-DD --end YYYY-MM-DD --out ./whoop.jsonl --json --pretty`

## Experiment protocol (agent-required)

- Canonical state: `~/.whoop-cli/experiments.json` only.
- Plan experiments with context at creation time:
  - `whoop experiment plan --name ... --behavior ... --start-date YYYY-MM-DD [--end-date YYYY-MM-DD] --description ... --why ... --hypothesis ... --success-criteria ... --protocol ... --json --pretty`
- Update context without creating duplicate state:
  - `whoop experiment context --id ... [--description ... --why ... --hypothesis ... --success-criteria ... --protocol ...] --json --pretty`
- Check lifecycle/status with:
  - `whoop experiment status [--status planned|running|completed] [--id ...] --json --pretty`
- Evaluate outcomes with:
  - `whoop experiment report --id ... --json --pretty`
- Profile scope is strict by default (active `--profile` only).
  - Use `--all-profiles` only when cross-profile visibility is explicitly needed.
- Prefer output field `sourceOfTruth` (path to canonical state file); `experimentsFile` is kept as compatibility alias.
- Avoid duplicating experiment state into other files unless the user explicitly asks for separate notes.

## Safety

- Never print client secrets or raw tokens.
- Keep API errors concise and actionable.
- Treat this integration as unofficial/non-affiliated.
