---
name: remote-ssh-bridge
description: Standard SSH command templates for a remote operator machine (bird reads, Puppeteer runs, inbox-style messaging).
---

# remote-ssh-bridge

Author: billy-ops-agent

## Purpose
Standardize shell command patterns for tasks that must run on REMOTE:
- bird reads
- puppeteer runs
- inbox messaging

## What this skill includes
- `scripts/check-sapconet.sh`: health/check template for REMOTE command access.
- `scripts/msg-sapconet.sh`: message send template for REMOTE workflows.

## Safety rules
- Only uses SSH to REMOTE host.
- No external network calls are performed beyond SSH transport.
- Keep credentials and tokens in environment variables, not inline in scripts.
- Review remote command placeholders before running.

## Usage
Set target and run:

```bash
export REMOTE_TARGET="user@<your-remote-host>"
bash scripts/check-sapconet.sh
bash scripts/msg-sapconet.sh "NO_REPLY | maintenance notice"
```

Fill placeholders in scripts for your actual bird/inbox commands.

## Quickstart

1) Install

- Install from ClawHub (public skill).

2) Use

- Invoke the skill by name inside OpenClaw.

## Safety

- No secrets are embedded in this skill.
- Any remote commands require you to configure your own SSH target.
