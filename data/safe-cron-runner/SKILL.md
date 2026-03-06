---
name: safe-cron-runner
version: 1.0.2
description: "Executes background tasks safely by dropping privileges and enforcing timeouts. Includes ISNAD signed manifest."
author: LeoAGI
metadata: { "openclaw": { "emoji": "🛡️", "category": "security" } }
---

# Safe Cron Runner 🛡️

**A secure background task executor for AI Agents.**

## Overview
This skill wraps background task execution to ensure that autonomous agents don't accidentally (or maliciously) execute long-running or privileged commands.

## Key Protections
1. **Privilege Dropping:** Automatically drops root privileges (switches to `nobody`) before executing the subprocess.
2. **Strict Timeouts:** Enforces hard timeouts to prevent infinite loops or resource exhaustion.
3. **Shell Injection Protection:** Uses list-based command execution (subprocess without shell) to prevent common command injection attacks.
4. **Transparent Logging:** Separates and logs `stdout`, `stderr`, and execution status for auditability.

## ISNAD Signed
This skill includes an ISNAD manifest (`isnad_manifest.json`) verifying the integrity of the release.

## Usage

```python
from safe_cron import SafeCronRunner

runner = SafeCronRunner(safe_user="nobody", timeout_sec=60)

# Execute command as a list for safety
result = runner.run_task(["ls", "-la", "/tmp"])
print(result)
```
