---
name: pc-assistant
description: PC healthcheck and diagnostics with detailed system information and actionable recommendations. Works on Windows, macOS, and Linux. Read-only system diagnostics. Supports scheduling via cron.
author: Muhammad Hakim
---

# PC Assistant - Healthcheck Skill

## Overview

This skill runs a comprehensive PC healthcheck that provides detailed system information along with actionable recommendations to fix any issues found. **Supports Windows, macOS, and Linux.**

## When to Use

- User asks for a "PC healthcheck", "system check", or "diagnostics"
- User wants to check storage, CPU, memory, GPU, or network
- User asks "how is my PC doing?" or "is everything ok?"
- User needs specific recommendations to fix issues (like low disk space)

## Requirements

- **Platform**: Windows, macOS, or Linux (including WSL)
- **Permissions**: Read-only for most checks
- **Tools used**: Platform-specific system utilities

## Execute Healthcheck

The skill automatically detects your OS and runs the appropriate script:

```bash
~/.npm-global/lib/node_modules/openclaw/skills/pc-assistant/scripts/healthcheck.sh    # Linux/WSL
~/.npm-global/lib/node_modules/openclaw/skills/pc-assistant/scripts/healthcheck.ps1   # Windows
~/.npm-global/lib/node_modules/openclaw/skills/pc-assistant/scripts/healthcheck.command  # macOS
```

Or use the convenience wrapper (auto-detects OS):

```bash
~/.npm-global/lib/node_modules/openclaw/skills/pc-assistant/scripts/run.sh
```

The script outputs:
- `healthcheck_YYYYMMDD_HHMMSS.txt` - Full human-readable report with recommendations
- `healthcheck_YYYYMMDD_HHMMSS.json` - JSON summary

## Platform-Specific Features

### Linux/WSL
- System overview (OS, kernel, uptime)
- Storage & disk (df, partitions, SMART)
- Network (interfaces, routes, DNS, ports)
- Processes & services (systemctl)
- Users & security (SSH keys, failed logins)
- Package management (apt, npm, pip)
- Containers (Docker, Podman)
- GPU info (nvidia-smi)
- Hardware (USB, PCI, temperature)

### Windows (PowerShell)
- System overview (Win32_OperatingSystem)
- CPU & memory (Win32_Processor, Win32_OperatingSystem)
- Storage (Win32_LogicalDisk)
- Network adapters
- Processes (Get-Process)
- Services (Get-Service)
- Installed software (registry)
- Security (Firewall, Windows Defender)
- Event logs

### macOS
- System overview (sw_vers, system_profiler)
- CPU & memory (vm_stat, sysctl)
- Storage (diskutil)
- Network (ifconfig, airport)
- Processes (ps)
- Launch agents & daemons
- Security (Firewall, Gatekeeper, FileVault)
- Homebrew packages
- Battery status

## What the Healthcheck Captures

| Section | Information |
|---------|-------------|
| **System Overview** | OS, kernel, uptime, user, shell |
| **CPU** | Model, cores, speed, usage |
| **Memory** | Total, free, used, percentage |
| **Storage** | Disk usage, partitions, SMART status |
| **Network** | Interfaces, IP addresses, DNS |
| **Processes** | Top CPU/memory consumers |
| **Services** | Running/stopped services |
| **Security** | Firewall, antivirus status |
| **Software** | Installed packages & apps |
| **Hardware** | GPU, USB, temperature |
| **Summary** | Health score + recommendations |

## Recommendations Included

The report automatically includes specific recommendations when issues are detected:

### Storage Issues (High disk usage)
- Specific folders to check
- Platform-specific cleanup instructions
- Docker/container cleanup commands

### Memory Issues
- How to free up RAM
- Which apps to close

### General Maintenance
- System update commands
- Security best practices

## Scheduling (Cron Jobs)

The skill includes a scheduler script for automated periodic healthchecks:

### Quick Start

```bash
# Run with defaults (saves to /tmp/pc-healthcheck-reports)
~/.npm-global/lib/node_modules/openclaw/skills/pc-assistant/scripts/schedule.sh

# Custom output folder
PC_ASSISTANT_OUTPUT_DIR="$HOME/Downloads/pc-assistant reports" \
  ~/.npm-global/lib/node_modules/openclaw/skills/pc-assistant/scripts/schedule.sh
```

### Configuration Options

Create a config file at `~/.config/pc-assistant.conf`:

```bash
# Output directory for reports
PC_ASSISTANT_OUTPUT_DIR="$HOME/Downloads/pc-assistant reports"

# Report filename prefix
PC_ASSISTANT_REPORT_PREFIX="HealthCheck"

# Days to keep old reports (default: 30)
PC_ASSISTANT_KEEP_DAYS=30

# Enable automatic cleanup of old reports
PC_ASSISTANT_CLEANUP=true
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PC_ASSISTANT_OUTPUT_DIR` | `/tmp/pc-healthcheck-reports` | Where to save reports |
| `PC_ASSISTANT_REPORT_PREFIX` | `HealthCheck` | Filename prefix |
| `PC_ASSISTANT_KEEP_DAYS` | `30` | Days to keep reports |
| `PC_ASSISTANT_CLEANUP` | `false` | Auto-delete old reports |
| `PC_ASSISTANT_CONFIG` | `~/.config/pc-assistant.conf` | Config file path |

### Cron Job Example

```bash
# Add to crontab (runs daily at midnight)
0 0 * * * PC_ASSISTANT_OUTPUT_DIR="$HOME/Downloads/pc-assistant reports" \
  ~/.npm-global/lib/node_modules/openclaw/skills/pc-assistant/scripts/schedule.sh
```

## Output

Reports are saved to:
- **Linux/WSL**: `/tmp/pc-healthcheck/` (or custom via config)
- **Windows**: `$env:TEMP\pc-healthcheck\` (usually `C:\Users\...\AppData\Local\Temp\pc-healthcheck\`)
- **macOS**: `/tmp/pc-healthcheck/`

When using scheduler: `HealthCheck_YYYYMMDD_HHMMSS.txt` and `.json`

## Tips

- The script is read-only and safe to run multiple times
- Reports are timestamped for historical tracking
- Use JSON output for integration with monitoring
- Set `PC_ASSISTANT_CLEANUP=true` to auto-remove old reports