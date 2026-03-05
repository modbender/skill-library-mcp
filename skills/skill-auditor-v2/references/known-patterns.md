# Known Malicious Patterns & IoC Database

## C2 Server IPs
| IP | Campaign | First Seen |
|----|----------|------------|
| 91.92.242.30 | ClawHavoc | 2026-02 |

## Malicious Domains
| Domain | Usage | Risk |
|--------|-------|------|
| glot.io | Hosts obfuscated scripts | HIGH |
| webhook.site | Data exfiltration endpoint | HIGH |
| pastebin.com | Payload hosting | HIGH |
| hastebin.com | Payload hosting | HIGH |
| ghostbin.com | Payload hosting | HIGH |
| ngrok.io | Tunnel (exfil endpoint) | HIGH |
| pipedream.net | Exfiltration endpoint | HIGH |
| requestbin.com | Exfiltration endpoint | HIGH |
| burpcollaborator.net | Pentest exfil | MEDIUM |

## Social Engineering Lures
- `OpenClawDriver` — Non-existent driver, tricks users into installing malware
- `ClawdBot Driver` — Social engineering lure
- `Required Driver` / `install driver` / `download driver` — Fake prerequisite

## Attack Campaigns

### ClawHavoc (Feb 2026)
- **341 malicious ClawHub skills** discovered
- Pattern: Fake prerequisites requesting binary downloads (`.exe`, `.dmg`, `.zip`)
- C2: 91.92.242.30
- MITRE: T1204.002 (User Execution: Malicious File), T1071 (Application Layer Protocol)
- References:
  - https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html
  - https://www.scworld.com/brief/reports-shed-light-on-more-openclaw-vulnerabilities

## Detection Categories

### Critical Patterns
1. **Fake Prerequisites** — `(prerequisite|setup).*download.*(openclaw-agent|openclaw-setup)\.(zip|exe|dmg)`
2. **C2 IP Contact** — Known malicious IPs in code
3. **Curl Pipe Shell** — `curl|wget ... | bash/sh` remote code execution
4. **Hardcoded Credentials** — API keys, tokens embedded in code
5. **Base64 Encoded Execution** — `eval/exec` on base64 decoded content
6. **Prompt Injection** — Instructions to override agent behavior in SKILL.md
7. **Zero-Width Characters** — Hidden text injection via Unicode zero-width chars
8. **Data Exfiltration** — Webhook URLs (Discord, Slack, Telegram bots)

### MITRE ATT&CK Mapping
| Pattern | MITRE ID | Tactic |
|---------|----------|--------|
| Remote script exec | T1059.004 | Execution |
| Obfuscated payloads | T1027 | Defense Evasion |
| Credential theft | T1552.001 | Credential Access |
| Data exfiltration | T1041 | Exfiltration |
| Supply chain | T1195.001 | Initial Access |
| Prompt injection | T1059.006 | Execution |
| Fake prerequisites | T1204.002 | Execution |
| Browser cred theft | T1555.003 | Credential Access |
| Crypto wallet theft | T1005 | Collection |
| Social engineering | T1566 | Initial Access |

## Whitelist (Score Reduction)

### Safe Binaries
git, gh, docker, kubectl, npm, node, python, pip, cargo, go, curl, wget, jq

### Safe Domains
github.com, npmjs.org, pypi.org, crates.io, anthropic.com, openclaw.ai, clawhub.ai

### Verified Authors
openclaw, anthropic-official
