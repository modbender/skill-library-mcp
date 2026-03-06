---
name: clawguard
description: Security scanner for OpenClaw/Clawdbot skills - detect malicious patterns before installation
author: devinfloyd1
version: 0.1.0
metadata: {"clawdbot":{"emoji":"🛡️","os":["darwin","linux","win32"]}}
---

# ClawGuard

**Security Scanner for OpenClaw/Clawdbot Skills**

Protect yourself from malicious skill installations. ClawGuard scans skills for dangerous patterns before you install them - including patterns from the **ClawHavoc campaign** (341 malicious skills discovered by Koi Security).

## Quick Start

```bash
# Scan a skill by name
python scan.py --skill <skill-name>

# Scan a skill by path  
python scan.py --path /path/to/skill

# Scan all installed skills
python scan.py --all
```

## What It Detects

| Category | Examples | Severity |
|----------|----------|----------|
| 🔴 **Reverse Shells** | socket.connect(), pty.spawn(), /dev/tcp | Critical |
| 🔴 **Data Exfiltration** | requests.post() to suspicious TLDs | Critical |
| 🔴 **Credential Harvest** | Reading ~/.ssh/id_rsa, AWS credentials | Critical |
| 🔴 **Obfuscation** | base64.b64decode(exec), chr() chains | Critical |
| 🔴 **ClawHavoc IOCs** | glot.io scripts, fake Apple URLs, known C2 IPs | Critical |
| 🟠 **Code Execution** | exec(), eval(), subprocess | High |
| 🟡 **Suspicious Network** | URL shorteners, weird ports | Medium |

## Output Formats

```bash
# Console (default) - colored terminal output
python scan.py --skill github

# JSON - machine-readable for CI/CD
python scan.py --skill github --format json

# Markdown - for sharing reports
python scan.py --skill github --format markdown
```

## Risk Scoring

| Score | Level | Action |
|-------|-------|--------|
| 0-10 | 🟢 Safe | Install freely |
| 11-25 | 🟢 Low | Quick review |
| 26-50 | 🟡 Medium | Review findings |
| 51-75 | 🔴 High | Review carefully |
| 76-100 | 🔴 Critical | **Do not install** |

## IOC Database

70+ indicators of compromise including:
- Remote access (reverse shells, C2)
- Data exfiltration
- Credential harvesting  
- Code obfuscation
- **Real ClawHavoc campaign IOCs** (from Koi Security research)
- Known malicious IPs, hashes, and skill names

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

## Credits

IOCs enriched with research from [Koi Security](https://www.koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting) - ClawHavoc campaign analysis by Oren Yomtov and Alex.

## Links

- [GitHub Repository](https://github.com/devinfloyd1/clawguard)
- [ClawHavoc Research](https://www.koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting)

---

**Built for the Clawdbot community** 🐾
