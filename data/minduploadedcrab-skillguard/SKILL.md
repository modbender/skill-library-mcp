---
name: minduploadedcrab-skillguard
description: "Security scanner for OpenClaw skills. Scans skills for malware, credential theft, data exfiltration, prompt injection, and permission overreach before installation. Run: python3 scripts/skillguard.py scan <skill-directory>"
version: 1.0.1
metadata:
  openclaw:
    emoji: "🛡️"
    requires:
      bins:
        - python3
    skillKey: skillguard
---

# SkillGuard — Security Scanner for OpenClaw Skills

Scans OpenClaw skills for security threats before installation. Catches agent-specific attacks that generic antivirus misses.

## Usage

```bash
# Scan a skill directory
python3 scripts/skillguard.py scan ~/.openclaw/workspace/skills/<skill-name>

# Scan with JSON output
python3 scripts/skillguard.py scan ~/.openclaw/workspace/skills/<skill-name> --json

# Scan all installed skills
python3 scripts/skillguard.py scan-all

# Quick summary of all skills
python3 scripts/skillguard.py audit
```

## What It Detects

1. **Credential Access** — reads of config files, env vars, wallet files, API keys
2. **Network Exfiltration** — outbound HTTP calls, encoded payloads, suspicious domains
3. **File System Abuse** — path traversal, writes outside skill directory, hidden files
4. **Prompt Injection** — SKILL.md content that manipulates agent behavior
5. **Dependency Risks** — suspicious npm post-install scripts, known bad packages
6. **Obfuscation** — extremely long lines, hex/unicode escape sequences
7. **Symlink Attacks** — symlinks escaping the skill directory to access sensitive files
8. **Config File Secrets** — hardcoded credentials in .json, .env, .yaml files

## Output

Each scan produces:
- **Risk Score**: 0-100 (0 = clean, 100 = critical threat)
- **Verdict**: PASS / WARN / FAIL
- **Findings**: Detailed list of issues with severity and evidence
