---
name: skillguard
version: 1.0.0
description: AI-powered security scanner for OpenClaw skills. Scans skill files for credential theft, data exfiltration, reverse shells, obfuscation, and other threats before installation.
metadata:
  {
    "openclaw": {
      "emoji": "🛡️",
      "requires": { "bins": ["python3"] }
    }
  }
---

# SkillGuard 🛡️

AI-powered security scanner for OpenClaw skills. Analyzes skill code for malicious behaviour before you install it.

## Commands

### Scan before install (recommended)

```bash
skillguard install <skill-name>
```

Downloads the skill to a temp directory, runs AI security analysis, shows verdict, then asks for confirmation before installing via clawhub.

**Example:**
```
skillguard install my-new-skill
```

### Audit installed skills

```bash
skillguard audit
```

Scans all skills in `/usr/lib/node_modules/openclaw/skills/`, `~/.openclaw/workspace/skills/`, and `~/.openclaw/skills/`. Prints a table summary with details on any flagged skills.

### Scan a local path

```bash
skillguard scan <path>
```

Scan any local skill directory without installing. Useful for reviewing skills you've already downloaded or developed locally.

**Example:**
```
skillguard scan ./my-skill-folder
skillguard scan /usr/lib/node_modules/openclaw/skills/some-skill
```

## Risk Levels

| Level  | Meaning |
|--------|---------|
| ✅ CLEAN  | No security issues detected |
| 🟡 LOW    | Minor concerns, generally safe |
| ⚠️ MEDIUM | Review recommended before installing |
| 🚨 HIGH   | Dangerous — do not install without careful manual review |

## What Gets Checked

- **Credential theft**: Reads to `~/.ssh/`, `~/.openclaw/`, API keys, `.env` files
- **Data exfiltration**: curl/wget/fetch POSTing data to external servers
- **Reverse shells**: netcat, bash TCP redirects, socat to external IPs
- **Privilege escalation**: sudo abuse, setuid bits, writing to `/etc/`
- **Persistence**: cron installs, systemd units, `.bashrc` modifications
- **Obfuscation**: base64-piped-to-bash, eval with dynamic content
- **Package smuggling**: undisclosed npm/pip installs
- **Reconnaissance**: network scanning, system info harvesting

## Usage by the AI Agent

When the user asks to install a skill, use skillguard first:

```bash
python3 /root/.openclaw/workspace/skills/skillguard/skillguard.py install <skill-name>
```

When the user asks to check their installed skills for security issues:

```bash
python3 /root/.openclaw/workspace/skills/skillguard/skillguard.py audit
```

When the user asks to check a specific local skill directory:

```bash
python3 /root/.openclaw/workspace/skills/skillguard/skillguard.py scan /path/to/skill
```

## Output Examples

**Clean skill:**
```
✅ SkillGuard: good-skill — Clean. Installing...
```

**Flagged skill:**
```
🚨 SkillGuard: bad-skill — Risk: HIGH
   Reads /root/.openclaw/*.json and POSTs to external IP.

   [HIGH] Data Exfiltration: curl POST of ~/.openclaw/openclaw.json to 45.33.32.156 [scripts/init.sh:14-22]
   [MEDIUM] Credential Theft: Reads ~/.ssh/id_rsa without disclosure [scripts/setup.sh:8]

Install bad-skill anyway? (type YES to confirm)
```

## Requirements

- Python 3.6+
- An Anthropic, OpenRouter, or DeepSeek API key configured in OpenClaw
- `clawhub` CLI (for `install` command only)

## Notes

- Binary files are automatically skipped
- Files larger than 100KB are truncated before analysis
- Analysis uses Claude Opus (or best available model) for maximum accuracy
- The scan itself is safe — skills are text files, not executed during scanning
