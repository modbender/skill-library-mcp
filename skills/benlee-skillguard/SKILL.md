---
name: skill-guard
version: 2.0.0
description: Security scanner that audits OpenClaw skills for malicious code, prompt injection, supply chain attacks, data exfiltration, and more
author: benjaminarp
tags: [security, scanner, audit, safety]
---

# Skill Guard v2 🛡️

Advanced security scanner for OpenClaw skills. Detects malicious code, prompt injection, supply chain attacks, data exfiltration, credential theft, and more — with smart domain analysis, tamper detection, and actionable recommendations.

## Commands

### `scan [dir]`
Audit ALL installed skills in ~/clawd/skills/ (or a custom directory).

```bash
python3 ~/clawd/skills/skill-guard/scripts/skillguard.py scan
python3 ~/clawd/skills/skill-guard/scripts/skillguard.py scan --json
python3 ~/clawd/skills/skill-guard/scripts/skillguard.py scan --report report.md
python3 ~/clawd/skills/skill-guard/scripts/skillguard.py scan --baseline  # force re-baseline
```

### `check <path>`
Scan a single skill directory, or a directory containing multiple skills.

```bash
python3 ~/clawd/skills/skill-guard/scripts/skillguard.py check ~/clawd/skills/some-skill
python3 ~/clawd/skills/skill-guard/scripts/skillguard.py check ~/clawd/skills/skill-guard/tests/
```

### `watch [dir]`
One-liner summary suitable for cron alerting.

```bash
python3 ~/clawd/skills/skill-guard/scripts/skillguard.py watch
```

Output formats:
- `SkillGuard: 24 scanned, 20 clean, 4 suspicious, 0 malicious`
- `⚠️ SkillGuard ALERT: <skill> files changed since baseline!`
- `🔴 SkillGuard ALERT: <skill> scored MALICIOUS!`

### `check-remote <slug>` (Future)
Will download a skill from ClawHub, scan it in a temp directory, and clean up. Requires ClawHub auth (not yet available). The temp-dir scanning infrastructure is ready.

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output machine-readable JSON |
| `--report <path>` | Write a markdown report file |
| `--baseline` | Force re-baseline of all file hashes |

## What It Detects

### Code Analysis
- eval/exec calls, shell injection, outbound HTTP requests
- Base64-encoded payloads (auto-decodes and inspects content)
- Hex-encoded suspicious strings
- Minified/obfuscated JavaScript
- Time-bomb patterns (date-conditional malicious code)

### Smart Domain Analysis
- Maintains allowlist of 80+ known legitimate API domains
- HTTP requests to known APIs = 0 risk points
- HTTP requests to unknown domains = 10 risk points (WARNING)
- Context-aware: "crypto-price" calling coingecko.com = expected, lower score

### Sensitive File Access
- SSH keys, AWS credentials, GPG keyrings
- Browser credential stores (Chrome, Firefox, Safari)
- Crypto wallets (MetaMask, Phantom, Solana, Ethereum)
- Keychain/keyring access
- Environment variable harvesting

### Prompt Injection
- Hidden HTML comments with override instructions
- Exfiltration instructions in documentation
- Social engineering phrases ("this is trusted", "pre-approved", etc.)
- Modification instructions targeting other skills/system files

### Supply Chain
- Typosquatting detection (Levenshtein distance on package names)
- Suspicious npm post-install scripts
- Known-malicious package detection

### Enhanced Detection (v2)
- **File permissions**: flags executable bit on .py, .js, .md files
- **Binary detection**: identifies ELF, Mach-O, PE binaries in skill dirs
- **Hardcoded secrets**: AWS keys (AKIA...), GitHub tokens (ghp_...), OpenAI keys (sk-...), Stripe keys, private key files
- **Write-outside-skill**: detects code writing to paths outside the skill directory
- **Unicode homoglyphs**: catches lookalike characters in filenames (Cyrillic а vs Latin a)
- **Excessive file count**: flags skills with 50+ files
- **Large files**: flags files over 500KB

### Network Threats
- Hardcoded IP addresses, reverse shells, DNS exfiltration
- WebSocket connections to external hosts

### Persistence
- Crontab modifications, launchd/systemd service creation
- Shell RC file modifications (.bashrc, .zshrc)

### Tamper Detection (v2)
- Computes SHA-256 hash of every file on first scan
- Stores baselines in baselines.json
- On re-scan, flags changed, added, or removed files
- Checks ClawHub origin version from .clawhub/origin.json

## Scoring (v2)

| Pattern | Points |
|---------|--------|
| HTTP to known API | 0 |
| HTTP to unknown domain | 10 |
| curl in documentation | 0 |
| subprocess call | 2 |
| subprocess + shell=True | 25 |
| Sensitive file access | 10-25 |
| Prompt injection phrase | 25 |
| Reverse shell | auto MALICIOUS |
| Sensitive access + outbound | auto MALICIOUS |
| Typosquatted package | 15 |
| JS in SVG | 25 |

### Risk Levels
- 🟢 **CLEAN**: Score 0-15
- 🟡 **SUSPICIOUS**: Score 16-40
- 🔴 **MALICIOUS**: Score 41+ or dangerous combo detected

### Recommendations Engine
Every finding includes a one-line recommendation explaining the risk and suggested action.

## Test Suite

The `tests/` directory contains 7 fake malicious skills for validation:

| Test Skill | Attack Vector |
|-----------|--------------|
| fake-weather | SSH key theft + POST to evil.com |
| fake-formatter | Base64-encoded reverse shell |
| fake-helper | Prompt injection + social engineering |
| fake-crypto | Wallet theft + C2 communication |
| fake-typosquat | Typosquatted package names |
| fake-timebomb | Date-activated SSH key exfiltration |
| fake-svgmalware | JavaScript embedded in SVG |

All 7 test skills score as 🔴 MALICIOUS.

## Requirements

Python 3 stdlib only. No external dependencies. Single file: `scripts/skillguard.py`.
