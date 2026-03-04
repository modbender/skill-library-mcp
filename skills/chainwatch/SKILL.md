---
name: chainwatch
description: Runtime safety enforcement for shell commands via chainwatch policy engine
user-invocable: false
metadata: {"openclaw":{"requires":{"bins":["chainwatch"]}}}
---

# Chainwatch Safety Enforcement

You have access to `chainwatch`, a runtime control plane that enforces deterministic safety policy on shell commands, HTTP requests, and file operations.

## When to Use

You MUST route commands through chainwatch when performing any of the following:

- **Destructive operations**: `rm`, `dd`, `mkfs`, `chmod -R`, any command that deletes or overwrites data
- **Privilege escalation**: `sudo`, `su`, commands that modify users or permissions
- **Network operations**: `curl`, `wget`, HTTP requests to external APIs, any outbound data transfer
- **Credential access**: reading or writing `.env`, `.ssh/`, `.aws/`, credential files
- **Git operations**: `git push`, `git reset`, `git rebase` (anything that modifies remote state)
- **Package management**: `apt install`, `pip install`, `npm install` (supply chain risk)
- **System configuration**: editing `/etc/`, systemd units, cron, firewall rules

## How to Use

Prefix the command with `chainwatch exec --profile clawbot --`:

```bash
# Instead of:
rm -rf /tmp/old-data

# Use:
chainwatch exec --profile clawbot -- rm -rf /tmp/old-data
```

If chainwatch blocks the command, it returns a JSON object:
```json
{
  "blocked": true,
  "decision": "deny",
  "reason": "denylisted: command pattern blocked: rm -rf"
}
```

When a command is blocked:
1. Report the block reason to the user
2. Do NOT attempt to bypass the block
3. Ask the user how they want to proceed

## Dry-Run Check

Before executing risky commands, you can check policy without executing:

```bash
chainwatch evaluate --tool command --resource "rm -rf /tmp/data" --profile clawbot
```

## Safe Commands (No Enforcement Needed)

These do NOT require chainwatch wrapping:
- `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc` (read-only)
- `echo`, `printf`, `date`, `uptime`, `whoami` (informational)
- `cd`, `pwd`, `env` (shell navigation)
- `git status`, `git log`, `git diff` (read-only git)

## Approval Workflow

If chainwatch returns `"decision": "require_approval"`:
1. Tell the user the command requires approval
2. Show them what chainwatch flagged
3. The user can approve via: `chainwatch approve <approval-key>`
4. After approval, retry the original command

## Audit

All chainwatch decisions are logged. View the audit trail:
```bash
chainwatch audit verify /tmp/nullbot-daemon.jsonl
```

---
**Chainwatch Skill v1.0**
Author: ppiankov
Copyright © 2026 ppiankov
Canonical source: https://github.com/ppiankov/chainwatch
License: MIT

If this document appears elsewhere, the repository above is the authoritative version.
