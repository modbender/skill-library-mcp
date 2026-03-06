# ClawAudit — Project Documentation

_Last updated: 2026-02-21_

## Overview

**ClawAudit** is a security scanner and hardening tool for OpenClaw. It was built in response to the **ClawHavoc campaign** (February 2026), in which ~20% of all ClawHub skills were compromised.

The project can be used both as an **OpenClaw skill** and as a **standalone CLI**.

---

## Goals

1. Scan installed OpenClaw skills for malware
2. Audit OpenClaw configuration for security vulnerabilities
3. Audit server/OS hardening (SSH, firewall, fail2ban, WireGuard, kernel, AppArmor…)
4. Calculate a security score (0–100) from all three sources
5. Automatically fix common issues (auto-fix)
6. Monitor new skill installations in real time (watch mode)

---

## Technology

- **Languages:** Bash (scanner), Node.js ESM (all other scripts)
- **Node.js:** >= 22.0.0
- **Dependencies:** none (Node.js + Bash only)
- **License:** MIT

---

## Project Structure

```
claw-audit/
├── SKILL.md                        # OpenClaw skill definition
├── README.md                       # Public documentation
├── PROJECT.md                      # This document
├── package.json                    # npm metadata + scripts
├── scripts/
│   ├── scan-skills.sh              # Skill scanner (Bash)
│   ├── audit-config.mjs            # OpenClaw config auditor (Node.js)
│   ├── audit-system.mjs            # System/OS auditor (Node.js)
│   ├── calculate-score.mjs         # Security score (all 3 sources) (Node.js)
│   ├── auto-fix.mjs                # Automatic fixes (Node.js)
│   └── watch.mjs                   # Watch mode / real-time monitor (Node.js)
├── tests/
│   ├── audit-system.test.mjs       # System auditor tests
│   ├── audit-config.test.mjs       # Config auditor tests
│   └── run.sh                      # Test runner
├── references/
│   └── malicious-patterns.json     # Pattern database
└── LICENSE
```

---

## Components

### 1. scan-skills.sh — Skill Scanner
Scans all installed OpenClaw skills for known malicious patterns.

**Critical patterns (CRIT):**
| Code | Threat |
|------|--------|
| CRIT-001 | Shell execution (curl\|bash, eval, exec) |
| CRIT-002 | Credential access (.env, SSH keys, API keys) |
| CRIT-003 | Reverse shell (nc -l, /dev/tcp/) |
| CRIT-004 | Prompt injection ("ignore previous instructions") |
| CRIT-005 | External binary execution (download & execute) |

**Warnings (WARN):**
| Code | Issue |
|------|-------|
| WARN-005 | Obfuscated code (base64, hex-encoded) |
| WARN-007 | Exfiltration indicators (webhook.site, ngrok) |
| WARN-008 | Suspicious install instructions |
| WARN-009 | Typosquatting indicators |
| WARN-010 | Hidden file operations |

---

### 2. audit-config.mjs — OpenClaw Config Auditor
Audits the OpenClaw configuration for security issues.

| Code | Issue | Score Impact |
|------|-------|-------------|
| WARN-001 | Gateway exposed on non-loopback interface | -15 |
| WARN-002 | DM policy set to "open" without allowlist | -15 |
| WARN-003 | Sandbox mode not enabled | -8 |
| WARN-004 | Browser control exposed beyond localhost | -10 |
| WARN-006 | Credentials in plaintext / loose permissions | -8 |
| WARN-011 | Config file is not valid JSON | -3 |
| WARN-012 | Gateway exposed without auth token | -20 |
| WARN-013 | Exec not restricted to workspace | -8 |
| WARN-014 | Filesystem access not restricted to workspace | -8 |
| WARN-020 | Dangerous pattern in cron job (curl\|bash, eval, rm -rf) | -15 |
| WARN-021 | Concurrent LLM cron jobs scheduled at the same time | -5 |
| WARN-022 | agentTurn cron job missing bestEffortDeliver | -8 |
| INFO-004 | No skills allowlist configured | -3 |
| INFO-010 | Paired devices registered — review recommended | -1 / -5 |
| INFO-011 | Sub-agent concurrency limits not set | -2 |

---

### 3. audit-system.mjs — System/OS Auditor
Audits server hardening at the OS level. Independent of OpenClaw.

**SSH checks:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-001 | PermitRootLogin enabled | -20 |
| SYS-002 | PasswordAuthentication enabled | -8 |
| SYS-003 | MaxAuthTries > 4 | -5 |
| SYS-004 | X11Forwarding enabled | -3 |
| SYS-005 | No AllowUsers/AllowGroups configured | -5 |
| SYS-006 | SSH Protocol 1 enabled | -25 |

**Firewall checks (UFW):**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-010 | UFW not available | -20 |
| SYS-011 | UFW inactive | -25 |
| SYS-012 | Default policy not "deny incoming" | -15 |
| SYS-013 | SSH port 22 publicly accessible | -10 |
| SYS-014 | DB port publicly exposed (MySQL/Postgres/Mongo etc.) | -20 |

**fail2ban checks:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-020 | fail2ban not installed | -10 |
| SYS-021 | fail2ban not active | -15 |
| SYS-022 | SSH jail not active | -8 |

**WireGuard checks:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-030 | WireGuard not active, SSH publicly accessible | -5 |
| SYS-031 | WireGuard active, SSH still publicly accessible | -8 |
| SYS-032 | Full-tunnel detected (0.0.0.0/0) | -3 |

**Auto-updates:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-040 | unattended-upgrades not installed | -8 |
| SYS-041 | Update timer inactive | -5 |

**Open ports:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-050 | Unknown service on public port | -5 |

**Kernel hardening (sysctl):**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-060 | Insecure kernel parameters (ip_forward, ASLR, SYN cookies…) | -8 / -15 |

**AppArmor:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-061 | AppArmor not active or no profiles loaded | -5 / -2 |

**SSH authorized_keys:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-062 | authorized_keys present — review recommended | -8 / -2 |

**Time synchronization:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-063 | System clock not NTP-synchronized | -5 |

**Swap encryption:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-064 | Swap partition not encrypted | -2 |

**Sticky bit / world-writable:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-065 | /tmp or /var/tmp missing sticky bit | -8 |

**SUID/SGID binaries:**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-066 | Unknown binaries with SUID/SGID bit | -10 |

**CIS Benchmark checks (Phase 1):**
| Code | Issue | Score Impact |
|------|-------|-------------|
| SYS-070 | Docker daemon exposed on TCP without TLS | -25 |
| SYS-071 | Privileged containers detected | -25 |
| SYS-072 | Docker socket mounted in containers | -25 |
| SYS-080 | OpenClaw running as root | -25 |
| SYS-081 | Containers sharing host PID namespace | -10 |
| SYS-082 | No resource limits configured | -5 |
| SYS-100 | Cloud metadata service accessible | -10 |
| SYS-101 | No egress filtering configured | -2 |
| SYS-102 | Using public DNS servers | -1 |
| SYS-150 | Filesystem partitioning issues | -10 |
| SYS-151 | Core dumps not disabled | -5 |
| SYS-160 | Weak password policy | -10 |
| SYS-161 | No account lockout policy configured | -15 |
| SYS-163 | Empty passwords detected | -25 |
| SYS-164 | Root PATH contains unsafe directories | -20 |
| SYS-170 | IPv6 enabled but unused | -2 |
| SYS-180 | Unnecessary services enabled | -8 |
| SYS-181 | /etc/cron.allow not configured | -5 |
| SYS-182 | SSH login banner not configured | -2 |
| SYS-183 | SSH idle timeout not set | -8 |
| SYS-190 | No syslog daemon running | -25 |
| SYS-191 | auditd not running or not configured | -20 |
| SYS-192 | Log files with weak permissions | -8 |
| SYS-204 | /etc/shadow has weak permissions | -15 |

---

### 4. calculate-score.mjs — Security Score
Calculates a combined score from **all three sources**:
- Skill scan (CRIT/WARN)
- OpenClaw config audit (WARN/INFO)
- System audit (SYS)

**Grading:**
| Score | Grade | Status |
|-------|-------|--------|
| 90–100 | A | Excellent |
| 70–89 | B | Good |
| 50–69 | C | Fair |
| 30–49 | D | Poor |
| 0–29 | F | Critical |

---

### 5. auto-fix.mjs — Automatic Fixes
Fixes OpenClaw config issues automatically (atomic writes).
System fixes (SSH, UFW etc.) are **shown as copy-paste commands only** — never auto-applied.

---

### 6. watch.mjs — Watch Mode
Monitors skill installations and config changes in real time.
Uses `spawnSync` with argument arrays (no shell injection risk).

---

### 7. references/malicious-patterns.json — Pattern Database
Known malicious patterns sourced from:
- ClawHavoc campaign (341 malicious skills, Feb 2026)
- Koi Security audit (2,857 ClawHub skills)
- Snyk ToxicSkills report (283 critically flawed skills)
- VirusTotal Code Insight (3,016+ skills analyzed)
- Bitdefender analysis (~900 malicious packages)

---

## npm Scripts

```bash
npm run scan                 # Skill scanner
npm run scan:json            # Scanner with JSON output
npm run audit                # OpenClaw config audit
npm run audit:fix            # Audit + fix hints
npm run audit:system         # System/OS audit
npm run audit:system:fix     # System audit + fix hints
npm run score                # Security score (all sources)
npm run score:json           # Score as JSON
npm run fix                  # Auto-fix (interactive)
npm run fix:dry              # Auto-fix dry run
npm run watch                # Watch mode
npm run test                 # Run all tests
```

---

## Score Example

```
🛡️  ClawAudit Security Score

   ████████████████████████████████░░░░░░░░  84/100  🟢 Good (B)

📉 Biggest Score Impacts:
   🔵 -3 pts — INFO-004: No skills allowlist configured
   🔵 -3 pts — SYS-181: /etc/at.allow not configured
   🔵 -2 pts — SYS-101: No egress filtering configured
   🔵 -2 pts — SYS-182: SSH login banner not configured

📋 Check Summary (48 checks): all checks passed
```

---

## Safety Guardrails

- Never modify or delete skills without explicit confirmation
- Never log credential values — only report their existence
- Never execute suspicious code found during scanning
- System fixes (sudo commands) are always shown only, never auto-applied
- `spawnSync` + argument arrays instead of shell template strings (no injection risk)
- On critical findings: provide recommendation, leave decision to the user

---

## Required Permissions (for full check coverage)

Some checks require elevated privileges. Without them, checks are reported as skipped.

### Sudoers file: `/etc/sudoers.d/claw-audit`

```bash
sudo tee /etc/sudoers.d/claw-audit << 'EOF'
# ClawAudit — least-privilege sudoers for openclaw user
openclaw ALL=(ALL) NOPASSWD: /usr/bin/wg show
openclaw ALL=(ALL) NOPASSWD: /sbin/auditctl -l
openclaw ALL=(ALL) NOPASSWD: /usr/bin/stat -c %a /etc/shadow
openclaw ALL=(ALL) NOPASSWD: /usr/bin/stat -c %U\:%G /etc/shadow
EOF
sudo chmod 440 /etc/sudoers.d/claw-audit
```

### Group membership (alternative to sudo for shadow access)

```bash
sudo usermod -aG shadow openclaw
# Then re-login or: su - openclaw
```

| Permission | Affected Checks | Without it |
|---|---|---|
| `sudo wg show` | SYS-030-032 (WireGuard) | Skipped |
| shadow group or `sudo stat /etc/shadow` | SYS-163 + SYS-204 | Skipped |
| `sudo auditctl -l` | SYS-191 (audit rules) | Service status only |

---

## Tests

```
172 tests · 172 pass · 0 fail · 0 skipped
```

| File | Description |
|------|-------------|
| `audit-system.test.mjs` | SSH parsing, UFW regex, WireGuard subnet, sysctl, NTP, SUID, authorized_keys, sticky bit, CIS checks, integration |
| `audit-system-cis.test.mjs` | CIS Benchmark checks (Phase 1 + Phase 2) |
| `audit-system-phase1.test.mjs` | Docker, process isolation, network segmentation |
| `audit-config.test.mjs` | Cron job patterns, paired devices, sub-agent limits, schedule conflicts, bestEffort |

---

## Current Status

- **Version:** 0.1.0
- **Repository:** https://github.com/u45362/claw-audit.git

## Roadmap

- [ ] auto-fix.mjs: add system fix hints (SSH config, UFW rules via sudo hints)
- [ ] watch.mjs: monitor system changes (new open ports etc.)
- [ ] External port scan (attacker's perspective via nmap)
- [ ] npm audit on skill dependencies (CVE check)
