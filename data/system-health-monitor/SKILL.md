---
name: system-health-monitor
description: "System health and security monitoring skill with 8-layer monitoring system. Provides real-time health scoring, security reporting, and performance analysis. Use when: checking system status, monitoring security events, or generating health reports."
homepage: https://github.com/openclaw/openclaw
author: "ZLMbot 🦞"
license: MIT
metadata: { "openclaw": { "emoji": "🏥", "requires": { "bins": ["systemctl", "jq"], "os": "linux" }, "tags": ["monitoring", "security", "health", "system"] } }
---

# System Health Monitor

System health and security monitoring skill with 8-layer monitoring system.

## Description

This skill provides real-time status reports, alerting, and historical analysis of system performance and security by integrating with the 8-layer monitoring infrastructure.

## When to Use

✅ **USE this skill when:**
- Checking overall system health status
- Monitoring security events and threats
- Analyzing system performance trends
- Generating health reports
- Investigating monitoring alerts
- Reviewing fail2ban activity

❌ **DON'T use this skill when:**
- Modifying system configuration → use system administration tools
- Installing packages → use apt/yum
- Managing user accounts → use useradd/usermod

## Usage

### Quick Health Check
```bash
/health status
```

### Detailed System Report
```bash
/health report
```

### Check Specific Monitoring Layer (1-8)
```bash
/health layer 3      # Check heartbeat monitoring
/health layer 6      # Check package integrity monitoring
```

### Security Overview
```bash
/health security
```

## Configuration

Optional configuration file at `config/health-monitor.json`:
```json
{
  "alert_threshold": 80,
  "report_frequency": "hourly",
  "notify_on_critical": true,
  "telegram_channel_id": "",
  "monitored_services": [
    "ssh-login-monitor",
    "heartbeat-monitor",
    "package-integrity-monitor"
  ]
}
```

## Monitoring Layers (8-Layer System)

| Layer | Service | Integration |
|-------|---------|-------------|
| 1 | SSH Login Monitor | Real-time login tracking |
| 2 | Heartbeat Monitor | Advanced health checks |
| 3 | Outbound Traffic Monitor | Network security |
| 4 | UFW Firewall | Network layer protection |
| 5 | Package Integrity Monitor | Software security |
| 6 | Report Monitor | Automated reporting |
| 7 | Cleanup Monitor | System maintenance |
| 8 | Internal Security Monitor | Network threat detection |

## Features

- **Real-time Health Scoring**: 0-100 score based on monitoring layer status
- **Alert System**: Notify on critical issues via Telegram
- **Historical Analysis**: Track system performance trends
- **Security Dashboard**: Consolidated security status view
- **Automated Reports**: Generate daily/weekly health reports

## Commands

### Get Current Status
```bash
bash scripts/health-check.sh status
```

### Generate Report
```bash
bash scripts/health-check.sh report
```

## Requirements

- **OS**: Linux (systemd-based distributions)
- OpenClaw Gateway running
- Systemd monitoring services enabled
- Dependencies: `systemctl`, `jq`
- Optional: `fail2ban`, `ufw` (for security features)

## Skill Development Details

- **Version**: 1.1.1
- **Author**: ZLMbot 🦞
- **Created**: 2026-02-28
- **Updated**: 2026-03-01 (fixed security scan issues)
- **License**: MIT

---
**Status**: 🟢 Active  
**Monitoring System**: ✅ 8-layer system  
**Last Updated**: 2026-03-01
