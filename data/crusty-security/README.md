# Crusty Security 🛡️

**On-host security monitoring for OpenClaw AI agents.** Scans files and skills for malware. Monitors agent behavior for compromise indicators. Audits host security posture.

[![ClawHub](https://img.shields.io/badge/ClawHub-crusty-emerald)](https://clawhub.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)

---

## Why Your Agent Needs This

AI agents download files, install skills, and execute code — all with your system privileges. A single prompt injection can lead to:

- 🦠 **Malware execution** via downloaded files or malicious skill scripts
- 🔗 **Data exfiltration** through hidden webhook calls or reverse shells
- 🧬 **Supply chain attacks** from compromised ClawHub skills
- 🔑 **Credential theft** from exposed `.env` files and API keys
- 🧠 **Agent hijacking** via modified SOUL.md, AGENTS.md, or MEMORY.md

Crusty Security is the first security skill built specifically for the OpenClaw agent threat model.

## Features

| Feature | Description |
|---------|-------------|
| **File Scanning** | ClamAV local scan with up-to-date signatures |
| **Skill Auditing** | Static analysis for reverse shells, crypto miners, data exfiltration, obfuscation |
| **Host Audit** | Cron jobs, open ports, SSH keys, file permissions, posture scoring (0-100) |
| **Agent Monitoring** | Detects modified config files, suspicious processes, unexpected outbound connections |
| **ClawHub Sync** | Tracks installed skill versions against ClawHub catalog, blocklist checking |
| **Quarantine** | Isolate threats with manifest tracking, never auto-deletes |
| **Reports** | Markdown security posture reports with recommendations |

## Quick Start

### 1. Install

```bash
clawhub install crusty-security
```

That's it. ClamAV is auto-installed on first scan if it's not already present. No separate setup step needed.

### 2. Start Scanning

```bash
# Scan a file
bash scripts/scan_file.sh /path/to/suspicious-file.pdf

# Scan your entire workspace
bash scripts/scan_file.sh -r /data/workspace

# Audit a skill before installing
bash scripts/audit_skill.sh /path/to/skill/

# Full host security audit
bash scripts/host_audit.sh
```

That's it. Crusty Security works immediately with ClamAV — no API keys required.

## How It Works: Skill + Dashboard

Crusty Security has two parts that work together — but the skill works great on its own too.

```
┌─────────────────────────────┐         ┌──────────────────────────────┐
│   YOUR OPENCLAW AGENT       │         │   CRUSTY SECURITY DASHBOARD  │
│   (your machine / VPS)      │         │   (crustysecurity.com)       │
│                             │  HTTPS  │                              │
│  Crusty Security Skill      │ ──────► │  Web Dashboard               │
│  ✓ Scans files locally      │  POST   │  ✓ View all scan results     │
│  ✓ Audits skills            │         │  ✓ Manage alerts & threats   │
│  ✓ Monitors agent behavior  │         │  ✓ Track agent health        │
│  ✓ Checks host security     │         │  ✓ Multi-agent fleet view    │
│                             │         │  ✓ Email/Slack notifications │
└─────────────────────────────┘         └──────────────────────────────┘
        runs on YOUR machine               runs at crustysecurity.com
```

**Key concepts:**
- The **skill** does all the actual security work — scanning, auditing, monitoring. It runs on your OpenClaw agent's machine.
- The **dashboard** is a web app where you view results, manage alerts, and monitor multiple agents from one place.
- Data flows **one way only**: skill → dashboard. The dashboard never connects *to* your agent. Works behind firewalls, NATs, VPNs — no port forwarding needed.
- The skill is **fully functional without the dashboard**. The dashboard is optional for users who want centralized visibility.

### Connecting Your Agent to the Dashboard (3 steps, 2 minutes)

**Step 1:** Sign up at [crustysecurity.com](https://crustysecurity.com), go to **Agents → + Add Agent**. Your API key is generated automatically — copy it.

**Step 2:** The Agents page shows a full copy-pasteable instruction block. Paste it to your OpenClaw agent, or manually set:
```bash
export CRUSTY_API_KEY="cg_live_xxxxxxxxxxxxxxxxxxxx"
export CRUSTY_DASHBOARD_URL="https://crustysecurity.com"
```

**Step 3:** Restart your OpenClaw agent. It appears in the dashboard within 5 minutes.

### What works without the dashboard

| Feature | Without Dashboard | With Dashboard |
|---------|:-:|:-:|
| File scanning (ClamAV) | ✅ | ✅ + history |
| Skill auditing | ✅ | ✅ + tracking |
| Host security audit | ✅ | ✅ + trends |
| Agent monitoring | ✅ | ✅ + alerts |
| Quarantine | ✅ | ✅ + remote view |
| Email/Slack alerts | ❌ | ✅ |
| Multi-agent fleet view | ❌ | ✅ |
| Scan scheduling from web | ❌ | ✅ |
| Security posture score | Local only | ✅ aggregated |

### For OpenClaw agents (reading this as SKILL.md)

If you're an OpenClaw agent and your human has configured `CRUSTY_API_KEY`, you should:
1. Include `--push` when running scans to send results to the dashboard
2. The heartbeat runs automatically every 5 minutes when the key is set
3. Use `python3 scripts/clawhub_sync.py --push` to sync skill inventory to dashboard

**⚠️ Cron job rule:** ALL cron jobs that execute commands (scans, heartbeats, syncs) MUST use `sessionTarget: "isolated"` with `payload.kind: "agentTurn"`. Never use `systemEvent` for jobs that need execution — it only injects text into the main session and can silently fail. See SKILL.md for the correct cron configuration.

## All Commands

| Command | Description |
|---------|-------------|
| `bash scripts/install_clamav.sh` | Install and configure ClamAV |
| `bash scripts/scan_file.sh <path>` | Scan a file with ClamAV |
| `bash scripts/scan_file.sh -r <dir>` | Recursive directory scan |
| `bash scripts/scan_file.sh --incremental -r <dir>` | Skip unchanged files |
| `bash scripts/scan_file.sh --quarantine <path>` | Quarantine a file |
| `bash scripts/audit_skill.sh <dir>` | Audit a skill for threats |
| `bash scripts/host_audit.sh` | Host security audit |
| `bash scripts/host_audit.sh --deep` | Deep host audit (includes file modifications) |
| `bash scripts/monitor_agent.sh` | Agent behavior integrity check |
| `bash scripts/generate_report.sh` | Generate security posture report |
| `python3 scripts/clawhub_sync.py` | Sync installed skills against ClawHub catalog |

All commands output JSON. All support `--help`.

## Scanning Stack

```
                    ┌──────────────────┐
   File arrives →   │  ClamAV (local)  │  ← Free, instant, signature-based detection
                    └──────────────────┘
```

ClamAV handles zip, rar, 7z, tar, gz archives natively. Encrypted archives are flagged as "unscanned."

## Skill Auditing — What It Catches

Static analysis specifically tuned for the OpenClaw threat model:

| Severity | Pattern |
|----------|---------|
| 🔴 Critical | `curl \| sh`, reverse shell patterns, crypto mining indicators |
| 🟠 High | `eval`/`exec` with dynamic input, base64 decode chains, webhook.site/ngrok exfil, credential harvesting, binaries in skill dirs |
| 🟡 Medium | Hidden files, system file access, hardcoded IPs, obfuscated code, persistence mechanisms (cron, systemd) |
| 🔵 Info | Large skill size, credential references in docs |

## Host Audit Scoring

The host audit produces a posture score from 0-100:

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100 | 🟢 Excellent | Minimal risk |
| 70-89 | 🟡 Good | Minor issues to address |
| 50-69 | 🟠 Fair | Several findings, take action |
| 0-49 | 🔴 Poor | Significant security issues |

Deductions: Critical (-25), High (-15), Medium (-10), Low (-5).

## Agent Behavior Monitoring

Detects indicators of agent compromise:

- Modified `AGENTS.md`, `SOUL.md`, `MEMORY.md`, `TOOLS.md` (config tampering)
- Unexpected cron jobs or scheduled tasks
- Suspicious outbound connections (IRC, Tor, backdoor ports)
- Files created outside workspace (`/tmp` executables, home directory changes)
- Suspicious processes (crypto miners, netcat listeners, tunneling tools)
- Exposed credentials (world-readable `.env` files, SSH keys)

## ClawHub Supply Chain Monitoring

The `clawhub_sync.py` script protects against malicious or compromised skills:

- Fetches the full ClawHub catalog (400+ skills)
- Compares installed skill versions against latest
- Checks against a blocklist of known-bad skills
- Flags skills not found on ClawHub (potential forks or custom builds)
- Detects version drift across multiple agents
- Pushes results to the dashboard (if configured)

```bash
# One-time sync
python3 scripts/clawhub_sync.py

# JSON output (for automation)
python3 scripts/clawhub_sync.py --json

# With dashboard push
python3 scripts/clawhub_sync.py --push
```

## Automatic Scan Schedule

Crusty Security **automatically configures recurring scans** when your OpenClaw agent first uses the skill. No manual setup needed. All cron jobs use **isolated sessions** with `agentTurn` to guarantee reliable execution (never `systemEvent`, which can silently fail). The agent sets up:

| Frequency | What runs | Requires Dashboard? |
|-----------|-----------|:---:|
| **Every 5 min** | Dashboard heartbeat (agent status) | ✅ |
| **Daily 3am** | Incremental workspace scan + agent integrity check | ❌ |
| **Weekly Sunday 3am** | Full workspace scan + host audit + all skills audit + security report | ❌ |
| **Every 12 hours** | ClawHub skill inventory sync | ✅ |
| **Monthly 1st** | Deep host security audit | ❌ |

You can adjust schedules by asking your agent to modify the cron jobs.

## Requirements

- **OS:** Linux (tested on Debian/Ubuntu, works in Docker)
- **Python:** 3.8+
- **ClamAV:** Installed via `install_clamav.sh` or manually
- **Disk:** ~300MB for ClamAV signatures

### Raspberry Pi / Low Memory

- `<2GB RAM`: Runs in on-demand mode (no ClamAV daemon)
- `<1GB RAM`: Use skill auditing + agent monitoring (lightweight shell/Python scripts)

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `CRUSTY_API_KEY` | — | No | Dashboard API key (from crustysecurity.com) |
| `CRUSTY_DASHBOARD_URL` | — | No | Dashboard URL |
| `CRUSTY_QUARANTINE` | `/tmp/crusty_quarantine` | No | Quarantine directory |
| `CRUSTY_LOG_DIR` | `/tmp/crusty_logs` | No | Scan log directory |
| `CRUSTY_MAX_FILE_SIZE` | `200M` | No | Max file size for scanning |
| `CRUSTY_WORKSPACE` | `/data/workspace` | No | Agent workspace path |

## File Structure

```
crusty-security/
├── SKILL.md              # Agent instructions (OpenClaw reads this)
├── README.md             # Human documentation (you're reading it)
├── LICENSE.txt           # MIT License
├── CHANGELOG.md          # Version history
├── scripts/
│   ├── install_clamav.sh     # ClamAV installer
│   ├── scan_file.sh          # File/directory scanner
│   ├── audit_skill.sh        # Skill static analysis
│   ├── host_audit.sh         # Host security audit
│   ├── monitor_agent.sh      # Agent behavior monitoring
│   ├── generate_report.sh    # Security report generator
│   ├── clawhub_sync.py       # ClawHub catalog sync
│   └── dashboard.sh          # Dashboard integration library
└── references/
    ├── setup.md              # Detailed setup guide
    ├── threat-patterns.md    # Threat pattern database
    └── remediation.md        # Incident response procedures
```

## Offline Mode

Crusty Security works fully offline with reduced capability:

| Feature | Offline | Online |
|---------|---------|--------|
| ClamAV file scanning | ✅ (local signatures) | ✅ (fresh signatures) |
| Skill auditing | ✅ (static analysis) | ✅ |
| Host auditing | ✅ | ✅ |
| Agent monitoring | ✅ | ✅ |
| ClawHub sync | ❌ | ✅ |

## Contributing

Issues and PRs welcome at [github.com/silentcool/crusty-security](https://github.com/silentcool/crusty-security).

## License

MIT — see [LICENSE.txt](LICENSE.txt).

## Links

- 🌐 **Dashboard:** [crustysecurity.com](https://crustysecurity.com)
- 📦 **ClawHub:** [clawhub.com](https://clawhub.com) (search "crusty-security")
- 🐙 **GitHub:** [github.com/silentcool/crusty-security](https://github.com/silentcool/crusty-security)
- 🦀 **Built by:** [Black Matter VC](https://blackmatter.vc)
