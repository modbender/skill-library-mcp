---
name: pr-triage
description: Triage GitHub PRs and issues using vision-based scoring. Use when a user wants to prioritize, score, review, de-duplicate, or batch-process open pull requests or issues against their project's mission and values. Supports onboarding (interview repo owner to build vision doc), scanning (score PRs with rubric), and reporting (generate actionable markdown reports). Works with any GitHub repo via gh CLI.
---

# PR Triage

Score and prioritize GitHub PRs against a project's vision document. Three-step workflow: onboard, scan, report.

## Quick Start

```bash
# 1. Onboard: gather repo context, interview the owner
python3 scripts/onboard.py https://github.com/owner/repo --output-dir ./triage-config

# 2. Scan: score open PRs against the vision
python3 scripts/scan.py https://github.com/owner/repo ./triage-config/vision.md --output scores.json

# 3. Report: generate markdown triage reports
python3 scripts/report.py scores.json --output-dir ./triage-reports
```

## Workflow

### Step 1: Onboard (one-time per repo)

Run `scripts/onboard.py` with a GitHub repo URL. It fetches the README, CONTRIBUTING.md, recent releases, and repo metadata via `gh` CLI, then outputs an interview prompt.

Use the interview prompt to ask the repo owner these questions:

**Identity & Mission:**
1. In one sentence, what is this project and who is it for?
2. What problem does it solve that alternatives do not?
3. What are your 3-5 non-negotiable principles?

**Priorities:**
4. Rank contribution areas by importance: security, bugs, features, performance, docs, tests, refactoring
5. What types of PRs would you auto-reject?
6. What types of PRs would you fast-track?

**Red/Green Flags:**
7. What patterns signal low-quality contributions?
8. What makes you excited to review a PR?
9. Specific areas where you want help?

**Context:**
10. Growth mode, maintenance mode, or transitioning?
11. Upcoming milestones affecting prioritization?
12. How do you handle breaking changes?

After the interview, generate two files in the output directory:
- `vision.md` - Project mission, identity, priorities, alignment signals
- `rubric.md` - Scoring rubric customized from `references/rubric-template.md`

### Step 2: Scan (run per triage session)

Run `scripts/scan.py` with the repo URL and vision doc path. It:
- Fetches open PRs via `gh pr list` (title, body, labels, stats, author, date)
- Applies rule-based scoring: base 50, with positive/negative modifiers
- Detects potential duplicates via title similarity
- Outputs JSON with scores, reasoning, and distribution

The scan uses heuristic scoring (keyword matching, diff size, test mentions). For deeper analysis, read the JSON output and apply additional LLM reasoning to ambiguous PRs (scores 40-60).

Options:
- `--count N` - Number of PRs to fetch (default: 100)
- `--output file.json` - Save to file instead of stdout

### Step 3: Report (run after scan)

Run `scripts/report.py` with the scan JSON. It generates four markdown files:
- `prioritize.md` - PRs scoring 80+ (fast-track for review)
- `review.md` - PRs scoring 50-79 (standard queue)
- `close.md` - PRs scoring below 50 (likely close or request changes)
- `summary.md` - Distribution, top 3, patterns, duplicates, active authors

## Scoring Overview

Base score: 50. Key modifiers:

| Signal | Points |
|--------|--------|
| Security fix | +20 |
| Bug fix with tests | +10 |
| Core functionality improvement | +10 |
| Performance (measured) | +8 |
| Small focused diff | +5 |
| Has tests | +5 |
| Spam/promotion | -30 |
| Unwanted dependency | -25 |
| Large diff, no tests | -15 |
| No description | -5 |

Full rubric: `references/rubric-template.md`
Example vision doc: `references/example-vision.md`

## Recurring Triage via Cron

Set up a cron job to scan weekly:

```
description: Weekly PR triage for owner/repo
schedule: "0 9 * * MON"
model: anthropic/claude-sonnet-4-20250514
channel: telegram
```

Cron prompt: "Run pr-triage scan on https://github.com/owner/repo using ./triage-config/vision.md, generate reports, and send the summary."

## Requirements

- `gh` CLI installed and authenticated (`gh auth login`)
- Python 3.10+
- No additional Python packages needed (stdlib only)
