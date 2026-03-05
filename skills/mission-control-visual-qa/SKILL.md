---
name: mission-control-visual-qa
description: Run Mission Control visual QA over SSH using Puppeteer screenshots and basic DOM checks.
---

# mission-control-visual-qa

Author: billy-ops-agent

## Purpose
Run visual QA (screenshots + basic DOM checks) for Mission Control pages on REMOTE via SSH (remote operator machine).

## What this skill includes
- `scripts/mission-control-visual-qa.js`: Puppeteer-based remote runner (intended to run on REMOTE).
- `scripts/run-mission-control-visual-qa.sh`: Local helper that copies and runs the Node script over `scp` + `ssh`.

## Safety rules
- Only target Mission Control pages you are authorized to inspect.
- Default output path is `~/.openclaw/workspace/output/visual-qa/` on REMOTE.
- No external network activity is performed by scripts other than SSH/SCP to REMOTE and page loads for supplied URLs.
- Script is read-only and does not submit forms or click destructive controls.

## Usage
From local machine:

```bash
bash scripts/run-mission-control-visual-qa.sh \
  "https://mission-control.example.local/dashboard" \
  "https://mission-control.example.local/status"
```

Optional env vars:
- `SSH_TARGET` (default: `neill@<YOUR_REMOTE_HOST>`)
- `REMOTE_RUN_DIR` (default: `~/.openclaw/workspace/mission-control-visual-qa-runner`)
- `OUTPUT_DIR` (default: `~/.openclaw/workspace/output/visual-qa/`)

## Expected output
On REMOTE host, each URL produces:
- `*.png` screenshot
- basic DOM result (`title` + presence of `main`, `h1`, and body text)
- final JSON summary printed to stdout

## Quickstart

1) Install

- Install from ClawHub (public skill).

2) Use

- Invoke the skill by name inside OpenClaw.

## Safety

- No secrets are embedded in this skill.
- Any remote commands require you to configure your own SSH target.
