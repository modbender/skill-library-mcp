# Crusty Security Setup Guide

## First Run

### 1. Run Setup

```bash
bash setup.sh
```

This automatically installs ClamAV if missing, creates data directories, and verifies everything works. No manual steps needed.

**ClamAV details:**
- Supported platforms: Ubuntu/Debian, RHEL/CentOS/Fedora, macOS (Homebrew)
- Auto-detects your OS and available RAM
- Low-RAM systems (<1GB): Automatically skips daemon mode, uses on-demand scanning
- To enable daemon mode manually (faster repeated scans, needs ≥2GB RAM): `bash scripts/install_clamav.sh --daemon`

### 2. Persistent Configuration (Optional)

Add to shell profile (`~/.bashrc`, `~/.zshrc`, or OpenClaw environment):

```bash
# Optional configuration
export CLAWGUARD_QUARANTINE="/tmp/clawguard_quarantine"
export CLAWGUARD_LOG_DIR="/tmp/clawguard_logs"
export CLAWGUARD_MAX_FILE_SIZE="200M"
export CLAWGUARD_WORKSPACE="/data/workspace"
```

## ClamAV Tuning

### Signature Updates
```bash
sudo freshclam              # Manual update
sudo systemctl start clamav-freshclam  # Start auto-update daemon
```

Recommended: run freshclam at least daily. Check freshness with `bash scripts/host_audit.sh`.

### Daemon vs On-Demand

| Mode | RAM | Speed | Use Case |
|------|-----|-------|----------|
| `clamd` (daemon) | ~800MB-1.2GB | <100ms/scan | Frequent scans, ≥2GB RAM |
| `clamscan` (on-demand) | ~300-500MB peak | 15-30s startup | Cron jobs, low-RAM hosts |

Enable daemon: `bash scripts/install_clamav.sh --daemon`

### Custom Signatures
Place `.ndb`, `.ldb`, or `.yar` files in `/var/lib/clamav/` (or equivalent for your OS).

## Recommended Scan Schedule

| Schedule | Command | Purpose |
|----------|---------|---------|
| Daily | `scripts/scan_file.sh --incremental -r /data/workspace` | Catch new threats fast |
| Weekly | `scripts/scan_file.sh -r /data/workspace` | Full scan |
| Daily | `scripts/monitor_agent.sh` | Agent integrity check |
| Weekly | `scripts/host_audit.sh` | Host security posture |
| Monthly | `scripts/host_audit.sh --deep` | Deep system audit |
| Weekly | `for d in skills/*/; do scripts/audit_skill.sh "$d"; done` | Skill supply chain audit |
| Weekly | `scripts/generate_report.sh --output /tmp/clawguard_logs/report.md` | Security report |
| On download | `scripts/scan_file.sh <file>` | Scan any downloaded file |
| Before install | `scripts/audit_skill.sh <skill_dir>` | Pre-install skill vetting |

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `CRUSTY_API_KEY` | (none) | Dashboard API key (from crustysecurity.com) |
| `CRUSTY_DASHBOARD_URL` | (none) | Dashboard URL |
| `CLAWGUARD_QUARANTINE` | `/tmp/clawguard_quarantine` | Where infected files are moved |
| `CLAWGUARD_LOG_DIR` | `/tmp/clawguard_logs` | Scan results and logs |
| `CLAWGUARD_MAX_FILE_SIZE` | `200M` | Max file size for ClamAV scanning |
| `CLAWGUARD_WORKSPACE` | `/data/workspace` | Agent workspace path for monitoring |
| `CLAWGUARD_FRESHCLAM_CONF` | (auto-detected) | Custom freshclam.conf path |

## Verification

After setup, verify everything works:

```bash
# Check ClamAV
clamscan --version

# Test file scan
echo "test" > /tmp/clawguard_test.txt
bash scripts/scan_file.sh /tmp/clawguard_test.txt
rm /tmp/clawguard_test.txt

# Test skill audit
bash scripts/audit_skill.sh /data/workspace/skills/clawguard/

# Test agent monitor
bash scripts/monitor_agent.sh

# Test host audit
bash scripts/host_audit.sh
```
