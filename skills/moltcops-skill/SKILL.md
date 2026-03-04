---
name: moltcops
version: 1.0.0
description: Pre-install security scanner for AI agent skills. Detects malicious patterns before you trust code. Local-first — code never leaves your machine.
---

# MoltCops — Skill Security Scanner

Scan any skill for security threats **before** you install it. Detects prompt injection, data exfiltration, sleeper triggers, drain patterns, and 16 more threat categories.

**Local-first.** Your code never leaves your machine. No API calls. No uploads. No accounts.

## When to Use

- **Before installing any skill** from ClawHub, GitHub, or other sources
- **Before running** skills shared by other agents
- **When evaluating** unknown code from any source
- **After ClawHavoc**: 341 malicious skills were found on ClawHub this week. Scan first.

## How to Run

```bash
python3 scripts/scan.py <path-to-skill-folder>
```

Example:
```bash
# Scan a skill before installing
python3 scripts/scan.py ~/.openclaw/skills/suspicious-skill

# Scan a freshly downloaded skill
python3 scripts/scan.py ./my-new-skill
```

**No dependencies required** — uses only Python 3 standard library.

## Reading Results

The scanner returns three verdicts:

| Verdict | Exit Code | Meaning |
|---------|-----------|---------|
| **PASS** | 0 | No critical or high-risk threats detected. Safe to install. |
| **WARN** | 1 | High-risk patterns found. Review findings before installing. |
| **BLOCK** | 2 | Critical threats detected. Do NOT install this skill. |

## What It Detects

20 detection rules across these threat categories:

| Category | Rules | Examples |
|----------|-------|---------|
| **Prompt Injection** | MC-001, MC-002, MC-003 | System prompt override, jailbreak payloads, tool-use steering |
| **Code Injection** | MC-004, MC-005, MC-006, MC-019 | Shell injection, eval/exec, base64-to-exec, child_process |
| **Data Exfiltration** | MC-007, MC-008, MC-009, MC-010, MC-020 | Webhook URLs, env var harvesting, SSH key access, credential files |
| **Hardcoded Secrets** | MC-011, MC-012 | API keys in source, private key material |
| **Financial** | MC-013 | Drain patterns, unlimited withdrawals |
| **Lateral Movement** | MC-014 | Git credential access, repo manipulation |
| **Persistence** | MC-015, MC-016 | SOUL.md writes, cron job creation |
| **Autonomy Abuse** | MC-017 | Destructive force flags (rm -rf, git push --force) |
| **Infrastructure** | MC-018 | Permission escalation (sudo, chmod 777) |

## False Positive Handling

The scanner includes context-aware filtering to reduce false positives:

- **Env var access** (MC-008): Only flags when variable names contain KEY, SECRET, PASSWORD, TOKEN, or CREDENTIAL
- **Git operations** (MC-014): Skips standard remotes (github.com, gitlab.com, bitbucket.org)
- **Force flags** (MC-017): Only flags on destructive operations, not install scripts

## Example Output

```
MoltCops Security Scanner
========================================
Scanning: ./suspicious-skill
Files: 5
Rules: 20

FINDINGS
----------------------------------------
[CRITICAL] MC-007: Exfiltration URL (main.py:14)
[CRITICAL] MC-004: Shell Injection (helper.sh:8)
[HIGH] MC-005: Dynamic Code Execution (main.py:22)

SUMMARY
========================================
Files scanned: 5
Total findings: 3
  Critical: 2
  High:     1
  Medium:   0

VERDICT: BLOCK
Critical threats detected. Do NOT install this skill.
```

## Web Scanner

For a browser-based version with the same engine, visit: **https://scan.moltcops.com**

## About MoltCops

MoltCops protects the AI agent ecosystem from malicious skills. While VirusTotal catches known malware signatures, MoltCops catches **behavioral patterns** — drain logic, sleeper triggers, prompt injection, and data exfiltration that signature-based scanning misses.

- Web: https://moltcops.com
- Moltbook: https://moltbook.com/u/MoltCops
