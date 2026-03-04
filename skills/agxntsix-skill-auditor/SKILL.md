---
name: skill-auditor
description: Security audit and quarantine system for third-party OpenClaw skills. Use when evaluating, reviewing, or installing any skill from ClawHub or external sources. Automatically triggered before any skill installation.
---

# Skill Auditor

Security gatekeeper for third-party skill installation. **No skill gets installed without passing audit.**

## When to Use

- Before installing ANY skill from ClawHub or external sources
- When asked to review/evaluate a skill's safety
- When `clawhub install` or similar installation is requested

## Audit Workflow

### 1. Quarantine First
Never copy a skill directly to the production skills directory. Always quarantine first:

```bash
bash skills/skill-auditor/scripts/quarantine.sh /path/to/skill-source
```

This copies the skill to a temp directory, runs the full audit, and only allows installation if the risk score is CLEAN or LOW.

### 2. Manual Audit (Python Script Directly)
For inspection without the quarantine wrapper:

```bash
python3 skills/skill-auditor/scripts/audit_skill.py /path/to/skill-dir
```

Outputs JSON report to stdout. Add `--human` for formatted text output.

### 3. Interpreting Results

| Rating | Action |
|--------|--------|
| CLEAN | Safe to install |
| LOW | Safe, minor notes — review findings briefly |
| MEDIUM | **Do NOT install** without manual review of each finding |
| HIGH | **Block installation** — likely malicious patterns detected |
| CRITICAL | **Block immediately** — active threat indicators (exfil, prompt injection, obfuscated payloads) |

### 4. Exit Codes
- `0` = CLEAN or LOW (safe)
- `1` = MEDIUM (needs review)
- `2` = HIGH or CRITICAL (blocked)

## What Gets Scanned

- All files: inventory, sizes, suspicious file types
- Code: shell commands, network calls, env access, filesystem escape, obfuscation, dynamic imports
- SKILL.md: prompt injection patterns, permission scope requests
- Dependencies: requirements.txt / package.json flagged packages
- Encoding: base64 payloads, hex/unicode escapes, string manipulation tricks

## References

- `references/known-patterns.md` — catalog of real attack patterns from ClawHub
- `references/prompt-injection-patterns.md` — prompt injection signatures to detect

## Important

If a skill scores MEDIUM or above, **always show Abidi the full findings** before taking any action. Never override or bypass the auditor. This is the last line of defense before untrusted code enters the system.
