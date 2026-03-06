---
name: securevibes-scanner
description: Run AI-powered application security scans on codebases. Use when asked to scan code for security vulnerabilities, generate threat models, review code for security issues, run incremental security scans, or set up continuous security monitoring via cron. Supports full scans (one-shot) and incremental scans (cron-driven, only new commits).
---

# SecureVibes Scanner

AI-native security platform that detects vulnerabilities using Claude AI. Multi-subagent pipeline: assessment → threat modeling → code review → report generation → optional DAST. Supports incremental scanning for continuous monitoring.

## Prerequisites

1. Install the CLI: `pipx install securevibes` (preferred) or `uv tool install securevibes`. Avoid `pip install` — it can create stale shims if you have multiple Python environments.
2. Authenticate with Anthropic (one of):
   - **Max/Pro subscription (recommended):** If you're authenticated via Claude Code or Claude CLI OAuth, no API key is needed. The Claude Agent SDK picks up your OAuth session automatically. When running inside OpenClaw, leave `ANTHROPIC_API_KEY` unset or blank — the SDK handles auth.
   - **API key:** `export ANTHROPIC_API_KEY=your-key-here` (from console.anthropic.com)

## Security Notes

- Always use the `scripts/scan.sh` wrapper for full scans — it validates paths and rejects shell metacharacters before invoking `securevibes`.
- **Never interpolate unsanitized user input into shell commands.**
- The wrapper uses `realpath` to resolve paths safely and rejects any path containing `;`, `|`, `&`, `$`, backticks, or other metacharacters.
- **Scan targets must be local directories.** Clone remote repos to a known safe location first, then pass the resolved path to the wrapper.
- **DAST scans make network requests** to the `--target-url` you provide. Only use against apps you own or have permission to test.

## Execution Model

**Full scans take 10-30 minutes across 4 phases.** Run them as background jobs (cron or subagent), not inline.

**Incremental scans take 2-10 minutes** — they only scan commits since the last run.

## Full Scan (One-Shot)

### Running a Scan

1. Clone the target repo to a local directory
2. Run the wrapper script: `bash scripts/scan.sh /path/to/repo --force --debug`
3. Results appear in `/path/to/repo/.securevibes/`

### Background Execution (Recommended)

For OpenClaw users, schedule scans as cron jobs:

- Use `sessionTarget: "isolated"` with `payload.kind: "agentTurn"`
- Set `payload.timeoutSeconds: 2700` (45 minutes) to allow all phases to complete
- Use `delivery.mode: "announce"` to get notified when done

The agentTurn message should instruct the subagent to:
1. `cd` into the repo and `git pull` for latest code
2. Clean previous `.securevibes/` artifacts
3. Run `securevibes scan . --force` via the wrapper script
4. Read and summarize the results from `.securevibes/scan_report.md`

## Incremental Scan (Continuous Monitoring)

The incremental scanner (`ops/incremental_scan.py`) tracks the last-scanned commit and only scans new commits. Designed for cron-driven continuous security monitoring.

### How It Works

1. Tracks an anchor commit in `.securevibes/incremental_state.json`
2. On each run: fetches remote, compares HEAD to anchor
3. If new commits exist: runs `securevibes pr-review` on the diff
4. Updates anchor to new HEAD after successful scan
5. If no new commits: exits cleanly (no scan, no cost)

### Setup

#### Step 1: Run an initial full scan (if not already done)

The incremental scanner requires `.securevibes/SECURITY.md` and `.securevibes/THREAT_MODEL.json` to exist. These come from an initial full scan:

```bash
securevibes scan <repo-path> --model sonnet
```

Skip this step if the repo already has a `.securevibes/` directory with these files.

#### Step 2: Bootstrap incremental state

Run the wrapper once to seed the anchor commit (no scan runs, just records current HEAD):

```bash
python3 ops/incremental_scan.py --repo <repo-path> --remote origin --branch main
```

This creates `.securevibes/incremental_state.json` with `status: "bootstrap"`.

#### Step 3: Configure the cron

For OpenClaw users, create a cron job:

```bash
openclaw cron create \
  --name "securevibes-incremental" \
  --cron "*/30 * * * *" \
  --tz "America/Los_Angeles" \
  --agent main \
  --session isolated \
  --timeout-seconds 900 \
  --announce \
  --message "Run incremental security scan: python3 <skill-path>/ops/incremental_scan.py --repo <repo-path> --remote origin --branch main --model sonnet --severity medium --scan-timeout-seconds 600. Read .securevibes/incremental_scan.log for results. If new findings, summarize them."
```

Replace `<skill-path>` with the installed skill path and `<repo-path>` with the target repo.

#### Step 4: Verify

```bash
# Check state
cat <repo-path>/.securevibes/incremental_state.json

# After first scheduled run, check logs
tail -10 <repo-path>/.securevibes/incremental_scan.log

# Check findings
cat <repo-path>/.securevibes/PR_VULNERABILITIES.json
```

### Incremental Scanner Options

```
python3 ops/incremental_scan.py [options]
```

| Option | Description |
|--------|-------------|
| `--repo` | Repository path (default: `.`) |
| `--branch` | Branch to track (default: `main`) |
| `--remote` | Git remote (default: `origin`) |
| `--model` | Claude model: `sonnet`, `haiku` (default: `sonnet`) |
| `--severity` | Minimum severity: `critical`, `high`, `medium`, `low` |
| `--scan-timeout-seconds` | Timeout per scan command (default: `900`) |
| `--git-timeout-seconds` | Timeout for git operations (default: `60`) |
| `--rewrite-policy` | History rewrite handling: `reset_warn`, `strict_fail`, `since_date` |
| `--since` | Override: scan commits since this date (ISO or YYYY-MM-DD) |

### Operational Guarantees

- **File lock** at `.securevibes/.incremental_scan.lock` prevents overlapping runs
- **Atomic state writes** (`fsync` + `os.replace`) prevent corruption
- **Structured logging** at `.securevibes/incremental_scan.log`
- **Run records** saved to `.securevibes/incremental_runs/` (one JSON per run)

### Rewrite Policy

When `last_seen_sha` is not an ancestor of the new remote HEAD (e.g., force push):

| Policy | Behavior |
|--------|----------|
| `reset_warn` | Reset anchor to new HEAD, continue |
| `strict_fail` | Fail and keep current anchor |
| `since_date` | Run a `--since <today>` scan for visibility, keep previous anchor |

## Full Scan Commands Reference

### Scan

`securevibes scan <path> [options]`

| Option | Description |
|--------|-------------|
| `-f, --format` | `markdown` (default), `json`, `text`, `table` |
| `-o, --output` | Custom output path |
| `-s, --severity` | Filter: `critical`, `high`, `medium`, `low` |
| `-m, --model` | Claude model (e.g., `sonnet`, `haiku`) |
| `--subagent` | Run one phase: `assessment`, `threat-modeling`, `code-review`, `report-generator`, `dast` |
| `--resume-from` | Resume from a specific phase onwards |
| `--dast` | Enable dynamic testing (requires `--target-url`) |
| `--target-url` | URL for DAST (e.g., `http://localhost:3000`) |
| `--force` | Skip prompts, overwrite existing artifacts |
| `--quiet` | Minimal output |
| `--debug` | Verbose diagnostics |

### Report

`securevibes report <path>` — Display a previously saved scan report.

## Mapping Requests to Actions

| User Says | Action |
|-----------|--------|
| "Scan this for security issues" | Full scan: `bash scripts/scan.sh <path> --force` |
| "Quick security check" | Full scan: `bash scripts/scan.sh <path> -m haiku --force` |
| "Threat model this project" | `bash scripts/scan.sh <path> --subagent threat-modeling --force` |
| "Just review the code" | `bash scripts/scan.sh <path> --subagent code-review --force` |
| "Show only critical/high findings" | `bash scripts/scan.sh <path> -s high --force` |
| "Full audit with DAST" | `bash scripts/scan.sh <path> --dast --target-url <url> --force` |
| "Set up continuous scanning" | Incremental setup: Steps 1-4 above |
| "Monitor this repo for security issues" | Incremental setup: Steps 1-4 above |
| "Show last scan results" | `securevibes report <path>` |

## Subagent Pipeline

Runs sequentially. Each phase builds on the previous:

1. **assessment** → Architecture & attack surface → `.securevibes/SECURITY.md`
2. **threat-modeling** → STRIDE-based analysis → `.securevibes/THREAT_MODEL.json`
3. **code-review** → Vulnerability detection → `.securevibes/VULNERABILITIES.json`
4. **report-generator** → Consolidated report → `.securevibes/scan_report.md`
5. **dast** (optional) → Dynamic validation against running app

## Presenting Results

After a scan completes:

1. Read `.securevibes/scan_report.md` (or `.securevibes/scan_results.json` for structured data)
2. Summarize: total findings by severity (Critical > High > Medium > Low)
3. Highlight top 3 most critical with file locations and remediation
4. Offer next steps: run DAST, fix specific issues, re-scan after changes

## Links

- **Website**: [https://securevibes.ai](https://securevibes.ai)
- **PyPI**: [https://pypi.org/project/securevibes/](https://pypi.org/project/securevibes/)
- **GitHub**: [https://github.com/anshumanbh/securevibes](https://github.com/anshumanbh/securevibes)
