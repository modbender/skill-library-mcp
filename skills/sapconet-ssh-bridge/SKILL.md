---
name: sapconet-ssh-bridge
description: Standard SAPCONET SSH command templates for bird reads, Puppeteer runs, and inbox messaging workflows.
---

# sapconet-ssh-bridge

Author: Billy (SAPCONET)

## Purpose
Standardize shell command patterns for tasks that must run on SAPCONET:
- bird reads
- puppeteer runs
- inbox messaging

## What this skill includes
- `scripts/check-sapconet.sh`: health/check template for SAPCONET command access.
- `scripts/msg-sapconet.sh`: message send template for SAPCONET workflows.

## Safety rules
- Only uses SSH to SAPCONET host.
- No external network calls are performed beyond SSH transport.
- Keep credentials and tokens in environment variables, not inline in scripts.
- Review remote command placeholders before running.

## Usage
Set target and run:

```bash
export SAPCONET_TARGET="neill@100.110.24.44"
bash scripts/check-sapconet.sh
bash scripts/msg-sapconet.sh "NO_REPLY | maintenance notice"
```

Fill placeholders in scripts for your actual bird/inbox commands.
