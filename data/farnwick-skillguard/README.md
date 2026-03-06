# SkillGuard 🛡️

AI-powered security scanner for OpenClaw skills.

SkillGuard uses LLM analysis to detect malicious code in OpenClaw skills before you install them — catching credential theft, data exfiltration, reverse shells, and other threats.

## Quick Start

```bash
# Scan + install a skill from clawhub (safest way to install)
python3 skillguard.py install some-skill-name

# Audit all installed skills
python3 skillguard.py audit

# Scan a local skill directory
python3 skillguard.py scan /path/to/skill
```

## How It Works

1. **Collect** — Reads SKILL.md + all scripts (.sh, .py, .js, etc.) up to 100KB each
2. **Analyze** — Sends file contents to Claude Opus (or configured LLM) with a focused security prompt
3. **Report** — Displays risk level (CLEAN / LOW / MEDIUM / HIGH) + specific findings
4. **Confirm** — For `install`, asks for confirmation before proceeding

## Example Output

```
🚨 SkillGuard: suspicious-skill — Risk: HIGH
   Reads /root/.openclaw/openclaw.json and sends to external IP.

   [HIGH] Data Exfiltration: curl POST of ~/.openclaw/*.json to 45.33.32.156 [init.sh:14-22]
   [MEDIUM] Credential Theft: Reads ~/.ssh/id_rsa without disclosure [setup.sh:8]

   ⚠ HIGH RISK: This skill is dangerous to install.
Install suspicious-skill anyway? (type YES to confirm)
```

```
✅ SkillGuard: helpful-skill — Clean. Installing...
```

## Audit Table

```
SkillGuard Audit — scanning 12 skills

  Scanning clawhub... ✅ CLEAN
  Scanning coding-agent... ✅ CLEAN
  Scanning discord... ✅ CLEAN
  ...

────────────────────────────────────────────────────────────
SKILL                          RISK         SUMMARY
────────────────────────────────────────────────────────────
clawhub                        CLEAN        No security issues detected
coding-agent                   CLEAN        No security issues detected
```

## What Gets Scanned

| Category | What it detects |
|----------|----------------|
| Credential Theft | `~/.ssh/`, `~/.openclaw/`, API keys, `.env` |
| Data Exfiltration | curl/wget/fetch with POST bodies to external servers |
| Reverse Shells | netcat, bash TCP redirects, socat |
| Privilege Escalation | sudo abuse, setuid, writing to `/etc/` |
| Persistence | cron installs, systemd units, `.bashrc` mods |
| Obfuscation | base64-piped-to-bash, eval with dynamic content |
| Package Smuggling | undisclosed npm/pip installs |
| Reconnaissance | network scanning, system info collection |

## Configuration

SkillGuard reads API credentials from `~/.openclaw/agents/main/agent/auth-profiles.json`.

Priority order:
1. Anthropic API key (direct) → uses Claude Opus
2. Anthropic token → uses Claude Opus
3. OpenRouter → uses Claude Opus via OpenRouter
4. DeepSeek → uses DeepSeek Chat

## Files

```
skillguard/
├── SKILL.md                    — OpenClaw skill manifest
├── README.md                   — This file
├── skillguard.py               — Main CLI script
└── prompts/
    └── security-analysis.txt   — LLM system prompt for security analysis
```

## Requirements

- Python 3.6+ (no external dependencies — uses stdlib only)
- OpenClaw with a configured LLM provider
- `clawhub` CLI for the `install` command
