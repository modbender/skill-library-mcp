---
name: trustmyagent
description: 🛡️ TrustMyAgent - Security posture monitoring for AI agents. Runs 41 stateless checks across 14 domains and calculates a trust score (0-100). Supports local-only mode (no network calls) and dry-run mode (preview before sending).
version: 1.0
author: Anecdotes AI Labs
license: MIT
homepage: https://www.trustmyagent.ai
repository: https://github.com/Anecdotes-Yair/trust-my-agent-ai
metadata:
  openclaw:
    emoji: "🛡️"
    category: security
    tags:
      - security
      - compliance
      - monitoring
      - trust
    requires:
      bins:
        - openssl
    shared: true
    install:
      - id: python3
        kind: brew
        formula: python3
        os:
          - darwin
        bins:
          - python3
        label: "Python 3 (Homebrew)"
      - id: python3-apt
        kind: node
        os:
          - linux
        bins:
          - python3
        label: "Python 3 (system)"
---

# 🛡️ TrustMyAgent - Security Agent

**Stateless security posture monitoring for AI agents.**

TrustMyAgent runs 41 read-only security checks across 14 domains on the host machine, calculates a trust score (0-100), and optionally reports results to a public [Trust Center](https://www.trustmyagent.ai/trust-center.html) dashboard. It is fully stateless — no files are written, no state is persisted, and no background processes are installed without explicit user consent.

> **Open source**: All check logic is visible in `run.py` and `checks/*.json`. The full source code is at [github.com/Anecdotes-Yair/trust-my-agent-ai](https://github.com/Anecdotes-Yair/trust-my-agent-ai).

## Setup

When the user asks to set up TrustMyAgent, walk them through the following steps. **Present each step to the user and wait for their approval before executing.** Do not run commands silently or skip user confirmation.

### Step 1: Verify Python 3

Check that Python 3 is available:

```bash
python3 --version
```

If Python 3 is not installed, ask the user before installing it:
- macOS: `brew install python3`
- Linux: `sudo apt-get install python3` or `sudo apk add python3`

### Step 2: Run a dry-run assessment

Run the security assessment in **dry-run mode** first so the user can review the results before any data leaves the machine:

```bash
python3 {baseDir}/run.py --dry-run
```

This runs all 41 checks and prints the full telemetry payload that *would* be sent — but sends nothing. Show the user the results and let them review:

- The trust score and tier
- Which checks passed and failed
- The exact JSON payload that would be transmitted

Ask the user: **"Would you like to send this report to the Trust Center dashboard, run in local-only mode (no network), or adjust any settings?"**

### Step 3: Run the full assessment (with user consent)

If the user approves sending telemetry:

```bash
python3 {baseDir}/run.py
```

If the user prefers local-only mode (no telemetry sent):

```bash
python3 {baseDir}/run.py --local-only
```

### Step 4: Schedule recurring assessments (optional)

Ask the user if they want to schedule automatic assessments. If they agree, suggest a cron job. The command varies by agent platform:

**OpenClaw agents:**
```bash
openclaw cron add --name "🛡️ TrustMyAgent" --cron "*/15 * * * *" --session agent:security:main --message "Run security assessment: python3 {baseDir}/run.py"
```

**Other agents / standalone:**
```bash
# Add to system crontab (runs every 15 minutes)
(crontab -l 2>/dev/null; echo "*/15 * * * * python3 {baseDir}/run.py --quiet") | crontab -
```

> The user can choose any interval or skip scheduling entirely.

## What Data Is Sent

When telemetry is enabled (the default), the following data is sent via HTTPS POST to `https://www.trustmyagent.ai/api/telemetry`:

| Field | Example | Purpose |
|-------|---------|---------|
| `agent.id` | `sha256(hostname)` | Unique identifier (derived from hostname hash, not the hostname itself) |
| `agent.name` | `"My Agent"` | Display name (from IDENTITY.md or env var) |
| `agent.platform` | `"darwin"` | OS type (darwin/linux) |
| `agent.detected_env` | `"macos_arm64"` | Runtime environment label |
| `posture.trust_tier` | `"HIGH"` | Computed trust tier |
| `posture.overall_score` | `92` | Numeric score 0-100 |
| `results[]` | `{check_id, passed, status}` | Per-check pass/fail status |
| `detections[]` | `{check_id, severity, risk}` | Failed checks with risk context |

**What is NOT sent:**
- No file contents, paths, or directory listings
- No environment variable values (only whether secret-like patterns exist)
- No process names, PIDs, or command lines
- No network traffic, IP addresses, or hostnames
- No credentials, tokens, or API keys
- No conversation transcripts or user data

The telemetry endpoint and all check logic are open source. You can verify exactly what is transmitted by using `--dry-run` mode.

### Opting out of telemetry

Use `--local-only` to run all checks without any network calls:

```bash
python3 {baseDir}/run.py --local-only
```

This gives you the full security assessment locally without sending anything.

## How It Works

1. **`run.py` executes on the host** — triggered manually, by cron, or by agent heartbeat
2. **41 security checks run** using bash commands and Python sensors (all read-only)
3. **Trust score is calculated** (0-100) based on pass/fail results and severity weighting
4. **Results are displayed** locally in the terminal
5. **(Optional) Telemetry is sent** to the Trust Center dashboard via HTTPS

No files are written locally. No state is persisted on the agent machine.

## Security Domains

| Domain | Checks | Focus |
|--------|--------|-------|
| **Physical Environment** | PHY-001 to PHY-005 | Disk encryption, container isolation, non-root execution |
| **Network** | NET-001 to NET-005 | Dangerous ports, TLS/SSL, DNS, certificates |
| **Secrets** | SEC-001 to SEC-005, MSG-005 | Env var secrets, cloud creds, private keys, conversation leaks |
| **Code** | COD-001 to COD-004 | Git security, no secrets in repos |
| **Logs** | LOG-001 to LOG-004 | System logging, audit readiness |
| **Skills** | SKL-001 to SKL-005, MSG-001, MSG-003 | Skill manifests, MCP server trust |
| **Integrity** | INT-001 to INT-005, MSG-002, MSG-006 | Backdoors, browser abuse, suspicious tool calls, URL reputation |
| **Social Guards** | SOC-001 to SOC-006, MSG-004 | Action logging, session transparency, Moltbook integrity, owner reputation |
| **Incident Prevention** | INC-001 to INC-005 | Process spawning, system load, port scanning |
| **Node Security** | NODE-001 to NODE-005 | Remote execution approval, token permissions, exec allowlists |
| **Media Security** | MEDIA-002 to MEDIA-003 | Temp directory permissions, file type validation |
| **Gateway Security** | GATEWAY-001 to GATEWAY-002 | Binding address, authentication |
| **Identity Security** | IDENTITY-001 to IDENTITY-002 | DM pairing allowlist, group chat allowlist |
| **SubAgent Security** | SUBAGENT-001 to SUBAGENT-002 | Concurrency limits, target allowlists |

## Check Types

### Bash checks (20 checks)
Defined in `checks/openclaw_checks.json`. Each check runs a shell command and evaluates the output against a `pass_condition` (`equals`, `contains`, `not_contains`, `exit_code_zero`, etc.).

### Python/Message-based checks (21 checks)
Defined in `checks/message_checks.json` and `checks/nodes_media_checks.json`. These are programmatic sensors that analyze secrets, session transcripts, MCP configs, skill manifests, and more.

### Platform Support
Checks auto-detect macOS vs Linux and use platform-appropriate commands. Checks can declare `"platforms": ["linux"]` to be gracefully skipped on unsupported platforms.

## Trust Tiers

| Tier | Score | Label |
|------|-------|-------|
| HIGH | 90-100 | Ready for Business |
| MEDIUM | 70-89 | Needs Review |
| LOW | 50-69 | Elevated Risk |
| UNTRUSTED | 0-49 | Critical Security Gaps |

Any critical-severity failure caps the score at 49 (UNTRUSTED). Three or more high-severity failures cap at 69 (LOW).

## Command Line Options

| Flag | Description |
|------|-------------|
| `--checks`, `-c` | Path to custom checks JSON file |
| `--timeout`, `-t` | Timeout per check in seconds (default: 30) |
| `--quiet`, `-q` | Minimal output |
| `--json`, `-j` | Output structured JSON to stdout |
| `--dry-run` | Run all checks and display the telemetry payload, but do not send it |
| `--local-only` | Run all checks locally without any network calls |
| `--no-notify` | Skip agent notifications for detections |

## Configuration

| Source | Description | Default |
|---------------------|-------------|---------|
| `IDENTITY.md` | Agent display name (read from `# Name` section) | `"Agent"` |
| `OPENCLAW_AGENT_NAME` env var | Overrides IDENTITY.md name | — |
| `OPENCLAW_AGENT_ID` env var | Agent identifier | SHA256 of hostname |
| `TRUSTMYAGENT_TELEMETRY_URL` env var | Server endpoint | `https://www.trustmyagent.ai/api/telemetry` |

## Files

```
Agent/
├── SKILL.md                        # This file
├── run.py                          # Main entry point (stateless runner)
└── checks/
    ├── openclaw_checks.json        # 20 bash-based security checks
    ├── message_checks.json         # 10 Python-based message/secret sensors
    ├── nodes_media_checks.json     # 11 infrastructure checks
    └── detection_kb.json           # Risk descriptions and remediation guidance
```

## Architecture

```
┌─────────────────┐                                 ┌──────────────────┐
│   Agent Host     │      POST /api/telemetry        │ 🛡️ TrustMyAgent  │
│                  │  ────────────────────────────►   │  Server           │
│  run.py          │  (only when telemetry enabled)  │  (Cloudflare)    │
│  ├─ bash checks  │                                 │  ├─ R2 storage   │
│  └─ python checks│                                 │  ├─ agents index │
│                  │                                 │  └─ trend history│
│  (no local state)│                                 │                  │
└─────────────────┘                                  └──────────────────┘
                                                            │
                                                     trust-center.html
                                                     (public dashboard)
```

## Privacy & Trust

- **Open source**: All code is MIT-licensed and publicly auditable at [github.com/Anecdotes-Yair/trust-my-agent-ai](https://github.com/Anecdotes-Yair/trust-my-agent-ai)
- **Stateless**: No files written, no state persisted, no background processes installed without consent
- **Opt-in telemetry**: Use `--local-only` to run entirely offline, or `--dry-run` to preview before sending
- **No secrets transmitted**: Checks detect the *presence* of issues, never transmit actual secret values
- **Transparent payload**: The `--dry-run` flag shows the exact JSON that would be sent
- **Server**: Operated by [Anecdotes AI](https://anecdotes.ai), a GRC (Governance, Risk, Compliance) company. Server code is at [github.com/Anecdotes-Yair/trust-my-agent-ai-website](https://github.com/Anecdotes-Yair/trust-my-agent-ai-website)

## Credits

Built by [Anecdotes AI](https://anecdotes.ai) for the AI agent ecosystem.
