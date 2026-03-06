---
name: crusty-security
version: 1.3.0
description: >
  Security and threat scanning skill for OpenClaw agents. Scans files and
  skills for malware. Monitors agent behavior for compromise indicators. Audits host
  security posture. Triggers on: "scan this file", "is this safe",
  "virus scan", "malware check", "security scan", "scan for threats",
  "check this download", "quarantine", "scan my system", "threat report",
  "scheduled scan", "audit host security", "audit this skill",
  "check agent integrity", "security report", "monitor agent".
homepage: https://crustysecurity.com
metadata: {"openclaw":{"requires":{"bins":["bash","python3"]}}}
---

# Crusty Security — Security & Threat Scanning

## Overview

Crusty Security protects OpenClaw agents against real threats: malware in downloaded files, compromised skills from ClawHub, data exfiltration, prompt injection payloads, and host-level compromise. It uses ClamAV for file scanning and AI-agent-specific static analysis.

**Threat model:** The agent itself is the attack surface. Prompt injection can lead to code execution. Malicious skills run with agent privileges. Crusty Security protects both the host AND the agent's integrity.

## Quick Reference

| Task | Command |
|------|---------|
| Install ClamAV | `bash scripts/install_clamav.sh` |
| Scan a file | `bash scripts/scan_file.sh /path/to/file` |
| Scan a directory | `bash scripts/scan_file.sh -r /path/to/dir` |
| Audit a skill | `bash scripts/audit_skill.sh /path/to/skill/` |
| Host security audit | `bash scripts/host_audit.sh` |
| Monitor agent integrity | `bash scripts/monitor_agent.sh` |
| Generate security report | `bash scripts/generate_report.sh` |

All scripts output JSON. All scripts support `--help`. All paths are relative to this skill directory.

## Setup (First Run)

Run `bash setup.sh` — that's it. This will:
1. Install ClamAV if missing
2. Configure freshclam (macOS Homebrew fix)
3. Send initial heartbeat to dashboard (if `CRUSTY_API_KEY` set)
4. Run initial host audit + workspace scan (populates dashboard immediately)
5. Check which scheduled scans need to be created

**⚠️ IMPORTANT — After setup.sh, you MUST create the cron jobs below using the OpenClaw cron tool.** Setup.sh handles the bash-level installation, but cron jobs require agent-level tools. Do this immediately after first install — don't wait for the user to ask.

### Required Cron Jobs (create on first install)

Check what's missing: `bash scripts/check_crons.sh`

Use the OpenClaw **cron tool** (`cron add`) to create these. Replace `{SKILL_DIR}` with the actual path to this skill directory and `{WORKSPACE}` with the workspace path (usually `/data/workspace`).

| Name | Schedule | sessionTarget | Payload |
|------|----------|---------------|---------|
| `crusty-daily-scan` | cron `0 3 * * *` | main / systemEvent | `Run Crusty Security daily scan: bash {SKILL_DIR}/scripts/scan_file.sh --incremental -r {WORKSPACE} && bash {SKILL_DIR}/scripts/monitor_agent.sh` |
| `crusty-weekly-full` | cron `0 3 * * 0` | main / systemEvent | `Run Crusty Security weekly scan: bash {SKILL_DIR}/scripts/scan_file.sh -r {WORKSPACE} && bash {SKILL_DIR}/scripts/host_audit.sh && bash {SKILL_DIR}/scripts/generate_report.sh --output /tmp/crusty_logs/weekly_report.md` |
| `crusty-monthly-deep` | cron `0 4 1 * *` | main / systemEvent | `Run Crusty Security monthly deep audit: bash {SKILL_DIR}/scripts/host_audit.sh --deep` |

### Dashboard Cron Jobs (only if `CRUSTY_API_KEY` is set)

| Name | Schedule | sessionTarget | Payload |
|------|----------|---------------|---------|
| `crusty-heartbeat` | every 300000ms (5 min) | main / systemEvent | `Crusty Security heartbeat: Run bash {SKILL_DIR}/scripts/dashboard.sh heartbeat` |
| `crusty-clawhub-sync` | every 43200000ms (12h) | isolated / agentTurn | `Run ClawHub security sync: python3 {SKILL_DIR}/scripts/clawhub_sync.py --push. Report any critical or high severity findings.` |

Check `cron list` first — skip any that already exist (match by name prefix `crusty-`).

See `references/setup.md` for detailed configuration.

## Dashboard Connection

If your human has configured `CRUSTY_API_KEY`, the skill sends scan results to the Crusty Security dashboard (crustysecurity.com):
- **Heartbeats** are sent every 5 minutes automatically — keeps the dashboard showing agent status
- **Scan results** are pushed when you add `--push` to scan commands
- **ClawHub sync** sends skill inventory with `python3 scripts/clawhub_sync.py --push`
- If `CRUSTY_API_KEY` is NOT set, everything works locally — no data is sent anywhere
- The dashboard never connects TO the agent — data flows one way (agent → dashboard)

## Scanning Workflows

### File Scanning

**Triggers:** "scan this file", "is this safe", "check this download", "virus scan"

1. Run `bash scripts/scan_file.sh <path>` for ClamAV local scan
2. Report results:
   - ✅ Clean — "No threats detected. Scanned with ClamAV, signatures from [date]."
   - ⚠️ Suspicious — "Low-confidence detection by ClamAV. Recommend quarantine for review."
   - 🚨 Malicious — "Threat detected: [name]. Recommend quarantine. Options: quarantine, delete, or ignore."

**For directories:**
```bash
bash scripts/scan_file.sh -r /data/workspace      # Full recursive scan
bash scripts/scan_file.sh -r --incremental /data/workspace  # Skip unchanged files
```

**Quarantine workflow:**
```bash
bash scripts/scan_file.sh --quarantine /path/to/file   # Move to quarantine
# Quarantine location: $CRUSTY_QUARANTINE (default: /tmp/crusty_quarantine)
# Manifest: /tmp/crusty_quarantine/manifest.json
```

**Important notes:**
- ClamAV prefers clamdscan (daemon) when available, falls back to clamscan
- Max file size default: 200M (configurable via `CRUSTY_MAX_FILE_SIZE`)
- Encrypted archives: flagged as "unscanned" — cannot inspect contents
- Large archives: ClamAV handles zip, rar, 7z, tar, gz natively

### Skill Auditing (Supply Chain Security)

**Triggers:** "audit this skill", "is this skill safe", "check skill security", "scan skill"

`bash scripts/audit_skill.sh /path/to/skill/directory/`

**What it checks:**
- 🔴 **Critical:** curl/wget piped to shell, reverse shell patterns, crypto mining indicators
- 🟠 **High:** eval/exec with dynamic input, base64 decode patterns, data exfiltration endpoints (webhook.site, ngrok, etc.), credential harvesting, binary executables, agent config modification
- 🟡 **Medium:** hidden files, system file access, hardcoded IPs, obfuscated code, persistence mechanisms (cron, systemd)
- 🔵 **Low/Info:** large skill size, credential references in docs

**Output:** Risk score (low/medium/high/critical) + detailed findings with evidence.

**When to use:**
- Before installing any skill from ClawHub
- When reviewing third-party skill contributions
- Periodically on all installed skills: `for d in /data/workspace/skills/*/; do bash scripts/audit_skill.sh "$d"; done`

### Host Security Audit

**Triggers:** "audit host", "security audit", "check host security"

`bash scripts/host_audit.sh` or `bash scripts/host_audit.sh --deep`

**Checks:**
- Suspicious cron jobs (curl piping, base64, reverse shells)
- Unexpected listening ports
- Recently modified system files (deep mode)
- SSH key audit (excessive keys, no-comment keys, root login)
- Sensitive file permissions (world-writable /etc/passwd, etc.)
- ClamAV signature freshness
- `openclaw security audit` (if available)

**Output:** Posture score (0-100) + findings. Score deductions: critical (-25), high (-15), medium (-10), low (-5).

### Agent Behavior Monitoring

**Triggers:** "check agent integrity", "monitor agent", "is the agent compromised"

`bash scripts/monitor_agent.sh`

**What it checks:**
- Recent modifications to AGENTS.md, SOUL.md, MEMORY.md, TOOLS.md, USER.md
- Memory file churn (>10 files modified = suspicious)
- Unexpected cron jobs (anything not clawguard/freshclam/standard maintenance)
- Suspicious outbound connections (IRC ports, backdoor ports, Tor)
- Files created outside workspace (/tmp executables, home directory changes)
- Suspicious processes (xmrig, nc -l, ncat, socat, chisel)
- High CPU processes (>80% — potential miners)
- Sensitive file exposure (.env files, world-readable SSH keys)

**Output:** Status (healthy / warnings_present / compromised_indicators) + findings.

### Security Report Generation

**Triggers:** "security report", "threat report", "posture report"

`bash scripts/generate_report.sh` or `bash scripts/generate_report.sh --days 30 --output report.md`

Compiles all recent scan results into a markdown security posture report with:
- Scan summary (total, clean, threats, errors)
- Threat details with file paths and actions taken
- Security posture score with emoji indicators
- Recommendations (missing tools, scan schedules)

## Automatic Scheduled Scanning

Cron jobs are defined in the **Setup (First Run)** section above. Create them immediately on first install using the OpenClaw cron tool. 

To verify all crons are configured: `bash scripts/check_crons.sh`

## False Positive Handling

ClamAV has moderate false positive rates. Strategy:

1. **Single ClamAV detection, known safe source → Likely false positive.** Log and skip.
2. **ClamAV detection, unknown source → Quarantine and investigate.**
3. **ClamAV detection + skill audit findings → Real threat.** Quarantine immediately.

**To handle a false positive:**
- Submit to ClamAV: https://www.clamav.net/reports/fp
- Document in scan logs for future reference

## Quarantine Procedures

**Location:** `$CRUSTY_QUARANTINE` (default: `/tmp/crusty_quarantine`)
**Manifest:** `manifest.json` in quarantine directory tracks original paths and timestamps.

```bash
# View quarantined files
cat /tmp/crusty_quarantine/manifest.json | python3 -m json.tool

# Restore a false positive
mv /tmp/crusty_quarantine/<file> /original/path/

# Permanently delete
rm -rf /tmp/crusty_quarantine/*
```

**Never use `clamscan --remove`.** Always quarantine first, verify, then delete.

## Offline Mode

Crusty Security works fully offline with reduced capability:
- ✅ ClamAV scanning (local signatures)
- ✅ Skill auditing (static analysis, no network needed)
- ✅ Host auditing (local checks)
- ✅ Agent monitoring (local checks)
- ⚠️ ClamAV signatures may be stale (check freshness in host audit)

## Resource-Constrained Environments (Raspberry Pi)

For hosts with <2GB RAM:
- `install_clamav.sh` auto-detects low RAM and skips daemon mode
- Use `clamscan` (on-demand) instead of `clamd` (daemon)
- Use incremental scanning (`--incremental`) to reduce scan time
- Skill auditing and agent monitoring have minimal resource requirements

For hosts with <1GB RAM:
- Consider skipping ClamAV entirely
- Use skill auditing + agent monitoring only
- These tools are shell/Python with negligible memory usage

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRUSTY_API_KEY` | (none) | Dashboard API key (`cg_live_...`) |
| `CRUSTY_DASHBOARD_URL` | `https://crustysecurity.com` | Dashboard URL |
| `CRUSTY_QUARANTINE` | `/tmp/crusty_quarantine` | Quarantine directory |
| `CRUSTY_LOG_DIR` | `/tmp/crusty_logs` | Scan log directory |
| `CRUSTY_MAX_FILE_SIZE` | `200M` | Max file size to scan |
| `CRUSTY_WORKSPACE` | auto-detected | Agent workspace path |

> **Backwards compat:** `CLAWGUARD_*` env vars are still supported but deprecated. Use `CRUSTY_*` going forward.

## Incident Response

When a real threat is confirmed, see `references/remediation.md` for the full checklist. Quick summary:

1. **Quarantine** the file immediately
2. **Assess scope** — was it executed? Did it modify other files?
3. **Check persistence** — cron jobs, SSH keys, shell profiles, systemd services
4. **Check exfiltration** — outbound connections, DNS queries, API key usage
5. **Rotate credentials** if any were potentially exposed
6. **Full scan** — `bash scripts/scan_file.sh -r /`
7. **Document** the incident
