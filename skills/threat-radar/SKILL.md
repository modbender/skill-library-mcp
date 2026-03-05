# threat-radar — Continuous Security Scanning & CVE Alerting

**Version:** 1.0.0  
**Category:** Security  
**Type:** Monitoring + Alerting  
**Published:** February 24, 2026

---

## What It Does

Continuous security posture monitoring that scans your running services, Docker images, and software dependencies for known CVEs. Alerts you via WhatsApp/Telegram/Discord when new vulnerabilities affect your stack.

**No external services required** — runs entirely within OpenClaw using public CVE feeds.

---

## Features

### Security Scanning

- **Docker image vulnerability scanning** — trivy-style CVE detection for your container images
- **Dependency auditing** — npm, pip, cargo lockfile analysis for known vulnerabilities
- **Port discovery** — identifies exposed services on your local network
- **SSL/TLS grading** — evaluates certificate validity and security config
- **OpenClaw config security** — checks your OpenClaw setup against best practices
- **Exposed service detection** — flags accidentally public services

### CVE Monitoring

- **Automatic CVE feeds** — pulls from NVD (National Vulnerability Database) and GitHub Advisories
- **Track your versions** — matches CVEs to YOUR installed software versions
- **Severity-based alerting** — CRITICAL immediately, HIGH in daily digest, LOW weekly summary
- **Recovery tracking** — knows when you patch and closes alerts

### Reporting

- **Weekly security digest** — Canvas dashboard or markdown report
- **Trend tracking** — is your security posture improving?
- **Remediation suggestions** — actionable fixes per finding
- **CWE references** — understand the vulnerability class

---

## Commands

### Scanning

```bash
threat-radar scan                    # Full security scan now
threat-radar scan --docker           # Docker images only
threat-radar scan --deps <path>      # Dependency audit (npm/pip/cargo)
threat-radar scan --ports            # Port scan (local network)
threat-radar scan --ssl <domain>     # SSL certificate check
threat-radar scan --openclaw         # OpenClaw config check
threat-radar scan --exposed          # Check for accidentally public services
```

### CVE Tracking

```bash
threat-radar cves                    # Show CVEs affecting your stack
threat-radar cves --critical         # Only CRITICAL severity
threat-radar cves --since <days>     # New CVEs in last N days
threat-radar watch <software> <v>    # Track specific software version
threat-radar unwatch <software>      # Stop tracking
threat-radar watches                 # List all watched software
```

### Reporting

```bash
threat-radar report                  # Generate full security report
threat-radar report --period=week    # Weekly summary
threat-radar report --period=month   # Monthly summary
threat-radar status                  # Quick security status
threat-radar history                 # View past scans
threat-radar trends                  # Posture improvement tracking
```

### Management

```bash
threat-radar init                    # Initialize threat-radar
threat-radar config show             # Show current configuration
threat-radar config update           # Update scan settings
threat-radar cron-install            # Set up scheduled daily scans + CVE checks
threat-radar cron-remove             # Remove scheduled scans
threat-radar data-refresh            # Force CVE database refresh
```

### Output

All commands support:
- `--json` — machine-readable JSON output
- `--csv` — comma-separated for spreadsheet import
- `--md` — markdown for reports
- `--no-color` — plain text (useful for logs)

---

## Example Usage

### Initial Setup

```bash
$ threat-radar init
✓ Initialized threat-radar
✓ Created ~/.openclaw/workspace/monitoring/threat-radar/
✓ Pulled CVE databases (NVD: 245,891 entries, GitHub: 14,329 advisories)
✓ Scanned Docker images: 3 images, 0 vulnerabilities found
✓ Scanned dependencies: npm 487 packages, pip 89 packages — 2 warnings
✓ Security score: 87/100

Ready to scan. Try: threat-radar scan --docker
```

### Full Security Scan

```bash
$ threat-radar scan
Scanning security posture...

[DOCKER IMAGES] ─────────────────────────────────────────
  openclaw-agent:latest        0 CVEs  ✓ Clean
  postgres:15                  2 CVEs  ⚠ Medium (libc, OpenSSL)
  redis:latest                 0 CVEs  ✓ Clean

[DEPENDENCIES] ──────────────────────────────────────────
  npm (workspace root)          3 CVEs  ⚠ 1 High, 2 Medium
    - lodash@4.17.19            CVE-2021-23337 (High: Prototype pollution)
    - axios@0.21.0              CVE-2021-41773 (Medium: XXE in parser)
    - ws@7.4.0                  CVE-2021-32640 (Medium: Buffer overflow)

[PORTS] ──────────────────────────────────────────────────
  192.168.1.50:80    (nginx)         ✓ Private network
  192.168.1.50:443   (nginx)         ✓ Private network
  10.10.10.230:6379  (redis)         ✓ Private network

[SSL/TLS] ────────────────────────────────────────────────
  openclaw.local                Grade A  Valid until Jun 24, 2026 ✓
  example.com                   Grade B  Warning: no HSTS header

[OPENCLAW CONFIG] ────────────────────────────────────────
  agentToAgent permissions      ✓ Restricted (not [*])
  Credential file permissions   ✓ 600 (not world-readable)
  Memory file permissions       ✓ 600
  Gateway auth enabled          ✓ Yes
  Sandbox restrictions          ⚠ exec-sandbox: false (accepted risk)

[EXPOSED SERVICES] ───────────────────────────────────────
  0 accidentally public services found ✓

SUMMARY
──────
Security Score: 82/100 (down 5 points from 87 on 2026-02-23)
Critical CVEs: 0
High CVEs: 1 (lodash)
Medium CVEs: 4 (axios, ws, libc, OpenSSL)
Low CVEs: 2
Estimated fix time: 2 hours (update npm packages)

Next scan: 2026-02-25 09:00 UTC (via cron)
```

### CVE Tracking

```bash
$ threat-radar cves --critical
Critical vulnerabilities affecting your stack:

None currently. Your environment is clean at this severity level.

$ threat-radar cves
CVEs affecting your stack:

[HIGH] ──────────────────────────────────────────────────
  CVE-2021-23337 (lodash)
    Package: lodash 4.17.19
    Component: Prototype pollution
    Fix: upgrade to 4.17.21 (available now)
    Reference: https://nvd.nist.gov/vuln/detail/CVE-2021-23337
    Status: UNFIXED (discovered 5 days ago)

[MEDIUM] ────────────────────────────────────────────────
  CVE-2021-41773 (axios)
    Package: axios 0.21.0
    Component: XXE in parameter parser
    Fix: upgrade to 0.27.0+ (available now)
    Status: UNFIXED (discovered 3 days ago)

  CVE-2021-32640 (ws)
    Package: ws 7.4.0
    Component: Buffer overflow in frame parsing
    Fix: upgrade to 8.0.0+ (available now)
    Status: UNFIXED

  CVE-2023-4807 (libc - in postgres:15 image)
    Component: Memory corruption in glibc malloc
    Fix: Rebuild image from postgres:15-alpine (fixed base image)
    Status: UNFIXED (image vulnerability)

  CVE-2024-1086 (OpenSSL - in postgres:15 image)
    Component: Key recovery in RSA operations
    Fix: Update Dockerfile to postgres:16 (has patch)
    Status: UNFIXED (image vulnerability)

View details: threat-radar cves <CVE-ID>
Set alert threshold: threat-radar config update --alert-level=medium
```

### Weekly Report

```bash
$ threat-radar report --period=week
┌─ SECURITY POSTURE REPORT (Feb 18 - Feb 24, 2026) ─────────────────────┐
│                                                                         │
│  Overall Score: 82/100 (was 85/100 on Feb 17)                         │
│                                                                         │
│  Metrics ────────────────────────────────────────────────────────────  │
│    Critical CVEs:      0 (↓ 0)                                          │
│    High CVEs:          1 (↑ 1, new: lodash)                            │
│    Medium CVEs:        4 (↔ 4)                                          │
│    Low CVEs:           2 (↓ 1, patched: urllib3)                       │
│    Unfixed vulnerabilities: 7 (↑ 2)                                    │
│    Average fix time: 1.8 hours (was 1.2)                               │
│                                                                         │
│  Trend Analysis ─────────────────────────────────────────────────────  │
│    Feb 17 (85/100) ↓ Feb 18 (83/100) ↓ Feb 19 (82/100) ↔ Feb 24      │
│    ⚠ Declining trend: +2 new CVEs found, zero patches applied         │
│                                                                         │
│  Action Items ──────────────────────────────────────────────────────── │
│    1. npm audit fix       — 3 packages, 15 min                         │
│    2. Update postgres:15  — rebuild from latest, 10 min                │
│    3. Review HSTS config  — grade B on example.com                     │
│                                                                         │
│  Docker Images (3 scanned) ──────────────────────────────────────────  │
│    openclaw-agent:latest    ✓ 0 CVEs                                  │
│    postgres:15              ⚠ 2 CVEs (libc, OpenSSL)                  │
│    redis:latest             ✓ 0 CVEs                                  │
│                                                                         │
│  Dependencies (npm + pip) ────────────────────────────────────────────  │
│    npm (workspace root)     ⚠ 3 High + Medium CVEs                    │
│      lodash, axios, ws                                                 │
│    pip (python deps)       ✓ 0 CVEs                                    │
│                                                                         │
│  Port Security (7 ports) ────────────────────────────────────────────  │
│    All ports on private network (10.0.0.0/8, 192.168.0.0/16) ✓       │
│                                                                         │
│  Next Actions ──────────────────────────────────────────────────────── │
│    □ Run: npm audit fix                                                │
│    □ Update base images: postgres:16 or postgres:15-alpine             │
│    □ Run: threat-radar scan (verify fixes)                             │
│                                                                         │
│  Alert Settings ────────────────────────────────────────────────────── │
│    Critical:  Alert immediately via WhatsApp                           │
│    High:      Daily digest (at 09:00 UTC)                              │
│    Medium:    Weekly report                                            │
│    Low:       Suppress (monthly audit only)                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

To apply remediations: threat-radar remediate --auto-npm
To stop alerts:        threat-radar config update --alert-level=critical
```

### Scheduled Scanning

```bash
$ threat-radar cron-install
✓ Installed daily security scan (09:00 UTC)
✓ Installed CVE feed refresh (every 6 hours)
✓ Installed weekly report (Monday 08:00 UTC)
✓ WhatsApp alerts: CRITICAL (immediate), HIGH (daily digest)

Cron schedule:
  - threat-radar scan         → daily 09:00 UTC
  - threat-radar data-refresh → every 6h (00:00, 06:00, 12:00, 18:00 UTC)
  - threat-radar report       → Monday 08:00 UTC

View logs: threat-radar logs [--tail=50]
```

---

## Installation

```bash
clawhub install threat-radar
```

## Configuration

Threat-radar stores config in `~/.openclaw/workspace/monitoring/threat-radar/config.json`:

```json
{
  "scan_paths": {
    "docker_images": true,
    "dependencies": ["npm", "pip"],
    "ports": true,
    "ssl_domains": ["example.com", "openclaw.local"],
    "openclaw_check": true,
    "exposed_scan": true
  },
  "alerts": {
    "critical": "immediate",
    "high": "daily_digest",
    "medium": "weekly",
    "low": "suppress"
  },
  "cve_feeds": ["nvd", "github"],
  "max_age_days": 30,
  "local_network_cidrs": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
  "ignored_cves": [],
  "watched_software": {}
}
```

Edit with: `threat-radar config update`

---

## How It Works

1. **Initialization** — Downloads latest CVE databases from NVD + GitHub Advisories (~500KB)
2. **Scanning** — Runs 7 security checks in parallel:
   - Docker image analysis (hashes vs CVE DB)
   - Dependency file parsing (npm/pip/cargo) → version extraction
   - Port scan (local network only, non-invasive)
   - SSL cert validation
   - Service exposure check (looks for :80, :443, :8080, etc. on public IPs)
   - OpenClaw config audit
3. **CVE Matching** — Compares detected versions against CVE database
4. **Alerting** — Dispatches alerts based on severity + cooldown
5. **History** — Stores scan results in SQLite (trend analysis)

**Performance:** Full scan ~30 seconds. CVE refresh ~10 seconds. Optimized for homelab scale.

---

## Integration with Other Skills

- **With infra-watchdog** — threat-radar feeds security events into watchdog alerts
- **With ops-journal** — CVE findings auto-logged for incident correlation
- **With daily-maintenance.sh** — integrated as Phase 8 (security scanning)

---

## Security Notes

- **Offline mode** — scans work without internet after initial CVE download
- **No credential exposure** — never scans credentials (security-hardener handles that)
- **Local network only** — port scanning stays within your private networks
- **Privacy** — no data sent external except NVD API calls (CVE checking)

---

## Troubleshooting

**Q: "CVE database outdated" warning**  
A: Run `threat-radar data-refresh` to pull latest feeds

**Q: Scan is slow**  
A: Disable slow checks: `threat-radar config update --skip-ports`

**Q: Too many alerts**  
A: Adjust severity: `threat-radar config update --alert-level=high`

**Q: False positive CVE**  
A: Mark as accepted risk: `threat-radar ignore CVE-XXXX-XXXXX`

---

## What's Next

- **Real-time CVE feed** (when a new vulnerability drops affecting you, know in minutes)
- **Remediation automation** (auto-file PRs to update dependencies)
- **Integration with vulnerability scanners** (nessus, qualys API)

---

## Support

For issues: Check `~/.openclaw/workspace/monitoring/threat-radar/threat-radar.log`

```bash
threat-radar logs --tail=100
threat-radar logs --follow  # Real-time logging
```

---

**Built for OpenClaw agents running homelab infrastructure.**
