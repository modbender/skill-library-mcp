---
name: skill-github-daily-ops
version: 1.0.0
description: Daily GitHub repo health check + safe Dependabot auto-merge. Outputs markdown report.
metadata:
  openclaw:
    requires: { bins: ["node"] }
---

# skill-github-daily-ops

Daily GitHub ops: health report per repo + safe auto-merge of Dependabot PRs (medium/low CVEs only).

## Usage

```bash
# Health report for all org repos
node scripts/daily-ops.js --org Zero2Ai-hub --report

# Auto-merge safe Dependabot PRs
node scripts/daily-ops.js --org Zero2Ai-hub --merge-dependabot

# Both — specific repos
node scripts/daily-ops.js --org Zero2Ai-hub --repos "repo1,repo2" --report --merge-dependabot
```

## Arguments

| Arg | Default | Description |
|---|---|---|
| `--org` | `$GITHUB_ORG` env | GitHub organization |
| `--repos` | all | Comma-separated repo names |
| `--report` | false | Output markdown health report |
| `--merge-dependabot` | false | Auto-merge safe Dependabot PRs |

## Environment Variables

| Var | Description |
|---|---|
| `GITHUB_TOKEN` | GitHub PAT (or reads from `~/.github_token`) |
| `GITHUB_ORG` | Default org |

## Auto-Merge Rules

- ✅ Merges: Dependabot PRs where severity is LOW or MEDIUM **and** CI passes
- ⛔ Skips: HIGH or CRITICAL CVE PRs (require human review)
- ⏳ Skips: PRs with failing or in-progress CI

## Report Output

Markdown table per repo with: open PRs, open issues, last commit date, Dependabot PR count.

## Cron Example

```bash
# Daily at 08:00 Dubai time (04:00 UTC)
0 4 * * * cd /path/to/workspace && node skills/skill-github-daily-ops/scripts/daily-ops.js --org Zero2Ai-hub --report --merge-dependabot >> /var/log/github-daily-ops.log 2>&1
```
