---
name: vps-health-auditor
description: Runs comprehensive diagnostics (CPU, RAM, disk, network, services,
  uptime) via SSH/local exec, analyzes with Ollama LLM for actionable insights.
---


# VPS Health Auditor v1.0.0

## 🎯 Purpose
Detect issues on Linux VPS/servers early. Checks:
- System resources (CPU, mem, disk usage)
- Network latency/bandwidth
- Key services (SSH, web server, DB)
- Uptime & logs
Generates PDF/HTML report via Ollama.

## 🚀 Quick Start
```
!vps-health-auditor --host example.com --user root --key ~/.ssh/id_rsa
```

## Files
- `scripts/healthcheck.sh`: Multi-platform audit script (Ubuntu/CentOS/Debian)
- `reports/template.md`: Ollama prompt for report gen

## Customization
Edit `scripts/healthcheck.sh` for custom checks. Add Ollama model in triggers.
